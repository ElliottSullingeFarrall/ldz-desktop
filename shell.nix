{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [
    pkgs.poetry
    pkgs.python3
  ];
  
  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";

  FLASK_APP = "source";
  FLASK_DEBUG = 1;
  FLASK_RUN_PORT = 4000;

  POETRY_VIRTUALENVS_IN_PROJECT = true;
  shellHook = ''
    poetry env use $(which python)
    poetry install
  '';
}