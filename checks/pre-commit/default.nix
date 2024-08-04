{ lib
, pkgs
, system
, ...
}:

lib.pre-commit-hooks.${system}.run {
  src = ../..;

  hooks = {

    /* --------------------------------- Editor --------------------------------- */

    editorconfig-checker.enable = true;
    end-of-file-fixer.enable = true;
    trim-trailing-whitespace.enable = true;

    typos = {
      enable = true;
      settings.configPath = "typos.toml";
    };

    /* --------------------------------- Checks --------------------------------- */

    nil.enable = true;
    check-json.enable = true;
    check-toml.enable = true;
    check-yaml.enable = true;

    check-python.enable = true;
    poetry-check.enable = true;

    /* --------------------------------- Format --------------------------------- */

    treefmt = {
      enable = true;
      package = lib.treefmt-nix.mkWrapper pkgs ../../treefmt.nix;
    };

    /* ----------------------------------- Git ---------------------------------- */

    convco.enable = true;
    no-commit-to-branch.enable = true;

    check-added-large-files.enable = true;
    check-vcs-permalinks.enable = true;
    detect-private-keys.enable = true;
    forbid-new-submodules.enable = true;

  };
}
