{ pkgs ? import <nixpkgs> {} }:
let
    pkg-build-requirements = {
        # Force dependencies here
    };
in
pkgs.poetry2nix.mkPoetryApplication {
    projectDir = ./.;
    python = pkgs.python3Full;
    preferWheels = true;
    overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (self: super:
        builtins.mapAttrs (package: build-requirements:
        (builtins.getAttr package super).overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg: if builtins.isString pkg then builtins.getAttr pkg super else pkg) build-requirements);
        })
        ) pkg-build-requirements
  );
}