import useSWR from 'swr'
import xtecLogo from '../assets/xtec.svg'

function fetcher(arg: any, ...args: any) {
  return fetch(arg, ...args).then(res => res.json())
}

// Componente para mostrar estadísticas de la clínica
function Stats() {
  const { data: patients, error: patientsError } = useSWR("/api/patients", fetcher)
  const { data: doctors, error: doctorsError } = useSWR("/api/doctors", fetcher)
  const { data: appointments, error: appointmentsError } = useSWR("/api/appointments", fetcher)

  if (patientsError || doctorsError || appointmentsError) {
    return <p className="text-center text-red-600 mt-5">Error cargando estadísticas.</p>
  }

  if (!patients || !doctors || !appointments) {
    return <p className="text-center text-yellow-600 mt-5">Cargando estadísticas...</p>
  }

  return (
    <div className="flex flex-col md:flex-row justify-center items-center gap-8 mt-8 text-center">
      <div className="bg-green-100 rounded p-5 shadow-md w-40">
        <h2 className="text-2xl font-bold text-green-800">{patients.length}</h2>
        <p className="text-green-700">Pacientes</p>
      </div>
      <div className="bg-blue-100 rounded p-5 shadow-md w-40">
        <h2 className="text-2xl font-bold text-blue-800">{doctors.length}</h2>
        <p className="text-blue-700">Doctores</p>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <div className="p-4 md:p-16">
      {/* Logo */}
      <div className="flex justify-center">
        <a href="https://xtec.dev" target="_blank" rel="noopener noreferrer">
          <img
            src={xtecLogo}
            className="rounded h-24 object-contain"
            alt="xtec.dev Logo"
          />
        </a>
      </div>

      

      {/* Estadísticas de la clínica */}
      <Stats />

      {/* Descripción de la web */}
      <div className="mt-10 text-center max-w-2xl mx-auto text-lg text-gray-700">
        <p>
          Bienvenido a <strong>Clinic Manager</strong>, un sistema completo para la gestión de clínicas.
          Aquí puedes administrar <strong>pacientes</strong>, <strong>doctores</strong> y <strong>diagnósticos</strong> .
        </p>
        <p className="mt-2">
          La web utiliza una <strong>base de datos</strong> para almacenar toda la información de manera segura,
          y cuenta con control de acceso según el <strong>rol del usuario</strong> (admin, doctor o paciente).
        </p>
      </div>
    </div>
  );
}
