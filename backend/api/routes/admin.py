from fastapi import APIRouter

from backend.db.queries import list_customers, list_applications

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/customers")
def admin_customers():
    return {"data": [list(r) for r in list_customers()]}


@router.get("/applications")
def admin_applications():
    return {"data": [list(r) for r in list_applications()]}
