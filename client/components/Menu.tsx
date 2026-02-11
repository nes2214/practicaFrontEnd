import { useState, useEffect } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { getToken, removeToken } from "../utils/auth";

export default function Menu() {
  const [loggedIn, setLoggedIn] = useState(!!getToken());
  const [isOpen, setIsOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [role, setRole] = useState<string | null>(null);
  const navigate = useNavigate();

  // Obtener rol desde el token (ajustar según tu implementación real)
  const getUserRole = () => {
    if (!getToken()) return null;
    try {
      const token = JSON.parse(atob(getToken().split(".")[1]));
      return token.role;
    } catch (e) {
      return null;
    }
  };

  useEffect(() => {
    setRole(getUserRole());
  }, [loggedIn]);

  useEffect(() => {
    const handleStorageChange = () => setLoggedIn(!!getToken());
    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = () => {
    removeToken();
    setLoggedIn(false);
    setRole(null);
    navigate("/login");
  };

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `group text-white flex flex-col gap-0.5 transition-all duration-300 no-underline ${
      isScrolled 
        ? (isActive ? "text-white" : "text-blue-100")
        : (isActive ? "text-white" : "text-blue-100")
    }`;

  return (
    <>
      <nav className={`fixed top-0 left-0 w-full flex items-center justify-between px-4 md:px-16 lg:px-24 xl:px-32 transition-all duration-500 z-50 ${
        isScrolled 
          ? "bg-gradient-to-r from-green-600 to-green-800 py-3 md:py-4 text-white" 
          : "bg-gradient-to-r from-green-600 to-green-800 py-3 md:py-4 text-white"
      }`}>
        
        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-3 no-underline">
          <span className="text-xl transition-all duration-500 text-white">
            Clinic Manager
          </span>
        </NavLink>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-4 lg:gap-8">
          <NavLink to="/" className={navLinkClass}>
            Home
            <div className="h-0.5 w-0 group-hover:w-full transition-all duration-300 bg-white" />
          </NavLink>
          
          <NavLink to="/about" className={navLinkClass}>
            About Us
            <div className="h-0.5 w-0 group-hover:w-full transition-all duration-300 bg-white" />
          </NavLink>

          {/* Doctors - solo admin */}
          {role === "admin" && (
            <NavLink to="/doctors" className={navLinkClass}>
              Doctors
              <div className="h-0.5 w-0 group-hover:w-full transition-all duration-300 bg-white" />
            </NavLink>
          )}

          {/* Patients - admin y doctor */}
          {(role === "admin" || role === "doctor") && (
            <NavLink to="/patients" className={navLinkClass}>
              Patients
              <div className="h-0.5 w-0 group-hover:w-full transition-all duration-300 bg-white" />
            </NavLink>
          )}

          {/* My Info - todos logueados */}
          {loggedIn && (
            <NavLink to="/user" className={navLinkClass}>
              My Info
              <div className="h-0.5 w-0 group-hover:w-full transition-all duration-300 bg-white" />
            </NavLink>
          )}
        </div>

        {/* Desktop Auth Buttons */}
        <div className="hidden md:flex items-center gap-4">
          {!loggedIn ? (
            <button 
              onClick={() => navigate("/login")}
              className="px-8 py-2.5 rounded-full font-medium transition-all duration-500 bg-white text-green-600 hover:bg-blue-50"
            >
              Login
            </button>
          ) : (
            <button
              onClick={handleLogout}
              className="px-8 py-2.5 rounded-full font-medium transition-all duration-500 bg-red-500 text-white hover:bg-red-600"
            >
              Logout
            </button>
          )}
        </div>

        {/* Mobile Menu Button */}
        <div className="flex items-center md:hidden">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-2 transition-all duration-300 text-white"
          >
            {!isOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <line x1="4" y1="6" x2="20" y2="6" />
                <line x1="4" y1="12" x2="20" y2="12" />
                <line x1="4" y1="18" x2="20" y2="18" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            )}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div className={`fixed top-0 left-0 w-full h-screen bg-white text-base flex flex-col md:hidden items-center justify-center gap-6 font-medium text-gray-800 transition-all duration-500 z-40 ${
        isOpen ? "translate-x-0" : "-translate-x-full"
      }`}>
        <button 
          className="absolute top-6 right-6 text-gray-700"
          onClick={() => setIsOpen(false)}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        <NavLink to="/" onClick={() => setIsOpen(false)} className="text-gray-800 hover:text-green-600 no-underline text-lg">
          Home
        </NavLink>
        
        <NavLink to="/about" onClick={() => setIsOpen(false)} className="text-gray-800 hover:text-green-600 no-underline text-lg">
          About Us
        </NavLink>

        {/* Doctors - solo admin */}
        {role === "admin" && (
          <NavLink to="/doctors" onClick={() => setIsOpen(false)} className="text-gray-800 hover:text-green-600 no-underline text-lg">
            Doctors
          </NavLink>
        )}

        {/* Patients - admin y doctor */}
        {(role === "admin" || role === "doctor") && (
          <NavLink to="/patients" onClick={() => setIsOpen(false)} className="text-gray-800 hover:text-green-600 no-underline text-lg">
            Patients
          </NavLink>
        )}

        {/* My Info */}
        {loggedIn && (
          <NavLink to="/user" onClick={() => setIsOpen(false)} className="text-gray-800 hover:text-green-600 no-underline text-lg">
            My Info
          </NavLink>
        )}

        <div className="mt-6">
          {!loggedIn ? (
            <button 
              onClick={() => {
                setIsOpen(false);
                navigate("/login");
              }}
              className="bg-green-600 text-white px-8 py-2.5 rounded-full hover:bg-green-700 transition-all duration-500"
            >
              Login
            </button>
          ) : (
            <button
              onClick={() => {
                handleLogout();
                setIsOpen(false);
              }}
              className="bg-red-600 text-white px-8 py-2.5 rounded-full hover:bg-red-700 transition-all duration-500"
            >
              Logout
            </button>
          )}
        </div>
      </div>
    </>
  );
}
