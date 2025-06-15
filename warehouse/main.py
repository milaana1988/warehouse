from fastapi import FastAPI
from . import schemas, crud
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/trucks", response_model=schemas.TruckRead, status_code=201,
          summary="Add a new truck to the database.",
          description="Add a new truck to the database. The truck will be "
                      "available for assignments.")
def add_truck(truck: schemas.TruckCreate) -> schemas.TruckRead:
    """Add a new truck to the database.

    Args:
        truck (schemas.TruckCreate): The truck to be added.

    Returns:
        schemas.TruckRead: The added truck.
    """
    return crud.add_truck(truck)


@app.post("/packages", response_model=schemas.PackageRead, status_code=201,
          summary="Add a new package to the database.",
          description="Add a new package to the database. The package will be "
                      "pending assignment.")
def add_package(pkg: schemas.PackageCreate) -> schemas.PackageRead:
    """Add a new package to the database.

    Args:
        pkg (schemas.PackageCreate): The package to be added.

    Returns:
        schemas.PackageRead: The added package.
    """
    return crud.add_package(pkg)


@app.post("/assign", response_model=schemas.AssignResponse,
          summary="Assign packages to a suitable truck.",
          description="Assign packages to a suitable truck based on the request."
                      "The response will contain assigned and deferred package IDs and a status message.")
def assign_truck(req: schemas.AssignRequest) -> schemas.AssignResponse:
    """Assign packages to a suitable truck.

    Args:
        req (schemas.AssignRequest): The request containing package IDs to be assigned.

    Returns:
        schemas.AssignResponse: Response containing assigned and deferred package IDs and a status message.

    Raises:
        HTTPException: If any package IDs are not found.
    """
    return crud.assign_truck(req)
