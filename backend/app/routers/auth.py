from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import uuid
from app.database import get_db
from app.models.tenant import User, Organization, RoleEnum, PasswordHistory
from app.schemas.schemas import UserCreate, UserLogin, Token, TokenRefresh, OrgCreate
from app.security import verify_password, get_password_hash, create_access_token, create_refresh_token, validate_password_policy
from jose import jwt, JWTError
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate, org: OrgCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        validate_password_policy(user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    org_id = str(uuid.uuid4())
    new_org = Organization(id=org_id, name=org.name)
    db.add(new_org)
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    new_user = User(
        id=user_id,
        org_id=org_id,
        email=user.email,
        hashed_password=hashed_password,
        role=RoleEnum.admin
    )
    db.add(new_user)
    
    pwd_history = PasswordHistory(id=str(uuid.uuid4()), user_id=user_id, hashed_password=hashed_password)
    db.add(pwd_history)
    
    db.commit()
    
    access_token = create_access_token(data={"sub": new_user.email, "org_id": org_id, "user_id": user_id, "role": new_user.role.value})
    refresh_token = create_refresh_token(data={"sub": new_user.email, "org_id": org_id, "user_id": user_id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials or inactive user")
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    access_token = create_access_token(data={"sub": user.email, "org_id": user.org_id, "user_id": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.email, "org_id": user.org_id, "user_id": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh(token_data: TokenRefresh, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token_data.refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User inactive or deleted")
            
        access_token = create_access_token(data={"sub": user.email, "org_id": user.org_id, "user_id": user.id, "role": user.role.value})
        refresh_token = create_refresh_token(data={"sub": user.email, "org_id": user.org_id, "user_id": user.id})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
