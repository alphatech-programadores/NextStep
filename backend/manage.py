from flask import Flask
from extensions import db, migrate
from models import user  # importa todos tus modelos aquí

app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)
migrate.init_app(app, db)

if __name__ == "__main__":
    app.run()
