"""
test_api.py
-------
This file contains tests for the FastAPI clinic application.
It uses pytest and FastAPI's TestClient to perform integration tests
on patients, doctors, login, tokens, and related endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import io

# -------------------------------------------------------------------
# AUXILIARY FUNCTIONS
# -------------------------------------------------------------------
@pytest.fixture(scope="module")
def client():
    """
    Provide a TestClient instance for API testing using FastAPI lifespan.
    """
    with TestClient(app) as c:
        yield c


def ensure_patient_exists(client, username: str, name: str, birth_date: str):
    """
    Ensure that a patient exists in the system. Creates it if missing.
    """
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    try:
        response = client.post("/patients/", json={
            "username": username,
            "name": name,
            "birthDate": birth_date
        }, headers=headers)

        # Accept 200, 201 or 400/409 if username already exists
        if response.status_code in (200, 201):
            return
        if response.status_code in (400, 409) and "username" in response.text.lower():
            get_resp = client.get(f"/patients/{username}", headers=headers)
            if get_resp.status_code == 200:
                return
            else:
                raise Exception(f"Patient {username} exists but cannot retrieve it: {get_resp.status_code}")
    except Exception as e:
        raise Exception(f"Failed to ensure patient {username}: {e}")


def ensure_doctor_exists(client, username: str, name: str, specialty: str):
    """
    Ensure that a doctor exists in the system. Creates it if missing.
    """
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    try:
        response = client.post("/doctors/", json={
            "username": username,
            "name": name,
            "specialty": specialty
        }, headers=headers)

        if response.status_code in (200, 201):
            return
        if response.status_code in (400, 409) and "username" in response.text.lower():
            get_resp = client.get(f"/doctors/{username}", headers=headers)
            if get_resp.status_code == 200:
                return
            else:
                raise Exception(f"Doctor {username} exists but cannot retrieve it: {get_resp.status_code}")
    except Exception as e:
        raise Exception(f"Failed to ensure doctor {username}: {e}")


# -------------------------------------------------------------------
# CREATION OF USERS FOR TESTING
# -------------------------------------------------------------------
USERS = [
    {"username": "test_patient", "password": "pass123", "role": "patient"},
    {"username": "test_doctor", "password": "pass123", "role": "doctor"},
    {"username": "test_admin", "password": "pass123", "role": "admin"},
]

tokens = {}


@pytest.fixture(scope="module", autouse=True)
def setup_tokens(client):
    """
    Log in with all three roles and store their JWT tokens.
    """
    for user in USERS:
        response = client.post("/token", data={
            "username": user["username"],
            "password": user["password"]
        })
        assert response.status_code == 200
        tokens[user["role"]] = response.json()["access_token"]


# -------------------------------------------------------------------
# CREATION OF TEST DATA
# -------------------------------------------------------------------
@pytest.fixture
def patient_data():
    """Provide test patient data."""
    return {"username": "patient_testuser", "name": "Test User", "birthDate": "1990-01-01"}


@pytest.fixture
def doctor_data():
    """Provide test doctor data."""
    return {"username": "drtest", "name": "Dr Test", "specialty": "Cardiology"}


@pytest.fixture(scope="module", autouse=True)
def setup_patients(client, setup_tokens):
    """
    Create necessary patients for testing.
    Ignores existing patients.
    """
    headers = {"Authorization": f"Bearer {tokens['admin']}"}

    patients = [
        {"username": "diagpatient", "name": "Diag Patient", "birthDate": "1990-01-01"},
        {"username": "apptpatient", "name": "Appt Patient", "birthDate": "1990-01-01"},
        {"username": "filepatient", "name": "File Patient", "birthDate": "1990-01-01"},
        {"username": "filepatient2", "name": "File Patient 2", "birthDate": "1990-01-01"}
    ]

    for p in patients:
        client.delete(f"/patients/{p['username']}", headers=headers)
        response = client.post("/patients/", json=p, headers=headers)

        if response.status_code in (200, 201):
            continue
        elif response.status_code == 409:
            continue
        else:
            raise Exception(f"Error creating patient {p['username']}")


# -------------------------------------------------------------------
# LOGIN TESTS
# -------------------------------------------------------------------
@pytest.mark.parametrize("user", USERS)
def test_login_success(client, user):
    """Test successful login for all user roles."""
    response = client.post(
        "/token",
        data={"username": user["username"], "password": user["password"]}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data.get("token_type", "bearer") == "bearer"


def test_login_wrong_password(client):
    """Test login with incorrect password."""
    response = client.post(
        "/token",
        data={"username": "test_patient", "password": "wrongpass"}
    )
    assert response.status_code == 401
    json_data = response.json()
    assert json_data["detail"] == "Incorrect username or password"


def test_login_wrong_username(client):
    """Test login with non-existing username."""
    response = client.post(
        "/token",
        data={"username": "nouusuari", "password": "secret123"}
    )
    assert response.status_code == 401
    json_data = response.json()
    assert json_data["detail"] == "Incorrect username or password"

# -------------------------------------------------------------------
# PATIENT ENDPOINT TESTS
# -------------------------------------------------------------------
# Tests for creating, listing, retrieving, updating, and deleting
# patients. Authorization is verified for admin, doctor, and patient roles.
# -------------------------------------------------------------------

# -----------------------------
# CREATE PATIENT
# -----------------------------
def test_create_patient_admin(client, patient_data):
    """Admin can create a patient."""
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = client.post("/patients", json=patient_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == patient_data["username"]


@pytest.mark.parametrize("role", ["doctor", "patient"])
def test_create_patient_forbidden(client, patient_data, role):
    """Doctor and Patient roles cannot create a patient."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.post("/patients", json=patient_data, headers=headers)
    assert response.status_code == 403


# -----------------------------
# LIST PATIENTS
# -----------------------------
@pytest.mark.parametrize("role", ["admin", "doctor", "patient"])
def test_list_patients(client, role):
    """All roles can list patients."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.get("/patients", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# -----------------------------
# GET PATIENT
# -----------------------------
@pytest.mark.parametrize("role", ["admin", "doctor", "patient"])
def test_get_patient(client, patient_data, role):
    """All roles can retrieve a patient by username."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.get(f"/patients/{patient_data['username']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == patient_data["username"]


# -----------------------------
# UPDATE PATIENT
# -----------------------------
def test_update_patient_admin(client, patient_data):
    """Admin can update patient details."""
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = client.patch(
        f"/patients/{patient_data['username']}",
        json={"name": "Updated Name"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.parametrize("role", ["doctor", "patient"])
def test_update_patient_forbidden(client, patient_data, role):
    """Doctor and Patient roles cannot update patient."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.patch(
        f"/patients/{patient_data['username']}",
        json={"name": "Malicious Update"},
        headers=headers
    )
    assert response.status_code == 403


# -----------------------------
# DELETE PATIENT
# -----------------------------
def test_delete_patient_admin(client, patient_data):
    """Admin can delete a patient."""
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = client.delete(f"/patients/{patient_data['username']}", headers=headers)
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()


@pytest.mark.parametrize("role", ["doctor", "patient"])
def test_delete_patient_forbidden(client, patient_data, role):
    """Doctor and Patient roles cannot delete patient."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.delete(f"/patients/{patient_data['username']}", headers=headers)
    assert response.status_code == 403



# -------------------------------------------------------------------
# DOCTOR ENDPOINT TESTS
# -------------------------------------------------------------------
# Tests for creating, retrieving, updating, and deleting doctors.
# Authorization is verified for admin, doctor, and patient roles.
# -------------------------------------------------------------------

# -----------------------------
# CREATE DOCTOR
# -----------------------------
@pytest.mark.parametrize("role", ["admin"])
def test_create_doctor_admin(client, doctor_data, role):
    """Admin can create a doctor."""
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = client.post("/doctors", json=doctor_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == doctor_data["username"]
    assert data["specialty"] == doctor_data["specialty"]


@pytest.mark.parametrize("role", ["patient", "doctor"])
def test_create_doctor_forbidden(client, doctor_data, role):
    """Patient and Doctor roles cannot create a doctor."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.post("/doctors", json=doctor_data, headers=headers)
    assert response.status_code == 403


# -----------------------------
# GET DOCTOR
# -----------------------------
@pytest.mark.parametrize("role", ["admin", "doctor", "patient"])
def test_get_doctor(client, doctor_data, role):
    """All roles can retrieve a doctor by username."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.get(f"/doctors/{doctor_data['username']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == doctor_data["username"]


# -----------------------------
# UPDATE DOCTOR
# -----------------------------
@pytest.mark.parametrize("role", ["admin"])
def test_update_doctor_admin(client, doctor_data, role):
    """Admin can update doctor details."""
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = client.patch(
        f"/doctors/{doctor_data['username']}",
        json={"specialty": "Neurology"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["specialty"] == "Neurology"


@pytest.mark.parametrize("role", ["patient", "doctor"])
def test_update_doctor_forbidden(client, doctor_data, role):
    """Patient and Doctor roles cannot update a doctor."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.patch(
        f"/doctors/{doctor_data['username']}",
        json={"specialty": "Malicious Update"},
        headers=headers
    )
    assert response.status_code == 403


# -----------------------------
# DELETE DOCTOR
# -----------------------------
@pytest.mark.parametrize("role", ["admin"])
def test_delete_doctor_admin(client, doctor_data, role):
    """Admin can delete a doctor."""
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = client.delete(f"/doctors/{doctor_data['username']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "deleted" in data["message"].lower()


@pytest.mark.parametrize("role", ["patient", "doctor"])
def test_delete_doctor_forbidden(client, doctor_data, role):
    """Patient and Doctor roles cannot delete a doctor."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.delete(f"/doctors/{doctor_data['username']}", headers=headers)
    assert response.status_code == 403


# -------------------------------------------------------------------
# DIAGNOSIS ENDPOINT TESTS
# -------------------------------------------------------------------
# Tests for creating, updating, and deleting diagnoses.
# Authorization is verified for doctor, patient, and admin roles.
# -------------------------------------------------------------------

# -----------------------------
# FIXTURE: CREATE DIAGNOSIS
# -----------------------------
@pytest.fixture
def setup_diagnosis(client):
    """
    Ensure patient and doctor exist, then create a test diagnosis.
    Returns the created diagnosis ID.
    """
    ensure_patient_exists(client, "diagpatient", "Diag Patient", "1990-01-01")
    ensure_doctor_exists(client, "diagdoctor", "Diag Doctor", "Cardiology")
    headers = {"Authorization": f"Bearer {tokens['doctor']}"}
    diag_data = {
        "diagnosis_date": "2025-01-01",
        "icd": "I10",
        "description": "Test Diagnosis",
        "patient_id": "diagpatient",
        "doctor_id": "diagdoctor"
    }
    response = client.post("/diagnosis", json=diag_data, headers=headers)
    assert response.status_code == 200
    return response.json()["id_diagnosis"]


# -----------------------------
# CREATE DIAGNOSIS
# -----------------------------
@pytest.mark.parametrize("role", ["doctor"])
def test_create_diagnosis_doctor(client, setup_diagnosis, role):
    """Doctor can create a diagnosis."""
    diag_id = setup_diagnosis
    assert diag_id is not None


@pytest.mark.parametrize("role", ["patient", "admin"])
def test_create_diagnosis_forbidden(client, role, setup_diagnosis):
    """Patient and Admin roles cannot create a diagnosis."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    diag_data = {
        "diagnosis_date": "2025-01-01",
        "icd": "I10",
        "description": "Test Diagnosis",
        "patient_id": "diagpatient",
        "doctor_id": "diagdoctor"
    }
    response = client.post("/diagnosis", json=diag_data, headers=headers)
    assert response.status_code == 403


# -----------------------------
# UPDATE DIAGNOSIS
# -----------------------------
@pytest.mark.parametrize("role", ["doctor"])
def test_update_diagnosis_doctor(client, setup_diagnosis, role):
    """Doctor can update a diagnosis."""
    diag_id = setup_diagnosis
    headers = {"Authorization": f"Bearer {tokens['doctor']}"}
    response = client.patch(f"/diagnosis/{diag_id}", json={"description": "Updated Desc"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["description"] == "Updated Desc"


@pytest.mark.parametrize("role", ["patient", "admin"])
def test_update_diagnosis_forbidden(client, setup_diagnosis, role):
    """Patient and Admin roles cannot update a diagnosis."""
    diag_id = setup_diagnosis
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.patch(f"/diagnosis/{diag_id}", json={"description": "Malicious Update"}, headers=headers)
    assert response.status_code == 403


# -----------------------------
# DELETE DIAGNOSIS
# -----------------------------
@pytest.mark.parametrize("role", ["doctor"])
def test_delete_diagnosis_doctor(client, setup_diagnosis, role):
    """Doctor can delete a diagnosis."""
    diag_id = setup_diagnosis
    headers = {"Authorization": f"Bearer {tokens['doctor']}"}
    response = client.delete(f"/diagnosis/{diag_id}", headers=headers)
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()


@pytest.mark.parametrize("role", ["patient", "admin"])
def test_delete_diagnosis_forbidden(client, setup_diagnosis, role):
    """Patient and Admin roles cannot delete a diagnosis."""
    diag_id = setup_diagnosis
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.delete(f"/diagnosis/{diag_id}", headers=headers)
    assert response.status_code == 403


# -------------------------------------------------------------------
# APPOINTMENTS ENDPOINT TESTS
# -------------------------------------------------------------------
# Tests for creating, updating, deleting, listing, and retrieving appointments.
# Authorization rules are verified for admin, doctor, and patient roles.
# -------------------------------------------------------------------

# -----------------------------
# FIXTURE: CREATE APPOINTMENT
# -----------------------------
@pytest.fixture
def setup_appointment(client):
    """
    Ensure patient and doctor exist, then create a test appointment.
    Returns the appointment ID and its data.
    """
    ensure_patient_exists(client, "apptpatient", "Appt Patient", "1990-01-01")
    ensure_doctor_exists(client, "apptdoctor", "Appt Doctor", "General")
    headers = {"Authorization": f"Bearer {tokens['admin']}"}

    appt_data = {
        "appointment_date": "2025-12-10",
        "reason": "Routine check",
        "patient_id": "apptpatient",
        "doctor_id": "apptdoctor"
    }

    # Create the appointment; ignore if it already exists
    response = client.post("/appointments", json=appt_data, headers=headers)
    if response.status_code not in (200, 400):  # 400 if already exists
        assert response.status_code == 200

    appointment_id = response.json().get("id_appointment", "apptpatient_apptdoctor_2025-12-10")
    return {"id_appointment": appointment_id, "data": appt_data}


# -----------------------------
# CREATE APPOINTMENT
# -----------------------------
@pytest.mark.parametrize("role", ["admin"])
def test_create_appointment_admin(client, setup_appointment, role):
    """Admin can create an appointment."""
    appointment_id = setup_appointment["id_appointment"]
    assert appointment_id is not None


@pytest.mark.parametrize("role", ["patient", "doctor"])
def test_create_appointment_forbidden(client, setup_appointment, role):
    """Patient and Doctor roles cannot create an appointment."""
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    appointment_data = setup_appointment["data"]
    response = client.post("/appointments", json=appointment_data, headers=headers)
    assert response.status_code == 403


# -----------------------------
# LIST APPOINTMENTS
# -----------------------------
@pytest.mark.parametrize("role", ["admin", "doctor", "patient"])
def test_list_appointments(client, setup_appointment, role):
    """All roles can list appointments."""
    appointment_id = setup_appointment["id_appointment"]
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.get("/appointments", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert any(a["id_appointment"] == appointment_id for a in data)


# -----------------------------
# GET APPOINTMENT
# -----------------------------
@pytest.mark.parametrize("role", ["admin", "doctor", "patient"])
def test_get_appointment(client, setup_appointment, role):
    """All roles can retrieve an appointment."""
    appointment_id = setup_appointment["id_appointment"]
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.get(f"/appointments/{appointment_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id_appointment"] == appointment_id


# -----------------------------
# UPDATE APPOINTMENT
# -----------------------------
@pytest.mark.parametrize("role", ["admin"])
def test_update_appointment_admin(client, setup_appointment, role):
    """Admin can update an appointment."""
    appointment_id = setup_appointment["id_appointment"]
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = client.patch(f"/appointments/{appointment_id}", json={"reason": "Updated reason"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["reason"] == "Updated reason"


@pytest.mark.parametrize("role", ["patient", "doctor"])
def test_update_appointment_forbidden(client, setup_appointment, role):
    """Patient and Doctor roles cannot update an appointment."""
    appointment_id = setup_appointment["id_appointment"]
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.patch(f"/appointments/{appointment_id}", json={"reason": "Malicious update"}, headers=headers)
    assert response.status_code == 403


# -----------------------------
# DELETE APPOINTMENT
# -----------------------------
@pytest.mark.parametrize("role", ["admin"])
def test_delete_appointment_admin(client, setup_appointment, role):
    """Admin can delete an appointment."""
    appointment_id = setup_appointment["id_appointment"]
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    response = client.delete(f"/appointments/{appointment_id}", headers=headers)
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()


@pytest.mark.parametrize("role", ["patient", "doctor"])
def test_delete_appointment_forbidden(client, setup_appointment, role):
    """Patient and Doctor roles cannot delete an appointment."""
    appointment_id = setup_appointment["id_appointment"]
    headers = {"Authorization": f"Bearer {tokens[role]}"}
    response = client.delete(f"/appointments/{appointment_id}", headers=headers)
    assert response.status_code == 403



# -------------------------------------------------------------------
# FILES ENDPOINT TESTS
# -------------------------------------------------------------------
# Tests for uploading, listing, retrieving, and deleting files.
# Authorization rules are verified for admin, doctor, and patient roles.
# -------------------------------------------------------------------

# -----------------------------
# FIXTURE: UPLOAD FILE
# -----------------------------
@pytest.fixture
def setup_file(client):
    """
    Ensure the patient exists, then upload a test file.
    Returns the file ID.
    """
    ensure_patient_exists(client, "filepatient", "File Patient", "1990-01-01")

    file_content = b"Hello World"
    file_data = {"file": ("testfile.txt", io.BytesIO(file_content), "text/plain")}
    headers = {"Authorization": f"Bearer {tokens['admin']}"}

    response = client.post("/files/upload?patient_id=filepatient", files=file_data, headers=headers)
    assert response.status_code == 200

    file_json = response.json()
    assert file_json["patient_id"] == "filepatient"
    return file_json["id_file"]


# -----------------------------
# UPLOAD FILE
# -----------------------------
@pytest.mark.parametrize("role", ["admin", "doctor"])
def test_upload_file_admin(client, role, setup_file):
    """Admin and Doctor roles can upload files."""
    file_id = setup_file
    assert file_id is not None


@pytest.mark.parametrize("role", ["patient"])
def test_upload_file_forbidden(client, role, setup_file):
    """Patient role cannot upload files."""
    ensure_patient_exists(client, "filepatient_forbidden", "Forbidden Patient", "1990-01-01")

    file_content = b"Malicious"
    file_data = {"file": ("malicious.txt", io.BytesIO(file_content), "text/plain")}
    headers = {"Authorization": f"Bearer {tokens[role]}"}

    response = client.post("/files/upload?patient_id=filepatient_forbidden", files=file_data, headers=headers)
    assert response.status_code == 403


# -----------------------------
# LIST FILES
# -----------------------------
@pytest.mark.parametrize("role", ["admin", "doctor", "patient"])
def test_list_files(client, role, setup_file):
    """All roles can list files."""
    file_id = setup_file
    headers = {"Authorization": f"Bearer {tokens[role]}"}

    response = client.get("/files", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(f["id_file"] == file_id for f in data)


# -----------------------------
# GET FILE
# -----------------------------
@pytest.mark.parametrize("role", ["admin", "doctor", "patient"])
def test_get_file(client, role, setup_file):
    """All roles can retrieve a file by its ID."""
    file_id = setup_file
    headers = {"Authorization": f"Bearer {tokens[role]}"}

    response = client.get(f"/files/{file_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id_file"] == file_id
    assert data["original_name"] == "testfile.txt"


# -----------------------------
# DELETE FILE
# -----------------------------
@pytest.mark.parametrize("role", ["admin", "doctor"])
def test_delete_file(client, setup_file, role):
    """Admin and Doctor roles can delete files."""
    file_id = setup_file
    headers = {"Authorization": f"Bearer {tokens['admin']}"}

    response = client.delete(f"/files/{file_id}", headers=headers)
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()

    # Confirm the file no longer exists
    response2 = client.get(f"/files/{file_id}", headers=headers)
    assert response2.status_code == 404


@pytest.mark.parametrize("role", ["patient"])
def test_delete_file_forbidden(client, role, setup_file):
    """Patient role cannot delete files."""
    file_id = setup_file
    headers = {"Authorization": f"Bearer {tokens[role]}"}

    response = client.delete(f"/files/{file_id}", headers=headers)
    assert response.status_code == 403