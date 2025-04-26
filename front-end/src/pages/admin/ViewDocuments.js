import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./ViewDocuments.css";

const ViewDocuments = () => {
  const [documents, setDocuments] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const fetchDocuments = async () => {
    try {
      const res = await axios.get("/api/user/documents", { withCredentials: true });
      setDocuments(res.data.documents);
    } catch (err) {
      console.error("Error fetching documents:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    try {
      await axios.delete(`/api/user/documents/${id}`, { withCredentials: true });
      fetchDocuments();
    } catch (err) {
      console.error("Error deleting document:", err);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  // Close dropdown if clicking outside
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
      {/* Dropdown Button on Top Left */}
      <div className="d-flex justify-content-start mb-2">
        <div className="position-relative" ref={dropdownRef}>
          <button
            className="btn btn-primary btn-sm"
            onClick={toggleDropdown}
          >
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

      {/* Page Heading */}
      <h2 className="mb-4 text-center">View Uploaded Documents</h2>

      {/* Documents Table */}
      <table className="table table-bordered table-hover">
        <thead className="table-primary">
          <tr>
            <th>ID</th>
            <th>Document Name</th>
            <th>Type</th>
            <th>Status</th>
            <th>Uploaded At</th>
            <th style={{ textAlign: "center" }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {documents.length === 0 ? (
            <tr>
              <td colSpan="6" className="text-center py-4">
                No documents found.
              </td>
            </tr>
          ) : (
            documents.map((doc) => (
              <tr key={doc.id}>
                <td>{doc.id}</td>
                <td>{doc.name}</td>
                <td>{doc.type}</td>
                <td>{doc.status}</td>
                <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                <td style={{ textAlign: "center" }}>
                  <a
                    href={doc.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-sm btn-info"
                  >
                    View
                  </a>
                  <button
                    className="btn btn-sm btn-danger ms-2"
                    onClick={() => handleDelete(doc.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ViewDocuments;
