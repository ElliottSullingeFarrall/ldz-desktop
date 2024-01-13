{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [
    # python3Full.pkgs.venvShellHook
    # python3Full.pkgs.setuptools
    # stdenv
    pkgs.poetry
    pkgs.python3Full
  ];

  # venvDir = ".venv";
  # postVenvCreation = ''
  #   pip install -r requirements.txt
  # '';
  
  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";

  POETRY_VIRTUALENVS_IN_PROJECT = true;
  shellHook = ''
    poetry env use $(which python)
    poetry install
  '';
  # shellHook = ''
  #   export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
  #     pkgs.stdenv.cc.cc
  #   ]}
  # '';
}