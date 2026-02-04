// src/components/addPatientsForm.tsx
import { useState } from "react";
import { Form, Button, Alert, Card } from "react-bootstrap";
import { getToken } from "../utils/auth";

interface AddPatientsFormProps {
  onPatientAdded: () => void;
  onCancel: () => void;
}

export default function AddPatientsForm({
  onPatientAdded,
  onCancel,
}: AddPatientsFormProps) {
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError(null);
  setLoading(true);

  try {
    const token = getToken();
    
    const res = await fetch("/api/patients", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        name,
        birthDate: birthdate  // ← CAMBIO AQUÍ: birthDate en lugar de birthdate
      }),
    });

    if (!res.ok) {
      let errorMessage = "No s'ha pogut crear el pacient";
      
      try {
        const errorData = await res.json();
        
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData) && errorData.length > 0) {
          // Manejo de errores de validación de Pydantic/FastAPI
          errorMessage = errorData.map(err => err.msg).join(", ");
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (parseError) {
        errorMessage = `Error HTTP ${res.status}`;
      }
      
      throw new Error(errorMessage);
    }

    // Resetea el formulario
    setUsername("");
    setName("");
    setBirthdate("");
    
    onPatientAdded();
  } catch (err) {
    console.error("Error completo:", err);
    
    if (err instanceof Error) {
      setError(err.message);
    } else {
      setError("No s'ha pogut crear el pacient. Error desconegut.");
    }
  } finally {
    setLoading(false);
  }
};
  return (
    <Card className="shadow-sm">
      <Card.Body>
        <Card.Title className="mb-4">Afegir Pacient</Card.Title>

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
            <Form.Label>Data de naixement *</Form.Label>
            <Form.Control
              type="date"
              value={birthdate}
              onChange={(e) => setBirthdate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              required
            />
            <Form.Text className="text-muted">
              Selecciona la data de naixement del pacient
            </Form.Text>
          </Form.Group>

          {error && (
            <Alert variant="danger" className="mb-3">
              <i className="bi bi-exclamation-triangle-fill me-2"></i>
              {error}
            </Alert>
          )}

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