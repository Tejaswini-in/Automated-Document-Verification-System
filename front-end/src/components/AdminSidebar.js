import React from "react";
import { Link } from "react-router-dom";

const AdminSidebar = () => {
  return (
    <div className="list-group">
      <Link to="/admin/dashboard" className="list-group-item">Dashboard</Link>
      <Link to="/admin/manage-users" className="list-group-item">Manage Users</Link>
      <Link to="/admin/forgery-reports" className="list-group-item">Forgery Reports</Link>
      <Link to="/admin/audit-logs" className="list-group-item">Audit Logs</Link>
    </div>
  );
};

export default AdminSidebar;
