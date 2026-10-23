"""
Workflow Module

Handles ticket lifecycle and assignment rules.
"""

from campusflow.validation import can_transition


VALID_STATUSES = {"open", "in_progress", "resolved"}


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign a ticket to a staff member."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            if ticket["status"] == "resolved":
                raise ValueError(
                    "Cannot assign a resolved ticket. Reopen it first."
                )

            ticket["assigned_to"] = staff_name.strip()
            return ticket

    raise KeyError(f"Ticket with ID {ticket_id} not found.")


def update_status(tickets, ticket_id, new_status):
    """Update a ticket only when the requested transition is legal."""
    if not isinstance(new_status, str) or new_status not in VALID_STATUSES:
        raise ValueError(
            "Invalid status. Must be 'open', 'in_progress', or 'resolved'."
        )

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            current_status = ticket["status"]

            if not can_transition(
                current_status,
                new_status,
                ticket.get("assigned_to"),
            ):
                raise ValueError(
                    f"Invalid status transition: {current_status} -> {new_status}."
                )

            ticket["status"] = new_status
            return ticket

    raise KeyError(f"Ticket with ID {ticket_id} not found.")
