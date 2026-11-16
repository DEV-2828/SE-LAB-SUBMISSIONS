"""Bike-Share Station Manager.

This module provides functionality to register bike stations,
rent bikes, issue unlock PINs, identify full stations, and reset stations.
"""

import secrets
import sqlite3
from typing import List, Optional

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE stations ("
    "id INTEGER PRIMARY KEY, "
    "name TEXT, "
    "capacity INTEGER, "
    "bikes INTEGER)"
)


def add_station(
    name: str,
    capacity: int,
    bikes: int,
    log: Optional[List[str]] = None
) -> List[str]:
    """Register a new station into the database."""
    if log is None:
        log = []
    conn.execute(
        "INSERT INTO stations (name, capacity, bikes) VALUES (?, ?, ?)",
        (name, capacity, bikes)
    )
    log.append(name)
    return log


def rent_bike(station_id: int) -> Optional[bool]:
    """Rent a bike from a station if available."""
    row = conn.execute(
        "SELECT bikes FROM stations WHERE id = ?",
        (station_id,)
    ).fetchone()
    if row and row[0] > 0:
        conn.execute(
            "UPDATE stations SET bikes = bikes - 1 WHERE id = ?",
            (station_id,)
        )
        return True
    return None


def unlock_pin() -> int:
    """Generate a cryptographically secure 4-digit unlock PIN."""
    return secrets.randbelow(9000) + 1000


def full_stations() -> List[str]:
    """Return names of all stations that are at maximum capacity."""
    stations = conn.execute(
        "SELECT name FROM stations WHERE bikes = capacity"
    ).fetchall()
    return [s[0] for s in stations]


def reset_station(station_id: int) -> None:
    """Reset the bike count of a station to zero."""
    try:
        conn.execute(
            "UPDATE stations SET bikes = 0 WHERE id = ?",
            (station_id,)
        )
    except sqlite3.Error as err:
        print(f"Failed to reset station {station_id}: {err}")


def has_bikes(station_id: int) -> bool:
    """Check if a given station has bikes available."""
    row = conn.execute(
        "SELECT bikes FROM stations WHERE id = ?",
        (station_id,)
    ).fetchone()
    if row is None or row[0] is None:
        return False
    return row[0] > 0


def main() -> None:
    """Execute demonstration routine."""
    add_station("Central Park", 10, 10)
    add_station("Metro Gate", 8, 2)
    print(rent_bike(2), rent_bike(9) is None)
    print(unlock_pin(), full_stations(), has_bikes(2))
    reset_station(1)


if __name__ == "__main__":
    main()
