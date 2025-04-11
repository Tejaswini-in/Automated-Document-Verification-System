// App.js
import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import AdminDashboard from "./pages/AdminDashboard";
import UserDashboard from "./pages/UserDashboard";
import Navbar from "./components/Navbar";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  const handleLogin = (auth, admin) => {
    setIsAuthenticated(auth);
    setIsAdmin(admin);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setIsAdmin(false);
  };

  return (
    <Router>
      <Navbar
        isAuthenticated={isAuthenticated}
        isAdmin={isAdmin}
        onLogout={handleLogout}
      />
      <div className="container mt-4">
        <Routes>
          <Route path="/" element={<Login onLogin={handleLogin} />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/admin/dashboard"
            element={
              isAuthenticated && isAdmin ? (
                <AdminDashboard />
              ) : (
                <Login onLogin={handleLogin} />
              )
            }
          />
          <Route
            path="/user/dashboard"
            element={
              isAuthenticated && !isAdmin ? (
                <UserDashboard />
              ) : (
                <Login onLogin={handleLogin} />
              )
            }
          />

          <Route path="*" element={<h4>404 - Page not found</h4>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
