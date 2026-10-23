"""Centralized validation for CampusFlow tickets."""

def validate_title(title: str) -> str:
    """Return a trimmed title or raise ValueError if blank."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title must not be blank.")
    return title.strip()


def validate_category(category: str) -> str:
    """Return a canonical category or raise ValueError."""
    if not isinstance(category, str):
        raise ValueError("Category must be a string.")

    categories = {
        "network": "Network",
        "hardware": "Hardware",
        "software": "Software",
        "other": "Other",
    }
    canonical = categories.get(category.strip().casefold())

    if canonical is None:
        raise ValueError(
            "Category must be Network, Hardware, Software, or Other."
        )
    return canonical


def validate_urgency(urgency: str) -> str:
    """Return canonical lower-case urgency or raise ValueError."""
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be low, medium, or high.")

    canonical = urgency.strip().casefold()
    if canonical not in {"low", "medium", "high"}:
        raise ValueError("Urgency must be low, medium, or high.")
    return canonical


def validate_affected_users(affected_users) -> int:
    """Require a strictly positive integer; reject bools and floats."""
    if type(affected_users) is not int or affected_users <= 0:
        raise ValueError("Affected users must be a positive integer.")
    return affected_users


def can_transition(
    current_status: str,
    new_status: str,
    assigned_to: str | None,
) -> bool:
    """Return whether a ticket status transition is legal."""
    if current_status == "open" and new_status == "in_progress":
        return isinstance(assigned_to, str) and bool(assigned_to.strip())

    return (
        (current_status == "in_progress" and new_status == "resolved")
        or (current_status == "resolved" and new_status == "open")
    )
