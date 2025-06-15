from decimal import Decimal
from fastapi import HTTPException, status
from . import models


def assign_to_best_fit(db, pkgs: list[models.Package], use_bin_packing: bool = False) -> tuple[list[int], list[int], str]:
    """
    Assign packages to trucks using either a bin-packing algorithm or a simple
    volume-based best-fit selection.

    Args:
        db: The database session.
        pkgs: The list of packages to be assigned.
        use_bin_packing: Whether to use the bin-packing algorithm (default: False).

    Returns:
        A tuple containing:
        - A list of assigned package IDs.
        - A list of deferred package IDs.
        - A status message.

    Raises:
        HTTPException: If no available trucks are found.
    """
    # Bin-packing path
    if use_bin_packing:
        return assign_with_bin_packing(db, pkgs)

    # --- Simple fill path (no bin-packing) ---
    # 1) Find one available truck
    trucks = (
        db.query(models.Truck)
        .filter(models.Truck.status == models.StatusTruck.AVAILABLE)
        .all()
    )
    if not trucks:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No available trucks; please retry later."
        )
    truck = trucks[0]

    # 2) Compute capacity and threshold
    capacity = truck.length * truck.width * truck.height  # Decimal
    threshold = Decimal('0.8')

    # 3) Gather volumes & check total volume
    volumes = [p.length * p.width * p.height for p in pkgs]
    total_vol = sum(volumes)

    if total_vol < threshold * capacity:
        # If under 80%, defer all packages
        deferred_ids = [p.id for p in pkgs]
        return [], deferred_ids, (
            f"Load <80% of truck {truck.id}; "
            f"{len(deferred_ids)} package(s) deferred."
        )

    # 4) Sort packages by their individual volume (largest first)
    sorted_pkgs = sorted(
        pkgs,
        key=lambda p: p.length * p.width * p.height,
        reverse=True
    )

    # 5) Assign until capacity is reached
    assigned_ids = []
    deferred_ids = []
    remaining = capacity
    for pkg in sorted_pkgs:
        vol = pkg.length * pkg.width * pkg.height
        if vol <= remaining:
            pkg.status = models.StatusPackage.ASSIGNED
            pkg.truck_id = truck.id
            assigned_ids.append(pkg.id)
            remaining -= vol
        else:
            deferred_ids.append(pkg.id)

    # 6) Update truck status if any were assigned
    if assigned_ids:
        truck.status = models.StatusTruck.LOADED

    # 7) Build and return the response
    message = (
        f"Assigned {len(assigned_ids)} pkg(s) to truck {truck.id}; "
        f"{len(deferred_ids)} deferred."
    )
    return assigned_ids, deferred_ids, message


def assign_with_bin_packing(db, pkgs: list[models.Package]) -> tuple[list[int], list[int], str]:
    """
    Assign packages to trucks using a simple bin-packing algorithm.

    The algorithm assigns packages to the first truck with enough capacity.
    If the package doesn't fit in any truck, it is deferred.

    Args:
        db: The database session.
        pkgs: The list of packages to be assigned.

    Returns:
        A tuple containing:
        - A list of assigned package IDs.
        - A list of deferred package IDs.
        - A status message.

    Raises:
        HTTPException: If no available trucks are found.
    """
    # 1) Load all available trucks
    trucks = (
        db.query(models.Truck)
        .filter(models.Truck.status == models.StatusTruck.AVAILABLE)
        .all()
    )
    if not trucks:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No available trucks; please retry later."
        )

    # 2) Initialize remaining capacity per truck
    for t in trucks:
        t.remaining = t.length * t.width * t.height
        t.assigned_pkgs = []

    # 3) Sort packages by descending volume
    pkg_vols = {p.id: p.length * p.width * p.height for p in pkgs}
    sorted_pkgs = sorted(pkgs, key=lambda p: pkg_vols[p.id], reverse=True)

    # 4) First-fit placement
    deferred_pkgs = []
    for pkg in sorted_pkgs:
        vol = pkg_vols[pkg.id]
        placed = False
        for t in trucks:
            if vol <= t.remaining:
                t.assigned_pkgs.append(pkg)
                t.remaining -= vol
                placed = True
                break
        if not placed:
            deferred_pkgs.append(pkg)

    # 5) Enforce threshold, finalize assignments
    assigned_ids = []
    final_deferred = []
    threshold = Decimal('0.8')
    for t in trucks:
        cap = t.length * t.width * t.height
        used = sum(pkg_vols[p.id] for p in t.assigned_pkgs)
        if used >= threshold * cap:
            for p in t.assigned_pkgs:
                p.status = models.StatusPackage.ASSIGNED
                p.truck_id = t.id
                assigned_ids.append(p.id)
            t.status = models.StatusTruck.LOADED
        else:
            # defer all in this truck
            final_deferred.extend(p.id for p in t.assigned_pkgs)

    # 6) Combine with packages that never fit
    final_deferred.extend(p.id for p in deferred_pkgs)

    # 7) Construct message
    message = (
        f"Assigned {len(assigned_ids)} pkg(s); "
        f"{len(final_deferred)} deferred."
    )
    return assigned_ids, final_deferred, message
