"""
main.py
-------
Model definitions

This file contains all Pydantic models used in the API, including
Patients, Doctors, Diagnosis, Appointments, Files, and Token models.
These models define both database representations and request/response
schemas for FastAPI endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime


# ===================================================================
#                            PATIENTS
# ===================================================================

class Patient(BaseModel):
    """
    Represents a patient row from the database.

    Attributes:
        username (str): Unique username of the patient.
        name (str): Full name of the patient.
        birthDate (date): Birthdate of the patient.
    """
    model_config = ConfigDict(from_attributes=True)

    username: str
    name: str
    birthDate: date = Field(alias="birthdate")


class PatientCreate(BaseModel):
    """
    Required fields to create a new patient.

    Attributes:
        username (str): Unique username of the patient (max length 50).
        name (str): Full name of the patient (max length 100).
        birthDate (date): Birthdate of the patient.
    """
    username: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    birthDate: date


class PatientUpdate(BaseModel):
    """
    Optional fields for partial update (PATCH) of a patient.

    Attributes:
        name (Optional[str]): Full name of the patient (max length 100).
        birthDate (Optional[date]): Birthdate of the patient.
    """
    name: Optional[str] = Field(None, max_length=100)
    birthDate: Optional[date] = None


# ===================================================================
#                            DOCTORS
# ===================================================================

class Doctor(BaseModel):
    """
    Represents a doctor row from the database.

    Attributes:
        username (str): Unique username of the doctor.
        name (str): Full name of the doctor.
        specialty (Optional[str]): Specialty of the doctor.
    """
    model_config = ConfigDict(from_attributes=True)

    username: str
    name: str
    specialty: Optional[str] = None


class DoctorCreate(BaseModel):
    """
    Required fields to create a new doctor.

    Attributes:
        username (str): Unique username of the doctor (max length 50).
        name (str): Full name of the doctor (max length 100).
        specialty (Optional[str]): Specialty of the doctor (max length 100).
    """
    username: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    specialty: Optional[str] = Field(None, max_length=100)


class DoctorUpdate(BaseModel):
    """
    Optional fields for partial update (PATCH) of a doctor.

    Attributes:
        name (Optional[str]): Full name of the doctor (max length 100).
        specialty (Optional[str]): Specialty of the doctor (max length 100).
    """
    name: Optional[str] = Field(None, max_length=100)
    specialty: Optional[str] = Field(None, max_length=100)


# ===================================================================
#                            DIAGNOSIS
# ===================================================================

class Diagnosis(BaseModel):
    """
    Represents a diagnosis row in the database.

    Attributes:
        id_diagnosis (int): Primary key of the diagnosis.
        diagnosis_date (date): Date of the diagnosis.
        icd (Optional[str]): ICD code of the diagnosis (max length 7).
        description (Optional[str]): Description of the diagnosis.
        patient_id (str): ID of the patient.
        doctor_id (Optional[str]): ID of the doctor (nullable).
    """
    model_config = ConfigDict(from_attributes=True)

    id_diagnosis: int
    diagnosis_date: date
    icd: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = None
    patient_id: str
    doctor_id: Optional[str] = None


class DiagnosisCreate(BaseModel):
    """
    Required fields to create a new diagnosis.

    Attributes:
        diagnosis_date (date): Date of the diagnosis.
        icd (Optional[str]): ICD code (max length 7).
        description (Optional[str]): Description of the diagnosis.
        patient_id (str): ID of the patient.
        doctor_id (Optional[str]): ID of the doctor (nullable).
    """
    diagnosis_date: date
    icd: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = None
    patient_id: str
    doctor_id: Optional[str] = None


class DiagnosisUpdate(BaseModel):
    """
    Optional fields for partial updates of a diagnosis (PATCH).

    Attributes:
        diagnosis_date (Optional[date]): Date of the diagnosis.
        icd (Optional[str]): ICD code (max length 7).
        description (Optional[str]): Description of the diagnosis.
        patient_id (Optional[str]): ID of the patient.
        doctor_id (Optional[str]): ID of the doctor.
    """
    diagnosis_date: Optional[date] = None
    icd: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = None
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None


# ===================================================================
#                          APPOINTMENTS
# ===================================================================

class Appointment(BaseModel):
    """
    Represents an appointment row from the database.

    Attributes:
        id_appointment (int): Primary key of the appointment.
        appointment_date (date): Date of the appointment.
        reason (str): Reason for the appointment.
        patient_id (str): ID of the patient.
        doctor_id (str): ID of the doctor.
    """
    model_config = ConfigDict(from_attributes=True)

    id_appointment: int
    appointment_date: date
    reason: str
    patient_id: str
    doctor_id: str


class AppointmentCreate(BaseModel):
    """
    Required fields to create a new appointment.

    Attributes:
        appointment_date (date): Date of the appointment.
        reason (str): Reason for the appointment.
        patient_id (str): ID of the patient.
        doctor_id (str): ID of the doctor.
    """
    appointment_date: date
    reason: str
    patient_id: str
    doctor_id: str


class AppointmentUpdate(BaseModel):
    """
    Optional fields for partial update (PATCH) of an appointment.

    Attributes:
        appointment_date (Optional[date]): Date of the appointment.
        reason (Optional[str]): Reason for the appointment.
        patient_id (Optional[str]): ID of the patient.
        doctor_id (Optional[str]): ID of the doctor.
    """
    appointment_date: Optional[date] = None
    reason: Optional[str] = None
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None


# ===================================================================
#                              FILES
# ===================================================================

class FileDB(BaseModel):
    """
    Represents a file row from the database.

    Attributes:
        id_file (int): Primary key of the file.
        file_name (str): Internal filename stored in bucket.
        original_name (str): Original uploaded filename.
        url (str): Public URL to access the file.
        mime_type (str): MIME type of the file.
        uploaded_at (datetime): Timestamp of upload.
        patient_id (Optional[str]): Associated patient ID.
        doctor_id (Optional[str]): Associated doctor ID.
        diagnosis_id (Optional[int]): Linked diagnosis ID.
        appointment_id (Optional[int]): Linked appointment ID.
    """
    model_config = ConfigDict(from_attributes=True)

    id_file: int
    file_name: str
    original_name: str
    url: str
    mime_type: str
    uploaded_at: datetime
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None
    diagnosis_id: Optional[int] = None
    appointment_id: Optional[int] = None


# ===================================================================
#                         TOKENS / JWT
# ===================================================================

class UserToken(BaseModel):
    """
    Represents the decoded JWT user information.

    Attributes:
        username (Optional[str]): Username of the user.
        role (Optional[str]): Role of the user ("patient", "doctor", "admin").
    """
    username: str | None
    role: str | None


class TokenResponse(BaseModel):
    """
    Response model for login endpoint.

    Attributes:
        access_token (str): JWT access token.
        token_type (str): Type of token, default "bearer".
    """
    access_token: str
    token_type: str = "bearer"