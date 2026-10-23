def extract_ticket_number(ticket_id):
    if isinstance(ticket_id, str):
        digits = "".join(ch for ch in ticket_id if ch.isdigit())
        if digits:
            return int(digits)
    return float('inf')


def get_work_queue(tickets):
    open_tickets = [t for t in tickets if t.get("status") == "open"]

    priority_rank = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4
    }
    
    def sorting_rule(ticket):
        rank = priority_rank.get(str(ticket.get("priority", "")).lower(), 99)
        return (rank, extract_ticket_number(ticket.get("id", "")))
        
    open_tickets.sort(key=sorting_rule)
    return open_tickets


def generate_report(tickets):
    total = len(tickets)
    by_status = {}
    by_priority = {}
    by_category = {}
    resolved_count = 0
    unresolved_count = 0

    for ticket in tickets:
        status = ticket.get("status")
        priority = ticket.get("priority")
        category = ticket.get("category")

        if status:
            by_status[status] = by_status.get(status, 0) + 1

        if priority:
            by_priority[priority] = by_priority.get(priority, 0) + 1

        if category:
            by_category[category] = by_category.get(category, 0) + 1

        if status == "resolved":
            resolved_count += 1
        elif status in ["open", "in_progress"]:
            unresolved_count += 1

    resolution_percentage = (resolved_count / total * 100.0) if total > 0 else 0.0

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
        "unresolved": unresolved_count,
        "resolved": resolved_count,
        "resolution_percentage": round(resolution_percentage, 2)
    }