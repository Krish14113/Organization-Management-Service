from app.db import orgs_collection, master_db, admins_collection
from app.core.security import hash_password, verify_password
from bson import ObjectId
from typing import Optional
import re
import pymongo.errors

def _safe_collection_name(name: str) -> str:
    # keep alphanum + underscore
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower().strip())
    return f"org_{cleaned}"

async def org_exists(name: str) -> bool:
    doc = await orgs_collection.find_one({"organization_name": name})
    return doc is not None

async def create_organization(name: str, email: str, password: str) -> dict:
    if await org_exists(name):
        raise ValueError("organization already exists")

    collection_name = _safe_collection_name(name)
    # create collection if not exists
    db = master_db
    try:
        # create collection explicitly (will fail if exists)
        await db.create_collection(collection_name)
    except Exception:
        # ignore if it already exists
        pass

    hashed = hash_password(password)
    admin_doc = {"email": email, "password": hashed, "created_at": None}
    res = await admins_collection.insert_one(admin_doc)
    admin_id = res.inserted_id

    org_doc = {
        "organization_name": name,
        "collection_name": collection_name,
        "admin_user_id": admin_id,
    }
    org_res = await orgs_collection.insert_one(org_doc)
    org_doc_out = {
        "id": str(org_res.inserted_id),
        "organization_name": name,
        "collection_name": collection_name,
        "admin_email": email,
    }
    return org_doc_out

async def get_org_by_name(name: str) -> Optional[dict]:
    doc = await orgs_collection.find_one({"organization_name": name})
    if not doc:
        return None
    admin = await admins_collection.find_one({"_id": doc.get("admin_user_id")})
    admin_email = admin.get("email") if admin else None
    return {
        "id": str(doc.get("_id")),
        "organization_name": doc.get("organization_name"),
        "collection_name": doc.get("collection_name"),
        "admin_email": admin_email,
    }

async def get_org_by_admin_email(email: str) -> Optional[dict]:
    admin = await admins_collection.find_one({"email": email})
    if not admin:
        return None
    org = await orgs_collection.find_one({"admin_user_id": admin["_id"]})
    return org

async def authenticate_admin(email: str, password: str) -> Optional[dict]:
    admin = await admins_collection.find_one({"email": email})
    if not admin:
        return None
    if not verify_password(password, admin["password"]):
        return None
    # find org associated with admin
    org = await orgs_collection.find_one({"admin_user_id": admin["_id"]})
    return {"admin": admin, "org": org}

async def delete_organization(name: str) -> bool:
    org = await orgs_collection.find_one({"organization_name": name})
    if not org:
        return False
    collection_name = org.get("collection_name")
    # drop dynamic collection if exists
    try:
        await master_db.drop_collection(collection_name)
    except Exception:
        pass
    # remove admin
    admin_id = org.get("admin_user_id")
    await admins_collection.delete_one({"_id": admin_id})
    # remove org record
    await orgs_collection.delete_one({"_id": org["_id"]})
    return True

async def rename_organization(old_name: str, new_name: str) -> Optional[dict]:
    org = await orgs_collection.find_one({"organization_name": old_name})
    if not org:
        return None
    new_collection_name = _safe_collection_name(new_name)
    # rename collection (if exists)
    try:
        await master_db.client[master_db.name].command(
            "renameCollection",
            f"{master_db.name}.{org['collection_name']}",
            to=f"{master_db.name}.{new_collection_name}",
            dropTarget=True
        )
    except Exception:
        # fallback: create new collection and copy (left as simple placeholder)
        try:
            await master_db.create_collection(new_collection_name)
        except Exception:
            pass
    # update org doc
    await orgs_collection.update_one({"_id": org["_id"]}, {"$set": {"organization_name": new_name, "collection_name": new_collection_name}})
    updated = await orgs_collection.find_one({"_id": org["_id"]})
    admin = await admins_collection.find_one({"_id": updated["admin_user_id"]})
    return {
        "id": str(updated["_id"]),
        "organization_name": updated["organization_name"],
        "collection_name": updated["collection_name"],
        "admin_email": admin.get("email") if admin else None,
    }
