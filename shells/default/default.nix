{ mkShell
, pkgs
, ...
}:

mkShell {
  name = "poetry";

  packages = with pkgs; [ poetry python310Full ];

  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";

  POETRY_VIRTUALENVS_IN_PROJECT = true;
  shellHook = ''
    poetry env use $(which python)
    poetry install
  '';
}
