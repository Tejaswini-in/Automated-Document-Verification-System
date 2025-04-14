import React, { useEffect, useState } from "react";
import axios from "axios";
import AdminSidebar from "../../components/AdminSidebar";

const ForgeryReports = () => {
  const [reports, setReports] = useState([]);

  const fetchReports = async () => {
    const res = await axios.get("http://localhost:5000/api/admin/reports");
    setReports(res.data);
  };

  useEffect(() => {
    fetchReports();
  }, []);

  return (
    <div className="row">
      <div className="col-md-3"><AdminSidebar /></div>
      <div className="col-md-9">
        <h4>Forgery Detection Reports</h4>
        <table className="table">
          <thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Result</th></tr></thead>
          <tbody>
            {reports.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.type}</td>
                <td>{r.status}</td>
                <td>{r.result}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ForgeryReports;
