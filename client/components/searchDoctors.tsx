import { useState } from "react";
import { Form, InputGroup } from "react-bootstrap";

interface SearchDoctorsProps {
  onSearch: (searchTerm: string) => void;
}

export default function SearchDoctors({ onSearch }: SearchDoctorsProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    onSearch(value);
  };

  const handleClear = () => {
    setSearchTerm("");
    onSearch("");
  };

  return (
    <InputGroup className="mb-4">
      <InputGroup.Text>
        <i className="bi bi-search"></i>
      </InputGroup.Text>
      <Form.Control
        type="text"
        placeholder="Buscar per nom, usuari o especialitat..."
        value={searchTerm}
        onChange={handleSearchChange}
        aria-label="Buscar doctors"
      />
      {searchTerm && (
        <button
          className="btn btn-outline-secondary"
          type="button"
          onClick={handleClear}
          aria-label="Netejar cerca"
        >
          <i className="bi bi-x-lg"></i>
        </button>
      )}
    </InputGroup>
  );
}