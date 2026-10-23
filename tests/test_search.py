
import unittest
from copy import deepcopy
from unittest.mock import patch

from campusflow.search import search_tickets


class TestSearchTickets(unittest.TestCase):
    """Test title searching, optional filters, and result sorting."""

    def setUp(self):
        self.tickets = {
            "T001": {
                "id": "T001",
                "title": "Wi-Fi router not working",
                "category": "Network",
                "priority": "high",
                "status": "open",
                "assigned_to": "Mentor A",
            },
            "T002": {
                "id": "T002",
                "title": "WIFI connection drops",
                "category": "Network",
                "priority": "critical",
                "status": "in_progress",
                "assigned_to": "Mentor B",
            },
            "T003": {
                "id": "T003",
                "title": "Wi-Fi access point failure",
                "category": "Network",
                "priority": "medium",
                "status": "open",
                "assigned_to": "Mentor C",
            },
            "T004": {
                "id": "T004",
                "title": "Laptop will not start",
                "category": "Hardware",
                "priority": "critical",
                "status": "open",
                "assigned_to": "Mentor D",
            },
            "T005": {
                "id": "T005",
                "title": "Software update failed",
                "category": "Software",
                "priority": "low",
                "status": "resolved",
                "assigned_to": "Mentor E",
            },
        }

    def search(
        self,
        title=None,
        category=None,
        status=None,
        priority=None,
        sort_results=False,
    ):
        """Call search_tickets using the standard fixture."""
        return search_tickets(
            self.tickets,
            title,
            category,
            status,
            priority,
            sort_results,
        )

    def test_title_search_is_case_insensitive(self):
        lower = self.search(title="Wi-Fi router not working")
        upper = self.search(title="Wi-Fi router not working")

        self.assertEqual(
            [t["id"] for t in lower],
            [t["id"] for t in upper],
        )

    def test_title_search_supports_substrings(self):
        results = self.search(title="router")

        self.assertEqual(
            [t["id"] for t in results],
            ["T001"],
        )

    def test_hyphenated_search_matches_same_punctuation(self):
        results = self.search(title="WI-FI")

        self.assertEqual(
            {t["id"] for t in results},
            {"T001", "T003"},
        )

    def test_title_search_does_not_claim_fuzzy_matching(self):
        # "wfi" is not a substring of "Wi-Fi".
        results = self.search(title="wfi")

        self.assertEqual(results, [])

    def test_category_filter(self):
        results = self.search(category="Network")

        self.assertEqual(
            {t["id"] for t in results},
            {"T001", "T002", "T003"},
        )

    def test_status_filter(self):
        results = self.search(status="open")

        self.assertEqual(
            {t["id"] for t in results},
            {"T001", "T003", "T004"},
        )

    def test_priority_filter(self):
        results = self.search(priority="critical")

        self.assertEqual(
            {t["id"] for t in results},
            {"T002", "T004"},
        )

    def test_all_supplied_filters_must_match(self):
        results = self.search(
            title="Wi-Fi router not working",
            category="Network",
            status="open",
            priority="high",
            sort_results=False
        )

        self.assertEqual(
            [t["id"] for t in results],
            ["T001"],
        )

    def test_empty_filters_do_not_filter_results(self):
        results = self.search(
            title="",
            category="",
            status="",
            priority="",
        )

        self.assertEqual(len(results), len(self.tickets))

    def test_none_filters_do_not_filter_results(self):
        results = self.search()

        self.assertEqual(len(results), len(self.tickets))

    def test_filters_can_be_combined_in_different_combinations(self):
        results = self.search(
            category="network",
            priority="medium",
        )

        self.assertEqual(
            [t["id"] for t in results],
            ["T003"],
        )

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.search(category="Finance")

    def test_invalid_status_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.search(status="pending")

    def test_invalid_priority_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.search(priority="urgent")

    def test_non_string_filter_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.search(category=123)

    def test_empty_ticket_dictionary_returns_empty_list(self):
        results = search_tickets(
            {},
            "wifi",
            None,
            None,
            None,
            False,
        )

        self.assertEqual(results, [])

    def test_search_does_not_modify_ticket_records(self):
        original = deepcopy(self.tickets)

        self.search(
            title="Wi-Fi router not working",
            category="Network",
            status="open",
            priority="high",
        )

        self.assertEqual(self.tickets, original)

    def test_results_contain_original_ticket_records(self):
        results = self.search(title="router")

        self.assertIs(results[0], self.tickets["T001"])

    def test_sorted_search_orders_by_priority_then_ticket_id(self):
        results = self.search(
            title="",
            sort_results=True,
        )

        self.assertEqual(
            [t["id"] for t in results],
            ["T002", "T004", "T001", "T003", "T005"],
        )

    def test_search_does_not_change_dictionary_keys(self):
        original_keys = list(self.tickets.keys())

        self.search(title="Wi-Fi router not working", sort_results=True)

        self.assertEqual(list(self.tickets.keys()), original_keys)


if __name__ == "__main__":
    unittest.main()
