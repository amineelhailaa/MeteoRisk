from sqlalchemy import create_engine,select, func
from sqlalchemy.orm import Session
from load.models import *

engine = create_engine("postgresql://postgres:postgres@postgres:5432/postgres")
with Session(engine) as session:
    stmt_cities_max_temp = (
        select(City, func.max(Temperature.temperature_max).label("max_temp"))
        .join(City.forecasts)
        .join(Forecast.temperature)
        .group_by(City.id)
        .order_by(func.max(Temperature.temperature_max).desc())
        .limit(5)
    )

    stmt_cities_max_rain = (
        select(City, func.max(Precipitation.precipitation_sum).label("max_rain"))
        .join(City.forecasts)
        .join(Forecast.precipitation)
        .group_by(City.id)
        .order_by(func.max(Precipitation.precipitation_sum).desc())
        .limit(5)
    )

    stmt_cities_max_risk = (
      select(
          City.name,
          func.avg(RiskAssessment.risk_score).label("average_risk"),
      )
      .join(City.forecasts)
      .join(Forecast.risk_assessment)
      .group_by(City.id, City.name)
      .order_by(func.avg(RiskAssessment.risk_score).desc())
        .limit(5)
  )

    stmt_period_max_risk = (
        select(
            Forecast.forecast_date,
            func.max(RiskAssessment.risk_score).label("max_risk")
        ).join(Forecast.risk_assessment)
        .group_by(Forecast.forecast_date)
        .order_by(func.max(RiskAssessment.risk_score).desc())
    )

    stmt_city_period_max_risk = (
        select(
            City.name,
            Forecast.forecast_date,
            RiskAssessment.risk_score,
            func.row_number().over(
                partition_by=City.id,
                order_by=RiskAssessment.risk_score.desc(),
            ).label("rank_period")
        ).join(City.forecasts)
        .join(Forecast.risk_assessment)
    )

    ranked =  stmt_city_period_max_risk.subquery()
    stmt_top_3_per_city = (
        select(ranked.c.name, ranked.c.forecast_date,ranked.c.risk_score, ranked.c.rank_period)
        .where(ranked.c.rank_period <= 3)
    )



    stmt_count_cities1 = select(func.count(func.distinct(City.name)))
    stmt_count_cities2 = select(func.count(City.id))
    stmt_max_temp = select(func.max(Temperature.temperature_max))
    stmt_max_rain = select(func.max(Precipitation.precipitation_sum))



    results_cities_max_temp = session.execute(stmt_cities_max_temp).all()
    results_cities_max_rain = session.execute(stmt_cities_max_rain).all()
    results_cities_max_risk = session.execute(stmt_cities_max_risk).all()
    results_period_max_risk = session.execute(stmt_period_max_risk).all()
    results_top_3_per_city = session.execute(stmt_top_3_per_city).all()
    results_count_cities_distinct = session.execute(stmt_count_cities1).scalar_one()
    results_count_cities = session.execute(stmt_count_cities2).scalar_one()
    results_max_temp = session.execute(stmt_max_temp).scalar_one()
    results_max_rain = session.execute(stmt_max_rain).scalar_one()










