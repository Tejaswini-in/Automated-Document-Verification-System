import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./ManageUsers.css"; // Optional: CSS

const ManageUsers = () => {
  const [users, setUsers] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

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
      fetchUsers();
    } catch (err) {
      console.error("Error toggling suspend:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      await axios.delete(`/api/admin/users/${id}`, { withCredentials: true });
      fetchUsers();
    } catch (err) {
      console.error("Error deleting user:", err);
    }
  };

  useEffect(() => {
    fetchUsers();
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
      <h2 className="mb-4 text-center">Manage Users</h2>

      {/* Users Table */}
      <table className="table table-bordered table-hover">
        <thead className="table-primary">
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Status</th>
            <th>Role</th>
            <th style={{ textAlign: "center" }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.length === 0 ? (
            <tr>
              <td colSpan="6" className="text-center py-4">No users found.</td>
            </tr>
          ) : (
            users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>{user.is_suspended ? "Suspended" : "Active"}</td>
                <td>{user.role}</td>
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
