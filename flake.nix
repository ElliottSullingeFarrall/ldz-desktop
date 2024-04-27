{
  description = "A Nix flake for the LDZ webapp.";

  inputs = {
    nixpkgs = {
      url = "github:NixOS/nixpkgs/nixos-23.11";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, ...}@inputs:
    inputs.flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = inputs.nixpkgs.legacyPackages.${system};
        poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs;};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            inotify-tools

            openssl
            (uwsgi.override { plugins = [ "python3" ]; })

            poetry
            python3
          ];
          
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";

          POETRY_VIRTUALENVS_IN_PROJECT = true;
          shellHook = ''
            poetry env use $(which python)
            poetry install --no-root
          '';
        };
      });
}