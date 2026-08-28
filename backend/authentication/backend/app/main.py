from fastapi import FastAPI

from backend.app.core.config import settings
from backend.app.db.database import Base, engine
from backend.app.routes import auth, teams, users

app = FastAPI(
    title="ProjectPulse AI Authentication API",
    version="1.0.0",
    description="Authentication, user, and team management APIs for ProjectPulse AI.",
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
