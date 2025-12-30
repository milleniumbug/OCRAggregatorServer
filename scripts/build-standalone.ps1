# get the directory for this script file
$ErrorActionPreference = "Stop"
$script_dir = Split-Path -Parent $MyInvocation.MyCommand.Definition

$ErrorActionPreference = "Stop"
. "$script_dir\util.ps1"

# check if `python` or `python3` exists
$python_command = "python"
if (Get-Command python -ErrorAction SilentlyContinue) {
    $python_command = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $python_command = "python3"
} else {
    Write-Host "Python not found!"
    exit 1
}
Write-Host "Python command: $python_command"

# get the directory for this script file
$script_dir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# get the parent directory
$parent_dir = Split-Path -Parent $script_dir

$venv_dir = "$parent_dir/venv"
$venv_scripts_dir = "bin"
# check if we are on windows
if ($env:OS -eq "Windows_NT") {
    $venv_scripts_dir = "Scripts"
}


$venv_activate = "$venv_dir/$venv_scripts_dir/Activate.ps1"
$data_dir = "$parent_dir/data"
$balloon_model_zip = "$data_dir/ImageTrans-Balloons-Model.zip"

# check if venv exists
if ( -not (Test-Path $venv_dir)) {
    & $python_command -m venv $venv_dir
} 
if ( -not (Test-Path $venv_dir)) {
    # fail
    Write-Host "venv failed to create!"
    exit 1
}
if ( -not (Test-Path $venv_activate)) {
    # fail
    Write-Host "venv exists but Activate.ps1 does not exist!"
    Write-Host "Please remove the venv directory and try again."
    exit 1
}
. "$venv_activate"

python -m pip install $parent_dir
python -m pip install pyinstaller

if ($env:IS_CI) {
    # if we're not on windows, run `df -h`
    if ($env:OS -ne "Windows_NT") {
        Write-Host "**** Disk space before build:"
        df -h
        Write-Host "**** Disk space used in venv:"
        du -hs $venv_dir
    }
    Write-Host "Purging pip cache..."
    python -m pip cache purge

    if ($env:OS -ne "Windows_NT") {
        Write-Host "**** Disk space before build (after pip cache purge):"
        df -h
    }
}

# We probably don't need this for the standalone build now.
# check if model.cfg, model.weights, and model.json exist
# if ( -not (Test-Path "$data_dir/model.cfg") -or -not (Test-Path "$data_dir/model.weights") -or -not (Test-Path "$data_dir/model.json")) {
#     # download model
#     Invoke-WebRequest "https://github.com/nikitalita/Bubble-detection-model/releases/download/0.0.1/ImageTrans-Balloons-Model.zip" -OutFile "$balloon_model_zip"
#     Expand-Archive -Force -Path "$balloon_model_zip" -DestinationPath "$data_dir"
#     Remove-Item "$balloon_model_zip"
# }

pyinstaller --noconfirm --clean --additional-hooks-dir hooks --name "ocr_aggregator_server" "$parent_dir/standalone.py"
deactivate
