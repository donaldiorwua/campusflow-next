
import unittest

from campusflow.reports import (
    extract_ticket_number,
    get_work_queue,
    generate_report,
)


class TestExtractTicketNumber(unittest.TestCase):
    """Tests for extracting numeric ticket IDs."""

    def test_extracts_number_from_ticket_id(self):
        self.assertEqual(extract_ticket_number("TICKET-001"), 1)
        self.assertEqual(extract_ticket_number("TKT-25"), 25)

    def test_extracts_multiple_digits(self):
        self.assertEqual(extract_ticket_number("BUG-2026-15"), 202615)

    def test_returns_infinity_when_no_digits_exist(self):
        self.assertEqual(extract_ticket_number("ABC"), float("inf"))

    def test_returns_infinity_for_empty_string(self):
        self.assertEqual(extract_ticket_number(""), float("inf"))

    def test_returns_infinity_for_non_string(self):
        self.assertEqual(extract_ticket_number(123), float("inf"))
        self.assertEqual(extract_ticket_number(None), float("inf"))


class TestGetWorkQueue(unittest.TestCase):
    """Tests for the original Open Work Queue."""

    def setUp(self):
        self.tickets = [
            {
                "id": "TICKET-4",
                "status": "open",
                "priority": "low",
            },
            {
                "id": "TICKET-3",
                "status": "open",
                "priority": "critical",
            },
            {
                "id": "TICKET-2",
                "status": "open",
                "priority": "high",
            },
            {
                "id": "TICKET-1",
                "status": "open",
                "priority": "critical",
            },
            {
                "id": "TICKET-5",
                "status": "in_progress",
                "priority": "critical",
            },
            {
                "id": "TICKET-6",
                "status": "resolved",
                "priority": "high",
            },
        ]

    def test_returns_only_open_tickets(self):
        result = get_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["TICKET-1", "TICKET-3", "TICKET-2", "TICKET-4"],
        )

    def test_sorts_by_priority_then_ticket_number(self):
        result = get_work_queue(self.tickets)

        priorities_and_ids = [
            (ticket["priority"], ticket["id"])
            for ticket in result
        ]

        self.assertEqual(
            priorities_and_ids,
            [
                ("critical", "TICKET-1"),
                ("critical", "TICKET-3"),
                ("high", "TICKET-2"),
                ("low", "TICKET-4"),
            ],
        )

    def test_priority_sort_is_case_insensitive(self):
        tickets = [
            {"id": "T-2", "status": "open", "priority": "HIGH"},
            {"id": "T-1", "status": "open", "priority": "high"},
        ]

        result = get_work_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T-1", "T-2"],
        )

    def test_unknown_priority_sorts_after_known_priorities(self):
        tickets = [
            {"id": "T-1", "status": "open", "priority": "unknown"},
            {"id": "T-2", "status": "open", "priority": "low"},
        ]

        result = get_work_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T-2", "T-1"],
        )

    def test_does_not_include_in_progress_or_resolved_tickets(self):
        result = get_work_queue(self.tickets)

        statuses = {ticket["status"] for ticket in result}

        self.assertEqual(statuses, {"open"})

    def test_empty_queue_returns_empty_list(self):
        self.assertEqual(get_work_queue([]), [])

    def test_missing_priority_is_handled(self):
        tickets = [
            {"id": "T-1", "status": "open"},
            {"id": "T-2", "status": "open", "priority": "low"},
        ]

        result = get_work_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T-2", "T-1"],
        )


class TestGenerateReport(unittest.TestCase):
    """Tests for report totals and aggregation."""

    def setUp(self):
        self.tickets = [
            {
                "id": "T-1",
                "status": "open",
                "priority": "high",
                "category": "network",
            },
            {
                "id": "T-2",
                "status": "in_progress",
                "priority": "critical",
                "category": "hardware",
            },
            {
                "id": "T-3",
                "status": "resolved",
                "priority": "high",
                "category": "network",
            },
            {
                "id": "T-4",
                "status": "closed",
                "priority": "low",
                "category": "software",
            },
            {
                "id": "T-5",
                "status": "resolved",
                "priority": "medium",
                "category": "hardware",
            },
            {
                "id": "T-6",
                "status": "reopened",
                "priority": "low",
                "category": "network",
            },
        ]

    def test_reports_total_ticket_count(self):
        report = generate_report(self.tickets)

        self.assertEqual(report["total"], 6)

    def test_counts_tickets_by_current_status(self):
        report = generate_report(self.tickets)

        self.assertEqual(
            report["by_status"],
            {
                "open": 1,
                "in_progress": 1,
                "resolved": 2,
                "closed": 1,
                "reopened": 1,
            },
        )

    def test_counts_tickets_by_priority(self):
        report = generate_report(self.tickets)

        self.assertEqual(
            report["by_priority"],
            {
                "high": 2,
                "critical": 1,
                "low": 2,
                "medium": 1,
            },
        )

    def test_counts_tickets_by_category(self):
        report = generate_report(self.tickets)

        self.assertEqual(
            report["by_category"],
            {
                "network": 3,
                "hardware": 2,
                "software": 1,
            },
        )

    def test_counts_only_open_and_in_progress_as_unresolved(self):
        report = generate_report(self.tickets)

        self.assertEqual(report["unresolved"], 2)

    def test_counts_only_currently_resolved_tickets(self):
        report = generate_report(self.tickets)

        self.assertEqual(report["resolved"], 2)

    def test_calculates_resolution_percentage(self):
        report = generate_report(self.tickets)

        # 2 resolved out of 6 tickets = 33.33%
        self.assertEqual(report["resolution_percentage"], 33.33)

   
    def test_all_tickets_resolved_returns_100_percent(self):
        tickets = [
            {
                "id": "T-1",
                "status": "resolved",
                "priority": "high",
                "category": "network",
            },
            {
                "id": "T-2",
                "status": "resolved",
                "priority": "low",
                "category": "hardware",
            },
        ]

        report = generate_report(tickets)

        self.assertEqual(report["resolved"], 2)
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["resolution_percentage"], 100.0)

    def test_reopened_ticket_counts_by_current_status(self):
        tickets = [
            {
                "id": "T-1",
                "status": "reopened",
                "priority": "high",
                "category": "network",
            },
            {
                "id": "T-2",
                "status": "resolved",
                "priority": "low",
                "category": "hardware",
            },
        ]

        report = generate_report(tickets)

        self.assertEqual(report["by_status"]["reopened"], 1)
        self.assertEqual(report["resolved"], 1)
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["resolution_percentage"], 50.0)

    def test_status_counts_do_not_double_count_tickets(self):
        report = generate_report(self.tickets)

        self.assertEqual(
            sum(report["by_status"].values()),
            report["total"],
        )

    def test_unresolved_and_resolved_are_mutually_exclusive(self):
        report = generate_report(self.tickets)

        # Tickets in other statuses, such as closed or reopened,
        # belong to neither of these two groups.
        self.assertLessEqual(
            report["resolved"] + report["unresolved"],
            report["total"],
        )

    def test_missing_optional_fields_do_not_crash_report(self):
        tickets = [
            {"id": "T-1", "status": "open"},
            {"id": "T-2", "priority": "high"},
            {"id": "T-3", "category": "network"},
            {},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total"], 4)
        self.assertEqual(report["by_status"], {"open": 1})
        self.assertEqual(report["by_priority"], {"high": 1})
        self.assertEqual(report["by_category"], {"network": 1})
        self.assertEqual(report["unresolved"], 1)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["resolution_percentage"], 0.0)


if __name__ == "__main__":
    unittest.main()
