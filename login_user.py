from database import User, SessionToken
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

import bcrypt
import secrets

from email_utils import send_verification_email

server = "127.0.0.1:5000"

def creat_session(session, user_id):
    token = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(hours=24)

    new_session = SessionToken(
        user_id=user_id,
        token=token,
        created_at=datetime.now(),
        expires_at=expires_at
    )
    session.add(new_session)
    session.commit()

    return token

def creating_verification(verification_token, email):
    verification_link = f"http://{server}/verify/{verification_token}"
    result = send_verification_email(email, verification_link)
    return result


def register(session: Session, name: str, email: str, password: str):
    user = session.query(User).filter(User.email == email).first()
    if user:
        return False, "This user alredy exists"
    
    if len(password) < 6:
        return False, "Your passwors is weak"
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    verification_token = secrets.token_urlsafe(32)

    new_user = User(
        name=name, 
        email=email, 
        password_hash=hashed.decode('utf-8'),
        is_verified=False,
        verification_token=verification_token,
        verification_sent_at=datetime.utcnow())
    session.add(new_user)
    session.commit()

    email_sent = creating_verification(verification_token, email)

    if not email_sent:
        return False, "не удалось отправить ссылку на ваш email. Проверьте email или попробуйте позже"
    return True, "Проверьте почту"
    # token = creat_session(session, new_user.user_id)

    # return True, token

def verify_user_email(session: Session, token: str):
    user = session.query(User).filter(User.verification_token == token).first()

    if user is None:
        return False, "Неверная ссылка или она устарела"
    
    if user.is_verified:
        return True, "Ваш email уже подтвержден, можете войти"
    
    user.is_verified = True
    user.verification_token = None
    session.commit()

    return True, "Ваш email успешно подтвержден, можете входить в аккаунт"


def login(session: Session, email: str, password: str):
    user = session.query(User).filter(User.email == email).first()
    if user is None:
        return False, "Sorry, this e-mail wasn't found"

    if user and not(bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))):
        return False, "Your password is wrong"
    
    # if not user.is_verified:
    #     creating_verification
    #     return None
    
    token = creat_session(session, user.user_id)
    return True, token

def logout(session: Session, token):
    session.query(SessionToken).filter(SessionToken.token == token).delete()
    session.commit()

def get_user_by_token(session, token):
    session_record = session.query(SessionToken).filter(
        SessionToken.token == token,
        SessionToken.expires_at > datetime.now()
    ).first()

    if not session_record:
        return None
    return session.query(User).filter(User.user_id == session_record.user_id).first()
    
        email=email, 
        password_hash=hashed.decode('utf-8'))
    session.add(new_user)
    session.commit()

    token = creat_session(session, new_user.user_id)

    return True, token

def login(session: Session, email: str, password: str):
    user = session.query(User).filter(User.email == email).first()
    if user is None:
        return False, "Sorry, this e-mail wasn't found"

    if user and not(bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))):
        return False, "Your password is wrong"
    
    token = creat_session(session, user.user_id)
    return True, token

def logout(session: Session, token):
    session.query(SessionToken).filter(SessionToken.token == token).delete()
    session.commit()

def get_user_by_token(session, token):
    session_record = session.query(SessionToken).filter(
        SessionToken.token == token,
        SessionToken.expires_at > datetime.now()
    ).first()

    if not session_record:
        return None
    return session.query(User).filter(User.user_id == session_record.user_id).first()
    
