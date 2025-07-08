from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate

migrate = Migrate()
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
jwt_redis_blacklist = set()