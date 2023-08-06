# author: nurfed (https://github.com/nurfed1)
# Copyright (c) 2023, nurfed

# setup variables
$cur = $PSScriptRoot
$opwd = $PWD

# pivot
Set-Location -Path $cur -ErrorAction SilentlyContinue
if (-not $?) { 
	echo "Directory `"$($cur)`" doesn't exist, aborting." 
	exit 1
}

# init/update the submodule
if ([string]::IsNullOrEmpty($env:DOTDROP_AUTOUPDATE) -or ($env:DOTDROP_AUTOUPDATE -eq "yes")) {
  git submodule update --init --recursive
  git submodule update --remote dotdrop
}

# check python executable
$pybin = "python3"
if (-not (Get-Command $pybin -ErrorAction SilentlyContinue)) {
	$pybin="python"
}
if (-not ((& $pybin -V) -match  "Python 3")) { 
	echo "install Python 3"
	exit 1
}

# launch dotdrop
$PYTHONPATH = $env:PYTHONPATH
$env:PYTHONPATH = "dotdrop;" + $env:PYTHONPATH
& $pybin -m dotdrop.dotdrop $args
$env:PYTHONPATH = $PYTHONPATH
$ret = $LASTEXITCODE

# pivot back
Set-Location -Path $opwd -ErrorAction SilentlyContinue
if (-not $?) { 
	echo "Directory `"$($opwd)`" doesn't exist, aborting." 
	exit 1
}

# exit with dotdrop exit code
exit $ret
