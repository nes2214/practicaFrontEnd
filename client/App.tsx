import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import AboutUs from "./pages/AboutUs";
import Login from "./pages/Login";
import UserInfo from "./pages/protected/UserInfo";
import ProtectedRoute from "./components/ProtectedRoute";
import Menu from "./components/Menu";

export default function App() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <Menu />

      <main className="flex-grow-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/about" element={<AboutUs />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/user" element={<UserInfo />} />
          </Route>
        </Routes>
      </main>

      <footer className="bg-dark text-white text-center py-3 mt-auto">
        <p>XTEC.DEV || CC-BY-SA 4.0</p>
      </footer>
    </div>
  );
}