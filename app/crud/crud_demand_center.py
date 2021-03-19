import logging
from typing import List
from pprint import pformat

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.demand_center import DemandCenter
from app.schemas.demand_center import DemandCenterCreate, DemandCenterUpdate

logger = logging.getLogger(__name__)


class CRUDDemandCenter(CRUDBase[DemandCenter, DemandCenterCreate, DemandCenterUpdate]):
    @staticmethod
    def get_demand_centers(db: Session) -> List[DemandCenter]:
        demand_centers = db.query(DemandCenter).all()
        logger.debug(f"Demand Centers List\n{pformat(demand_centers)}")
        return demand_centers


demand_center = CRUDDemandCenter(DemandCenter)
