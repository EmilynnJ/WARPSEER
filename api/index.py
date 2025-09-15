import sys
import os
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "apps" / "backend" / "src"
sys.path.insert(0, str(backend_path))

# Import your FastAPI app
from soulseer.main import app

# Create handler for Vercel
def handler(request, context):
    """Vercel serverless function handler"""
    from mangum import Mangum
    handler = Mangum(app)
    return handler(request, context)