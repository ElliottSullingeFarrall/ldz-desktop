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
        devShells = {
          default = pkgs.mkShell {
            packages = [
              pkgs.poetry
              pkgs.python3
            ];
            
            LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";

            FLASK_APP = "src";
            FLASK_DEBUG = 1;
            FLASK_RUN_PORT = 4000;

            POETRY_VIRTUALENVS_IN_PROJECT = true;
            shellHook = ''
              poetry env use $(which python)
              poetry install
            '';
          };
        };
      });
}