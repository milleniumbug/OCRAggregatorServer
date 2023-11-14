
# get the directory for this script file
$script_dir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# get the parent directory
$parent_dir = Split-Path -Parent $script_dir

# get the last part of the parent directory
$parent_dir_name = Split-Path -Leaf $parent_dir

$venv_dir = "$parent_dir/venv"

# remove venv, build, dist, data, ocr_aggregator_server.egg-info directories and ocr_aggregator_server.spec
Remove-Item -Recurse -Force -erroraction silentlycontinue "$venv_dir" 
Remove-Item -Recurse -Force -erroraction silentlycontinue "$parent_dir/build"
Remove-Item -Recurse -Force -erroraction silentlycontinue "$parent_dir/dist"
Remove-Item -Recurse -Force -erroraction silentlycontinue "$parent_dir/ocr_aggregator_server.egg-info"
Remove-Item -Recurse -Force -erroraction silentlycontinue "$parent_dir/data/model.*"
Remove-Item -Recurse -Force -erroraction silentlycontinue "$parent_dir/data/ImageTrans-Balloons-Model.zip"
Remove-Item -Recurse -Force -erroraction silentlycontinue "$parent_dir/libdarknetpy"
Remove-Item -Force -erroraction silentlycontinue "$parent_dir/ocr_aggregator_server.spec"