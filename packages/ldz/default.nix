{ lib
, pkgs
, ...
}:

let
  inherit (lib.poetry2nix.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
in
mkPoetryApplication rec {
  pname = "ldz";

  projectDir = ../..;
  python = pkgs.python310Full;
  preferWheels = true;

  desktopItem = pkgs.makeDesktopItem {
    name = "LDZ";
    comment = "App for use in the University of Surrey's LDZ";
    desktopName = "LDZ App";
    exec = "${pname}";
    icon = "${pname}";
    terminal = false;
    type = "Application";
  };
  postPatch = ''
    mkdir -p $out/share/applications
    cp ${desktopItem}/share/applications/* $out/share/applications
    mkdir -p $out/share/pixmaps
    ln -s $out/lib/python3.10/site-packages/ldz/assets/stag.png $out/share/pixmaps/ldz.png
  '';
}
