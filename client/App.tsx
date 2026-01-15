import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Menu from './pages/Menu';
import AboutUs from './pages/AboutUs';

export default function App() {
  return (
    <BrowserRouter>
      <Menu />
      <Routes>
        <Route path="/" element={<Home />} /> {/* Home */}
        <Route path="/about" element={<AboutUs />} /> {/* Home */}
      </Routes>
      {/* Footer fixat a la part inferior */}
      <footer className="fixed-bottom bg-dark text-white text-center py-3 mt-auto">
          <p>XTEC.DEV || CC-BY-SA 4.0</p>
      </footer>
    </BrowserRouter>
  );
}