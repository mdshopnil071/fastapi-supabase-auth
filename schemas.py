from pydantic import BaseModel, EmailStr, Field

class UserAuth(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")