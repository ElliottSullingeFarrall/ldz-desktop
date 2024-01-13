{ pkgs ? import <nixpkgs> {} }:
let
    pkg-build-requirements = {
        # tkcalendar = [ "setuptools" ];
        # altgraph = [ "setuptools" ];
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