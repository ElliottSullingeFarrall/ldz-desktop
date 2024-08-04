{
  projectRootFile = ".git/config";
  settings.global.excludes = [
    ".editorconfig"
    "src/assets/*"
  ];
  programs = {
    actionlint.enable = true;
    beautysh.enable = true;
    deadnix.enable = true;
    isort.enable = true;
    jsonfmt.enable = true;
    mdformat.enable = true;
    mypy.enable = true;
    nixpkgs-fmt.enable = true;
    prettier.enable = true;
    ruff.enable = true;
    shfmt.enable = true;
    statix.enable = true;
    taplo.enable = true;
    yamlfmt.enable = true;
  };
  settings.formatter = {
    yamlfmt.excludes = [ ".github/workflows/*.yaml" ];
  };
}
