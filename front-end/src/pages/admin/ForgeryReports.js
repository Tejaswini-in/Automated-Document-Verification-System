import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./ManageUsers.css"; // optional

const ForgeryReports = () => {
  const [reports, setReports] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const fetchReports = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/admin/reports");
      setReports(res.data);
    } catch (err) {
      console.error("Failed to fetch reports", err);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const getForgeryStatus = (status) => {
    return status === "Verified" ? "Genuine" : "Forged";
  };

  return (
    <div className="container mt-4">
      {/* Dropdown Button */}
      <div className="d-flex justify-content-start mb-2">
        <div className="position-relative" ref={dropdownRef}>
          <button className="btn btn-primary btn-sm" onClick={toggleDropdown}>
            ☰
          </button>
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

      <h2 className="mb-4 text-center">Forgery Detection Reports</h2>

      <table className="table table-bordered table-hover">
        <thead className="table-primary">
          <tr>
            <th>Sr. No.</th>
            <th>Email</th>
            <th>Document Type</th>
            <th>Status</th>
            <th>Uploaded Document</th>
            <th>Forgery Report</th>
          </tr>
        </thead>
        <tbody>
          {reports.length === 0 ? (
            <tr>
              <td colSpan="6" className="text-center py-4">
                No Forgery Detection Reports found.
              </td>
            </tr>
          ) : (
            reports.map((report, index) => (
              <tr key={report.id}>
                <td>{index + 1}</td>
                <td>{report.email}</td>
                <td>{report.type}</td>
                <td>{report.status}</td>
                <td>
                  <a
                    href={report.document_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-sm btn-outline-primary"
                  >
                    View
                  </a>
                </td>
                <td>
                  <span
                    className={
                      report.status === "Verified"
                        ? "text-success fw-bold"
                        : "text-danger fw-bold"
                    }
                  >
                    {getForgeryStatus(report.status)}
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ForgeryReports;
