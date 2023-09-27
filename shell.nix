{ pkgs ? import <nixpkgs> { } }:

let
  pythonEnv = pkgs.python3Full.withPackages(ps: with ps; [ 
    virtualenv
    pip
  ]);
in
with pkgs;
mkShell {
  packages = [
    pythonEnv
  ];
  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc
    ]}
  '';
}