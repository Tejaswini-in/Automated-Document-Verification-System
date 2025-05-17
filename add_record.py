# API Documentation for Verification Data Endpoint

"""
Endpoint: POST http://localhost:5000/admin/verification-data

Request Headers:
Content-Type: application/json

Request Body Format:
{
    "name": "FULL NAME",
    "id_number": "DOCUMENT ID NUMBER",
    "document_type": "DOCUMENT TYPE"
}

Document Types Supported:
- "aadhaar"    - For Aadhaar Cards
- "pan"        - For PAN Cards
- "driving_license" - For Driving Licenses
- "voter_id"   - For Voter ID Cards
- "passport"   - For Passports

Example Request Body:
{
    "name": "JOHN DOE",
    "id_number": "1234 5678 9012",
    "document_type": "aadhaar"
}

Responses:
- Success (200 OK):
  {
      "message": "Verification data added successfully"
  }
  or
  {
      "message": "Verification data updated successfully"
  }

- Error (400 Bad Request):
  {
      "error": "Error message details"
  }

Notes:
- The id_number must be unique across all records
- If a record with the same id_number exists, it will be updated
- All fields (name, id_number, document_type) are required
""" 