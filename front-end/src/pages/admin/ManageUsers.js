import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ManageUsers.css"; // Reusing ManageUsers style for consistent UI

const ForgeryDetection = () => {
  const [reports, setReports] = useState([]);

  const fetchReports = async () => {
    try {
      const res = await axios.get("/api/admin/reports", { withCredentials: true });
      setReports(res.data.reports || []);
    } catch (err) {
      console.error("Error fetching forgery reports:", err);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Forgery Detection Reports</h2>
      <table className="table table-bordered table-hover">
        <thead className="table-primary">
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Document Type</th>
            <th>Status</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
          {reports.length === 0 ? (
            <tr>
              <td colSpan="5" className="text-center py-4">No reports found.</td>
            </tr>
          ) : (
            reports.map((report) => (
              <tr key={report.id}>
                <td>{report.id}</td>
                <td>{report.username}</td>
                <td>{report.type}</td>
                <td>{report.status}</td>
                <td>{report.result}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ForgeryDetection;
