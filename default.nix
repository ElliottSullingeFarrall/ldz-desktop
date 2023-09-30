{ pkgs ? import <nixpkgs> { } }:
# Broke
pkgs.stdenv.mkDerivation rec {
    name = "ldz";
    propogatedBuildInputs = [
        (pkgs.python3Full.withPackages(ps: with ps; [ 
            virtualenv
            pip
            (buildPythonPackage rec {
                pname = "utils";
                version = "1.0.0";
                src = ./src/utils.py;
                doCheck = false;
                })
        ]))
    ];
    dontUnpack = true;
    installPhase = "install -Dm755 ${./src/source.py} $out/bin/${name}";

    desktopItem = pkgs.makeDesktopItem {
        name = "${name}";
        exec = "${name}";
        desktopName = "LDZ";
        icon = "${./src/images/stag.ico}";
    };
}