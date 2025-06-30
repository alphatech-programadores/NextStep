{ pkgs ? import <nixpkgs> {} }:

let
  # Define la versión de Python que queremos usar para todo
  python = pkgs.python310; # Usaremos Python 3.10 consistentemente

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
  
    (python.withPackages (p: [
      p.flask
      p.flask-sqlalchemy
      flask_jwt_extended
      p.flask-mail
      p.flask-cors
      p.flask-migrate
      p.python-dotenv
      p.werkzeug
      p.numpy 
      p.nltk 
      p.pyjwt 
      p.psycopg2
      p.gunicorn

      # Si usas scikit-learn o pandas para el módulo de recomendación
      # p.scikit-learn
      # p.pandas
    ]))
    
  ];

  shellHook = ''
    export FLASK_APP=app.py
    export FLASK_ENV=development
    
    # --- ¡IMPORTANTE: NO ACTIVAR VENV LOCAL AQUÍ! ---
    # Todas las librerías de Python están disponibles directamente en este entorno Nix.
  '';

}