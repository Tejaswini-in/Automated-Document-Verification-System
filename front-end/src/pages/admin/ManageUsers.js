import React, { useEffect, useState } from "react";
import axios from "axios";
import AdminSidebar from "../../components/AdminSidebar";

const ManageUsers = () => {
    const [users, setUsers] = useState([]);

    const fetchUsers = async () => {
        try {
            const res = await axios.get("http://localhost:5000/api/admin/users");
            console.log(res.data); // Log the response to check the structure
            setUsers(res.data.users || res.data); // Use res.data.users if response is wrapped
        } catch (error) {
            console.error("Error fetching users:", error);
        }
    };

    const deleteUser = async (id) => {
        try {
            await axios.delete(`http://localhost:5000/api/admin/users/${id}`);
            fetchUsers();
        } catch (error) {
            console.error("Error deleting user:", error);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    return (
        <div className="row">
            <div className="col-md-3"><AdminSidebar /></div>
            <div className="col-md-9">
                <h4>Manage Users</h4>
                <table className="table">
                    <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Action</th></tr></thead>
                    <tbody>
                        {users.map(u => (
                            <tr key={u.id}>
                                <td>{u.id}</td>
                                <td>{u.username}</td>
                                <td>{u.email}</td>
                                <td>
                                    <button className="btn btn-danger btn-sm" onClick={() => deleteUser(u.id)}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ManageUsers;
