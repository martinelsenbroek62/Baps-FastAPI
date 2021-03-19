import logging
from typing import List
from pprint import pformat

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.demand_revision import DemandRevision
from app.schemas.demand_revision import DemandRevisionCreate, DemandRevisionUpdate

logger = logging.getLogger(__name__)


class CRUDDemandRevision(
    CRUDBase[DemandRevision, DemandRevisionCreate, DemandRevisionUpdate]
):
    @staticmethod
    def get_demand_revisions(db: Session) -> List[DemandRevision]:
        demand_revisions = db.query(DemandRevision).all()
        logger.debug(f"Demand Revision List\n{pformat(demand_revisions)}")
        return demand_revisions

    @staticmethod
    def get_demand_revisions_count(db: Session, month: int, year: int) -> int:
        demand_revisions_count = (
            db.query(DemandRevision)
            .filter(sa.func.extract("year", DemandRevision.revision_date) == year)
            .filter(sa.func.extract("month", DemandRevision.revision_date) == month)
            .count()
        )
        logger.debug(f"Found {demand_revisions_count} for year-month {year}-{month}")

        return demand_revisions_count


demand_revision = CRUDDemandRevision(DemandRevision)
