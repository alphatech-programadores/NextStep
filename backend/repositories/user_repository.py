# repositories/user_repository.py
from models.user import User
from models.role import Role
from extensions import db

class UserRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_by_email(self, email: str) -> User | None:
        """Finds a user by their email."""
        return self.db_session.query(User).filter_by(email=email).first()

    def create_user(self, email: str, name: str, password_hash: str, role_id: int) -> User:
        """Creates a new user."""
        user = User(email=email, name=name, password_hash=password_hash, role_id=role_id)
        self.db_session.add(user)
        return user

    def update_user(self, user: User, data: dict) -> User:
        """Updates an existing user's attributes."""
        user.name = data.get("name", user.name)
        return user

    def delete_user(self, user: User):
        """Deletes a user."""
        self.db_session.delete(user)

    def get_role_by_name(self, role_name: str) -> Role | None:
        """Finds a role by its name."""
        return self.db_session.query(Role).filter_by(name=role_name).first()

    def create_role(self, role_name: str) -> Role:
        """Creates a new role."""
        role = Role(name=role_name)
        self.db_session.add(role)
        return role

    # Add other user-specific queries as needed, e.g.,
    # def get_all_students(self) -> list[User]:
    #     return self.db_session.query(User).join(Role).filter(Role.name == 'student').all()