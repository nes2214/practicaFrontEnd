"""
db.py
-----
Database module for Clinic Manager.

This module handles the database connection pool, table creation,
role management, grants, and row-level security (RLS) policies. It
provides a lifespan context for FastAPI and initializes the database
with required tables, roles, policies, and test users.
"""

from contextlib import asynccontextmanager
from os import environ
from typing import AsyncIterator

import asyncpg
from loguru import logger
from starlette.types import ASGIApp
from dotenv import load_dotenv
from users import hash_password

load_dotenv()

DATABASE_URL = environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables.")


@asynccontextmanager
async def lifespan(app: ASGIApp) -> AsyncIterator[None]:
    """
    Async context manager for FastAPI lifespan.

    Creates a connection pool, initializes the database, and ensures
    the pool is closed on shutdown.
    """
    app.state.pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=1,
        max_size=10,
    )
    try:
        await init_db(app.state.pool)
        yield
    finally:
        if hasattr(app.state, "pool"):
            try:
                await app.state.pool.close()
                logger.info("Database pool closed successfully.")
            except Exception as e:
                logger.error(f"Error closing pool: {e}")


# ============================================================
#                     TABLE DEFINITIONS
# ============================================================

patients_table = """
CREATE TABLE IF NOT EXISTS patients (
    username VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    birthDate DATE NOT NULL
);
"""

doctors_table = """
CREATE TABLE IF NOT EXISTS doctors (
    username VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100)
);
"""

diagnosis_table = """
CREATE TABLE IF NOT EXISTS diagnosis (
    id_diagnosis SERIAL PRIMARY KEY,
    diagnosis_date DATE NOT NULL,
    icd VARCHAR(7),
    description TEXT,
    patient_id VARCHAR(50) NOT NULL REFERENCES patients(username) ON DELETE CASCADE,
    doctor_id VARCHAR(50) REFERENCES doctors(username) ON DELETE SET NULL
);
"""

appointments_table = """
CREATE TABLE IF NOT EXISTS appointments (
    id_appointment SERIAL PRIMARY KEY,
    appointment_date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    reason TEXT,
    patient_id VARCHAR(50) NOT NULL REFERENCES patients(username) ON DELETE CASCADE,
    doctor_id VARCHAR(50) REFERENCES doctors(username) ON DELETE SET NULL
);
"""

files_table = """
CREATE TABLE IF NOT EXISTS files (
    id_file SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    url TEXT NOT NULL,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    patient_id VARCHAR(50) NOT NULL REFERENCES patients(username) ON DELETE CASCADE,
    doctor_id VARCHAR(50) REFERENCES doctors(username) ON DELETE SET NULL,
    diagnosis_id INTEGER REFERENCES diagnosis(id_diagnosis) ON DELETE CASCADE,
    appointment_id INTEGER REFERENCES appointments(id_appointment) ON DELETE CASCADE
);
"""

users_table = """
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(50) PRIMARY KEY,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('patient', 'doctor', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


# ============================================================
#                     ROLE CREATION
# ============================================================

roles_sql = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='patient') THEN
        CREATE ROLE patient;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='doctor') THEN
        CREATE ROLE doctor;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='anonymous') THEN
        CREATE ROLE anonymous;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='admin') THEN
        CREATE ROLE admin LOGIN PASSWORD 'admin';
    END IF;
END $$;
"""


# ============================================================
#                     RLS + POLICIES
# ============================================================

rls_sql = """
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE diagnosis ENABLE ROW LEVEL SECURITY;

-- PATIENT POLICIES
DO $$
BEGIN
    BEGIN
        CREATE POLICY patients_patient ON patients
            FOR SELECT TO patient
            USING (username = current_user);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;

    BEGIN
        CREATE POLICY diagnosis_patient ON diagnosis
            FOR SELECT TO patient
            USING (patient_id = current_user);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;

    BEGIN
        CREATE POLICY doctors_patient ON doctors
            FOR SELECT TO patient
            USING (
                username IN (SELECT doctor_id FROM diagnosis WHERE patient_id = current_user)
            );
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;
    
-- DOCTOR POLICIES
    BEGIN
        CREATE POLICY diagnosis_doctor ON diagnosis
            FOR SELECT TO doctor
            USING (doctor_id = current_user);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;

    BEGIN
        CREATE POLICY patients_doctor ON patients
            FOR SELECT TO doctor
            USING (
                username IN (SELECT patient_id FROM diagnosis WHERE doctor_id = current_user)
            );
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;
    
-- ANONYMOUS POLICIES
    BEGIN
        CREATE POLICY diagnosis_anonymous ON diagnosis
            FOR SELECT TO anonymous
            USING (false);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;
END $$;
"""

rls_appointments_sql = """
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    -- El pacient veu només les seves cites
    BEGIN
        CREATE POLICY appointments_patient_select ON appointments
            FOR SELECT TO patient
            USING (patient_id = current_user);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;

    -- El doctor veu només les cites on participa
    BEGIN
        CREATE POLICY appointments_doctor_select ON appointments
            FOR SELECT TO doctor
            USING (doctor_id = current_user);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;

    -- Anonymous no veu res
    BEGIN
        CREATE POLICY appointments_anonymous_noaccess ON appointments
            FOR SELECT TO anonymous
            USING (false);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;
END $$;
"""

rls_files_sql = """
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    -- Pacient pot veure només fitxers associats a ell
    BEGIN
        CREATE POLICY files_patient_select ON files
            FOR SELECT TO patient
            USING (patient_id = current_user);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;

    -- Doctor pot veure els fitxers associats als seus patients, diagnosis o appointments
    BEGIN
        CREATE POLICY files_doctor_select ON files
            FOR SELECT TO doctor
            USING (
                -- Fitxers dels seus pacients
                patient_id IN (SELECT patient_id FROM diagnosis WHERE doctor_id = current_user)
                OR
            
                -- Fitxers associats a diagnòstics creats pel doctor
                diagnosis_id IN (SELECT id_diagnosis FROM diagnosis WHERE doctor_id = current_user)
                OR
            
                -- Fitxers associats a cites on participa el doctor
                appointment_id IN (SELECT id_appointment FROM appointments WHERE doctor_id = current_user)
            );
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;

    -- Anonymous no veu res
    BEGIN
        CREATE POLICY files_anonymous_noaccess ON files
            FOR SELECT TO anonymous
            USING (false);
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;
END $$;
"""

# ============================================================
#                     GRANTS
# ============================================================

grants_sql = """
GRANT SELECT ON ALL TABLES IN SCHEMA public TO patient;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO doctor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO admin;
"""


# ============================================================
#                     INIT DATABASE
# ============================================================

async def init_db(pool: asyncpg.Pool) -> None:
    """
    Initialize the database: tables, roles, RLS policies, grants, and test users.

    Args:
        pool (asyncpg.Pool): Connection pool to execute queries.

    Raises:
        Exception: If any step of database initialization fails.
    """
    try:
        async with pool.acquire() as conn:
            # Create tables
            await conn.execute(patients_table)
            await conn.execute(doctors_table)
            await conn.execute(diagnosis_table)
            await conn.execute(appointments_table)
            await conn.execute(files_table)
            await conn.execute(users_table)

            # Create roles
            await conn.execute(roles_sql)

            # Apply grants
            await conn.execute(grants_sql)

            # Apply RLS policies (patients, appointments, files)
            # Assume RLS SQL strings defined above
            await conn.execute(rls_sql)
            await conn.execute(rls_appointments_sql)
            await conn.execute(rls_files_sql)

            # Create test users
            test_users = [
                ("test_patient", "pass123", "patient"),
                ("test_doctor", "pass123", "doctor"),
                ("test_admin", "pass123", "admin"),
            ]
            for username, password, role in test_users:
                hashed = hash_password(password)
                await conn.execute(
                    """
                    INSERT INTO users (username, hashed_password, role)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (username) DO NOTHING
                    """,
                    username, hashed, role
                )

        logger.info("Clinical database initialized successfully.")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise