import React from "react";
import { Link } from "react-router-dom";

const AdminDashboard = () => {
  return (
    <div className="container mt-5">
      <h2>Admin Dashboard</h2>
      <p><b>Welcome, Admin!</b> Here you can manage users, documents, and review verification reports.</p>
      <ul className="list-group">
        <li className="list-group-item">
          <Link to="/admin/manage-users" style={{ textDecoration: 'none', color: 'inherit' }}>
            📋 <b>Manage Users</b>
          </Link>
        </li>
        <li className="list-group-item">
          <Link to="/admin/view-documents" style={{ textDecoration: 'none', color: 'inherit' }}>
            📄 <b>View Documents</b>
          </Link>
        </li>
        <li className="list-group-item">
          <Link to="/admin/forgery-reports" style={{ textDecoration: 'none', color: 'inherit' }}>
            🔍 <b>AI Forgery Reports</b>
          </Link>
        </li>
        <li className="list-group-item">
          <Link to="/admin/audit-logs" style={{ textDecoration: 'none', color: 'inherit' }}>
            🕵️ <b>Audit Logs</b>
          </Link>
        </li>
      </ul>
    </div>
  );
};

export default AdminDashboard;
