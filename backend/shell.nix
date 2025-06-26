{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python310;

  flask_jwt_extended = python.pkgs.buildPythonPackage rec {
    pname = "Flask-JWT-Extended";
    version = "4.6.0";
    src = pkgs.python310.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-khXQWpQT04VXZLzWcDXnWBnSOvL6+2tVGX61ozE/37I=";
    };
    propagatedBuildInputs = [ python.pkgs.flask python.pkgs.setuptools ];
  };

in
pkgs.mkShell {
  buildInputs = [
    python
    python.pkgs.pip
    python.pkgs.virtualenv
    python.pkgs.flask
    python.pkgs.flask_sqlalchemy
    python.pkgs.python-dotenv
    python.pkgs.werkzeug
    python.pkgs.flask_migrate
    python.pkgs.flask-cors
    python.pkgs.flask_mail
    python.pkgs.psycopg2
    python.pkgs.nltk
    python.pkgs.gunicorn
    flask_jwt_extended
    pkgs.gcc
    pkgs.libstdcxx5
  ];

shellHook = ''
  export FLASK_APP=app.py
  export FLASK_ENV=development
'';

}

