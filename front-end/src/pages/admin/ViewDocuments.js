import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ManageUsers.css"; // Reuse the same CSS for consistent UI

const ViewDocuments = () => {
  const [documents, setDocuments] = useState([]);

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
      fetchDocuments(); // Refresh list
    } catch (err) {
      console.error("Error deleting document:", err);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <div className="container mt-4">
      <h2 className="mb-4">View Uploaded Documents</h2>
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
              <td colSpan="6" className="text-center py-4">No documents found.</td>
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
