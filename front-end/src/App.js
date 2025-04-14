// App.js
import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import AdminDashboard from "./pages/AdminDashboard";
import UserDashboard from "./pages/UserDashboard";
import Upload from "./pages/Upload"; // Import Upload
import Navbar from "./components/Navbar";

// Admin Pages
import ManageUsers from "./pages/admin/ManageUsers";
import ViewDocuments from "./pages/admin/ViewDocuments";
import ForgeryReports from "./pages/admin/ForgeryReports";
import AuditLogs from "./pages/admin/AuditLogs";

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

          {/* Protected Admin Routes */}
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
            path="/admin/manage-users"
            element={
              isAuthenticated && isAdmin ? (
                <ManageUsers />
              ) : (
                <Login onLogin={handleLogin} />
              )
            }
          />
          <Route
            path="/admin/view-documents"
            element={
              isAuthenticated && isAdmin ? (
                <ViewDocuments />
              ) : (
                <Login onLogin={handleLogin} />
              )
            }
          />
          <Route
            path="/admin/forgery-reports"
            element={
              isAuthenticated && isAdmin ? (
                <ForgeryReports />
              ) : (
                <Login onLogin={handleLogin} />
              )
            }
          />
          <Route
            path="/admin/audit-logs"
            element={
              isAuthenticated && isAdmin ? (
                <AuditLogs />
              ) : (
                <Login onLogin={handleLogin} />
              )
            }
          />

          {/* Protected User Routes */}
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
          <Route
            path="/user/upload"
            element={
              isAuthenticated && !isAdmin ? (
                <Upload />
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
