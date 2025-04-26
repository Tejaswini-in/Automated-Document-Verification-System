import React from "react";
import { Link } from "react-router-dom";

const AdminDashboard = () => {
  return (
    <div className="container mt-5" style={{ backgroundColor: '#f0f2f5', padding: '30px', borderRadius: '10px' }}>
      <h2 className="text-center mb-4">Admin Dashboard</h2>
      <p className="text-center mb-5">
        Welcome, Admin! Here you can manage users, documents, and review verification reports.
      </p>

      <ul className="list-group">
        <li
          className="list-group-item mb-3"
          style={{ backgroundColor: '#e3f2fd', borderRadius: '8px' }}
        >
          <Link
            to="/admin/manage-users"
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            📋 <b>Manage Users</b>
          </Link>
        </li>

        <li
          className="list-group-item mb-3"
          style={{ backgroundColor: '#e3f2fd', borderRadius: '8px' }}
        >
          <Link
            to="/admin/view-documents"
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            📄 <b>View Documents</b>
          </Link>
        </li>

        <li
          className="list-group-item mb-3"
          style={{ backgroundColor: '#e3f2fd', borderRadius: '8px' }}
        >
          <Link
            to="/admin/forgery-reports"
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            🔍 <b>AI Forgery Reports</b>
          </Link>
        </li>

        <li
          className="list-group-item"
          style={{ backgroundColor: '#e3f2fd', borderRadius: '8px' }}
        >
          <Link
            to="/admin/audit-logs"
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            🕵️ <b>Audit Logs</b>
          </Link>
        </li>
      </ul>
    </div>
  );
};

export default AdminDashboard;
