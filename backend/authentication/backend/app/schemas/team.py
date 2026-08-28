from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TeamOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_by: int

    model_config = ConfigDict(from_attributes=True)


class TeamMemberOut(BaseModel):
    id: int
    team_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
