import unittest
from copy import deepcopy

from campusflow.workflow import assign_ticket, update_status


class TestWorkflow(unittest.TestCase):

    def setUp(self):
        self.mock_tickets = [
            {
                "id": "T001",
                "title": "Wi-Fi down",
                "status": "open",
                "assigned_to": None,
            }
        ]

    def test_assign_ticket_success(self):
        updated_ticket = assign_ticket(
            self.mock_tickets, "T001", "Grace Hopper"
        )
        self.assertEqual(updated_ticket["assigned_to"], "Grace Hopper")

    def test_unassigned_ticket_cannot_be_in_progress(self):
        original = deepcopy(self.mock_tickets)

        with self.assertRaises(ValueError):
            update_status(self.mock_tickets, "T001", "in_progress")

        self.assertEqual(self.mock_tickets, original)

    def test_unassigned_open_to_in_progress_rejected(self):
        self.test_unassigned_ticket_cannot_be_in_progress()

    def test_valid_ticket_lifecycle(self):
        assign_ticket(self.mock_tickets, "T001", "Ada Lovelace")

        ticket = update_status(self.mock_tickets, "T001", "in_progress")
        self.assertEqual(ticket["status"], "in_progress")

        ticket = update_status(self.mock_tickets, "T001", "resolved")
        self.assertEqual(ticket["status"], "resolved")

        ticket = update_status(self.mock_tickets, "T001", "open")
        self.assertEqual(ticket["status"], "open")

    def test_resolved_ticket_cannot_be_reassigned(self):
        assign_ticket(self.mock_tickets, "T001", "Ada Lovelace")
        update_status(self.mock_tickets, "T001", "in_progress")
        update_status(self.mock_tickets, "T001", "resolved")

        original = deepcopy(self.mock_tickets)

        with self.assertRaises(ValueError):
            assign_ticket(self.mock_tickets, "T001", "Grace Hopper")

        self.assertEqual(self.mock_tickets, original)

    def test_invalid_transition_does_not_change_ticket(self):
        original = deepcopy(self.mock_tickets)

        with self.assertRaises(ValueError):
            update_status(self.mock_tickets, "T001", "resolved")

        self.assertEqual(self.mock_tickets, original)


    def test_resolved_ticket_mutations_rejected(self):
        self.test_resolved_ticket_cannot_change_status()

    def test_resolved_ticket_cannot_change_status(self):
        assign_ticket(self.mock_tickets, "T001", "Ada Lovelace")
        update_status(self.mock_tickets, "T001", "in_progress")
        update_status(self.mock_tickets, "T001", "resolved")

        original = deepcopy(self.mock_tickets)

        with self.assertRaises(ValueError):
            update_status(self.mock_tickets, "T001", "in_progress")

        self.assertEqual(self.mock_tickets, original)


if __name__ == "__main__":
    unittest.main()
