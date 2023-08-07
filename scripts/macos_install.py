import os, pathlib, platform, shutil, subprocess, sys, urllib.request, zipfile
import delocate.fuse
# clear downloads dir
shutil.rmtree("downloads", ignore_errors=True)
 
# Download requirements from pip
subprocess.check_call(["arch", "-x86_64", sys.executable, "-m", "pip", "download", "-r", "requirements.txt", "-d", "downloads"])

# list all the files ending in "x86_64.whl"
whl_files_x86 = [f for f in os.listdir("downloads") if f.endswith("x86_64.whl")]

# capture s/([^-]+)\-([0-9\.]+).*\.whl$/\1==\2/
requirements_to_dl = []
for whl_file in whl_files_x86:
    package_name = whl_file.split("-")[0]
    package_version = whl_file.split("-")[1]
    requirement = package_name + "==" + package_version
    requirements_to_dl.append((requirement, whl_file))
    print ("downloading arm64 version of " + requirement)

# Download requirements from pip
for requirement, whl_file in requirements_to_dl:
    # join tuple
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "download", "--platform", "macosx_11_0_arm64", "--no-deps", "--only-binary", ":all:", "-d", "downloads", requirement])
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "download", "--platform", "macosx_12_0_arm64", "--no-deps", "--only-binary", ":all:", "-d", "downloads", requirement])
        except subprocess.CalledProcessError:
            print("Failed to download amd64 " + requirement)
            pass


# list the downloads directory, and find the files ending in "arm64.whl"
whl_files_arm64 = [f for f in os.listdir("downloads") if f.endswith("arm64.whl")]

files_to_fuse = []

# check the downloads directory for matching files ending in "x86_64.whl"
for whl_file in whl_files_x86:
    # split the filename into package name and version
    package_name = whl_file.split("-")[0]
    # check if the package name exists in the arm64 list
    found = False
    for armfile in whl_files_arm64:
        if package_name in armfile:
            files_to_fuse.append((whl_file, armfile))
            found = True
            break
    if not found:
        print("Failed to find arm64 version of " + package_name)
        # remove the x86_64 version from the downloads directory, and the list
        os.remove(os.path.join("downloads", whl_file))


for x86_file, arm_file in files_to_fuse:
    print("Fusing " + x86_file + " and " + arm_file)
    delocate.fuse.fuse_wheels(os.path.join("downloads", x86_file), os.path.join("downloads", arm_file), os.path.join("downloads", x86_file.replace("x86_64", "universal2")))
    os.remove(os.path.join("downloads", x86_file))
    os.remove(os.path.join("downloads", arm_file))