export interface Doctor {
  username: string;
  name: string;
  specialty: string | null;
}

export interface Patient {
  username: string;
  name: string;
  birthdate: string;
}