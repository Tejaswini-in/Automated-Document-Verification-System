import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Upload.css";

const Upload = () => {
  const [documents, setDocuments] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(
        `http://localhost:5000/api/user/documents?page=${currentPage}&limit=${itemsPerPage}`,
        { withCredentials: true }
      );
      setDocuments(res.data.documents);
      setTotalPages(res.data.totalPages || 1);
    } catch (err) {
      console.error("Error fetching documents:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    try {
      await axios.delete(`http://localhost:5000/api/user/documents/${id}`, {
        withCredentials: true,
      });
      fetchDocuments();
    } catch (err) {
      console.error("Error deleting document:", err);
    }
  };

  const getDisplayName = (docType) => {
    const map = {
      aadhaar: "Aadhaar Photo",
      pan: "PAN Card",
      driving_license: "Driving License Photo",
      passport: "Passport Photo",
      voter_id: "Voter ID Photo",
    };
    return map[docType] || docType;
  };

  const handlePageChange = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [currentPage]);

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Uploaded Documents</h2>
      <table className="table table-bordered table-hover">
        <thead className="table-primary">
          <tr>
            <th>Sr. No.</th>
            <th>Document Type</th>
            <th>Document Name</th>
            <th>Status</th>
            <th style={{ textAlign: "center" }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {documents.length === 0 ? (
            <tr>
              <td colSpan="5" className="text-center py-4">
                No documents found.
              </td>
            </tr>
          ) : (
            documents.map((doc, index) => (
              <tr key={doc.id}>
                <td>{(currentPage - 1) * itemsPerPage + index + 1}</td>
                <td>{doc.type}</td>
                <td>{getDisplayName(doc.type)}</td>
                <td>{doc.status}</td>
                <td style={{ textAlign: "center" }}>
                  <a
                    href={`http://localhost:5000${doc.file_url}`}
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

      {/* Pagination */}
      <nav>
        <ul className="pagination justify-content-center">
          <li className={`page-item ${currentPage === 1 ? "disabled" : ""}`}>
            <button className="page-link" onClick={() => handlePageChange(currentPage - 1)}>
              Previous
            </button>
          </li>
          {[...Array(totalPages)].map((_, index) => (
            <li
              key={index}
              className={`page-item ${currentPage === index + 1 ? "active" : ""}`}
            >
              <button className="page-link" onClick={() => handlePageChange(index + 1)}>
                {index + 1}
              </button>
            </li>
          ))}
          <li className={`page-item ${currentPage === totalPages ? "disabled" : ""}`}>
            <button className="page-link" onClick={() => handlePageChange(currentPage + 1)}>
              Next
            </button>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Upload;
