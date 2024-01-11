{ pkgs ? import <nixpkgs> {} }:

with pkgs;
mkShell {
  buildInputs = [
    python3Full.pkgs.venvShellHook
    (
      python3Full.withPackages(ps: with ps; [ 
        (
          buildPythonPackage rec {
            pname = "tkcalendar";
            version = "1.6.1";
            src = pkgs.fetchPypi {
              inherit pname version;
              sha256 = "sha256-Xt+VjApZQp6QMJ6bgFsuIpGSu8q5UkYCRyBNcDDupc8=";
            };
            propagatedBuildInputs = [
              babel
            ];
            doCheck = false;
          }
        )
        (
        pandas.overrideAttrs (attrs: rec {
          enableParallelBuilding = false;
        })
        )
        openpyxl
        platformdirs
      ])
    )
  ];

  nativeBuildInputs = with python3Full.pkgs; [
    setuptools
  ];

  propagatedBuildInputs = [
    stdenv
  ];

  venvDir = ".venv";
  postVenvCreation = ''
    pip install -r requirements.txt
  '';
  
  # LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
  # shellHook = ''
  #   export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
  #     pkgs.stdenv.cc.cc
  #   ]}
  # '';
}