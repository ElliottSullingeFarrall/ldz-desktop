{ pkgs ? import <nixpkgs> {} }:
let
    poetry2nix = import( pkgs.fetchFromGitHub {
        owner = "nix-community";
        repo = "poetry2nix";
        rev = "master";
        sha256 = "sha256-puYyylgrBS4AFAHeyVRTjTUVD8DZdecJfymWJe7H438=";
    }) {};
    pkg-build-requirements = {
        # Force dependencies here
    };
in
poetry2nix.mkPoetryApplication {
    projectDir = ./.;
    python = pkgs.python3Full;
    preferWheels = true;
    overrides = poetry2nix.defaultPoetryOverrides.extend (self: super:
        builtins.mapAttrs (package: build-requirements:
        (builtins.getAttr package super).overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg: if builtins.isString pkg then builtins.getAttr pkg super else pkg) build-requirements);
        })
        ) pkg-build-requirements
  );
}