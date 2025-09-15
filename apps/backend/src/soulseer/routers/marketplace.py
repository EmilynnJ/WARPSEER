from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token
from ..config import settings
import stripe
import secrets

router = APIRouter(prefix="/marketplace", tags=["marketplace"])
stripe.api_key = settings.stripe_secret_key

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sync")
async def sync_products(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    """Sync products from Stripe catalog"""
    # Admin only
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    if user.email.lower() != settings.admin_email.lower():
        raise HTTPException(403, "Admin only")
    
    # Fetch from Stripe
    products = stripe.Product.list(active=True, limit=100)
    
    for sp in products.data:
        # Check if exists
        existing = db.query(models.Product).filter(
            models.Product.stripe_product_id == sp.id
        ).one_or_none()
        
        # Get default price
        prices = stripe.Price.list(product=sp.id, active=True, limit=1)
        price_cents = prices.data[0].unit_amount if prices.data else 0
        
        if existing:
            existing.name = sp.name
            existing.active = sp.active
            existing.description = sp.description or ""
            existing.price_cents = price_cents
            existing.image_url = sp.images[0] if sp.images else ""
        else:
            product = models.Product(
                stripe_product_id=sp.id,
                name=sp.name,
                kind=sp.metadata.get('kind', 'digital'),
                active=sp.active,
                description=sp.description or "",
                price_cents=price_cents,
                image_url=sp.images[0] if sp.images else "",
                stock_quantity=-1  # Unlimited by default
            )
            db.add(product)
    
    db.commit()
    return {"ok": True}

@router.get("/products")
async def list_products(kind: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Product).filter(models.Product.active == True)
    if kind:
        query = query.filter(models.Product.kind == kind)
    
    products = query.all()
    return {
        "items": [
            {
                "id": p.id,
                "stripe_product_id": p.stripe_product_id,
                "name": p.name,
                "description": p.description,
                "price_cents": p.price_cents,
                "image_url": p.image_url,
                "kind": p.kind,
                "stock_quantity": p.stock_quantity,
                "reader_id": p.reader_id
            }
            for p in products
        ]
    }

@router.post("/checkout")
async def create_checkout(payload: dict, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    """Create order and process payment"""
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    items = payload.get('items', [])
    shipping_address = payload.get('shipping_address')
    
    if not items:
        raise HTTPException(400, "No items in cart")
    
    total_cents = 0
    order_items = []
    
    for item in items:
        product = db.query(models.Product).filter(
            models.Product.id == item['product_id']
        ).one_or_none()
        
        if not product or not product.active:
            raise HTTPException(404, f"Product {item['product_id']} not available")
        
        # Check stock
        if product.stock_quantity != -1 and product.stock_quantity < item.get('quantity', 1):
            raise HTTPException(400, f"Insufficient stock for {product.name}")
        
        item_total = product.price_cents * item.get('quantity', 1)
        total_cents += item_total
        
        order_items.append({
            'product': product,
            'quantity': item.get('quantity', 1),
            'price_cents': product.price_cents
        })
    
    # Debit wallet
    from ..services.wallet import debit
    try:
        debit(db, user.id, total_cents, ref_type='order', ref_id='pending')
    except:
        raise HTTPException(402, "Insufficient balance")
    
    # Create order
    order = models.Order(
        order_uid=secrets.token_urlsafe(12),
        buyer_id=user.id,
        total_cents=total_cents,
        status='paid'
    )
    db.add(order)
    db.flush()
    
    # Add order items
    for oi in order_items:
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=oi['product'].id,
            quantity=oi['quantity'],
            price_cents=oi['price_cents']
        )
        db.add(order_item)
        
        # Update stock
        if oi['product'].stock_quantity != -1:
            oi['product'].stock_quantity -= oi['quantity']
        
        # Credit reader if product belongs to one
        if oi['product'].reader_id:
            from ..services.billing import credit_reader
            reader_amount = oi['price_cents'] * oi['quantity'] * settings.reader_share_pct // 100
            credit_reader(db, oi['product'].reader_id, reader_amount, ref_type='order', ref_id=order.order_uid)
    
    # Add shipping address if physical products
    if shipping_address and any(oi['product'].kind == 'physical' for oi in order_items):
        addr = models.ShippingAddress(
            order_id=order.id,
            name=shipping_address.get('name', ''),
            address_line1=shipping_address.get('address_line1', ''),
            address_line2=shipping_address.get('address_line2', ''),
            city=shipping_address.get('city', ''),
            state=shipping_address.get('state', ''),
            postal_code=shipping_address.get('postal_code', ''),
            country=shipping_address.get('country', 'US')
        )
        db.add(addr)
    
    db.commit()
    return {"order_uid": order.order_uid, "total_cents": total_cents}

@router.get("/orders")
async def list_orders(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    orders = db.query(models.Order).filter(
        models.Order.buyer_id == user.id
    ).order_by(models.Order.id.desc()).limit(50).all()
    
    return {
        "items": [
            {
                "order_uid": o.order_uid,
                "total_cents": o.total_cents,
                "status": o.status
            }
            for o in orders
        ]
    }