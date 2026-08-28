from sqlalchemy import Column, Integer, MetaData, Table
from app.core.database import Base

# The authentication module owns the real users table; this is only schema metadata.
users = Table('users', Base.metadata, Column('id', Integer, primary_key=True))
