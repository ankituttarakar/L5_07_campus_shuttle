"""Campus Shuttle Timetable & Fleet Tracker.

This module manages campus shuttle routes, records trip passenger logs,
calculates average passenger loads, detects underused routes, assigns drivers,
and synchronizes fleet data with persistent JSON storage.
"""

from datetime import datetime
import json
from pathlib import Path
import secrets

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_FLEET_FILE = BASE_DIR / "fleet.json"
MIN_CAPACITY = 10
AVAILABLE_DRIVERS = ("Prakash", "Leela", "Imran", "Tom")

# Global routes dictionary representing the active fleet state.
routes = {
    "R1": {"name": "Main Gate - Library", "trips": []},
    "R2": {"name": "Hostel - Sports Complex", "trips": []},
    "R3": {"name": "Admin Block - Metro", "trips": []},
}


def init_default_routes():
    """Reset the global routes dictionary to baseline starter routes."""
    routes.clear()
    routes.update({
        "R1": {"name": "Main Gate - Library", "trips": []},
        "R2": {"name": "Hostel - Sports Complex", "trips": []},
        "R3": {"name": "Admin Block - Metro", "trips": []},
    })
    return routes


def add_trip_log(route_id, passenger_count, logs=None):
    """Log a trip passenger count for a given route and update log records.

    Args:
        route_id (str): Identifier of the shuttle route (e.g. 'R1').
        passenger_count (int): Non-negative number of passengers carried.
        logs (list, optional): List of log strings. Defaults to a new list.

    Returns:
        list: Updated list of log strings.

    Raises:
        KeyError: If route_id is not present in routes.
        ValueError: If passenger_count is not a non-negative integer.
    """
    if route_id not in routes:
        raise KeyError(f"Route '{route_id}' does not exist.")

    if (
        not isinstance(passenger_count, int)
        or isinstance(passenger_count, bool)
    ):
        raise ValueError(
            f"Invalid passenger count '{passenger_count}': must be an integer."
        )

    if passenger_count < 0:
        raise ValueError(
            f"Invalid passenger count {passenger_count}: cannot be negative."
        )

    if logs is None:
        logs = []

    routes[route_id]["trips"].append(passenger_count)
    log_entry = (
        f"{datetime.now().isoformat()}: {route_id} carried {passenger_count}"
    )
    logs.append(log_entry)
    return logs


def remove_route(route_id):
    """Remove a route from the active fleet.

    Args:
        route_id (str): Identifier of the route to remove.

    Returns:
        bool: True if route was removed, False if it was not found.
    """
    if route_id in routes:
        del routes[route_id]
        return True
    return False


def average_load(route_id):
    """Calculate the average passenger load for a specified route.

    Args:
        route_id (str): Identifier of the shuttle route.

    Returns:
        float | None: Average passenger count, 0.0 if no trips, or None if
        the route does not exist.
    """
    if route_id not in routes:
        return None

    trips = routes[route_id].get("trips", [])
    if not trips:
        return 0.0

    return sum(trips) / len(trips)


def underused_routes(threshold=MIN_CAPACITY):
    """Identify routes whose average passenger load falls below a threshold.

    Args:
        threshold (int | float): Minimum acceptable average passenger load.

    Returns:
        list: Route IDs with average load strictly less than the threshold.
    """
    flagged = []
    for route_id in routes:
        avg = average_load(route_id)
        if avg is not None and avg < threshold:
            flagged.append(route_id)
    return flagged


def assign_driver(route_id=None):
    """Assign an available driver randomly to a given route.

    Args:
        route_id (str, optional): Route identifier for the assignment.

    Returns:
        str: Name of the assigned driver.
    """
    _ = route_id  # Acknowledged route assignment context
    return secrets.choice(AVAILABLE_DRIVERS)


def save_fleet_data(file_path=None):
    """Save the in-memory route dictionary to a JSON file on disk.

    Args:
        file_path (str | Path, optional): Destination file path.

    Returns:
        Path: Path where the fleet data was saved.
    """
    target_path = Path(file_path) if file_path else DEFAULT_FLEET_FILE
    with open(target_path, "w", encoding="utf-8") as file_handle:
        json.dump(routes, file_handle, indent=2)
    return target_path


def load_fleet_data(file_path=None):
    """Load and update route data from a JSON file on disk.

    Args:
        file_path (str | Path, optional): Source file path.

    Returns:
        dict: The updated routes dictionary.

    Raises:
        OSError: If file reading fails.
        json.JSONDecodeError: If JSON parsing fails.
    """
    target_path = Path(file_path) if file_path else DEFAULT_FLEET_FILE
    with open(target_path, "r", encoding="utf-8") as file_handle:
        loaded = json.load(file_handle)

    routes.clear()
    routes.update(loaded)
    return routes


def sync_fleet_data(file_path=None):
    """Synchronize current fleet route data with a JSON file on disk.

    Writes the in-memory route dictionary to the file, then reloads it
    to ensure persistence consistency and data integrity.

    Args:
        file_path (str | Path, optional): Path to destination JSON file.

    Returns:
        dict: The reloaded fleet data dictionary.

    Raises:
        OSError: If reading or writing to the file fails.
        json.JSONDecodeError: If the stored data cannot be parsed.
    """
    target_path = Path(file_path) if file_path else DEFAULT_FLEET_FILE
    save_fleet_data(target_path)
    return load_fleet_data(target_path)


def main(fleet_file=None):
    """Run interactive demonstration of the campus shuttle tracking system."""
    init_default_routes()
    print("=== Campus Shuttle Timetable & Fleet Tracker ===")

    # Log valid trips
    add_trip_log("R1", 32)
    add_trip_log("R1", 28)
    add_trip_log("R2", 4)

    # Demonstrate safe rejection of invalid passenger counts
    for route, bad_count in [("R2", -6), ("R3", "full")]:
        try:
            add_trip_log(route, bad_count)
        except ValueError as err:
            print(f"Validation Notice: Rejected trip for {route} - {err}")

    # Display operational status
    print("Driver for R1:", assign_driver("R1"))
    print("Underused routes:", underused_routes())
    print("R1 average load:", average_load("R1"))

    # Persist fleet data
    sync_fleet_data(fleet_file)
    print("Fleet data synchronized to fleet.json.")

    # Remove route R3 and demonstrate safe post-removal lookup
    remove_route("R3")
    print("Route R3 has been removed from active fleet.")

    # Interactive route lookup with validation
    choice = input("Route to look up (Enter for R2): ").strip() or "R2"
    if choice in routes:
        print(f"Trips on {choice}: {routes[choice]['trips']}")
    else:
        print(f"Route '{choice}' not found in active fleet.")

    # Safely retrieve average for removed route
    r3_avg = average_load("R3")
    if r3_avg is None:
        print("R3 average: Route not found (safely handled after removal)")
    else:
        print("R3 average:", r3_avg)


if __name__ == "__main__":
    main()
