from datetime import UTC, datetime

from app.models import InventoryCount, InventoryCountStatus, User


class EmptyInventoryCountError(ValueError):
    """Raised when a draft without items is submitted."""


class SubmittedInventoryCountError(ValueError):
    """Raised when an already submitted count is submitted again."""


def submit_inventory_count(
    inventory_count: InventoryCount,
    submitted_by: User,
    *,
    submitted_at: datetime | None = None,
) -> None:
    if inventory_count.status is not InventoryCountStatus.DRAFT:
        raise SubmittedInventoryCountError("Submitted counts are read-only")
    if not inventory_count.items:
        raise EmptyInventoryCountError("Cannot submit an empty count")
    inventory_count.status = InventoryCountStatus.SUBMITTED
    inventory_count.submitted_by = submitted_by
    inventory_count.submitted_at = submitted_at or datetime.now(UTC)
