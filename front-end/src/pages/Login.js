// src/pages/Login.js

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();

    // ✅ Hardcoded login logic
    if (email === "admin@docverify.com" && password === "admin123") {
      onLogin(true, true); // isAuthenticated = true, isAdmin = true
      navigate("/admin/dashboard");
    } else if (email === "user@docverify.com" && password === "user123") {
      onLogin(true, false); // isAuthenticated = true, isAdmin = false
      navigate("/user/dashboard");
    } else {
      alert("Invalid credentials");
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: "500px" }}>
      <h2 className="text-center mb-4">Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group mb-3">
          <label>Email address</label>
          <input
            type="email"
            className="form-control"
            value={email}
            placeholder="admin@docverify.com OR user@docverify.com"
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group mb-4">
          <label>Password</label>
          <input
            type="password"
            className="form-control"
            value={password}
            placeholder="admin123 OR user123"
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary w-100">
          Login
        </button>
      </form>
    </div>
  );
};

export default Login;
