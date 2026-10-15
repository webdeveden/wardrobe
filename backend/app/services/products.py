from sqlalchemy.orm import joinedload, selectinload

from app.models import Product

# Eager-load everything a ProductOut needs in a fixed number of queries (no N+1).
PRODUCT_LOAD_OPTIONS = (
    joinedload(Product.category),
    joinedload(Product.era),
    selectinload(Product.images),
)
