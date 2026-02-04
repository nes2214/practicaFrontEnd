// src/components/AddDoctorForms.tsx
import { useState } from "react";
import { Form, Button, Alert, Card } from "react-bootstrap";
import { getToken } from "../utils/auth";

interface AddDoctorFormsProps {
  onDoctorAdded: () => void;
  onCancel: () => void;
}

export default function AddDoctorForms({
  onDoctorAdded,
  onCancel,
}: AddDoctorFormsProps) {
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const token = getToken();
      
      const res = await fetch("/api/doctors", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          name,
          specialty: specialty || null, // Envía null si está vacío
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Error creating doctor");
      }

      // Resetea el formulario
      setUsername("");
      setName("");
      setSpecialty("");
      
      onDoctorAdded();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "No s'ha pogut crear el doctor");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="shadow-sm">
      <Card.Body>
        <Card.Title className="mb-4">Afegir Doctor</Card.Title>

        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Username *</Form.Label>
            <Form.Control
              type="text"
              placeholder="Introdueix el username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
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
                "Guardar"
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