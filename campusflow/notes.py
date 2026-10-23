"""
Notes Module for CampusFlow Next.

Handles ticket notes, validation, and sequential per-ticket note IDs.
Enforces lifecycle invariants: only open or in_progress tickets accept notes.
"""

def generate_note_id(ticket: dict) -> str:
    """Generate the next sequential note ID for a ticket (e.g. 'N001', 'N002')."""
    notes = ticket.get("notes") or []

    if not isinstance(notes, list):
        raise ValueError("Ticket notes must be a list.")

    max_number = 0

    for note in notes:
        if not isinstance(note, dict):
            raise ValueError("Each note must be a dictionary.")

        note_id = note.get("note_id", "")

        if (
            isinstance(note_id, str)
            and note_id.startswith("N")
            and note_id[1:].isdigit()
        ):
            max_number = max(max_number, int(note_id[1:]))

    return f"N{max_number + 1:03d}"


def add_note(ticket: dict, author: str, message: str) -> dict:
    """
    Validates ticket status and inputs before appending a note.
    Appends new note to ticket['notes'] and returns the created note dict.
    Raises ValueError on validation failure without modifying ticket['notes'].
    """
    if ticket.get("status") not in ("open", "in_progress"):
        raise ValueError(
            "Only open or in-progress tickets can accept notes."
        )

    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author must not be blank.")

    if not isinstance(message, str):
        raise ValueError("Note message must be a string.")

    cleaned_message = message.strip()
    if not 5 <= len(cleaned_message) <= 300:
        raise ValueError(f"Note message must contain 5 to 300 characters (got {len(cleaned_message)}).")

    existing_notes = ticket.get("notes", [])
    if not isinstance(existing_notes, list):
        raise ValueError("Ticket notes must be a list.")

    note = {
        "note_id": generate_note_id(ticket),
        "author": author.strip(),
        "message": cleaned_message,
    }

    # Mutate the ticket only after all validation has succeeded (validate-before-mutate)
    ticket.setdefault("notes", []).append(note)
    return note
