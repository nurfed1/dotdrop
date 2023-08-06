# author: nurfed (https://github.com/nurfed1)
# Copyright (c) 2023, nurfed

$fold = "dotfiles"
$conf = "config.yaml"

# copy dotdrop entry point
Copy-Item -Path dotdrop/dotdrop.ps1 -Destination dotdrop.ps1
New-Item -Path $fold -Type Directory -ErrorAction SilentlyContinue

if (-not (Test-Path -Path $conf -PathType Leaf)) {
  # init config file
  Set-Content -Path $conf -Value @"
config:
  backup: true
  create: true
  dotpath: $($fold)
dotfiles:
profiles:
"@;
}
