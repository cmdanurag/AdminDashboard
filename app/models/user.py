import uuid
from sqlalchemy import Column,String,Boolean,DateTime,Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__= "users"
    id = Column(UUID(as_uuid=True), primary_key=True,default = uuid.uuid4)
    name = Column(String,nullable = False)
    email = Column(String,unique = True,nullable = False)
    hashed_password = Column(String,nullable = False)
    is_admin = Column(Boolean,default = False)
    created_at = Column(DateTime,server_default = func.now())