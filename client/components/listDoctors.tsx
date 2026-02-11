// src/components/ListDoctors.tsx
import { useState } from "react";
import { Table, Button, Alert, Modal } from "react-bootstrap";
import { Doctor } from "../utils/types";
import { getToken } from "../utils/auth";

interface ListDoctorsProps {
  doctors: Doctor[];
  onDoctorDeleted: () => void;
  onDoctorEdit: (doctor: Doctor) => void;
}

export default function ListDoctors({ doctors, onDoctorDeleted, onDoctorEdit }: ListDoctorsProps) {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [doctorToDelete, setDoctorToDelete] = useState<Doctor | null>(null);

  const handleDeleteClick = (doctor: Doctor) => {
    setDoctorToDelete(doctor);
    setShowModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!doctorToDelete) return;

    setError(null);
    setLoading(doctorToDelete.username);
    setShowModal(false);

    try {
      const token = getToken();
      
      const res = await fetch(`/api/doctors/${doctorToDelete.username}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Error eliminant el doctor");
      }

      onDoctorDeleted();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "No s'ha pogut eliminar el doctor");
    } finally {
      setLoading(null);
      setDoctorToDelete(null);
    }
  };

  const handleCancelDelete = () => {
    setShowModal(false);
    setDoctorToDelete(null);
  };

  return (
    <>
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)} className="mb-3">
          {error}
        </Alert>
      )}
      
      {doctors.length === 0 ? (
        <p>No hi ha doctors disponibles</p>
      ) : (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Username</th>
              <th>Especialitat</th>
              <th>Accions</th>
            </tr>
          </thead>
          <tbody>
            {doctors.map((doc, index) => (
              <tr key={doc.username || index}>
                <td>{index + 1}</td>
                <td>{doc.name}</td>
                <td>{doc.username}</td>
                <td>
                  {doc.specialty ? (
                    <span>{doc.specialty}</span>
                  ) : (
                    <span className="text-muted">Sense especialitat</span>
                  )}
                </td>
                <td>
                  <div className="d-flex gap-2">
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => onDoctorEdit(doc)}
                    >
                      <i className="bi bi-pencil me-1"></i>
                      Editar
                    </Button>
                    <Button 
                      variant="danger" 
                      size="sm"
                      onClick={() => handleDeleteClick(doc)}
                      disabled={loading === doc.username}
                    >
                      {loading === doc.username ? (
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
          Estàs segur que vols eliminar el doctor{" "}
          <strong>{doctorToDelete?.name}</strong> ({doctorToDelete?.username})?
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