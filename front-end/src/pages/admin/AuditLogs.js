import React, { useEffect, useState } from "react";
import axios from "axios";
import AdminSidebar from "../../components/AdminSidebar";

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);

  const fetchLogs = async () => {
    const res = await axios.get("http://localhost:5000/api/admin/audit-logs");
    setLogs(res.data);
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="row">
      <div className="col-md-3"><AdminSidebar /></div>
      <div className="col-md-9">
        <h4>Audit Logs</h4>
        <table className="table">
          <thead><tr><th>ID</th><th>Action</th><th>User</th><th>Timestamp</th></tr></thead>
          <tbody>
            {logs.map(l => (
              <tr key={l.id}>
                <td>{l.id}</td>
                <td>{l.action}</td>
                <td>{l.user_id}</td>
                <td>{new Date(l.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AuditLogs;
