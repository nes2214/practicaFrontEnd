import { useEffect, useState } from "react";
import { Container, Row, Col, Button, Alert, Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom"; // <-- IMPORTA useNavigate
import AddDoctorForms from "../../components/addDoctorForms";
import EditDoctorForm from "../../components/editDoctor";
import { getToken, getUserRole } from "../../utils/auth";
import ListDoctors from "../../components/listDoctors";
import SearchDoctors from "../../components/searchDoctors";
import { Doctor } from "../../utils/types";

export default function Doctors() {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [filteredDoctors, setFilteredDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState<Doctor | null>(null);

  
  
  const fetchDoctors = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = getToken();

      const res = await fetch("/api/doctors", {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });

      if (!res.ok) {
        throw new Error(`HTTP error ${res.status}`);
      }

      const data: Doctor[] = await res.json();
      setDoctors(data);
      setFilteredDoctors(data);
    } catch (err) {
      console.error(err);
      setError("No s'han pogut carregar els doctors");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDoctors();
  }, []);

  const handleSearch = (searchTerm: string) => {
    if (!searchTerm.trim()) {
      setFilteredDoctors(doctors);
      return;
    }

    const lowerSearch = searchTerm.toLowerCase();
    const filtered = doctors.filter((doctor) => {
      const matchName = doctor.name?.toLowerCase().includes(lowerSearch);
      const matchUsername = doctor.username?.toLowerCase().includes(lowerSearch);
      const matchSpecialty = doctor.specialty?.toLowerCase().includes(lowerSearch);

      return matchName || matchUsername || matchSpecialty;
    });

    setFilteredDoctors(filtered);
  };

  if (loading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" role="status" variant="primary">
          <span className="visually-hidden">Carregant...</span>
        </Spinner>
        <p className="mt-3">Carregant doctors…</p>
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
            <h2 className="mb-0">Doctors</h2>
            <Button
              variant="primary"
              onClick={() => setShowForm(true)}
              disabled={showForm || editingDoctor !== null}
            >
              <i className="bi bi-plus-circle me-2"></i>
              Afegir Doctor
            </Button>
          </div>
        </Col>
      </Row>

      {showForm && (
        <Row className="mb-4">
          <Col>
            <AddDoctorForms
              onDoctorAdded={() => {
                setShowForm(false);
                fetchDoctors();
              }}
              onCancel={() => setShowForm(false)}
            />
          </Col>
        </Row>
      )}

      {editingDoctor && (
        <Row className="mb-4">
          <Col>
            <EditDoctorForm
              doctor={editingDoctor}
              onDoctorUpdated={() => {
                setEditingDoctor(null);
                fetchDoctors();
              }}
              onCancel={() => setEditingDoctor(null)}
            />
          </Col>
        </Row>
      )}

      <Row>
        <Col>
          <SearchDoctors onSearch={handleSearch} />
        </Col>
      </Row>

      <Row>
        <Col>
          {filteredDoctors.length === 0 && doctors.length > 0 ? (
            <Alert variant="info">
              No s'han trobat doctors amb els criteris de cerca.
            </Alert>
          ) : (
            <ListDoctors 
              doctors={filteredDoctors} 
              onDoctorDeleted={fetchDoctors}
              onDoctorEdit={(doctor) => {
                setShowForm(false);
                setEditingDoctor(doctor);
              }}
            />
          )}
        </Col>
      </Row>
    </Container>
  );
}
