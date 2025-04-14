import React from "react";
import { Link } from "react-router-dom";

const AdminDashboard = () => {
  return (
    <div className="container mt-5">
      <h2>Admin Dashboard</h2>
      <p>Welcome, Admin! Here you can manage users, documents, and review verification reports.</p>
      <ul className="list-group">
        <li className="list-group-item">
          <Link to="/admin/manage-users">📋 Manage Users</Link>
        </li>
        <li className="list-group-item">
          <Link to="/admin/view-documents">📄 View Documents</Link>
        </li>
        <li className="list-group-item">
          <Link to="/admin/forgery-reports">🔍 AI Forgery Reports</Link>
        </li>
        <li className="list-group-item">
          <Link to="/admin/audit-logs">🕵️ Audit Logs</Link>
        </li>
      </ul>
    </div>
  );
};

export default AdminDashboard;
