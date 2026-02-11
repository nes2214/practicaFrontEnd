// src/components/EditDoctorForm.tsx
import { useState } from "react";
import { Form, Button, Alert, Card } from "react-bootstrap";
import { getToken } from "../utils/auth";
import { Doctor } from "../utils/types";

interface EditDoctorFormProps {
  doctor: Doctor;
  onDoctorUpdated: () => void;
  onCancel: () => void;
}

export default function EditDoctorForm({
  doctor,
  onDoctorUpdated,
  onCancel,
}: EditDoctorFormProps) {
  const [name, setName] = useState(doctor.name);
  const [specialty, setSpecialty] = useState(doctor.specialty || "");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const token = getToken();
      
      const res = await fetch(`/api/doctors/${doctor.username}`, {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          specialty: specialty || null,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Error actualitzant el doctor");
      }

      onDoctorUpdated();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "No s'ha pogut actualitzar el doctor");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="shadow-sm">
      <Card.Body>
        <Card.Title className="mb-4">Editar Doctor: {doctor.username}</Card.Title>

        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Username</Form.Label>
            <Form.Control
              type="text"
              value={doctor.username}
              disabled
              readOnly
            />
            <Form.Text className="text-muted">
              El username no es pot modificar
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Nom complet *</Form.Label>
            <Form.Control
              type="text"
              placeholder="Introdueix el nom complet"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Especialitat</Form.Label>
            <Form.Control
              type="text"
              placeholder="Introdueix l'especialitat"
              value={specialty}
              onChange={(e) => setSpecialty(e.target.value)}
            />
            <Form.Text className="text-muted">
              Exemple: Cardiologia, Pediatria, Traumatologia, etc.
            </Form.Text>
          </Form.Group>

          {error && <Alert variant="danger" className="mb-3">{error}</Alert>}

          <div className="d-flex gap-2">
            <Button
              type="submit"
              variant="primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Guardant...
                </>
              ) : (
                "Guardar canvis"
              )}
            </Button>

            <Button
              type="button"
              variant="secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel·lar
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
}