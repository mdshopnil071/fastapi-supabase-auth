from fastapi import FastAPI, HTTPException, Header, status
from database import supabase
from schemas import UserAuth
from typing import Optional

app = FastAPI(title="Supabase Authentication API")

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(credentials: UserAuth):
    if not credentials.email or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email and password are required"}
        )
    
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Signup failed. User already exists or invalid data."}
            )
        return {
            "message": "User registered successfully",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "created_at": str(response.user.created_at)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )

@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(credentials: UserAuth):
    if not credentials.email or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email and password are required"}
        )
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid login credentials"}
        )

@app.get("/public/info", status_code=status.HTTP_200_OK)
def get_public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile", status_code=status.HTTP_200_OK)
def get_profile(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"}
        )
    
    token = authorization.split("Bearer ")[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"}
        )
    
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid or expired token"}
            )
            
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "created_at": str(user.created_at)
            }
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"}
        )


@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: dict = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )

@app.get("/protected/dashboard")
def get_dashboard(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    return {
        "message": f"Welcome to your private dashboard, {user.email}!",
        "status": "authenticated"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)