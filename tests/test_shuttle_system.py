"""Unit tests for Campus Shuttle Timetable & Fleet Tracker."""

import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import shuttle_system


class TestCampusShuttleSystem(unittest.TestCase):
    """Test suite verifying shuttle system core features and edge cases."""

    def setUp(self):
        """Preserve and isolate active route state before each test."""
        self.original_routes = copy.deepcopy(shuttle_system.routes)
        shuttle_system.init_default_routes()

    def tearDown(self):
        """Restore global route state after each test."""
        shuttle_system.routes = self.original_routes

    def test_log_valid_passenger_counts(self):
        """Verify logging valid positive integer passenger counts."""
        logs = shuttle_system.add_trip_log("R1", 25)
        self.assertEqual(shuttle_system.routes["R1"]["trips"], [25])
        self.assertEqual(len(logs), 1)
        self.assertIn("R1 carried 25", logs[0])

        shuttle_system.add_trip_log("R1", 30, logs)
        self.assertEqual(shuttle_system.routes["R1"]["trips"], [25, 30])
        self.assertEqual(len(logs), 2)
        self.assertIn("R1 carried 30", logs[1])

    def test_reject_negative_passenger_counts(self):
        """Verify rejection of negative passenger counts with ValueError."""
        with self.assertRaises(ValueError):
            shuttle_system.add_trip_log("R1", -1)

        with self.assertRaises(ValueError):
            shuttle_system.add_trip_log("R2", -6)

        # Confirm state remained uncorrupted
        self.assertEqual(shuttle_system.routes["R1"]["trips"], [])

    def test_reject_non_integer_passenger_counts(self):
        """Verify rejection of non-integer passenger counts."""
        invalid_inputs = ["full", "25", 12.5, True, False, None, [10]]
        for invalid_val in invalid_inputs:
            with self.subTest(invalid_val=invalid_val):
                with self.assertRaises(ValueError):
                    shuttle_system.add_trip_log("R1", invalid_val)

        self.assertEqual(shuttle_system.routes["R1"]["trips"], [])

    def test_independent_log_state_across_calls(self):
        """Ensure default log parameter does not retain state across calls."""
        log1 = shuttle_system.add_trip_log("R1", 10)
        self.assertEqual(len(log1), 1)

        log2 = shuttle_system.add_trip_log("R2", 15)
        self.assertEqual(len(log2), 1)
        self.assertIsNot(log1, log2)

    def test_average_load_calculation(self):
        """Verify exact calculation of average passenger load."""
        shuttle_system.add_trip_log("R1", 20)
        shuttle_system.add_trip_log("R1", 40)
        self.assertEqual(shuttle_system.average_load("R1"), 30.0)

    def test_handling_route_with_no_trips(self):
        """Ensure route with zero trips returns 0.0 without division error."""
        self.assertEqual(shuttle_system.routes["R1"]["trips"], [])
        self.assertEqual(shuttle_system.average_load("R1"), 0.0)

    def test_underused_route_detection(self):
        """Verify flagging of routes operating below capacity threshold."""
        shuttle_system.add_trip_log("R1", 35)  # avg 35 >= 10
        shuttle_system.add_trip_log("R2", 4)   # avg 4 < 10
        # R3 has 0 trips, avg 0.0 < 10

        flagged = shuttle_system.underused_routes(threshold=10)
        self.assertIn("R2", flagged)
        self.assertIn("R3", flagged)
        self.assertNotIn("R1", flagged)

    def test_unknown_and_removed_routes(self):
        """Verify behavior when handling non-existent or deleted routes."""
        # Add to non-existent route raises KeyError
        with self.assertRaises(KeyError):
            shuttle_system.add_trip_log("UNKNOWN", 10)

        # Average load of non-existent route returns None
        self.assertIsNone(shuttle_system.average_load("UNKNOWN"))

        # Remove route returns True for existing, False for non-existing
        self.assertTrue(shuttle_system.remove_route("R3"))
        self.assertNotIn("R3", shuttle_system.routes)
        self.assertFalse(shuttle_system.remove_route("R3"))

        # Average load of removed route returns None safely
        self.assertIsNone(shuttle_system.average_load("R3"))

    def test_driver_assignment(self):
        """Verify assigned drivers belong to authorized fleet drivers."""
        for _ in range(20):
            driver = shuttle_system.assign_driver("R1")
            self.assertIn(driver, shuttle_system.AVAILABLE_DRIVERS)

    def test_saving_and_loading_fleet_json(self):
        """Verify serialization and re-loading using temporary file."""
        shuttle_system.add_trip_log("R1", 25)
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = Path(tmp_dir) / "test_fleet.json"

            saved_path = shuttle_system.save_fleet_data(temp_file)
            self.assertTrue(saved_path.exists())

            # Load into fresh state
            shuttle_system.routes.clear()
            loaded = shuttle_system.load_fleet_data(temp_file)
            self.assertEqual(loaded["R1"]["trips"], [25])

            # Sync function
            shuttle_system.add_trip_log("R1", 35)
            synced = shuttle_system.sync_fleet_data(temp_file)
            self.assertEqual(synced["R1"]["trips"], [25, 35])

    def test_handling_invalid_json_or_file_errors(self):
        """Verify error handling on corrupted JSON file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_file = Path(tmp_dir) / "corrupt.json"
            bad_file.write_text("{invalid_json: true", encoding="utf-8")

            with self.assertRaises(json.JSONDecodeError):
                shuttle_system.load_fleet_data(bad_file)

    def test_interactive_main_default_lookup(self):
        """Test main() interactive flow with default empty Enter input."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_fleet = Path(tmp_dir) / "fleet.json"
            with patch("builtins.input", return_value=""), patch(
                "sys.stdout", new_callable=io.StringIO
            ) as mock_out:
                shuttle_system.main(fleet_file=tmp_fleet)
                output = mock_out.getvalue()
                banner = "=== Campus Shuttle Timetable & Fleet Tracker ==="
                self.assertIn(banner, output)
                self.assertIn("Trips on R2: [4]", output)
                self.assertIn("R3 average: Route not found", output)

    def test_interactive_main_custom_and_unknown_lookup(self):
        """Test main() interactive flow with custom and unknown routes."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_fleet = Path(tmp_dir) / "fleet.json"
            with patch("builtins.input", return_value="R1"), patch(
                "sys.stdout", new_callable=io.StringIO
            ) as mock_out:
                shuttle_system.main(fleet_file=tmp_fleet)
                output = mock_out.getvalue()
                self.assertIn("Trips on R1: [32, 28]", output)

            with patch("builtins.input", return_value="R99"), patch(
                "sys.stdout", new_callable=io.StringIO
            ) as mock_out:
                shuttle_system.main(fleet_file=tmp_fleet)
                output = mock_out.getvalue()
                self.assertIn("Route 'R99' not found in active fleet.", output)


if __name__ == "__main__":
    unittest.main()
