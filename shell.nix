{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  nativeBuildInputs = [
    (pkgs.python3Full.withPackages(ps: with ps; [ 
      virtualenv
      pip
    ]))
    pkgs.stdenv
  ];
  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
  # shellHook = ''
  #   export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
  #     pkgs.stdenv.cc.cc
  #   ]}
  # '';
  shellHook = ''
    venv/bin/python /home/elliott/Git/LDZ-Apps/src/source.py
  '';
}