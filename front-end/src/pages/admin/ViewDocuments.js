import React, { useEffect, useState } from "react";
import axios from "axios";
import AdminSidebar from "../../components/AdminSidebar";

const ViewDocuments = () => {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true); // For loading state
  const [error, setError] = useState(null); // For handling errors

  // Fetch documents from backend API
  const fetchDocs = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/admin/documents");
      setDocs(res.data);
    } catch (err) {
      setError("Failed to fetch documents");
      console.error("Error fetching documents:", err);
    } finally {
      setLoading(false);
    }
  };

  // Verify document
  const verifyDoc = async (id) => {
    try {
      await axios.put(`http://localhost:5000/api/admin/documents/${id}/verify`);
      fetchDocs();
    } catch (err) {
      setError("Failed to verify document");
      console.error("Error verifying document:", err);
    }
  };

  // Delete document
  const deleteDoc = async (id) => {
    try {
      await axios.delete(`http://localhost:5000/api/admin/documents/${id}`);
      fetchDocs();
    } catch (err) {
      setError("Failed to delete document");
      console.error("Error deleting document:", err);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  if (loading) {
    return <div>Loading...</div>; // Display loading message
  }

  return (
    <div className="row">
      <div className="col-md-3">
        <AdminSidebar />
      </div>
      <div className="col-md-9">
        <h4>View Documents</h4>
        
        {error && <div className="alert alert-danger">{error}</div>} {/* Display error message */}

        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Type</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {docs.length === 0 ? (
              <tr>
                <td colSpan="4">No documents found</td> {/* Message when no documents exist */}
              </tr>
            ) : (
              docs.map((d) => (
                <tr key={d.id}>
                  <td>{d.id}</td>
                  <td>{d.doc_type}</td>
                  <td>{d.status}</td>
                  <td>
                    {d.status !== "verified" && (
                      <button
                        className="btn btn-success btn-sm me-2"
                        onClick={() => verifyDoc(d.id)}
                      >
                        Verify
                      </button>
                    )}
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => deleteDoc(d.id)}
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
    </div>
  );
};

export default ViewDocuments;
