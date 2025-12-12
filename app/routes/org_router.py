from fastapi import APIRouter, HTTPException, Depends, Header, Security
from app.models.schemas import OrgCreate, AdminLogin, TokenResponse, OrgUpdate
from app.crud import org_crud
from app.core.security import create_access_token, decode_token
from app.db import master_db, orgs_collection, admins_collection
from typing import Optional

router = APIRouter()

@router.post("/org/create", summary="Create a new organization")
async def create_org(payload: OrgCreate):
    try:
        org = await org_crud.create_organization(payload.organization_name, payload.email, payload.password)
        return {"status": "success", "data": org}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/org/get", summary="Get organization by name")
async def get_org(organization_name: str):
    doc = await org_crud.get_org_by_name(organization_name)
    if not doc:
        raise HTTPException(status_code=404, detail="Org not found")
    return {"status": "success", "data": doc}

@router.post("/admin/login", summary="Admin login")
async def admin_login(payload: AdminLogin):
    info = await org_crud.authenticate_admin(payload.email, payload.password)
    if not info:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    admin = info["admin"]
    org = info["org"]
    token = create_access_token({"admin_id": str(admin["_id"]), "org_id": str(org["_id"])})
    return {"access_token": token, "token_type": "bearer"}

# Simple dependency to require Authorization: Bearer <token>
from fastapi import Request
async def get_current_admin(request: Request, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Authorization must be Bearer")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    try:
        payload = decode_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

@router.delete("/org/delete", summary="Delete organization (authenticated)")
async def delete_org(organization_name: str, payload=Depends(get_current_admin)):
    # payload contains admin_id and org_id
    # ensure that the token admin belongs to the org being deleted
    org = await org_crud.get_org_by_name(organization_name)
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")
    # payload['org_id'] is ObjectId string; compare with org['id']
    if str(payload.get("org_id")) != org["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this organization")
    ok = await org_crud.delete_organization(organization_name)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to delete organization")
    return {"status": "deleted", "organization": organization_name}

@router.put("/org/update", summary="Update organization (rename or change admin email)")
async def update_org(update: OrgUpdate, payload=Depends(get_current_admin)):
    # Only allow update for admin's org
    org_id = payload.get("org_id")
    if not org_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    # fetch current org record by id
    from bson import ObjectId
    org_doc = await orgs_collection.find_one({"_id": ObjectId(org_id)})
    if not org_doc:
        raise HTTPException(status_code=404, detail="Org not found")
    # handle rename
    result = {}
    if update.organization_name:
        updated = await org_crud.rename_organization(org_doc["organization_name"], update.organization_name)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to rename org")
        result["organization"] = updated
    if update.admin_email:
        # update admin email
        await admins_collection.update_one({"_id": org_doc["admin_user_id"]}, {"$set": {"email": update.admin_email}})
        result["admin_email_updated_to"] = update.admin_email
    return {"status": "success", "data": result}
