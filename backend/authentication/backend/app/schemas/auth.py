from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserLogin(BaseModel):
    username: str = Field(..., description="Email address used for login")
    password: str = Field(..., min_length=8, description="Password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class RegisterUser(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="TEAM_MEMBER")

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
