import { useEffect, useState } from "react";
import { Container, Row, Col, Button, Alert, Spinner } from "react-bootstrap";
import AddPatientsForm from "../../components/addPatientForm";
import { Patient } from "../../utils/types";
import ListPatients from "../../components/listPatients";
import SearchPatients from "../../components/searchPatinents";
import EditPatientForm from "../../components/editPatient";
import { getToken, getUserRole } from "../../utils/auth";
import { useNavigate } from "react-router-dom"; 

export default function Patients() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);EditPatientForm
  const [editingPatient, setEditingPatient] = useState<Patient | null>(null);


  const fetchPatients = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = getToken();

      const res = await fetch("api/patients", {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });

      if (!res.ok) {
        throw new Error(`HTTP error ${res.status}`);
      }

      const data: Patient[] = await res.json();
      console.log("Patients data:", data);
      setPatients(data);
      setFilteredPatients(data); // ← AÑADE ESTA LÍNEA
    } catch (err) {
      console.error(err);
      setError("No s'han pogut carregar els pacients");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const calculateAge = (birthdate: string): number => {
    const birth = new Date(birthdate);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    
    return age;
  };

  const handleSearch = (searchTerm: string) => {
    if (!searchTerm.trim()) {
      setFilteredPatients(patients);
      return;
    }

    const lowerSearch = searchTerm.toLowerCase();
    const filtered = patients.filter((patient) => {
      const matchName = patient.name?.toLowerCase().includes(lowerSearch);
      const matchUsername = patient.username?.toLowerCase().includes(lowerSearch);
      const matchBirthdate = patient.birthdate?.toLowerCase().includes(lowerSearch);
      
      return matchName || matchUsername || matchBirthdate;
    });

    setFilteredPatients(filtered);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ca-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" role="status" variant="primary">
          <span className="visually-hidden">Carregant...</span>
        </Spinner>
        <p className="mt-3">Carregant pacients…</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container className="py-5">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h2 className="mb-0">Pacients</h2>
            <Button
              variant="primary"
              onClick={() => setShowForm(true)}
              disabled={showForm}
            >
              <i className="bi bi-plus-circle me-2"></i>
              Afegir Pacient
            </Button>
          </div>
        </Col>
      </Row>

      {showForm && (
        <Row className="mb-4">
          <Col>
            <AddPatientsForm
              onPatientAdded={() => { 
                setShowForm(false);
                fetchPatients();
              }}
              onCancel={() => setShowForm(false)}
            />
          </Col>
        </Row>
      )}
      {editingPatient && (
        <Row className="mb-4">
          <Col>
            <EditPatientForm
              patient={editingPatient}
              onPatientUpdated={() => {
                setEditingPatient(null);
                fetchPatients();
              }}
              onCancel={() => setEditingPatient(null)}
            />
          </Col>
        </Row>
      )}

      <Row>
        <Col>
          <SearchPatients onSearch={handleSearch} />
        </Col>
      </Row>

      <Row>
        <Col>
          {filteredPatients.length === 0 && patients.length > 0 ? (
            <Alert variant="info">
              No s'han trobat pacients amb els criteris de cerca.
            </Alert>
          ) : (
          <ListPatients 
            patients={filteredPatients} 
            onPatientDeleted={fetchPatients}
            onPatientEdit={(patient) => {
              setShowForm(false); // oculta el formulario de añadir
              setEditingPatient(patient); // muestra el formulario de edición
            }}
          />
     
          )}
        </Col>
      </Row>
    </Container>
  );
}