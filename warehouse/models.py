from sqlalchemy import (
    Column, Integer, Numeric, Enum, DateTime, ForeignKey
)
from sqlalchemy.sql import func
import enum
from .database import Base


class StatusTruck(enum.Enum):
    AVAILABLE = "AVAILABLE"
    LOADED    = "LOADED"
    MAINT      = "MAINTENANCE"


class StatusPackage(enum.Enum):
    PENDING  = "PENDING"
    ASSIGNED = "ASSIGNED"
    SHIPPED  = "SHIPPED"


class Truck(Base):
    __tablename__ = "trucks"
    id     = Column("TruckID", Integer, primary_key=True, index=True)
    length = Column(Numeric(10,2), nullable=False)
    width  = Column(Numeric(10,2), nullable=False)
    height = Column(Numeric(10,2), nullable=False)
    status = Column(Enum(StatusTruck), default=StatusTruck.AVAILABLE)


class Package(Base):
    __tablename__ = "packages"
    id       = Column("PackageID", Integer, primary_key=True, index=True)
    length   = Column(Numeric(10,2), nullable=False)
    width    = Column(Numeric(10,2), nullable=False)
    height   = Column(Numeric(10,2), nullable=False)
    status   = Column(Enum(StatusPackage), default=StatusPackage.PENDING)
    truck_id = Column(Integer, ForeignKey("trucks.TruckID"), nullable=True)
