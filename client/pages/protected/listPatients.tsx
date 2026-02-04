import { Container, Row, Col, Table } from "react-bootstrap";
import {Patient} from "../../utils/types"


interface ListPatientsProps {
  patients: Patient[];
}
export default function listPatients({patients}: ListPatientsProps){
    return <div>
        <Container>
            <Row>
        <Col>
          {patients.length === 0 ? (
            <p>No hi ha patients disponibles</p>
          ) : (
            <Table striped bordered hover >
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Username</th>
                  <th>Birthdate</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((pat, index) => (
                  <tr key={pat.username || index}>
                    <td>{index + 1}</td>
                    <td>{pat.name}</td>
                    <td>{pat.username}</td>
                    <td>{pat.birthdate}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Col>
      </Row>
        </Container>
    </div>
}