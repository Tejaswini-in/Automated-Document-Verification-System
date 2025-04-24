import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ManageUsers.css"; // Optional: if you want to keep CSS separate

const ManageUsers = () => {
  const [users, setUsers] = useState([]);

  const fetchUsers = async () => {
    try {
      const res = await axios.get("/api/admin/users", { withCredentials: true });
      setUsers(res.data.users);
    } catch (err) {
      console.error("Error fetching users:", err);
    }
  };

  const handleToggleSuspend = async (id) => {
    try {
      await axios.post(`/api/admin/users/${id}/suspend-toggle`, {}, { withCredentials: true });
      fetchUsers(); // Refresh list
    } catch (err) {
      console.error("Error toggling suspend:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      await axios.delete(`/api/admin/users/${id}`, { withCredentials: true });
      fetchUsers(); // Refresh list
    } catch (err) {
      console.error("Error deleting user:", err);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Manage Users</h2>
      <table className="table table-bordered table-hover">
        <thead className="table-primary">
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Status</th>
            <th style={{ textAlign: "center" }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.length === 0 ? (
            <tr>
              <td colSpan="5" className="text-center py-4">No users found.</td>
            </tr>
          ) : (
            users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>{user.is_suspended ? "Suspended" : "Active"}</td>
                <td style={{ textAlign: "center" }}>
                  <button
                    className={`btn btn-sm ${user.is_suspended ? "btn-success" : "btn-warning"}`}
                    onClick={() => handleToggleSuspend(user.id)}
                  >
                    {user.is_suspended ? "Unsuspend" : "Suspend"}
                  </button>
                  <button
                    className="btn btn-sm btn-danger ms-2"
                    onClick={() => handleDelete(user.id)}
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

export default ManageUsers;
