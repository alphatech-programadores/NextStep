# backend/utils/file_upload.py

import os
from flask import current_app

def allowed_file(filename, allowed_extensions):
    """
    Verifica si la extensión del archivo es permitida.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_subdir, allowed_extensions):
    """
    Guarda un archivo subido en la carpeta de uploads.

    Args:
        file (FileStorage): El objeto de archivo subido (de request.files).
        upload_subdir (str): La subcarpeta dentro de UPLOAD_FOLDER (ej. 'cvs', 'profile_pics').
        allowed_extensions (set): Conjunto de extensiones permitidas para este tipo de archivo.

    Returns:
        tuple: (relative_filepath, error_message)
               relative_filepath: La ruta relativa del archivo guardado si fue exitoso, None si hubo error.
               error_message: Un mensaje de error si algo salió mal, None si fue exitoso.
    """
    if file.filename == '':
        return None, "No se seleccionó ningún archivo."

    # Asegurarse de que el nombre del archivo es seguro
    filename = secure_filename(file.filename)

    if not allowed_file(filename, allowed_extensions):
        return None, f"Tipo de archivo no permitido. Extensiones válidas: {', '.join(allowed_extensions)}"

    # Crear la subcarpeta si no existe (ej. uploads/cvs/, uploads/profile_pics/)
    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_subdir)
    os.makedirs(target_dir, exist_ok=True) # crea directorios si no existen

    # Construir la ruta completa donde se guardará el archivo
    filepath = os.path.join(target_dir, filename)

    try:
        file.save(filepath)
        # Devuelve la ruta relativa desde UPLOAD_FOLDER para guardar en la BD
        return os.path.join(upload_subdir, filename), None 
    except Exception as e:
        current_app.logger.error(f"Error al guardar archivo {filename} en {filepath}: {e}")
        return None, f"Error interno al guardar el archivo: {str(e)}"