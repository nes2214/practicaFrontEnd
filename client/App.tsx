import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import AboutUs from "./pages/AboutUs";
import Login from "./pages/Login";
import UserInfo from "./pages/protected/UserInfo";
import ProtectedRoute from "./components/ProtectedRoute";
import Menu from "./components/Menu";
import Doctors from "./pages/protected/Doctors";
import Patients from "./pages/protected/Pacients";
import "./main.css";

export default function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <Menu />

      {/* Agregado pt-20 o pt-24 para compensar el navbar fixed */}
      <main className="flex-grow pt-20 md:pt-24">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/about" element={<AboutUs />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/user" element={<UserInfo />} />
            <Route path="/doctors" element={<Doctors />} />
            <Route path="/patients" element={<Patients />} />
          </Route>
        </Routes>
      </main>

      <footer className="bg-gradient-to-r from-green-600 to-green-800 py-4 md:py-4 text-white text-center mt-auto">
        <p className="mb-0">XTEC.DEV || CC-BY-SA 4.0</p>
      </footer>
    </div>
  );
}