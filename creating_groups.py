from database import User, Group
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def create_group(session: Session, user_id: int, name_of_group: str):
    user = session.query(User).filter(User.user_id == user_id).first()
    if user is None:
        return False, "Нужно авторизоваться"
    new_group = Group(
        name = name_of_group,
        owner_id = user_id
    )

    session.add(new_group)
    session.commit()

    new_group.participants.append(user)
    session.commit()

    return True, "success"

def add_participant(session: Session, owner_id: int, participan_email: str, group_id: int):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    participant = session.query(User).filter(User.email == participan_email).first()
    if group.owner_id != owner_id:
        return False, "нет прав для добавления"
    if participant is None:
        return False, "такого пользователя не существует"
    if participant in group.participants:
        return False, "пользователь уже состоит в группе"
    
    group.participants.append(participant)
    session.commit()

    return True, "success"

def remove_participant(session: Session, owner_id: int, participan_email: str, group_id: int):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    participant = session.query(User).filter(User.email == participan_email).first()
    if group.owner_id != owner_id:
        return False, "нет прав для удаления"
    if participant is None:
        return False, "такого пользователя не существует"
    if participant not in group.participants:
        return False, "пользователь не состоит в этой группе"
    
    group.participants.remove(participant)
    session.commit()

    return True, "success"

def is_user_in_group(session: Session, group_id: int, user_id: int):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    user = session.query(User).filter(User.user_id == user_id).first()
    # for participant in group.participants:
    if user in group.participants:
        return True
    return False

def get_user_groups(session: Session, user_id: int):
    user = session.query(User).filter(User.user_id == user_id).first()
    if user is None:
        return []
    return list(user.member_of_groups)

def get_group_by_id(session: Session, group_id: int):
    return session.query(Group).filter(Group.group_id == group_id).first()

def get_group_members(session: Session, group_id: int):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group is None:
        return []
    return list(group.participants)