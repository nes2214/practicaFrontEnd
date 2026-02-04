import { Container, Row, Col, Table } from "react-bootstrap";
import {Doctor} from "../../utils/types"


interface ListDoctorsProps {
  doctors: Doctor[];
}

export default function ListDoctors({ doctors }: ListDoctorsProps) {
  return (
    <Container>
      <Row>
        <Col>
          {doctors.length === 0 ? (
            <p>No hi ha doctors disponibles</p>
          ) : (
            <Table striped bordered hover >
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Username</th>
                  <th>Especialitat</th>
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
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Col>
      </Row>
    </Container>
  );
}