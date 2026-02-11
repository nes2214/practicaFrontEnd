import { useState } from "react";
import { Form, Button, Alert, Card, Spinner } from "react-bootstrap";
import { getToken } from "../utils/auth";
import { Patient } from "../utils/types";

interface EditPatientFormProps {
  patient: Patient;
  onPatientUpdated: () => void;
  onCancel: () => void;
}

export default function EditPatientForm({
  patient,
  onPatientUpdated,
  onCancel,
}: EditPatientFormProps) {
  const [name, setName] = useState(patient.name);
  const [birthdate, setBirthdate] = useState(patient.birthdate);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const token = getToken();
      
      const res = await fetch(`/api/patients/${patient.username}`, {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          birthdate,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Error actualitzant el pacient");
      }

      onPatientUpdated();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "No s'ha pogut actualitzar el pacient");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="shadow-sm">
      <Card.Body>
        <Card.Title className="mb-4">Editar Pacient</Card.Title>

        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Username</Form.Label>
            <Form.Control
              type="text"
              value={patient.username}
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
            <Form.Label>Data de naixement *</Form.Label>
            <Form.Control
              type="date"
              value={birthdate}
              onChange={(e) => setBirthdate(e.target.value)}
              required
            />
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
                  <Spinner animation="border" size="sm" className="me-2" />
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