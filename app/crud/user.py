from sqlalchemy.orm import Session

from app.core.security.password import hash_password
from app.db.models.user import User
from app.schemas.user import UserCreate


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        username=user_in.username,
        name=user_in.name,
        phone=user_in.phone,
        hashed_password=hash_password(user_in.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
