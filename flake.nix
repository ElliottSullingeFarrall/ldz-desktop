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

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      in
      {
        packages = {
          default = self.packages.${system}.ldz;
          ldz = mkPoetryApplication rec {
            pname = "ldz";
            version = "v1.4";

            projectDir = ./.;
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
        devShells.default = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.ldz ];
          packages = [ pkgs.poetry ];
        };
      }) // {
        overlays.ldz = final: prev: {
          ldz = self.packages.x86_64-linux.ldz;
        };
      };
}