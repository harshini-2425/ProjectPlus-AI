import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, MetaData, Table
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import Base
from app.main import app
from app.core.database import get_db

load_dotenv()
database_url = os.getenv('TEST_DATABASE_URL') or os.getenv('DATABASE_URL')
if not database_url or not database_url.startswith('postgresql+psycopg://'):
    raise RuntimeError('Set TEST_DATABASE_URL or DATABASE_URL to a PostgreSQL connection string before running tests.')
engine=create_engine(database_url, pool_pre_ping=True)
Session=sessionmaker(bind=engine,autoflush=False)
Base.metadata.create_all(engine)
users=Base.metadata.tables['users']

def seed_users(db):
    for user_id in (1, 2, 3):
        db.execute(insert(users).values(id=user_id).on_conflict_do_nothing(index_elements=['id']))
    db.commit()

def override_db():
    db=Session()
    try: yield db
    finally: db.close()
app.dependency_overrides[get_db]=override_db

import pytest
@pytest.fixture
def client():
    with TestClient(app) as c: yield c
@pytest.fixture(autouse=True)
def clean():
    db=Session()
    for table in reversed(Base.metadata.sorted_tables):
        if table.name != 'users':
            db.execute(table.delete())
    seed_users(db)
    db.close()
