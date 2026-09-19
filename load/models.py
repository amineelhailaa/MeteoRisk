
from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class City(Base):
    __tablename__ = "cities"
    __table_args__ = (
        UniqueConstraint(
            "name",
            "country",
            "latitude",
            "longitude",
            name="uq_city_identity",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    forecasts = relationship(
        "Forecast",
        back_populates="city",
        cascade="all, delete-orphan",
    )


class Forecast(Base):
    __tablename__ = "forecasts"
    __table_args__ = (
        UniqueConstraint(
            "city_id",
            "forecast_date",
            "source",
            name="uq_forecast_city_date_source",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    city_id = Column(
        BigInteger,
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
    )
    forecast_date = Column(Date, nullable=False)
    extracted_at = Column(DateTime(timezone=True), nullable=False)
    source = Column(String(50), nullable=False, default="open-meteo")
    weather_code = Column(Integer, nullable=False)

    city = relationship("City", back_populates="forecasts")
    temperature = relationship(
        "Temperature",
        back_populates="forecast",
        uselist=False,
        cascade="all, delete-orphan",
    )
    precipitation = relationship(
        "Precipitation",
        back_populates="forecast",
        uselist=False,
        cascade="all, delete-orphan",
    )
    wind = relationship(
        "Wind",
        back_populates="forecast",
        uselist=False,
        cascade="all, delete-orphan",
    )
    risk_assessment = relationship(
        "RiskAssessment",
        back_populates="forecast",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Temperature(Base):
    __tablename__ = "temperatures"

    forecast_id = Column(
        BigInteger,
        ForeignKey("forecasts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    temperature_min = Column(Float, nullable=False)
    temperature_max = Column(Float, nullable=False)
    category = Column(String(30), nullable=True)

    forecast = relationship("Forecast", back_populates="temperature")


class Precipitation(Base):
    __tablename__ = "precipitations"

    forecast_id = Column(
        BigInteger,
        ForeignKey("forecasts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    precipitation_sum = Column(Float, nullable=False)
    probability_max = Column(Float, nullable=False)
    category = Column(String(30), nullable=True)

    forecast = relationship("Forecast", back_populates="precipitation")


class Wind(Base):
    __tablename__ = "winds"

    forecast_id = Column(
        BigInteger,
        ForeignKey("forecasts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    speed_10m_max = Column(Float, nullable=False)
    gusts_10m_max = Column(Float, nullable=False)
    category = Column(String(30), nullable=True)

    forecast = relationship("Forecast", back_populates="wind")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    forecast_id = Column(
        BigInteger,
        ForeignKey("forecasts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    risk_score = Column(Float, nullable=False)
    weather_score = Column(Float, nullable=True)
    risk_level = Column(String(30), nullable=True)

    forecast = relationship("Forecast", back_populates="risk_assessment")
