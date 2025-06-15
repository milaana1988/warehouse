# Warehouse Package Assignment Service

## Overview
This service provides a RESTful API to manage trucks and packages, and to assign packages to trucks ensuring at least 80% volume utilization before shipment. It uses FastAPI and SQLite for quick development, with recommendations for a production-grade SQL database.

## Features
- Add trucks with specified dimensions
- Add packages with specified dimensions
- Assign packages to the best-fit truck (≥80% fill)
- Defer shipments if utilization <80%
- Automatic error handling with appropriate HTTP status codes

## Prerequisites
- Python 3.9+
- `pip` package manager

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/milaana1988/warehouse.git
   cd warehouse
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup
- For development, SQLite is used by default.
- The database file `warehouse.db` will be created automatically.
- To view the database:
  ```bash
  sqlite3 warehouse.db
  .tables
  ```
- **Production Recommendation**: Migrate to a full SQL database like PostgreSQL or MSSQL for better concurrency and operational support.


### Alembic Migrations (If Needed)
If you choose to use Alembic for database migrations:
1. Install Alembic:
   ```bash
   pip install alembic
   ```
2. Initialize Alembic (once):
   ```bash
   alembic init alembic
   ```
3. Configure `alembic.ini` and `env.py` to point at your SQLALCHEMY_DATABASE_URL.
4. Generate a new migration:
   ```bash
   alembic revision --autogenerate -m "Add new tables or changes"
   ```
5. Apply migrations:
   ```bash
   alembic upgrade head
   ```
   
## Running the Service
Start the FastAPI server with Uvicorn:
```bash
uvicorn warehouse.main:app --reload --host 127.0.0.1 --port 8000
```
- API docs: `http://127.0.0.1:8000/docs`

## API Endpoints
- **POST /trucks**: Create a new truck  
  - Body: `{ "length": 10.5, "width": 4.2, "height": 3.0 }`  
  - Response: `201 Created`, Truck object

- **POST /packages**: Create a new package  
  - Body: `{ "length": 2.0, "width": 1.5, "height": 1.0 }`  
  - Response: `201 Created`, Package object

- **POST /assign**: Assign packages to a truck  
  - Body: `{ "package_ids": [1, 2, 3] }`  
  - Response:
    - `200 OK` with assigned/deferred lists if ≥80% fill
    - `202 Accepted` if <80% fill (all deferred)
    - Appropriate error codes for missing data or no trucks

## Error Handling
The API returns meaningful HTTP status codes:
- `422 Unprocessable Entity`: Validation errors (missing/invalid fields, package too large)
- `404 Not Found`: Package ID does not exist
- `409 Conflict`: No available trucks
- `400 Bad Request`: Input validation by Pydantic
- `500 Internal Server Error`: Unexpected errors


## Testing Examples

Below are end-to-end examples to verify `/assign` behavior in both modes.

### Setup (run once)
```bash
rm -f warehouse.db
uvicorn warehouse.main:app --reload --host 127.0.0.1 --port 8000 &
curl -s -X POST http://127.0.0.1:8000/trucks -H "Content-Type: application/json" -d '{"length":10,"width":10,"height":10}'
curl -s -X POST http://127.0.0.1:8000/trucks -H "Content-Type: application/json" -d '{"length":7,"width":10,"height":10}'
curl -s -X POST http://127.0.0.1:8000/packages -H "Content-Type: application/json" -d '{"length":7,"width":10,"height":10}'
curl -s -X POST http://127.0.0.1:8000/packages -H "Content-Type: application/json" -d '{"length":7,"width":5,"height":10}'
curl -s -X POST http://127.0.0.1:8000/packages -H "Content-Type: application/json" -d '{"length":7,"width":5,"height":10}'
```

### Test A: Without Bin-Packing
```bash
curl -i -X POST http://127.0.0.1:8000/assign      -H "Content-Type: application/json"      -d '{
           "package_ids": [1,2,3],
           "use_bin_packing": false
         }'
```
**Expected response:**
```json
{
  "assigned": [1],
  "deferred": [2, 3],
  "message": "Assigned 1 pkg(s) to truck 1; 2 deferred."
}
```

### Test B: With Bin-Packing
```bash
curl -i -X POST http://127.0.0.1:8000/assign      -H "Content-Type: application/json"      -d '{
           "package_ids": [1,2,3],
           "use_bin_packing": true
         }'
```
**Expected response:**
```json
{
  "assigned": [2, 3],
  "deferred": [1],
  "message": "Assigned 2 pkg(s); 1 deferred."
}
```


## Google Doc For the Diaphragm
    https://docs.google.com/document/d/1w6QXgxNtpx1XNQoggtGKywYenBgCgMTbZOu6gdSFXgo/edit?usp=sharing
