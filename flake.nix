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

        backendSource = pkgs.lib.cleanSource ./backend;

        nextstepBackend = pkgs.stdenv.mkDerivation {
          pname = "nextstep-backend";
          version = "1.0.0";
          src = backendSource;

          buildInputs = [ pythonEnv ];

          installPhase = ''
            mkdir -p $out/app
            cp -r $src/* $out/app/
          '';
        };

        # Definir la baseImage por separado
        # No es necesario definirla si se usa directamente en 'from'
        # baseImage = pkgs.dockerTools.pullImage {
        #   imageName = "nixos/nix";
        #   imageDigest = "sha256:388839071c356e80b27563503b44b82d4778401314902b7405e6080353c7c25c";
        #   finalImageTag = "23.11";
        # };

        dockerImage = pkgs.dockerTools.buildImage {
           name = "nextstep-backend";
           tag = "latest";
           
           # CORRECCIÓN: Cambia 'from' por 'fromImage'
           fromImage = pkgs.dockerTools.pullImage {
             imageName = "nixos/nix";
             imageDigest = "sha256:388839071c356e80b27563503b44b82d4778401314902b7405e6080353c7c25c";
             finalImageTag = "23.11";
           };
           
           contents = [
             nextstepBackend
             pythonEnv
           ];
           
           config = {
             Cmd = [ "${pythonEnv}/bin/gunicorn" "app:create_app" "--bind" "0.0.0.0:5000" "--workers" "2" ];
             ExposedPorts = { "5000/tcp" = {}; }; # Sintaxis más común y robusta
             WorkingDir = "/app";
           };
         };

      in {
        packages = {
          nextstep-backend-docker = dockerImage;
          default = dockerImage;
        };

        devShells = {
          default = pkgs.mkShell {
            packages = [ pythonEnv ];
            shellHook = ''
              export FLASK_APP=backend/app.py
              export FLASK_ENV=development
              echo "Entorno de desarrollo Flask activado."
            '';
          };
        };
      }
    );
}

