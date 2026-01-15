import { BrowserRouter, Routes, Route } from "react-router-dom";
import Menu from "./pages/Menu";
import Home from "./pages/Home";
import AboutUs from "./pages/AboutUs";
import Login from "./pages/Login";
import UserInfo from "./pages/UserInfo";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <BrowserRouter>
      <div className="d-flex flex-column min-vh-100">
        {/* Menu sempre visible */}
        <Menu />

        {/* Contingut principal: ocupa l'espai restant */}
        <main className="flex-grow-1">
          <Routes>
            {/* Rutes públiques */}
            <Route path="/login" element={<Login />} />
            <Route path="/about" element={<AboutUs />} />

            {/* Rutes protegides */}
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Home />} />
              <Route path="/user" element={<UserInfo />} />
            </Route>
          </Routes>
        </main>

        {/* Footer al final */}
        <footer className="bg-dark text-white text-center py-3 mt-auto">
          <p>XTEC.DEV || CC-BY-SA 4.0</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}