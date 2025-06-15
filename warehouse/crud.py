from fastapi import HTTPException, status
from . import models, schemas, assignments
from .database import session_scope


def add_truck(truck: schemas.TruckCreate) -> schemas.TruckRead:
    """
    Add a new truck to the database.

    Args:
        truck (schemas.TruckCreate): The truck to be added.

    Returns:
        schemas.TruckRead: The added truck.
    """
    with session_scope() as db:
        db_truck = models.Truck(**truck.dict())
        db.add(db_truck)
        db.flush()
        db.refresh(db_truck)
        return schemas.TruckRead.from_orm(db_truck)


def add_package(pkg: schemas.PackageCreate) -> schemas.PackageRead:
    """
    Add a new package to the database.

    Args:
        pkg (schemas.PackageCreate): The package to be added.

    Returns:
        schemas.PackageRead: The added package.
    """
    with session_scope() as db:
        db_pkg = models.Package(**pkg.dict())
        db.add(db_pkg)
        db.flush()
        db.refresh(db_pkg)
        return schemas.PackageRead.from_orm(db_pkg)


def assign_truck(req: schemas.AssignRequest) -> schemas.AssignResponse:
    """
    Assign packages to a suitable truck, utilizing a bin-packing algorithm if specified.

    Args:
        req (schemas.AssignRequest): The request containing package IDs and an optional flag for bin-packing.

    Returns:
        schemas.AssignResponse: The response containing lists of assigned and deferred package IDs, along with a status message.

    Raises:
        HTTPException: If any package IDs are not found in the database.
    """
    with session_scope() as db:
        # Load and validate packages from the database
        pkgs = (
            db.query(models.Package)
              .filter(models.Package.id.in_(req.package_ids))
              .all()
        )

        # Check for missing package IDs
        if len(pkgs) != len(req.package_ids):
            missing = set(req.package_ids) - {p.id for p in pkgs}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Package(s) not found: {missing}"
            )

        # Run assignment logic with optional bin-packing
        assigned_ids, deferred_ids, msg = assignments.assign_to_best_fit(
            db, pkgs, use_bin_packing=req.use_bin_packing
        )

        # Return the assignment response
        return schemas.AssignResponse(
            assigned=assigned_ids,
            deferred=deferred_ids,
            message=msg
        )
