# create_test_notifications.py
from app import create_app
from services.notification_service import NotificationService
from extensions import db # Para asegurar el commit
from models.user import User # Para obtener usuarios existentes para notificaciones

# Crea una instancia de tu aplicación Flask
app = create_app()

def create_notifications():
    with app.app_context():
        notification_service = NotificationService()

        # --- Usuarios de Prueba ---
        # Asegúrate de que estos emails existan en tu base de datos (puedes verificarlos en tu seed_db.py)
        # Reemplaza con emails de estudiantes y/o instituciones existentes.
        student_email = "estudiante4@example.com" # Un estudiante de ejemplo
        institution_email = "institucion1@example.com" # Una institución de ejemplo
        
        # Opcional: Verificar que los usuarios existan antes de enviarles notificaciones
        student_user = User.query.filter_by(email=student_email).first()
        institution_user = User.query.filter_by(email=institution_email).first()

        if not student_user:
            print(f"Advertencia: Usuario estudiante '{student_email}' no encontrado. No se crearán notificaciones para él.")
        if not institution_user:
            print(f"Advertencia: Usuario institución '{institution_email}' no encontrado. No se crearán notificaciones para él.")

        print("--- Creando Notificaciones de Prueba ---")

        # 1. Notificación para un estudiante (cambio de estado de aplicación)
        if student_user:
            try:
                notification_service.create_and_send_notification(
                    recipient_email=student_email,
                    type="application_status_change",
                    message="¡Tu postulación para 'Desarrollador Frontend' ha sido revisada!",
                    link="/applications/123", # Enlace a una postulación específica
                    related_id=123,
                    sender_email=institution_email
                )
                print(f"Notificación de cambio de estado creada para {student_email}")
            except Exception as e:
                print(f"Error al crear notificación para {student_email}: {e}")

        # 2. Notificación para un estudiante (nueva vacante relevante)
        if student_user:
            try:
                notification_service.create_and_send_notification(
                    recipient_email=student_email,
                    type="new_vacant_match",
                    message="¡Tenemos una nueva vacante de 'Analista de Datos' que coincide con tu perfil!",
                    link="/vacancies/456", # Enlace a una vacante específica
                    related_id=456,
                    sender_email="sistema@nextstep.com"
                )
                print(f"Notificación de nueva vacante creada para {student_email}")
            except Exception as e:
                print(f"Error al crear notificación para {student_email}: {e}")

        # 3. Notificación para un estudiante (mensaje genérico)
        if student_user:
            try:
                notification_service.create_and_send_notification(
                    recipient_email=student_email,
                    type="system_message",
                    message="Bienvenido al nuevo sistema de notificaciones de NextStep.",
                    link="/notifications",
                    sender_email="sistema@nextstep.com"
                )
                print(f"Notificación de sistema creada para {student_email}")
            except Exception as e:
                print(f"Error al crear notificación para {student_email}: {e}")

        # Opcional: Notificación para una institución (nueva postulación)
        if institution_user:
            try:
                notification_service.create_and_send_notification(
                    recipient_email=institution_email,
                    type="new_application",
                    message="¡Tienes una nueva postulación para tu vacante de 'Diseñador UI/UX'!",
                    link="/institution/vacancies/789/applications",
                    related_id=789,
                    sender_email=student_email
                )
                print(f"Notificación de nueva postulación creada para {institution_email}")
            except Exception as e:
                print(f"Error al crear notificación para {institution_email}: {e}")

        db.session.commit() # Asegura que todos los cambios se guarden en la DB
        print("--- Proceso de creación de notificaciones de prueba finalizado. ---")

if __name__ == '__main__':
    create_notifications()