{
  description = "A Nix flake for the LDZ application.";

  inputs = {
    nixpkgs = {
      url = "github:NixOS/nixpkgs/nixos-23.11";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, ...}@inputs:
    inputs.flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = inputs.nixpkgs.legacyPackages.${system};
        poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs;};
      in
      {
        packages = {
          default = self.packages.${system}.ldz;
          ldz = poetry2nix.mkPoetryApplication rec {
            pname = "ldz";
            version = "v1.4";

            projectDir = self;
            python = pkgs.python3Full;
            preferWheels = true;
            # overrides = poetry2nix.defaultPoetryOverrides.extend (self: super:
            #   builtins.mapAttrs (package: build-requirements:
            #   (builtins.getAttr package super).overridePythonAttrs (old: {
            #       buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg: if builtins.isString pkg then builtins.getAttr pkg super else pkg) build-requirements);
            #   })
            #   ) {};
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
              ln -s $out/lib/python3.11/site-packages/ldz/images/stag.png $out/share/pixmaps/ldz.png
            '';
          };
        };
        devShells = {
          default = self.devShells.${system}.ldz;
          ldz = pkgs.mkShell {
            # inputsFrom = [ self.packages.${system}.ldz ];
            packages = with pkgs; [ poetry python3Full ];

            # LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";

            POETRY_VIRTUALENVS_IN_PROJECT = true;
            shellHook = ''
              poetry env use $(which python)
              poetry install --no-root
            '';
          };
        };
        overlay = final: prev: {
          ldz = self.packages.${system}.ldz;
        };
      });
}