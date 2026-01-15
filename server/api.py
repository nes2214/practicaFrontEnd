"""
api.py
------
API module for Clinic Manager.

This module defines FastAPI routes for user authentication,
patient and doctor management, appointments, diagnoses, and file handling.
It includes dependencies for database access, OAuth2 authentication,
and role-based access control (RBAC) to secure routes.
"""

from fastapi import APIRouter, Depends, Body, Path, Query, Request, UploadFile, File, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import asyncpg
from asyncpg.exceptions import UniqueViolationError
import uuid
from typing import List, Optional
from loguru import logger
import time

from storage import client, settings
from users import verify_password, create_access_token, get_user, decode_access_token, create_user
from model import (
    Patient, PatientCreate, PatientUpdate,
    Doctor, DoctorCreate, DoctorUpdate,
    Diagnosis, DiagnosisCreate, DiagnosisUpdate,
    Appointment, AppointmentUpdate, AppointmentCreate,
    FileDB,
    TokenResponse, UserToken
)

clinic_router = APIRouter()


# -------------------------------
# DATABASE DEPENDENCY
# -------------------------------
def get_postgres(request: Request) -> asyncpg.Pool:
    """
    Dependency to provide the asyncpg connection pool.

    Args:
        request (Request): FastAPI request object.

    Returns:
        asyncpg.Pool: The database connection pool.
    """
    return request.app.state.pool


# -------------------------------
# OAUTH2 SCHEME
# -------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserToken:
    """
    Decode JWT token and return the current user.

    Args:
        token (str): JWT token from Authorization header.

    Raises:
        HTTPException: If token is invalid or expired.

    Returns:
        UserToken: Object containing username and role.
    """
    user = decode_access_token(token)
    if not user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# -------------------------------
# ROLE DEPENDENCY
# -------------------------------
def require_role(allowed_roles: List[str]):
    """
    Dependency factory to enforce role-based access control.

    Args:
        allowed_roles (List[str]): List of roles allowed to access the route.

    Returns:
        Callable: A dependency that raises HTTP 403 if role is not allowed.
    """
    def role_checker(user: UserToken = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return role_checker

# -------------------------------
# Public Test Method
# -------------------------------
# Servei web de prova.
@clinic_router.get("/api/time")
def get_current_time():
    return {"time": time.time()}


# -------------------------------
# LOGIN (GET TOKEN)
# -------------------------------
@clinic_router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    pool: asyncpg.Pool = Depends(get_postgres)
):
    """
    Authenticate user and return JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Contains username and password.
        pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If credentials are invalid.

    Returns:
        TokenResponse: Access token for authenticated user.
    """
    user_row = await get_user(form_data.username, pool)
    if not user_row or not verify_password(form_data.password, user_row["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_token = UserToken(username=user_row["username"], role=user_row["role"])
    access_token = create_access_token(data={"sub": user_token.username, "role": user_token.role})
    return TokenResponse(access_token=access_token)


# -------------------------------
# CREATE USER
# -------------------------------
@clinic_router.post("/users", response_model=UserToken)
async def create_new_user(
    username: str = Body(...),
    password: str = Body(...),
    role: str = Body("patient"),
    pool: asyncpg.Pool = Depends(get_postgres)
):
    """
    Create a new user with the specified role.

    Args:
        username (str): Desired username.
        password (str): Plain password.
        role (str): Role of the user ('patient', 'doctor', 'admin').
        pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If username already exists.

    Returns:
        UserToken: Username and role of the created user.
    """
    try:
        await create_user(username, password, pool, role)
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    return UserToken(username=username, role=role)


# -------------------------------
# CURRENT USER
# -------------------------------
@clinic_router.get("/users/me", response_model=UserToken)
async def read_users_me(current_user: UserToken = Depends(get_current_user)):
    """
    Get information of the currently authenticated user.

    Args:
        current_user (UserToken): Provided by get_current_user dependency.

    Returns:
        UserToken: Username and role of the current user.
    """
    return current_user


# =====================================================================
#                               PATIENTS
# =====================================================================

@clinic_router.post("/patients", response_model=Patient, dependencies=[Depends(require_role(["admin"]))])
async def create_patient(
    patient: PatientCreate = Body(...),
    db_pool: asyncpg.Pool = Depends(get_postgres),
) -> Patient:
    """
    Create a new patient record.

    Args:
        patient (PatientCreate): Patient data to insert.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If username already exists or database error occurs.

    Returns:
        Patient: Created patient record.
    """
    query = """
        INSERT INTO patients (username, name, birthDate)
        VALUES ($1, $2, $3)
        RETURNING username, name, birthDate
    """
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(query, patient.username, patient.name, patient.birthDate)

        if not row:
            raise HTTPException(status_code=500, detail="Failed to create patient")

        return Patient(**row)

    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail="Internal error creating patient")


@clinic_router.get("/patients", response_model=List[Patient], dependencies=[Depends(require_role(["admin", "doctor", "patient"]))])
async def list_patients(
    db_pool: asyncpg.Pool = Depends(get_postgres),
) -> List[Patient]:
    """
    Retrieve a list of all patients.

    Args:
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If database query fails.

    Returns:
        List[Patient]: List of all patients in the system.
    """
    query = "SELECT username, name, birthDate FROM patients ORDER BY username"

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [Patient(**r) for r in rows]

    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(status_code=500, detail="Error fetching patients")


@clinic_router.get("/patients/{username}", response_model=Patient, dependencies=[Depends(require_role(["admin", "doctor", "patient"]))])
async def get_patient(
    username: str,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Retrieve a single patient by username.

    Args:
        username (str): Patient username to query.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If patient not found or database error occurs.

    Returns:
        Patient: Patient data for the specified username.
    """
    query = "SELECT username, name, birthDate FROM patients WHERE username=$1"

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(query, username)

        if not row:
            raise HTTPException(status_code=404, detail="Patient not found")

        return Patient(**row)

    except Exception as e:
        logger.error(f"Error fetching patient: {e}")
        raise HTTPException(status_code=500, detail="Internal error fetching patient")


@clinic_router.patch("/patients/{username}", response_model=Patient, dependencies=[Depends(require_role(["admin"]))])
async def update_patient(
    username: str,
    updates: PatientUpdate,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Update patient details (name and/or birth date).

    Args:
        username (str): Username of patient to update.
        updates (PatientUpdate): Fields to update (optional).
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If patient not found or database error occurs.

    Returns:
        Patient: Updated patient data.
    """
    query = """
        UPDATE patients
        SET name = COALESCE($1, name),
            birthDate = COALESCE($2, birthDate)
        WHERE username = $3
        RETURNING username, name, birthDate
    """

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(query, updates.name, updates.birthDate, username)

        if not row:
            raise HTTPException(status_code=404, detail="Patient not found")

        return Patient(**row)

    except Exception as e:
        logger.error(f"Error updating patient: {e}")
        raise HTTPException(status_code=500, detail="Internal error updating patient")


@clinic_router.delete("/patients/{username}", dependencies=[Depends(require_role(["admin"]))])
async def delete_patient(
    username: str,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Delete a patient by username.

    Args:
        username (str): Username of patient to delete.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If patient not found or database error occurs.

    Returns:
        dict: Message confirming deletion.
    """
    query = "DELETE FROM patients WHERE username=$1 RETURNING username"

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(query, username)

        if not row:
            raise HTTPException(status_code=404, detail="Patient not found")

        return {"message": f"Patient {username} deleted"}

    except Exception as e:
        logger.error(f"Error deleting patient: {e}")
        raise HTTPException(status_code=500, detail="Internal error deleting patient")


# =====================================================================
#                               DOCTORS
# =====================================================================

@clinic_router.post("/doctors", response_model=Doctor, dependencies=[Depends(require_role(["admin"]))])
async def create_doctor(
    doctor: DoctorCreate,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Create a new doctor record.

    Args:
        doctor (DoctorCreate): Doctor data to insert.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If username already exists or database error occurs.

    Returns:
        Doctor: Created doctor record.
    """
    query = """
        INSERT INTO doctors (username, name, specialty)
        VALUES ($1, $2, $3)
        RETURNING username, name, specialty
    """

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(query, doctor.username, doctor.name, doctor.specialty)

        if not row:
            raise HTTPException(status_code=500, detail="Failed to create doctor")

        return Doctor(**row)

    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Doctor username already exists")
    except Exception as e:
        logger.error(f"Error creating doctor: {e}")
        raise HTTPException(status_code=500, detail="Internal error creating doctor")


@clinic_router.get("/doctors", response_model=List[Doctor], dependencies=[Depends(require_role(["admin", "doctor", "patient"]))])
async def list_doctors(db_pool: asyncpg.Pool = Depends(get_postgres)):
    """
    Retrieve a list of all doctors.

    Args:
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If database query fails.

    Returns:
        List[Doctor]: List of all doctors in the system.
    """
    query = "SELECT username, name, specialty FROM doctors ORDER BY username"

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(query)

        return [Doctor(**r) for r in rows]

    except Exception as e:
        logger.error(f"Error fetching doctors: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@clinic_router.get("/doctors/{username}", response_model=Doctor, dependencies=[Depends(require_role(["admin", "doctor", "patient"]))])
async def get_doctor(username: str, db_pool: asyncpg.Pool = Depends(get_postgres)):
    """
    Retrieve a single doctor by username.

    Args:
        username (str): Doctor username to query.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If doctor not found.

    Returns:
        Doctor: Doctor data for the specified username.
    """
    query = "SELECT username, name, specialty FROM doctors WHERE username=$1"

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, username)

    if not row:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return Doctor(**row)


@clinic_router.patch("/doctors/{username}", response_model=Doctor, dependencies=[Depends(require_role(["admin"]))])
async def update_doctor(
    username: str,
    updates: DoctorUpdate,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Update doctor details (name and/or specialty).

    Args:
        username (str): Username of doctor to update.
        updates (DoctorUpdate): Fields to update (optional).
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If doctor not found.

    Returns:
        Doctor: Updated doctor data.
    """
    query = """
        UPDATE doctors
        SET name = COALESCE($1, name),
            specialty = COALESCE($2, specialty)
        WHERE username = $3
        RETURNING username, name, specialty
    """

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, updates.name, updates.specialty, username)

    if not row:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return Doctor(**row)


@clinic_router.delete("/doctors/{username}", dependencies=[Depends(require_role(["admin"]))])
async def delete_doctor(username: str, db_pool: asyncpg.Pool = Depends(get_postgres)):
    """
    Delete a doctor by username.

    Args:
        username (str): Username of doctor to delete.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If doctor not found.

    Returns:
        dict: Message confirming deletion.
    """
    query = "DELETE FROM doctors WHERE username=$1 RETURNING username"

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, username)

    if not row:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return {"message": f"Doctor {username} deleted"}


# =====================================================================
#                               DIAGNOSIS
# =====================================================================

@clinic_router.post("/diagnosis", response_model=Diagnosis, dependencies=[Depends(require_role(["doctor"]))])
async def create_diagnosis(
    diag: DiagnosisCreate,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Create a new diagnosis record.

    Args:
        diag (DiagnosisCreate): Diagnosis data to insert.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If creation fails.

    Returns:
        Diagnosis: Created diagnosis record.
    """
    query = """
        INSERT INTO diagnosis (diagnosis_date, icd, description, patient_id, doctor_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id_diagnosis, diagnosis_date, icd, description, patient_id, doctor_id
    """

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            query,
            diag.diagnosis_date, diag.icd, diag.description, diag.patient_id, diag.doctor_id
        )

    if not row:
        raise HTTPException(status_code=500, detail="Failed to create diagnosis")

    return Diagnosis(**row)


@clinic_router.get("/diagnosis", response_model=List[Diagnosis], dependencies=[Depends(require_role(["admin", "doctor", "patient"]))])
async def list_diagnosis(db_pool: asyncpg.Pool = Depends(get_postgres)):
    """
    Retrieve a list of all diagnoses.

    Args:
        db_pool (asyncpg.Pool): Database connection pool.

    Returns:
        List[Diagnosis]: List of all diagnosis records.
    """
    query = """
        SELECT id_diagnosis, diagnosis_date, icd, description, patient_id, doctor_id
        FROM diagnosis
        ORDER BY id_diagnosis
    """

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(query)

    return [Diagnosis(**r) for r in rows]


@clinic_router.get("/diagnosis/{id_diagnosis}", response_model=Diagnosis, dependencies=[Depends(require_role(["doctor", "patient"]))])
async def get_diagnosis(id_diagnosis: int, db_pool: asyncpg.Pool = Depends(get_postgres)):
    """
    Retrieve a single diagnosis by its ID.

    Args:
        id_diagnosis (int): ID of the diagnosis.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If diagnosis not found.

    Returns:
        Diagnosis: Diagnosis record for the given ID.
    """
    query = """
        SELECT id_diagnosis, diagnosis_date, icd, description, patient_id, doctor_id
        FROM diagnosis
        WHERE id_diagnosis = $1
    """

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, id_diagnosis)

    if not row:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    return Diagnosis(**row)


@clinic_router.patch("/diagnosis/{id_diagnosis}", response_model=Diagnosis, dependencies=[Depends(require_role(["doctor"]))])
async def update_diagnosis(
    id_diagnosis: int,
    updates: DiagnosisUpdate,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Update an existing diagnosis record.

    Args:
        id_diagnosis (int): ID of the diagnosis to update.
        updates (DiagnosisUpdate): Fields to update (optional).
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If diagnosis not found.

    Returns:
        Diagnosis: Updated diagnosis record.
    """
    query = """
        UPDATE diagnosis
        SET diagnosis_date = COALESCE($1, diagnosis_date),
            icd = COALESCE($2, icd),
            description = COALESCE($3, description),
            patient_id = COALESCE($4, patient_id),
            doctor_id = COALESCE($5, doctor_id)
        WHERE id_diagnosis = $6
        RETURNING id_diagnosis, diagnosis_date, icd, description, patient_id, doctor_id
    """

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            query,
            updates.diagnosis_date,
            updates.icd,
            updates.description,
            updates.patient_id,
            updates.doctor_id,
            id_diagnosis
        )

    if not row:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    return Diagnosis(**row)


@clinic_router.delete("/diagnosis/{id_diagnosis}", dependencies=[Depends(require_role(["doctor"]))])
async def delete_diagnosis(
    id_diagnosis: int,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Delete a diagnosis by ID.

    Args:
        id_diagnosis (int): ID of the diagnosis to delete.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If diagnosis not found.

    Returns:
        dict: Confirmation message of deletion.
    """
    query = "DELETE FROM diagnosis WHERE id_diagnosis=$1 RETURNING id_diagnosis"

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, id_diagnosis)

    if not row:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    return {"message": f"Diagnosis {id_diagnosis} deleted"}


# =====================================================================
#                             APPOINTMENTS
# =====================================================================

@clinic_router.post("/appointments", response_model=Appointment, dependencies=[Depends(require_role(["admin"]))])
async def create_appointment(
    ap: AppointmentCreate,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Create a new appointment record.

    Args:
        ap (AppointmentCreate): Appointment data to insert.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If creation fails.

    Returns:
        Appointment: Created appointment record.
    """
    query = """
        INSERT INTO appointments (appointment_date, reason, patient_id, doctor_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id_appointment, appointment_date, reason, patient_id, doctor_id
    """

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, ap.appointment_date, ap.reason, ap.patient_id, ap.doctor_id)

    if not row:
        raise HTTPException(status_code=500, detail="Failed to create appointment")

    return Appointment(**row)


@clinic_router.get("/appointments", response_model=List[Appointment], dependencies=[Depends(require_role(["admin", "doctor", "patient"]))])
async def list_appointments(db_pool: asyncpg.Pool = Depends(get_postgres)):
    """
    Retrieve a list of all appointments.

    Args:
        db_pool (asyncpg.Pool): Database connection pool.

    Returns:
        List[Appointment]: List of all appointments.
    """
    query = """
        SELECT id_appointment, appointment_date, reason, patient_id, doctor_id
        FROM appointments
        ORDER BY appointment_date DESC
    """

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(query)

    return [Appointment(**r) for r in rows]


@clinic_router.get("/appointments/{id_appointment}", response_model=Appointment, dependencies=[Depends(require_role(["admin", "doctor", "patient"]))])
async def get_appointment(
    id_appointment: int,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Retrieve a single appointment by its ID.

    Args:
        id_appointment (int): ID of the appointment.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If appointment not found.

    Returns:
        Appointment: Appointment record for the given ID.
    """
    query = """
        SELECT id_appointment, appointment_date, reason, patient_id, doctor_id
        FROM appointments
        WHERE id_appointment = $1
    """

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, id_appointment)

    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return Appointment(**row)


@clinic_router.patch("/appointments/{id_appointment}", response_model=Appointment, dependencies=[Depends(require_role(["admin"]))])
async def update_appointment(
    id_appointment: int,
    updates: AppointmentUpdate,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Update an existing appointment record.

    Args:
        id_appointment (int): ID of the appointment to update.
        updates (AppointmentUpdate): Fields to update (optional).
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If appointment not found.

    Returns:
        Appointment: Updated appointment record.
    """
    query = """
        UPDATE appointments
        SET appointment_date = COALESCE($1, appointment_date),
            reason = COALESCE($2, reason),
            patient_id = COALESCE($3, patient_id),
            doctor_id = COALESCE($4, doctor_id)
        WHERE id_appointment = $5
        RETURNING id_appointment, appointment_date, reason, patient_id, doctor_id
    """

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            query,
            updates.appointment_date,
            updates.reason,
            updates.patient_id,
            updates.doctor_id,
            id_appointment
        )

    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return Appointment(**row)


@clinic_router.delete("/appointments/{id_appointment}", dependencies=[Depends(require_role(["admin"]))])
async def delete_appointment(
    id_appointment: int,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Delete an appointment by ID.

    Args:
        id_appointment (int): ID of the appointment to delete.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If appointment not found.

    Returns:
        dict: Confirmation message of deletion.
    """
    query = "DELETE FROM appointments WHERE id_appointment=$1 RETURNING id_appointment"

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, id_appointment)

    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return {"message": f"Appointment {id_appointment} deleted"}


# =====================================================================
#                                 FILES
# =====================================================================

@clinic_router.post("/files/upload", response_model=FileDB, dependencies=[Depends(require_role(["admin", "doctor"]))])
async def upload_file(
    patient_id: str = Query(...),
    doctor_id: Optional[str] = Query(None),
    diagnosis_id: Optional[int] = Query(None),
    appointment_id: Optional[int] = Query(None),
    file: UploadFile = File(...),
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Upload a file for a patient, optionally linked to a doctor, diagnosis, or appointment.

    Args:
        patient_id (str): ID of the patient the file is associated with.
        doctor_id (Optional[str]): ID of the doctor uploading the file.
        diagnosis_id (Optional[int]): Optional ID of the linked diagnosis.
        appointment_id (Optional[int]): Optional ID of the linked appointment.
        file (UploadFile): The file to upload.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If upload to Filebase fails.

    Returns:
        FileDB: Metadata of the uploaded file.
    """

    # Generate a unique name for the object stored in Filebase bucket
    file_name = f"{uuid.uuid4()}_{file.filename}"

    # ---------- Upload to Filebase ----------
    try:
        client.put_object(
            bucket_name=settings.bucket_name,
            object_name=file_name,
            data=file.file,
            length=-1,  # streaming upload
            part_size=10 * 1024 * 1024,  # 10 MB chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filebase upload failed: {e}")

    # ---------- Retrieve IPFS CID from Filebase ----------
    try:
        stat = client.stat_object(settings.bucket_name, file_name)
        cid = stat.metadata.get("x-amz-meta-cid")

        if not cid:
            raise Exception("CID not found in Filebase metadata")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Filebase CID: {e}")

    # ---------- Build real Filebase Gateway URL ----------
    url = f"https://{settings.filebase_gateway}/ipfs/{cid}"

    # ---------- Insert metadata into DB ----------
    query = """
            INSERT INTO files (file_name, original_name, url, mime_type, uploaded_at, \
                               patient_id, doctor_id, diagnosis_id, appointment_id)
            VALUES ($1, $2, $3, $4, NOW(), $5, $6, $7, $8) RETURNING
            id_file, file_name, original_name, url, mime_type, uploaded_at,
            patient_id, doctor_id, diagnosis_id, appointment_id \
            """

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            query,
            file_name,
            file.filename,
            url,
            file.content_type,
            patient_id,
            doctor_id,
            diagnosis_id,
            appointment_id,
        )

    return FileDB(**row)


@clinic_router.get("/files", response_model=List[FileDB], dependencies=[Depends(require_role(["admin", "doctor", "patient"]))])
async def list_files(db_pool: asyncpg.Pool = Depends(get_postgres)):
    """
    Retrieve a list of all files.

    Args:
        db_pool (asyncpg.Pool): Database connection pool.

    Returns:
        List[FileDB]: List of all uploaded files.
    """
    query = """
        SELECT
            id_file, file_name, original_name, url, mime_type, uploaded_at,
            patient_id, doctor_id, diagnosis_id, appointment_id
        FROM files
        ORDER BY uploaded_at DESC
    """

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(query)

    return [FileDB(**r) for r in rows]


@clinic_router.get("/files/{id_file}", response_model=FileDB, dependencies=[Depends(require_role(["admin", "doctor", "patient"]))])
async def get_file(id_file: int, db_pool: asyncpg.Pool = Depends(get_postgres)):
    """
    Retrieve metadata for a specific file by its ID.

    Args:
        id_file (int): ID of the file.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If the file is not found.

    Returns:
        FileDB: Metadata of the requested file.
    """
    query = """
        SELECT
            id_file, file_name, original_name, url, mime_type, uploaded_at,
            patient_id, doctor_id, diagnosis_id, appointment_id
        FROM files
        WHERE id_file = $1
    """

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, id_file)

    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    return FileDB(**row)


@clinic_router.delete("/files/{id_file}", dependencies=[Depends(require_role(["admin", "doctor"]))])
async def delete_file(
    id_file: int,
    db_pool: asyncpg.Pool = Depends(get_postgres),
):
    """
    Delete a file from Filebase and its metadata from the database.

    Args:
        id_file (int): ID of the file to delete.
        db_pool (asyncpg.Pool): Database connection pool.

    Raises:
        HTTPException: If the file does not exist or deletion fails.

    Returns:
        dict: Confirmation message of deletion.
    """
    # Retrieve the object name
    query = "SELECT file_name FROM files WHERE id_file = $1"

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(query, id_file)

    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    object_name = row["file_name"]

    # Delete from Filebase
    try:
        client.remove_object(settings.bucket_name, object_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filebase delete error: {e}")

    # Delete from database
    delete_query = "DELETE FROM files WHERE id_file = $1"

    async with db_pool.acquire() as conn:
        await conn.execute(delete_query, id_file)

    return {"message": f"File {id_file} deleted"}