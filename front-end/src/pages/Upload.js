import React from 'react';
export default function Upload() {
  return (
    <div className="container mt-5">
      <h2>Upload Document</h2>
      <form>
        <div className="mb-3">
          <label>Select Document Type</label>
          <select className="form-select">
            <option>Aadhaar</option>
            <option>PAN</option>
            <option>Passport</option>
          </select>
        </div>
        <div className="mb-3">
          <label>Choose File</label>
          <input type="file" className="form-control" />
        </div>
        <button className="btn btn-primary">Submit</button>
      </form>
    </div>
  );
}
