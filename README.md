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
### 1. FastAPI for Backend
FastAPI is chosen because it is fast, modern, and automatically generates OpenAPI/Swagger documentation.<br>
Its async-first architecture pairs well with MongoDB’s async driver (`motor`), improving performance and scalability.

---

### 2. MongoDB + Motor
MongoDB’s schema flexibility makes it ideal for multi-tenant systems where each organization may store different structures.<br>
Motor provides non-blocking asynchronous access, which fits naturally with FastAPI’s async request handling.

---

### 3. Master Database Structure
A single **master database** stores:<br>
• `organizations` → organization metadata<br>
• `admins` → admin login credentials<br>
This centralizes all tenant information, simplifies indexing, and makes it easy to map incoming requests to their organizations.

---

### 4. Dynamic Collection per Organization
Each organization gets its own collection named `org_<cleaned_name>`.<br>
This gives lightweight isolation between tenants without the complexity of provisioning multiple databases.

---

### 5. JWT Authentication
Authentication uses JSON Web Tokens (JWT), allowing stateless and scalable authorization.<br>
Each token includes both `admin_id` and `org_id`, enabling the backend to authorize organization-specific operations without repeated database lookups.

---

### 6. Password Hashing with bcrypt
bcrypt is secure and widely used, but limited to 72 bytes.<br>
To prevent runtime errors, password inputs are safely truncated before hashing while maintaining strong security.

---

### 7. Docker & Docker Compose
Docker ensures consistent environment setup across different machines.<br>
Docker Compose runs FastAPI + MongoDB together, making the project easy to test, run, and review for the assignment.

---

### 8. Simplicity and Limitations
This architecture intentionally prioritizes clarity and assignment requirements.<br>
However, some limitations exist:

- Renaming collections can require elevated MongoDB privileges.<br>
- The “collection-per-tenant” model offers basic separation but **not full isolation**, which is acceptable for a prototype but not ideal for large-scale production.

---


## Do I think this is a good architecture with a scalable design?
Yes — for an assignment or early-stage prototype, this architecture is good. FastAPI + MongoDB is lightweight, fast to build, easy to deploy with Docker, and supports flexible data structures. The dynamic collection model (org_<name>) keeps each organization’s data separated in a simple way.


## What are the trade-offs with the tech stack and design choices?
The main limitation is that using one MongoDB database with many collections provides only logical isolation, not strong isolation. As the number of organizations grows, managing many collections, indexes, backups, and migrations can become harder. A single Mongo instance also allows a “noisy tenant” to impact others. bcrypt also has a 72-byte limit, so passwords need truncation or a different hashing algorithm.


## Can this architecture be improved?
Yes. For better scalability and isolation, I would switch to a database-per-tenant model or a hybrid model where small tenants share a DB and large tenants get dedicated DBs. This simplifies backups, improves security boundaries, and prevents workload interference. Adding Redis caching, Kubernetes for autoscaling, and managed MongoDB (Atlas) would also make the system much more production-ready.
