{ pkgs ? import <nixpkgs> { }, self ? ./. }:

pkgs.python3Packages.buildPythonApplication {
  pname = "radio";
  src = self;
  version = "0.1";
  propagatedBuildInputs = with pkgs.python3Packages; [ pip ffmpeg-python youtube-dl ];
}