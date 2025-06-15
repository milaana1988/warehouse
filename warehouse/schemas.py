from pydantic import BaseModel, condecimal, ConfigDict
from typing import List, Optional

PositiveDec = condecimal(gt=0, max_digits=10, decimal_places=2)


class TruckCreate(BaseModel):
    length: PositiveDec
    width: PositiveDec
    height: PositiveDec


class TruckRead(TruckCreate):
    id: int
    status: str
    model_config = ConfigDict(from_attributes=True)


class PackageCreate(BaseModel):
    length: PositiveDec
    width: PositiveDec
    height: PositiveDec


class PackageRead(PackageCreate):
    id: int
    status: str
    truck_id: Optional[int]
    model_config = ConfigDict(from_attributes=True)


class AssignRequest(BaseModel):
    package_ids: List[int]
    use_bin_packing: bool = False
    model_config = ConfigDict(from_attributes=True)


class AssignResponse(BaseModel):
    assigned: List[int]
    deferred: List[int]
    message: str
    model_config = ConfigDict(from_attributes=True)
