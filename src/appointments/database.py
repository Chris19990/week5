import sqlite3

from src.config import APPOINTMENTS_DB_PATH


def get_connection():
    connection = sqlite3.connect(
        APPOINTMENTS_DB_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # ========================================================
    # CLINICS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clinics (
            clinic_id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL,
            daily_limit INTEGER NOT NULL,
            opening_time TEXT NOT NULL,
            closing_time TEXT NOT NULL,
            saturday_opening_time TEXT,
            saturday_closing_time TEXT,
            active INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    # ========================================================
    # SERVICES
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS services (
            service_id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            duration_minutes INTEGER NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    # ========================================================
    # APPOINTMENTS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            clinic_location TEXT NOT NULL,
            service TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def seed_demo_data():
    connection = get_connection()
    cursor = connection.cursor()

    # ========================================================
    # DEMO CLINICS
    # ========================================================

    clinics = [
        (
            "CLINIC-CENTRAL",
            "Central Clinic",
            "14 Wellness Avenue, Central District",
            10,
            "08:00",
            "18:00",
            "09:00",
            "14:00",
            1,
        ),
        (
            "CLINIC-LAKESIDE",
            "Lakeside Clinic",
            "8 Care Street, Lakeside District",
            8,
            "08:00",
            "18:00",
            "09:00",
            "14:00",
            1,
        ),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO clinics (
            clinic_id,
            name,
            address,
            daily_limit,
            opening_time,
            closing_time,
            saturday_opening_time,
            saturday_closing_time,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        clinics,
    )

    # ========================================================
    # DEMO SERVICES
    # ========================================================

    services = [
        (
            "SERVICE-GENERAL",
            "General outpatient consultation",
            60,
            1,
        ),
        (
            "SERVICE-FOLLOWUP",
            "Follow-up consultation",
            30,
            1,
        ),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO services (
            service_id,
            name,
            duration_minutes,
            active
        )
        VALUES (?, ?, ?, ?)
        """,
        services,
    )

    # ========================================================
    # EXISTING DEMO APPOINTMENTS
    # ========================================================

    demo_appointments = [
        (
            "HC-1001",
            "P-001",
            "Demo Patient",
            "Central Clinic",
            "General outpatient consultation",
            "2026-09-10",
            "10:00",
            "SCHEDULED",
            "2026-09-01T10:00:00",
            "2026-09-01T10:00:00",
        ),
        (
            "HC-1002",
            "P-002",
            "Demo Patient Two",
            "Lakeside Clinic",
            "Follow-up consultation",
            "2026-09-12",
            "14:00",
            "SCHEDULED",
            "2026-09-01T11:00:00",
            "2026-09-01T11:00:00",
        ),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO appointments (
            appointment_id,
            patient_id,
            patient_name,
            clinic_location,
            service,
            appointment_date,
            appointment_time,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        demo_appointments,
    )

    connection.commit()
    connection.close()
