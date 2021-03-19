import calendar
import logging
from datetime import datetime, timezone
from io import StringIO
from pprint import pprint
from typing import List

import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.routes.deps import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/sku/{sku}", response_model=List[schemas.Demand])
def read_demand_sku(sku: str, db: Session = Depends(get_db)):
    demand = crud.demand.get_by_sku(db=db, sku=sku)
    return demand


@router.get("/revisions", response_model=List[schemas.DemandRevision])
def read_demand_revisions(db: Session = Depends(get_db)):
    revisions = crud.demand_revision.get_demand_revisions(db=db)
    return revisions


@router.get("/t", response_model=List[schemas.DemandFull])
def read_demand(db: Session = Depends(get_db), _all: bool = False, revision: int = 0):
    demand = crud.demand.get_demand(db=db, _all=_all, revision=revision)
    logger.info(pprint(demand))

    if demand:
        df_month = pd.DataFrame.from_dict(
            [schemas.Demand.from_orm(d).dict() for d in demand]
        )
        df_qtr = df_month.groupby(
            ["revision_id", "sku", "demand_center_id", "year", "quarter"]
        ).sum()
        df_yr = df_month.groupby(
            ["revision_id", "sku", "demand_center_id", "year"]
        ).sum()
        print(df_month)
        print(df_qtr.reset_index().drop(columns=["month"]))
        print(df_yr.reset_index().drop(columns=["month"]))

    return demand


def group_is_actual(df: pd.DataFrame):
    if df["is_actual"].all():
        df["is_actual"] = 1
    else:
        df["is_actual"] = 0

    return df


@router.get("/", response_model=schemas.DemandSummary)
def read_demand_summary(
    db: Session = Depends(get_db), _all: bool = False, revision: int = 0
):
    if revision == 0 and _all is False:
        return schemas.DemandSummary(
            monthly=[],
            quarterly=[],
            yearly=[]
        )
    
    demand = crud.demand.get_demand(db=db, _all=_all, revision=revision)
    pprint(demand)

    df_month = pd.DataFrame.from_dict(
        [schemas.Demand.from_orm(d).dict() for d in demand]
    )
    df_qtr = (
        df_month.groupby(  # pylint: disable=no-member
            ["revision_id", "sku", "year", "quarter"]
        )
        .apply(group_is_actual)
        .groupby(["revision_id", "sku", "year", "quarter"])
        .sum()
        .assign(is_actual=lambda _df: _df["is_actual"].astype(bool))
        .reset_index()
        .drop(columns=["month", "demand_center_id"])
    )
    df_yr = (
        df_month.groupby(["revision_id", "sku", "year"])  # pylint: disable=no-member
        .apply(group_is_actual)
        .groupby(["revision_id", "sku", "year"])
        .sum()
        .assign(is_actual=lambda _df: _df["is_actual"].astype(bool))
        .reset_index()
        .drop(columns=["month", "demand_center_id"])
    )

    pprint(
        {
            "monthly": [
                schemas.Demand(**r) for r in df_month.to_dict(orient="records")
            ],
            "quarterly": [
                schemas.DemandQuarter(**r) for r in df_qtr.to_dict(orient="records")
            ],
            "yearly": [
                schemas.DemandYear(**r) for r in df_yr.to_dict(orient="records")
            ],
        }
    )

    return schemas.DemandSummary(
        monthly=[schemas.Demand(**r) for r in df_month.to_dict(orient="records")],
        quarterly=[
            schemas.DemandQuarter(**r) for r in df_qtr.to_dict(orient="records")
        ],
        yearly=[schemas.DemandYear(**r) for r in df_yr.to_dict(orient="records")],
    )

    # return demand


def perform_calcs(df) -> pd.DataFrame:
    return df.assign(
        accuracy=lambda _df: 1
        - (abs(_df["demand_1"] - _df["demand_2"]) / _df["demand_1"]),
        tracking_signals=lambda _df: (_df["demand_1"] - _df["demand_2"])
        / abs(_df["demand_1"] - _df["demand_2"]),
        bias=lambda _df: (_df["demand_1"] - _df["demand_2"]).sum() / _df.shape[0],
        mad=lambda _df: abs((_df["demand_1"] - _df["demand_2"])).sum() / _df.shape[0],
        mse=lambda _df: ((_df["demand_1"] - _df["demand_2"]) ** 2).sum() / _df.shape[0],
        mape=lambda _df: abs(
            (_df["demand_1"] - _df["demand_2"]) / _df["demand_1"]
        ).sum()
        / _df.shape[0],
        smape=lambda _df: (
            (
                abs(_df["demand_2"] - _df["demand_1"])
                / (abs(_df["demand_1"]) + abs(_df["demand_2"]))
                / 2
            ).sum()
            / _df.shape[0]
        ),
        wmape=lambda _df: (
            (abs(_df["demand_1"] - _df["demand_2"])).sum() / _df["demand_1"].sum()
        ),
    )


def perform_f_calcs(df) -> pd.DataFrame:
    return df.assign(
        difference=lambda _df: _df["demand_1"] - _df["demand_2"],
        difference_percentage=lambda _df: (_df["demand_1"] - _df["demand_2"])
        / ((_df["demand_1"] + _df["demand_2"]) / 2),
    )


@router.get("/variance", response_model=schemas.VarianceSummary)
def calculate_variance(rev1: int, rev2: int, db: Session = Depends(get_db)):
    rev1_demand = crud.demand.get_demand(db=db, _all=False, revision=rev1)
    rev2_demand = crud.demand.get_demand(db=db, _all=False, revision=rev2)

    rev1_demand = pd.DataFrame.from_dict(
        [schemas.Demand.from_orm(d).dict() for d in rev1_demand]
    ).assign(date=lambda _df: pd.to_datetime(_df["date"]))
    rev2_demand = pd.DataFrame.from_dict(
        [schemas.Demand.from_orm(d).dict() for d in rev2_demand]
    ).assign(date=lambda _df: pd.to_datetime(_df["date"]))

    # sum over demand center
    merged = pd.merge(
        left=rev1_demand,
        right=rev2_demand,
        how="outer",
        on=["sku", "date", "year", "quarter", "month", "demand_center_id"],
        suffixes=("_1", "_2"),
    )

    pprint(merged.columns)
    forecasts = merged[
        (merged["is_actual_1"] == False)  # pylint: disable=singleton-comparison
        & (merged["is_actual_2"] == False)  # pylint: disable=singleton-comparison
    ]
    forecasts = forecasts.groupby(by=["sku"]).apply(perform_calcs)
    forecasts.to_csv("fvf.csv")

    avf = merged[
        (merged["is_actual_1"] == True)  # pylint: disable=singleton-comparison
        & (merged["is_actual_2"] == False)  # pylint: disable=singleton-comparison
    ]
    avf.to_csv("avf.csv")
    avf = avf.groupby(by=["sku"]).apply(perform_f_calcs)

    return schemas.VarianceSummary(
        actual=[schemas.VarianceActual(**r) for r in avf.to_dict(orient="records")],
        forecast=[
            schemas.VarianceForecast(**r) for r in forecasts.to_dict(orient="records")
        ],
    )


@router.post("/upload")
def create_file(
    file: UploadFile = File(...),
    description: str = Body(...),
    db=Depends(get_db),
):
    demand_revision = None
    try:
        df = pd.read_csv(file.file, parse_dates=["month"])
        logger.debug(str(df.head()))
        # validate csv

        # fetch demand centers
        demand_centers = crud.demand_center.get_demand_centers(db=db)
        demand_centers_dict = {d.name: d.id for d in demand_centers}

        # create revision
        this_date = datetime.now(timezone.utc)
        existing_revisions_count = crud.demand_revision.get_demand_revisions_count(
            db=db, month=this_date.month, year=this_date.year
        )

        demand_revision = crud.demand_revision.create(
            db=db,
            obj_in=schemas.DemandRevisionCreate(
                description=description,
                name=(
                    f"{calendar.month_name[this_date.month]} "
                    f"{this_date.year} v{existing_revisions_count}"
                ),
                revision_date=this_date,
                user_id=1,
            ),
        )
        logger.debug(str(demand_revision))

        new_demand = [
            schemas.DemandCreate(
                revision_id=demand_revision.id,
                sku=r.sku,
                demand=r.demand,
                date=r.month.date(),
                demand_center_id=demand_centers_dict[r.demand_center],
            )
            for r in df.itertuples()
        ]

        crud.demand.create_all(db=db, create_demand=new_demand)

        return {"status": "success"}
    except Exception:  # pylint: disable=broad-except
        if demand_revision:
            crud.demand_revision.remove(db=db, id=demand_revision.id)
    finally:
        file.file.close()


@router.get("/download")
def download_file(revision: int, db: Session = Depends(get_db)):
    demand = crud.demand.get_demand(db=db, _all=False, revision=revision)
    demand_data = [
        {
            "sku": d.sku,
            "demand": d.demand,
            "demand_center": d.demand_center.name,
            "month": d.date,
        }
        for d in demand
    ]
    df = pd.DataFrame(demand_data)
    str_buffer = StringIO()
    df.to_csv(str_buffer, index=False)
    str_buffer.seek(0)

    return StreamingResponse(
        str_buffer,
        headers={"Content-Disposition": 'attachment; filename="demand_forecast.csv"'},
        media_type="text/csv",
    )
