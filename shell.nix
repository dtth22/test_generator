{pkgs, ...}: {
  enterShell = ''
    exec fish
  '';

  languages.python = {
    enable = true;
    venv = {
      enable = true;
      requirements = builtins.readFile ./requirements.txt;
    };
  };
}
