"""Persistent registry for applications monitored by CloudOps AI."""

import os
import sqlite3
from pathlib import Path

from .validation import validate_application


DEFAULT_DB_PATH = "data/applications.db"


def get_db_path():
    return Path(os.environ.get("CLOUDOPS_DB_PATH", DEFAULT_DB_PATH))


def get_connection():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_registry():
    """Create the application registry table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                environment TEXT NOT NULL,
                health_url TEXT NOT NULL,
                metrics_url TEXT,
                enabled INTEGER NOT NULL DEFAULT 1,
                monitoring_approved INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(applications)")
        }

        if "monitoring_approved" not in columns:
            connection.execute(
                "ALTER TABLE applications "
                "ADD COLUMN monitoring_approved INTEGER NOT NULL DEFAULT 0"
            )


def list_applications():
    """Return all registered applications."""
    initialize_registry()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, environment, health_url,
                   metrics_url, enabled, monitoring_approved, created_at
            FROM applications
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def add_application(name, environment, health_url, metrics_url=None):
    """Store a validated application and return its database ID."""
    validate_application(name, environment, health_url, metrics_url)
    initialize_registry()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO applications
                (name, environment, health_url, metrics_url)
            VALUES (?, ?, ?, ?)
            """,
            (name, environment, health_url, metrics_url),
        )
        return cursor.lastrowid


def set_monitoring_approval(application_id, approved):
    """Approve or revoke monitoring for a registered application.

    Return True if the application exists, otherwise False.
    This only updates the registry; it does not activate Prometheus targets.
    """
    if type(application_id) is not int or application_id < 1:
        raise ValueError("Application ID must be a positive integer")

    if type(approved) is not bool:
        raise ValueError("Approval status must be a boolean")

    initialize_registry()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE applications
            SET monitoring_approved = ?
            WHERE id = ?
            """,
            (int(approved), application_id),
        )

        return cursor.rowcount > 0
