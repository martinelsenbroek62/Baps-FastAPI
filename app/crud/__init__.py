from .crud_user import user
from .crud_demand import demand
from .crud_demand_revision import demand_revision
from .crud_demand_center import demand_center

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
