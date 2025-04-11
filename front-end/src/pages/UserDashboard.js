import React, { useState } from "react";
import axios from "axios";

const UserDashboard = () => {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState("aadhaar");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setMessage("Please select a document to verify.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("doc_type", docType);  // Make sure this matches Flask form field

    try {
      setLoading(true);
      const response = await axios.post("http://localhost:5000/verify/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });

      

      const { status, extracted } = response.data;

      if (status === "Verified") {
        setMessage(`✅ Verified: ${status}\n\n📄 Extracted Text:\n${extracted}`);
      } else {
        setMessage(`❌ Rejected: ${status}\n\n📄 Extracted Text:\n${extracted}`);
      }
    } catch (err) {
      console.error(err);
      setMessage(
        "❌ Verification failed. Server error: " +
          (err.response?.data?.message || "Unknown error.")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <h2>User Dashboard</h2>
      <p>Upload your document for verification:</p>

      <form onSubmit={handleSubmit} className="card p-4 shadow-sm">
        <div className="mb-3">
          <label className="form-label">Select Document</label>
          <input
            type="file"
            className="form-control"
            onChange={handleFileChange}
            accept=".pdf,.jpg,.jpeg,.png"
          />
          <div className="form-text">
            Choose from your device (PDF, JPG, PNG)
          </div>
        </div>

        <div className="mb-3">
          <label className="form-label">Document Type</label>
          <select
            className="form-select"
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
          >
            <option value="aadhaar">Aadhaar</option>
            <option value="pan">PAN</option>
            <option value="govt">Government ID</option>
          </select>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Verifying..." : "Verify Document"}
        </button>
      </form>

      {message && (
        <div className="alert alert-info mt-4" style={{ whiteSpace: "pre-wrap" }}>
          {message}
        </div>
      )}
    </div>
  );
};

export default UserDashboard;
