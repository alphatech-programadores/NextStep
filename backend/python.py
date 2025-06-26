from models.user import User
u = User.query.first()
print(u.last_password_reset)