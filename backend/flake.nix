
{
  description = "Backend Flask para NextStep";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11"; # Puedes usar una versión más reciente si lo deseas
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Define el entorno de Python para tu aplicación (similar a tu shell.nix)
        pythonEnv = pkgs.python310.withPackages (p: [
          p.flask
          p.flask-sqlalchemy
          p.flask-jwt-extended
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
          p.scikit-learn
          p.pandas
          p.flask-bcrypt
        ]);

        # Tu aplicación Flask
        nextstepBackend = pkgs.stdenv.mkDerivation {
          pname = "nextstep-backend";
          version = "1.0.0";
          src = ./backend; # <--- CAMBIO CLAVE: Apunta al directorio 'backend'

          buildInputs = [ pythonEnv ];

          installPhase = ''
            mkdir -p $out/bin
            cp -r $src/* $out/app # Copia el contenido del backend a /app en la imagen
            # Asegúrate de que el archivo 'app.py' esté en la raíz de /app
            mv $out/app/app.py $out/app/
          '';
        };

        # Define la imagen Docker
        dockerImage = pkgs.dockerTools.buildImage {
            name = "nextstep-backend";
            tag = "latest";

            copyToRoot = pkgs.buildEnv {
              name = "app-env";
              paths = [
                nextstepBackend
                pythonEnv
              ];
            };

            config = {
              # ----- LÍNEA MODIFICADA -----
              Cmd = [ "/bin/gunicorn" "wsgi:app" "--bind" "0.0.0.0:5000" "--workers" "2" ]; # Cambiado de "app:create_app" a "wsgi:app"
              
              ExposedPorts = { "5000/tcp" = {}; };
              WorkingDir = "/app"; # Asegúrate de que tu código está en /app dentro del contenedor
            };
          };

      in {
        # Para usar con 'nix build .#dockerImage'
        packages.default = dockerImage;
        # Para usar con 'nix develop' para un shell de desarrollo
        devShells.default = pkgs.mkShell {
          packages = [ pythonEnv ];
          shellHook = ''
            export FLASK_APP=backend/app.py # <--- CAMBIO: Ruta a app.py relativa a la raíz del flake
            export FLASK_ENV=development
            echo "Entorno de desarrollo Flask activado."
          '';
        };
      }
    );
}
