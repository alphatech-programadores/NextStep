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
        # CAMBIO CLAVE AQUÍ: Usamos pkgs.lib.cleanSource para copiar el contenido del directorio backend
        # Esto asegura que el contenido de 'backend' se copie correctamente como fuente.
        backendSource = pkgs.lib.cleanSource ./backend;

        nextstepBackend = pkgs.stdenv.mkDerivation {
          pname = "nextstep-backend";
          version = "1.0.0";
          src = backendSource; # Usar la fuente limpia del directorio backend

          buildInputs = [ pythonEnv ];

          installPhase = ''
            mkdir -p $out/app # Crea el directorio de la aplicación en $out
            cp -r $src/* $out/app/ # Copia todo el contenido de $src (que es el directorio backend) a /app
            # No es necesario mover app.py si ya está en la raíz de $src
          '';
        };

        # Define la imagen Docker
        dockerImage = pkgs.dockerTools.buildImage {
          name = "nextstep-backend";
          tag = "latest";
          from = pkgs.dockerTools.pullImage {
            imageName = "nixos/nix";
            imageDigest = "sha256:388839071c356e80b27563503b44b82d4778405e6080353c7c25c";
            finalImageTag = "23.11";
          };
          contents = [
            nextstepBackend
            # No es necesario incluir pythonEnv aquí si nextstepBackend ya lo tiene en su PATH
            # y si los scripts se ejecutan en el contexto de nextstepBackend.
            # Sin embargo, para mayor seguridad y si gunicorn no está en el PATH de nextstepBackend,
            # podemos mantenerlo o asegurar que el Cmd apunte a la ruta completa.
            # Por ahora, lo mantenemos como estaba en tu versión anterior para evitar nuevos errores.
            pythonEnv
          ];
          config = {
            Cmd = [ "${pythonEnv}/bin/gunicorn" "app:create_app" "--bind" "0.0.0.0:5000" "--workers" "2" ];
            ExposedPorts = [ "5000" ];
            WorkingDir = "/app"; # Directorio de trabajo dentro del contenedor
          };
        };

      in {
        # Para usar con 'nix build .#dockerImage'
        packages.default = dockerImage;
        # Para usar con 'nix develop' para un shell de desarrollo
        devShells.default = pkgs.mkShell {
          packages = [ pythonEnv ];
          shellHook = ''
            export FLASK_APP=backend/app.py # Ruta a app.py relativa a la raíz del flake
            export FLASK_ENV=development
            echo "Entorno de desarrollo Flask activado."
          '';
        };
      }
    );
}

