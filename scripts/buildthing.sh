pip install --platform=arm64 --platform=x86_64 --no-deps numpy --target foo/

MAKEFLAGS="-j$(nproc)" pip install --platform=arm64 --platform=x86_64 --no-deps --target test/ altgraph blinker certifi charset-normalizer click filelock fire Flask Flask-Cors fsspec fugashi huggingface-hub idna iniconfig itsdangerous jaconv Jinja2 loguru macholib manga-ocr MarkupSafe mpmath networkx np packaging Pillow pip pluggy pyinstaller pyinstaller-hooks-contrib pyperclip pytesseract pytest PyYAML regex requests safetensors setuptools six sympy termcolor tokenizers torch tqdm transformers typing_extensions unidic-lite urllib3 Werkzeug

MAKEFLAGS="-j$(nproc)" /usr/bin/pip3 install --platform=arm64 --platform=x86_64 --no-deps --target=test2/ "pytest>=3.0.7" "Flask>=2.0.2" "flask-cors>=3.0.10" "manga-ocr>=0.1.4" "opencv-python" "Pillow~=9.0.0" "np~=1.0.2" "pytesseract" "requests" altgraph blinker certifi charset-normalizer click filelock fire fsspec fugashi huggingface-hub idna iniconfig itsdangerous jaconv Jinja2 loguru macholib MarkupSafe mpmath networkx packaging pip pluggy pyinstaller pyinstaller-hooks-contrib pyperclip PyYAML regex safetensors setuptools six sympy termcolor tokenizers  tqdm transformers typing_extensions unidic-lite urllib3 Werkzeug torch

MAKEFLAGS="-j$(nproc)" /usr/bin/pip3 download --platform=x86_64 --no-deps "pytest>=3.0.7" "Flask>=2.0.2" "flask-cors>=3.0.10" "manga-ocr>=0.1.4" "opencv-python" "Pillow~=9.0.0" "np~=1.0.2" "pytesseract" "requests" altgraph blinker certifi charset-normalizer click filelock fire fsspec fugashi huggingface-hub idna iniconfig itsdangerous jaconv Jinja2 loguru macholib MarkupSafe mpmath networkx packaging pip pluggy pyinstaller pyinstaller-hooks-contrib pyperclip PyYAML regex safetensors setuptools six sympy termcolor tokenizers  tqdm transformers typing_extensions unidic-lite urllib3 Werkzeug torch


cat ../requirements.txt | xargs -n 1 pip3 download --platform=macosx_11_0_arm64 --only-binary :all: 
arch -x86_64 /usr/bin/pip3 download --platform=macosx_11_0_arm64 --only-binary :all: "pytest>=3.0.7" "Flask>=2.0.2" "flask-cors>=3.0.10" "manga-ocr>=0.1.4" "opencv-python" "Pillow~=9.0.0" "np~=1.0.2" "pytesseract" "requests" 

arch -arm64 /usr/bin/pip3 download --platform=macosx_10_9_x86_64 --only-binary :all: "pytest>=3.0.7" "Flask>=2.0.2" "flask-cors>=3.0.10" "manga-ocr>=0.1.4" "opencv-python" "Pillow~=9.0.0" "np~=1.0.2" "pytesseract" "requests" 

MAKEFLAGS="-j$(nproc)" /usr/bin/pip3 install --platform=arm64  --only-binary=:all: --target=test2/  "Pillow~=9.0.0"

tokenizers safetensors

MAKEFLAGS="-j$(nproc)" arch -x86_64 /usr/bin/pip3 install --no-cache-dir --platform=x86_64 --no-deps --no-clean --target test3/ safetensors

MAKEFLAGS="-j$(nproc)" CMAKE_ARGS="-DPYTHON3_LIMITED_API=ON -DOPENCV_SKIP_PYTHON_LOADER=OFF" CFLAGS="-I/usr/local/include -Wno-error=implicit-function-declaration" pip install --platform=arm64 --platform=x86_64 --no-deps --no-clean --target foo/  opencv-python


MAKEFLAGS="-j$(nproc)" /usr/bin/pip3 install --platform=x86_64 --no-deps --no-clean --target test/  opencv-python
MAKEFLAGS="-j$(nproc)" /Users/nikita/Library/Python/3.9/bin/pip install --platform=x86_64 --no-deps --no-clean --target thang/  opencv-python


opencv-python

/private/var/folders/m3/dc5k9yy51d536ggcbcjn_fvm0000gn/T/pip-build-env-_bqng_t5/overlay/lib/python3.11/site-packages/skbuild/setuptools_wrap.py