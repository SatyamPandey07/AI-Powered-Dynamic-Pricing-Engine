from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import uuid
import secrets
import string
from app.database import get_db
from app.models.tenant import User, RoleEnum, PasswordHistory
from app.schemas.schemas import UserResponse, UserInvite, UserUpdate
from app.dependencies import require_auth, require_role, audit_log
from app.security import get_password_hash

router = APIRouter(prefix="/api/users", tags=["users"])

def generate_temp_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(chars) for _ in range(16))

@router.get("", response_model=List[UserResponse])
async def get_users(request: Request, db: Session = Depends(get_db), auth=Depends(require_auth)):
    users = db.query(User).filter(User.org_id == auth.org_id, User.is_active == True).all()
    return users

@router.post("", response_model=UserResponse)
@audit_log(action="create", resource_type="user")
async def invite_user(request: Request, user_data: UserInvite, db: Session = Depends(get_db), auth=Depends(require_role("admin"))):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    try:
        role_enum = RoleEnum(user_data.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    temp_password = generate_temp_password()
    hashed_password = get_password_hash(temp_password)
    
    new_user = User(
        id=str(uuid.uuid4()),
        org_id=auth.org_id,
        email=user_data.email,
        hashed_password=hashed_password,
        role=role_enum
    )
    db.add(new_user)
    
    pwd_history = PasswordHistory(id=str(uuid.uuid4()), user_id=new_user.id, hashed_password=hashed_password)
    db.add(pwd_history)
    
    db.commit()
    db.refresh(new_user)
    
    # In a real system, send email with temp_password here
    print(f"Invite sent to {new_user.email} with temp password: {temp_password}")
    
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
@audit_log(action="update_role", resource_type="user")
async def update_user(request: Request, user_id: str, user_data: UserUpdate, db: Session = Depends(get_db), auth=Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id, User.org_id == auth.org_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    try:
        role_enum = RoleEnum(user_data.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    user.role = role_enum
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
@audit_log(action="deactivate", resource_type="user")
async def delete_user(request: Request, user_id: str, db: Session = Depends(get_db), auth=Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id, User.org_id == auth.org_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_active = False
    db.commit()
    return {"message": "User deactivated successfully"}
