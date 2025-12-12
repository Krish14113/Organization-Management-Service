# Organization Management Service — Backend

FastAPI + MongoDB backend for the Organization Management Service assignment.  

## Project status
- FastAPI backend running
- MongoDB (Docker) running
- Dockerized (docker-compose)
- Admin authentication with JWT
- Dynamic collection naming org_<cleaned_name>
- Password hashing (bcrypt) with safe truncation for 72-byte bcrypt limit

## Tech stack
- Python 3.11
- FastAPI
- Motor (async MongoDB driver)
- MongoDB (docker: mongo:6.0)
- Uvicorn
- PyJWT, Passlib (bcrypt)
- Docker & Docker Compose

## Repo layout
```
org-management-backend/
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  ├─ config.py
│  │  └─ security.py
│  ├─ db.py
│  ├─ models/
│  │  └─ schemas.py
│  ├─ crud/
│  │  └─ org_crud.py
│  ├─ routes/
│  │  └─ org_router.py
│  └─ utils/
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt
├─ README.md
└─ diagram.png
```

## Setup — Docker
1. Install Docker Desktop.
2. Copy .env.example → .env and edit:
```
MONGO_URI=mongodb://mongo:27017
MASTER_DB=master_db
JWT_SECRET=change_this_to_secure_random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
3. Run:
```
docker compose up -d --build
```
4. Visit http://localhost:8000/docs

## Setup — Local
1. Install MongoDB locally.
2. Create venv & install requirements:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Run:
```
uvicorn app.main:app --reload --port 8000
```

## Endpoints
- POST /org/create
- POST /admin/login
- GET /org/get
- DELETE /org/delete
- PUT /org/update

## Curl examples
Create org:
```
curl -s -X POST http://localhost:8000/org/create   -H "Content-Type: application/json"   -d '{"organization_name":"TestOrg","email":"admin@test.com","password":"secret123"}'
```

Admin login:
```
curl -s -X POST http://localhost:8000/admin/login   -H "Content-Type: application/json"   -d '{"email":"admin@test.com","password":"secret123"}'
```

Delete org:
```
curl -s -X DELETE "http://localhost:8000/org/delete?organization_name=TestOrg"   -H "Authorization: Bearer $TOKEN"
```


## Diagram
Diagram.png included in repository.


## Brief Notes
1. FastAPI for Backend
Chosen because it is fast, modern, and automatically generates API docs.
It supports async operations, which pairs well with MongoDB’s async driver (motor).
2. MongoDB + Motor
MongoDB is schema-flexible, making it suitable for multi-tenant data.
Motor provides non-blocking async access, improving performance with FastAPI.
3. Master Database Structure
A single master DB stores:
organizations → org metadata
admins → admin login credentials
This centralizes tenant management and keeps indexing simple.
4. Dynamic Collection per Organization
Each organization gets a collection named org_<cleaned_name>.
This provides lightweight isolation without needing multiple databases.
5. JWT Authentication
JWT tokens allow stateless authentication.
Tokens include admin_id and org_id so the backend can authorize org-specific actions.
6. Password Hashing with bcrypt
bcrypt is secure but limited to 72 bytes.
We safely truncate passwords before hashing to avoid runtime errors.
7. Docker & docker-compose
Used for running the backend and MongoDB consistently across machines.
Ensures reviewers can reproduce the environment easily.
8. Simplicity and Limitations
This design prioritizes clarity and meeting assignment requirements.
Limitations:
Renaming collections may require Mongo admin privileges.
Collection-per-tenant provides basic separation but not full isolation (acceptable for prototype).


## Do I think this is a good architecture with a scalable design?
Yes — for an assignment or early-stage prototype, this architecture is good. FastAPI + MongoDB is lightweight, fast to build, easy to deploy with Docker, and supports flexible data structures. The dynamic collection model (org_<name>) keeps each organization’s data separated in a simple way.


## What are the trade-offs with the tech stack and design choices?
The main limitation is that using one MongoDB database with many collections provides only logical isolation, not strong isolation. As the number of organizations grows, managing many collections, indexes, backups, and migrations can become harder. A single Mongo instance also allows a “noisy tenant” to impact others. bcrypt also has a 72-byte limit, so passwords need truncation or a different hashing algorithm.


## Can this architecture be improved?
Yes. For better scalability and isolation, I would switch to a database-per-tenant model or a hybrid model where small tenants share a DB and large tenants get dedicated DBs. This simplifies backups, improves security boundaries, and prevents workload interference. Adding Redis caching, Kubernetes for autoscaling, and managed MongoDB (Atlas) would also make the system much more production-ready.