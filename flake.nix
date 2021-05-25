{
  description = "An internet radio service";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in
      rec {
        packages = flake-utils.lib.flattenTree {
          radio = import ./default.nix { inherit pkgs; inherit self; };
        };
        defaultPackage = packages.radio;
        apps.radio = flake-utils.lib.mkApp { drv = packages.radio; };
        defaultApp = apps.radio;
      }
    );
}
