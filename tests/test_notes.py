
import json
import tempfile
import unittest
from pathlib import Path

from campusflow.notes import (
    generate_note_id,
    add_note,
)


class TestGenerateNoteId(unittest.TestCase):
    """Test sequential note ID generation for each ticket."""

    def test_first_note_id_is_n001(self):
        ticket = {"id": "T001", "notes": []}

        self.assertEqual(generate_note_id(ticket), "N001")

    def test_next_id_increments_sequentially(self):
        ticket = {
            "id": "T001",
            "notes": [
                {"note_id": "N001"},
                {"note_id": "N002"},
            ],
        }

        self.assertEqual(generate_note_id(ticket), "N003")

    def test_generates_id_after_highest_existing_id(self):
        ticket = {
            "notes": [
                {"note_id": "N001"},
                {"note_id": "N005"},
                {"note_id": "N003"},
            ]
        }

        self.assertEqual(generate_note_id(ticket), "N006")

    def test_ignores_malformed_note_ids(self):
        ticket = {
            "notes": [
                {"note_id": "invalid"},
                {"note_id": "NABC"},
                {"note_id": "N002"},
                {"note_id": "002"},
            ]
        }

        self.assertEqual(generate_note_id(ticket), "N003")

    def test_missing_notes_starts_at_n001(self):
        self.assertEqual(generate_note_id({"id": "T001"}), "N001")

    def test_none_notes_starts_at_n001(self):
        self.assertEqual(
            generate_note_id({"notes": None}),
            "N001",
        )

    def test_rejects_non_list_notes(self):
        ticket = {"notes": "not a list"}

        with self.assertRaisesRegex(ValueError, "must be a list"):
            generate_note_id(ticket)

    def test_rejects_non_dictionary_note(self):
        ticket = {"notes": ["invalid note"]}

        with self.assertRaisesRegex(
            ValueError, "must be a dictionary"
        ):
            generate_note_id(ticket)


class TestAddNote(unittest.TestCase):
    """Test note creation, validation, and lifecycle rules."""

    def setUp(self):
        self.ticket = {
            "id": "T001",
            "status": "open",
            "notes": [],
        }

    def test_adds_note_with_expected_fields(self):
        note = add_note(
            self.ticket,
            "Mentor A",
            "Wi-Fi router reboot attempted",
        )

        self.assertEqual(
            note,
            {
                "note_id": "N001",
                "author": "Mentor A",
                "message": "Wi-Fi router reboot attempted",
            },
        )

        self.assertEqual(self.ticket["notes"], [note])

    def test_strips_author_and_message_whitespace(self):
        note = add_note(
            self.ticket,
            "  Mentor A  ",
            "  Router reboot completed  ",
        )

        self.assertEqual(note["author"], "Mentor A")
        self.assertEqual(note["message"], "Router reboot completed")

    def test_accepts_open_ticket(self):
        note = add_note(self.ticket, "Mentor A", "Check router")

        self.assertEqual(note["note_id"], "N001")

    def test_accepts_in_progress_ticket(self):
        self.ticket["status"] = "in_progress"

        note = add_note(self.ticket, "Mentor A", "Check router")

        self.assertEqual(note["note_id"], "N001")

    def test_rejects_resolved_ticket(self):
        self.ticket["status"] = "resolved"

        with self.assertRaisesRegex(ValueError, "Only open or in-progress tickets"):            
            add_note(self.ticket, "Mentor A", "Check router")

        self.assertEqual(self.ticket["notes"], [])

    def test_rejects_closed_ticket(self):
        self.ticket["status"] = "closed"

        with self.assertRaises(ValueError):
            add_note(self.ticket, "Mentor A", "Check router")

        self.assertEqual(self.ticket["notes"], [])

    def test_rejects_reopened_ticket_if_status_is_not_supported(self):
        self.ticket["status"] = "reopened"

        with self.assertRaises(ValueError):
            add_note(self.ticket, "Mentor A", "Check router")

        self.assertEqual(self.ticket["notes"], [])

    def test_rejects_missing_status(self):
        del self.ticket["status"]

        with self.assertRaises(ValueError):
            add_note(self.ticket, "Mentor A", "Check router")

        self.assertEqual(self.ticket["notes"], [])

    def test_rejects_blank_author(self):
        for author in ("", "   ", "\t\n"):
            with self.subTest(author=repr(author)):
                ticket = {
                    "id": "T001",
                    "status": "open",
                    "notes": [],
                }

                with self.assertRaisesRegex(
                    ValueError, "author must not be blank"
                ):
                    add_note(ticket, author, "Check router")

                self.assertEqual(ticket["notes"], [])

    def test_rejects_non_string_author(self):
        for author in (None, 123, [], {}):
            with self.subTest(author=repr(author)):
                with self.assertRaises(ValueError):
                    add_note(self.ticket, author, "Check router")

                self.assertEqual(self.ticket["notes"], [])

    def test_rejects_non_string_message(self):
        for message in (None, 123, [], {}):
            with self.subTest(message=repr(message)):
                with self.assertRaisesRegex(
                    ValueError, "message must be a string"
                ):
                    add_note(self.ticket, "Mentor A", message)

                self.assertEqual(self.ticket["notes"], [])

    def test_accepts_message_at_minimum_length(self):
        note = add_note(self.ticket, "Mentor A", "12345")

        self.assertEqual(note["message"], "12345")

    def test_accepts_message_at_maximum_length(self):
        message = "x" * 300

        note = add_note(self.ticket, "Mentor A", message)

        self.assertEqual(len(note["message"]), 300)

    def test_rejects_message_shorter_than_minimum(self):
        with self.assertRaisesRegex(ValueError, "5 to 300 characters"):
            add_note(self.ticket, "Mentor A", "1234")

        self.assertEqual(self.ticket["notes"], [])

    def test_rejects_message_longer_than_maximum(self):
        with self.assertRaisesRegex(ValueError, "5 to 300 characters"):
            add_note(self.ticket, "Mentor A", "x" * 301)

        self.assertEqual(self.ticket["notes"], [])

    def test_validates_message_length_after_trimming(self):
        with self.assertRaises(ValueError):
            add_note(self.ticket, "Mentor A", "   ab   ")

        self.assertEqual(self.ticket["notes"], [])

    def test_rejected_note_does_not_consume_id(self):
        with self.assertRaises(ValueError):
            add_note(self.ticket, "   ", "Invalid author")

        note = add_note(
            self.ticket,
            "Mentor A",
            "Wi-Fi router reboot attempted",
        )

        self.assertEqual(note["note_id"], "N001")

    def test_repeated_notes_receive_sequential_ids(self):
        first = add_note(
            self.ticket, "Mentor A", "Wi-Fi router reboot attempted"
        )
        second = add_note(
            self.ticket, "Mentor B", "Investigating switch ports"
        )

        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N002")
        self.assertEqual(len(self.ticket["notes"]), 2)

    def test_each_ticket_has_independent_note_ids(self):
        another_ticket = {
            "id": "T002",
            "status": "open",
            "notes": [],
        }

        first = add_note(
            self.ticket, "Mentor A", "Wi-Fi router reboot attempted"
        )
        second = add_note(
            another_ticket, "Mentor B", "Investigating switch ports"
        )

        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N001")

    def test_failed_validation_does_not_change_existing_notes(self):
        add_note(self.ticket, "Mentor A", "Wi-Fi router reboot attempted")
        original_notes = self.ticket["notes"].copy()

        with self.assertRaises(ValueError):
            add_note(self.ticket, "Mentor B", "bad")

        self.assertEqual(self.ticket["notes"], original_notes)


class TestNoteLifecycle(unittest.TestCase):
    """Test the requested add-resolve-reject-reopen workflow."""

    def setUp(self):
        self.ticket = {
            "id": "T001",
            "status": "open",
            "notes": [],
        }

    def test_notes_survive_resolution_and_reopening(self):
        first = add_note(
            self.ticket,
            "Mentor A",
            "Wi-Fi router reboot attempted",
        )
        second = add_note(
            self.ticket,
            "Mentor B",
            "Investigating switch ports",
        )

        self.ticket["status"] = "resolved"

        with self.assertRaises(ValueError):
            add_note(
                self.ticket,
                "Mentor C",
                "Testing after resolution",
            )

        self.assertEqual(
            [n["note_id"] for n in self.ticket["notes"]],
            ["N001", "N002"],
        )

        self.ticket["status"] = "open"

        third = add_note(
            self.ticket,
            "Mentor C",
            "Testing after reopening",
        )

        self.assertEqual(third["note_id"], "N003")
        self.assertEqual(
            [n["note_id"] for n in self.ticket["notes"]],
            ["N001", "N002", "N003"],
        )

        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N002")


class TestNotePersistence(unittest.TestCase):
    """Test JSON round-tripping and continued ID generation."""

    def test_save_and_reload_preserves_notes_and_next_id(self):
        ticket = {
            "id": "T001",
            "status": "open",
            "notes": [],
        }

        add_note(
            ticket,
            "Mentor A",
            "Wi-Fi router reboot attempted",
        )
        add_note(
            ticket,
            "Mentor B",
            "Investigating switch ports",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "tickets.json"

            # Simulate saving the ticket collection.
            file_path.write_text(
                json.dumps({"T001": ticket}, indent=4),
                encoding="utf-8",
            )

            # Simulate loading it after a restart.
            loaded_data = json.loads(
                file_path.read_text(encoding="utf-8")
            )
            loaded_ticket = loaded_data["T001"]

            self.assertEqual(loaded_ticket["notes"], ticket["notes"])

            next_id = generate_note_id(loaded_ticket)
            self.assertEqual(next_id, "N003")

            third = add_note(
                loaded_ticket,
                "Mentor C",
                "Testing after restart",
            )

            self.assertEqual(third["note_id"], "N003")
            self.assertEqual(len(loaded_ticket["notes"]), 3)

    def test_save_and_reload_preserves_notes_on_resolved_ticket(self):
        ticket = {
            "id": "T001",
            "status": "resolved",
            "notes": [
                {
                    "note_id": "N001",
                    "author": "Mentor A",
                    "message": "Wi-Fi router reboot attempted",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "tickets.json"

            file_path.write_text(
                json.dumps({"T001": ticket}, indent=4),
                encoding="utf-8",
            )

            loaded_ticket = json.loads(
                file_path.read_text(encoding="utf-8")
            )["T001"]

            self.assertEqual(loaded_ticket["status"], "resolved")
            self.assertEqual(
                loaded_ticket["notes"],
                ticket["notes"],
            )
            self.assertEqual(generate_note_id(loaded_ticket), "N002")


if __name__ == "__main__":
    unittest.main()
