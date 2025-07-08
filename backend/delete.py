from extensions import db
from app import create_app  # Importa la función, NO la instancia

app = create_app()

with app.app_context():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f"Vaciando tabla {table.name}")
        db.session.execute(table.delete())
    db.session.commit()
    print("✔ Base de datos vaciada con éxito.")
