
"""
Ticket search, filter validation, and optional sorting for CampusFlow Next.

Search supports case-insensitive title substring matching and exact matching
for category, status, and priority. Results can optionally be sorted by
priority and then by the numeric portion of the ticket ID.
"""


# Canonical values are lowercase because validators use casefold().
VALID_CATEGORIES = {"network", "hardware", "software"}
VALID_STATUSES = {"open", "in_progress", "resolved", "closed"}
VALID_PRIORITIES = {"critical", "high", "medium", "low"}

PRIORITY_RANK = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}


def validate_title(title):
    """Normalize a title search term; return None if no filter is supplied.

    Raises:
        TypeError: If title is neither a string nor None.
    """
    if title is None:
        return None

    if not isinstance(title, str):
        raise TypeError("Invalid title: title must be a string.")

    cleaned_title = title.strip().casefold()

    # An empty optional filter means that all titles are eligible.
    return cleaned_title or None


def validate_category(category):
    """Normalize a category filter and validate its allowed values.

    Returns None when no category filter is supplied.

    Raises:
        TypeError: If category is neither a string nor None.
        ValueError: If a nonblank category is unsupported.
    """
    if category is None:
        return None

    if not isinstance(category, str):
        raise TypeError("Invalid category: category must be a string.")

    cleaned_category = category.strip().casefold()

    if not cleaned_category:
        return None

    if cleaned_category not in VALID_CATEGORIES:
        raise ValueError(
            "Ticket category must be Network, Hardware, or Software."
        )

    return cleaned_category


def validate_status(status):
    """Normalize a status filter and validate its allowed values.

    Returns None when no status filter is supplied.

    Raises:
        TypeError: If status is neither a string nor None.
        ValueError: If a nonblank status is unsupported.
    """
    if status is None:
        return None

    if not isinstance(status, str):
        raise TypeError("Invalid status: status must be a string.")

    cleaned_status = status.strip().casefold()

    if not cleaned_status:
        return None

    if cleaned_status not in VALID_STATUSES:
        raise ValueError(
            "Ticket status must be Open, In_progress, Resolved, or Closed."
        )

    return cleaned_status


def validate_priority(priority):
    """Normalize a priority filter and validate its allowed values.

    Returns None when no priority filter is supplied.

    Raises:
        TypeError: If priority is neither a string nor None.
        ValueError: If a nonblank priority is unsupported.
    """
    if priority is None:
        return None

    if not isinstance(priority, str):
        raise TypeError("Invalid priority: priority must be a string.")

    cleaned_priority = priority.strip().casefold()

    if not cleaned_priority:
        return None

    if cleaned_priority not in VALID_PRIORITIES:
        raise ValueError(
            "Ticket priority must be critical, high, medium, or low."
        )

    return cleaned_priority


def extract_ticket_number(ticket_id):
    """Extract digits from a ticket ID for numeric sorting.

    Returns infinity when the ID is not a string containing digits.
    All digits are concatenated, so 'TICKET-12' returns 12.
    """
    if isinstance(ticket_id, str):
        digits = "".join(ch for ch in ticket_id if ch.isdigit())

        if digits:
            return int(digits)

    # IDs without digits sort after IDs with numeric portions.
    return float("inf")


def search_tickets(
    tickets,
    title,
    category,
    status,
    priority,
    sort_results
):
    """Search tickets using optional filters and optional sorting.

    Args:
        tickets: Dictionary mapping ticket keys to ticket dictionaries.
        title: Optional substring to search for in ticket titles.
        category: Optional exact category filter.
        status: Optional exact status filter.
        priority: Optional exact priority filter.
        sort_results: If True, sort by priority and then ticket number.

    Returns:
        A list of matching ticket dictionaries. The input dictionary
        and its ticket records are not modified.

    Raises:
        TypeError: If tickets is not a dictionary, or a ticket record
            is not a dictionary.
        TypeError/ValueError: If a supplied filter is invalid.
    """
    if not isinstance(tickets, dict):
        raise TypeError("Tickets must be a dictionary.")

    # Validate all filters before searching any records.
    cleaned_title = validate_title(title)
    cleaned_category = validate_category(category)
    cleaned_status = validate_status(status)
    cleaned_priority = validate_priority(priority)

    matches = []

    # A dictionary stores tickets as key-value pairs. Iterate over its
    # values because the values contain the actual ticket records.
    for ticket in tickets.values():
        if not isinstance(ticket, dict):
            raise TypeError("Each ticket must be a dictionary.")

        # Normalize stored fields too, so comparisons are case-insensitive.
        ticket_title = str(ticket.get("title", "")).strip().casefold()
        ticket_category = str(
            ticket.get("category", "")
        ).strip().casefold()
        ticket_status = str(
            ticket.get("status", "")
        ).strip().casefold()
        ticket_priority = str(
            ticket.get("priority", "")
        ).strip().casefold()

        # Title uses substring matching; other filters use exact matching.
        if cleaned_title is not None:
            if cleaned_title not in ticket_title:
                continue

        if cleaned_category is not None:
            if ticket_category != cleaned_category:
                continue

        if cleaned_status is not None:
            if ticket_status != cleaned_status:
                continue

        if cleaned_priority is not None:
            if ticket_priority != cleaned_priority:
                continue

        matches.append(ticket)

    if sort_results:
        def sort_key(ticket):
            """Return priority rank followed by numeric ticket ID."""
            rank = PRIORITY_RANK.get(
                str(ticket.get("priority", "")).strip().casefold(),
                99,
            )
            number = extract_ticket_number(ticket.get("id", ""))

            return rank, number

        # sorted() creates a new list; the original records remain unchanged.
        return sorted(matches, key=sort_key)

    return matches
