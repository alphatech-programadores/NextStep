{ pkgs ? import <nixpkgs> {} }:

let
  # Define la versión de Python que queremos usar para todo
  python = pkgs.python310; # Usaremos Python 3.10 consistentemente

  # Definición personalizada de Flask-JWT-Extended
  # Esto es útil si la versión que necesitas no está directamente en pkgs.python310.pkgs
  # o si necesita alguna configuración específica.
  # Es crucial que aquí declares todas sus dependencias que necesite instalar Nix.
  flask_jwt_extended = python.pkgs.buildPythonPackage rec {
    pname = "Flask-JWT-Extended";
    version = "4.6.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-khXQWpQT04VXZLzWcDXnWBnSOvL6+2tVGX61ozE/37I=";
    };
    # Las dependencias que Flask-JWT-Extended necesita, instaladas por Nix
    propagatedBuildInputs = [ 
      python.pkgs.flask 
      python.pkgs.setuptools 
      python.pkgs.pyjwt # Flask-JWT-Extended depende de PyJWT
    ]; 
  };

in
pkgs.mkShell {
  buildInputs = [
    # --- ESTE ES EL BLOQUE CLAVE: TODOS TUS PAQUETES DE PYTHON VAN AQUÍ ---
    (python.withPackages (p: [
      p.flask
      p.flask-sqlalchemy
      flask_jwt_extended # Referencia a la definición personalizada de arriba
      p.flask-mail
      p.flask-cors
      p.flask-migrate
      p.python-dotenv
      p.werkzeug
      p.numpy  # NumPy será instalado y gestionado por Nix
      p.nltk   # NLTK será instalado y gestionado por Nix
      p.pyjwt  # Aseguramos PyJWT directamente también
      p.psycopg2 # Si usas PostgreSQL
      p.gunicorn # Si usas Gunicorn para producción

      # Si usas scikit-learn o pandas para el módulo de recomendación
      # p.scikit-learn
      # p.pandas
    ]))
    
    # --- Dependencias del Sistema (SOLO si no vienen con los paquetes de Python) ---
  ];

  shellHook = ''
    export FLASK_APP=app.py
    export FLASK_ENV=development
    
    # --- ¡IMPORTANTE: NO ACTIVAR VENV LOCAL AQUÍ! ---
    # Todas las librerías de Python están disponibles directamente en este entorno Nix.
  '';

}