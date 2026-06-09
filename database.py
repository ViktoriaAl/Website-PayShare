from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import declarative_base, Session, relationship

from datetime import datetime

engine = create_engine("sqlite:///users_data.db", connect_args={'check_same_thread':False})
Base = declarative_base()

group_members = Table(
    'group_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user_info.user_id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups_info.group_id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'user_info'

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    password_hash = Column(String)

    owned_groups = relationship("Group", back_populates="owner")
    member_of_groups = relationship("Group", secondary=group_members, back_populates="participants")
    user_bank = relationship("UserGroupBank", back_populates="user")

class Group(Base):
    __tablename__ = 'groups_info'

    group_id = Column(Integer, primary_key=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("user_info.user_id"))
    
    owner = relationship("User", back_populates="owned_groups")
    participants = relationship("User", secondary=group_members, back_populates="member_of_groups")
    participant_bank = relationship("UserGroupBank", back_populates="group")

class UserGroupBank(Base):
    __tablename__ = 'user_group_bank'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_info.user_id"))
    group_id = Column(Integer, ForeignKey("groups_info.group_id"))
    balance = Column(Integer, default=0)

    user = relationship("User", back_populates="participant_bank")
    group = relationship("Group", back_populates="user_bank")

class SessionToken(Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_info.user_id"))

    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)

Base.metadata.create_all(engine)
db_session = Session(engine)

    