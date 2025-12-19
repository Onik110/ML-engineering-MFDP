from sqlmodel import Session, select
import bcrypt
import re
from models.user import User

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def set_password(self, password_: str):
        self._validate_password(password_)
        self.password = self._hash_password(password_)

    def validate_email(self, email_: str) -> bool:

        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not pattern.match(email_):
            raise ValueError("Invalid email format. Example: user@example.com")
        return True

    def _validate_password(self, password_: str):
        if len(password_) < 8:
            raise ValueError("The password must contain at least 8 characters!")
    
    def _hash_password(self, password_: str) -> str:
        return bcrypt.hashpw(password_.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password_: str) -> bool:
        return bcrypt.checkpw(
            password_.encode('utf-8'),
            self.password.encode('utf-8') 
        )

    def get_by_email(self, email: str) -> User | None:
        return self.session.exec(select(User).where(User.email == email)).first()
  
    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def create_user(self, email: str, password: str) -> User:
        if self.get_by_email(email):
            raise ValueError("User with this email already exists") 

        self.validate_email(email)
        self._validate_password(password)


        user = User(
            email=email,
            password=self._hash_password(password)
            
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def get_all_users(self) -> list[User]:
        return self.session.exec(select(User)).all()