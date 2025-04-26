import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./ManageUsers.css"; // Reuse same styling for consistency

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const fetchLogs = async () => {
    try {
      const res = await axios.get("/api/admin/audit-logs", { withCredentials: true });
      setLogs(res.data.logs || []);
    } catch (err) {
      console.error("Error fetching audit logs:", err);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  return (
    <div className="container mt-4">
      {/* Dropdown Navigation */}
      <div className="d-flex justify-content-start mb-2">
        <div className="position-relative" ref={dropdownRef}>
          <button className="btn btn-primary btn-sm" onClick={toggleDropdown}>☰</button>
          {dropdownOpen && (
            <div
              className="dropdown-menu show p-2 custom-dropdown"
              style={{
                position: "absolute",
                top: "40px",
                left: 0,
                minWidth: "160px",
                backgroundColor: "#f8f9fa",
                border: "1px solid #ccc",
                borderRadius: "5px",
                zIndex: 1000,
              }}
            >
              <Link to="/admin/manage-users" className="dropdown-item">Manage Users</Link>
              <Link to="/admin/view-documents" className="dropdown-item">View Documents</Link>
              <Link to="/admin/forgery-reports" className="dropdown-item">Forgery Reports</Link>
              <Link to="/admin/audit-logs" className="dropdown-item">Audit Logs</Link>
            </div>
          )}
        </div>
      </div>

      {/* Title */}
      <h2 className="mb-4 text-center">Audit Logs</h2>

      {/* Table */}
      <table className="table table-bordered table-hover">
        <thead className="table-primary">
          <tr>
            <th>ID</th>
            <th>Action</th>
            <th>User ID</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 ? (
            <tr>
              <td colSpan="4" className="text-center py-4">No logs available.</td>
            </tr>
          ) : (
            logs.map((log) => (
              <tr key={log.id}>
                <td>{log.id}</td>
                <td>{log.action}</td>
                <td>{log.user_id}</td>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default AuditLogs;
