// frontend/src/pages/AdminDashboard.js

import React from "react";

const AdminDashboard = () => {
  return (
    <div className="container mt-5">
      <h2>Admin Dashboard</h2>
      <p>Welcome, Admin! Here you can manage users, documents, and review verification reports.</p>
      <ul className="list-group">
        <li className="list-group-item">📋 Manage Users</li>
        <li className="list-group-item">📄 View Documents</li>
        <li className="list-group-item">🔍 AI Forgery Reports</li>
        <li className="list-group-item">🕵️ Audit Logs</li>
      </ul>
    </div>
  );
};

export default AdminDashboard;
