#!/bin/sh
pip install venv || true
rm -rf downloads
arch -x86_64 pip3 download -r requirements.txt -d downloads
# list all the packages ending with arm64.whl in the downloads folder, and transform it into a pip requirement
# for exmaple, regex-2023.6.3-cp39-cp39-macosx_11_0_arm64.whl becomes regex==2023.6.3
# then download the "macosx_11_0_arm64" packages into the downloads folder
# ls downloads | grep amd64.whl | sed -E 's/([^-]+)\-([0-9\.]+).*\.whl$/\1=\2/' | xargs -n 1 pip3 download --platform=macosx_10_9_x86_64 --no-deps -d downloads
ls downloads | grep x86_64.whl | sed -E 's/([^-]+)\-([0-9\.]+).*\.whl$/\1==\2/' | xargs -n 1 pip3 download --platform=macosx_11_0_arm64 --no-deps -d downloads --only-binary :all:
ls downloads | grep x86_64.whl | sed -E 's/([^-]+)\-([0-9\.]+).*\.whl$/\1==\2/' | xargs -n 1 pip3 download --platform=macosx_12_0_arm64 --no-deps -d downloads --only-binary :all:

# remove any x86_64.whl packages that have a matching `universal2.whl` package
# for example, if we have `MarkupSafe-2.1.3-cp39-cp39-macosx_10_9_universal2.whl` and `MarkupSafe-2.1.3-cp39-cp39-macosx_10_9_x86_64.whl`
# we want to remove the x86_64 package
cd downloads 
ls -1 | grep universal2.whl | sed -E 's/universal2.whl$/x86_64.whl/' | xargs -n 1 rm -f 

ls -1 | grep 64.whl | xargs -n 2 delocate-fuse -w combined 

# for each package, run delocate-fuse to create a universal2.whl package
cd combined
# ls -1 | grep x86_64.whl | sed -E 's/(.*)x86_64.whl$/\1x86_64.whl \1universal2.whl/' | xargs -n 1 echo | xargs -n 2 mv
# ls -1 | grep arm64.whl | xargs -n 1 rm -f 