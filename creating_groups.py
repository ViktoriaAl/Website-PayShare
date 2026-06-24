from database import User, Group, UserGroupBank
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

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

    bank_entry = UserGroupBank(
        user_id=user.user_id,
        group_id=new_group.group_id,
        balance=0
    )

    session.add(bank_entry)

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

    bank_entry = UserGroupBank(
        user_id=participant.user_id,
        group_id=group.group_id,
        balance=0
    )

    session.add(bank_entry)

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

def select_payer(session: Session, group_id: int):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        return None
    
    bank_entries = group.participants_bank
    if not bank_entries:
        return None
    
    balances = [entry.balance for entry in bank_entries]
    if all(b == 0 for b in balances):
        chosen = random.choice([entry.user for entry in bank_entries])
    else:
        min_balance_index = balances.index(min(balances))
        chosen = bank_entries[min_balance_index].user
    
    group.current_payer_id = chosen.user_id
    session.commit()

    return chosen

def set_payer_by_name(session: Session, group_id: int, participan_name: str):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        return False, "группа не найдена"
    
    participan = None
    for member in group.participants:
        if member.name == participan_name:
            participan = member
            break
    
    if participan is None:
        return False, "нет такого участника"
    
    group.current_payer_id = member.user_id
    session.commit()

    return True, "success"

def add_payment(session: Session, group_id: int, amount: float):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        return False, "группа не найдена"
    
    if not group.current_payer_id:
        return False, "не выбран, кто платит"
    
    bank_entry = session.query(UserGroupBank).filter(
        UserGroupBank.group_id == group_id,
        UserGroupBank.user_id == group.current_payer_id
    ).first()

    if bank_entry is None:
        return False, "запись баланса не найдена"
    
    bank_entry.balance += amount
    session.commit()

    return True, "success"
    


        return False, "нет прав для добавления"
    if participant is None:
        return False, "такого пользователя не существует"
    if participant in group.participants:
        return False, "пользователь уже состоит в группе"
    
    group.participants.append(participant)

    bank_entry = UserGroupBank(
        user_id=participant.user_id,
        group_id=group.group_id,
        balance=0
    )

    session.add(bank_entry)

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

def select_payer(session: Session, group_id: int):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        return None
    
    bank_entries = group.participants_bank
    if not bank_entries:
        return None
    
    balances = [entry.balance for entry in bank_entries]
    if all(b == 0 for b in balances):
        chosen = random.choice([entry.user for entry in bank_entries])
    else:
        min_balance_index = balances.index(min(balances))
        chosen = bank_entries[min_balance_index].user
    
    group.current_payer_id = chosen.user_id
    session.commit()

    return chosen

def set_payer_by_name(session: Session, group_id: int, participan_name: str):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        return False, "группа не найдена"
    
    participan = None
    for member in group.participants:
        if member.name == participan_name:
            participan = member
            break
    
    if participan is None:
        return False, "нет такого участника"
    
    group.current_payer_id = member.user_id
    session.commit()

    return True, "success"

def add_payment(session: Session, group_id: int, amount: float):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        return False, "группа не найдена"
    
    if not group.current_payer_id:
        return False, "не выбран, кто платит"
    
    bank_entry = session.query(UserGroupBank).filter(
        UserGroupBank.group_id == group_id,
        UserGroupBank.user_id == group.current_payer_id
    )

    if bank_entry is None:
        return False, "запись баланса не найдена"
    
    bank_entry.balance += amount
    session.commit()

    return True, "success"
    


