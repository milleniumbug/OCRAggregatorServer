python -m venv venv

# check if we are on windows
if ($env:OS -eq "Windows_NT") {
    $venv_scripts_dir = "Scripts"
} else {
    $venv_scripts_dir = "bin"
}

if (${env:LIBDARKNETPY_PREFIX} -eq $null || ${env:LIBDARKNETPY_PREFIX} -eq "") {
    $LIBDARKNETPY_DIR = "../libdarknetpy"
} else {
    $LIBDARKNETPY_DIR = ${env:LIBDARKNETPY_PREFIX} + "/libdarknetpy"
}

. "venv/$venv_scripts_dir/Activate.ps1"
python -m pip install cmake
pip install --verbose "$LIBDARKNETPY_DIR"
python -m pip install -r requirements.txt
python -m pip install .
python -m pip install pyinstaller
cd data
wget -nv https://github.com/nikitalita/Bubble-detection-model/releases/download/0.0.1/ImageTrans-Balloons-Model.zip
unzip -o ImageTrans-Balloons-Model.zip
rm ImageTrans-Balloons-Model.zip
cd ..
pyinstaller --clean --additional-hooks-dir hooks --name "ocr_aggregator_server" standalone.py
deactivate
Remove-Item venv -Recurse -Force
