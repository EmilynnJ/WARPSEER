from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token
from ..config import settings

router = APIRouter(prefix="/cms", tags=["cms"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _ensure_admin(token):
    email = token.get("email")
    if not email or email.lower() != settings.admin_email.lower():
        raise HTTPException(403, "Admins only")

@router.get("/{slug}")
async def get_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(models.CmsPage).filter(models.CmsPage.slug == slug).one_or_none()
    if not page:
        # Return empty page shell so admin can populate later
        return {"slug": slug, "title": slug.replace('-', ' ').title(), "html_content": ""}
    return {"slug": page.slug, "title": page.title, "html_content": page.html_content}

@router.post("/{slug}")
async def upsert_page(slug: str, payload: dict, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    _ensure_admin(token)
    title = payload.get("title") or slug.replace('-', ' ').title()
    html = payload.get("html_content", "")
    page = db.query(models.CmsPage).filter(models.CmsPage.slug == slug).one_or_none()
    if not page:
        page = models.CmsPage(slug=slug, title=title, html_content=html)
        db.add(page)
    else:
        page.title = title
        page.html_content = html
        db.add(page)
    db.commit()
    return {"ok": True}