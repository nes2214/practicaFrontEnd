// src/components/ListPatients.tsx
import { useState } from "react";
import { Table, Button, Alert, Modal } from "react-bootstrap";
import { Patient } from "../utils/types";
import { getToken } from "../utils/auth";

interface ListPatientsProps {
  patients: Patient[];
  onPatientDeleted: () => void;
  onPatientEdit: (patient: Patient) => void;
}

export default function ListPatients({ patients, onPatientDeleted, onPatientEdit }: ListPatientsProps) {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [patientToDelete, setPatientToDelete] = useState<Patient | null>(null);

  const handleDeleteClick = (patient: Patient) => {
    setPatientToDelete(patient);
    setShowModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!patientToDelete) return;

    setError(null);
    setLoading(patientToDelete.username);
    setShowModal(false);

    try {
      const token = getToken();
      
      const res = await fetch(`/api/patients/${patientToDelete.username}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Error eliminant el pacient");
      }

      onPatientDeleted();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "No s'ha pogut eliminar el pacient");
    } finally {
      setLoading(null);
      setPatientToDelete(null);
    }
  };

  const handleCancelDelete = () => {
    setShowModal(false);
    setPatientToDelete(null);
  };

  return (
    <>
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)} className="mb-3">
          {error}
        </Alert>
      )}
      
      {patients.length === 0 ? (
        <p>No hi ha pacients disponibles</p>
      ) : (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Username</th>
              <th>Data de naixement</th>
              <th>Accions</th>
            </tr>
          </thead>
          <tbody>
            {patients.map((pat, index) => (
              <tr key={pat.username || index}>
                <td>{index + 1}</td>
                <td>{pat.name}</td>
                <td>{pat.username}</td>
                <td>{pat.birthdate}</td>
                <td>
                  <div className="d-flex gap-2">
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => onPatientEdit(pat)}
                    >
                      <i className="bi bi-pencil me-1"></i>
                      Editar
                    </Button>
                    <Button 
                      variant="danger" 
                      size="sm"
                      onClick={() => handleDeleteClick(pat)}
                      disabled={loading === pat.username}
                    >
                      {loading === pat.username ? (
                        <>
                          <span 
                            className="spinner-border spinner-border-sm me-1" 
                            role="status" 
                            aria-hidden="true"
                          />
                          Eliminant...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-trash me-1"></i>
                          Eliminar
                        </>
                      )}
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      <Modal show={showModal} onHide={handleCancelDelete}>
        <Modal.Header closeButton>
          <Modal.Title>Confirmar eliminació</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Estàs segur que vols eliminar el pacient{" "}
          <strong>{patientToDelete?.name}</strong> ({patientToDelete?.username})?
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCancelDelete}>
            Cancel·lar
          </Button>
          <Button variant="danger" onClick={handleConfirmDelete}>
            Eliminar
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}