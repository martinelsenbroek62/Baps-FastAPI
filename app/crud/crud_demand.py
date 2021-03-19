import logging
from typing import Any, Dict, Optional, Union, List
from pprint import pformat, pprint

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.demand import Demand
from app.schemas.demand import DemandCreate, DemandUpdate

logger = logging.getLogger(__name__)

# pylint not working with python 3.9 for now
# pylint: disable=unsubscriptable-object
class CRUDDemand(CRUDBase[Demand, DemandCreate, DemandUpdate]):
    # def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
    #     return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_sku(db: Session, *, sku: str) -> Optional[List[Demand]]:
        demand_list = db.query(Demand).filter(Demand.sku == sku).all()
        pprint(demand_list)
        pprint(type(demand_list[0].month))
        return demand_list

    @staticmethod
    def get_demand(db: Session, _all: bool, revision: int) -> List[List[Demand]]:
        if _all:
            demand_list = db.query(Demand).all()
            logger.debug(f"Demand List (all)\n{pformat(demand_list)}")
            return demand_list

        if revision:
            demand_list = db.query(Demand).filter(Demand.revision_id == revision).all()
            logger.debug(f"Demand List for Revision {revision}\n{pformat(demand_list)}")
            return demand_list

        demand_list = (
            db.query(Demand)
            .filter(Demand.revision_id == db.query(func.max(Demand.revision_id)))
            .all()
        )
        logger.debug(f"Demand List for latest revision\n{pformat(demand_list)}")
        return demand_list

    def create_all(
        self, db: Session, *, create_demand: List[DemandCreate]
    ) -> List[DemandCreate]:
        demand_json = [jsonable_encoder(obj_in) for obj_in in create_demand]
        demand_models = [self.model(**obj_json) for obj_json in demand_json]
        db.add_all(demand_models)
        db.commit()
        # db.refresh(demand)
        return create_demand

    def update(
        self,
        db: Session,
        *,
        db_obj: Demand,
        obj_in: Union[DemandUpdate, Dict[str, Any]],
    ) -> Demand:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        # if update_data["password"]:
        #     hashed_password = get_password_hash(update_data["password"])
        #     del update_data["password"]
        #     update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)


demand = CRUDDemand(Demand)
