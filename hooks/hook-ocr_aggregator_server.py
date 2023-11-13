# -*- coding: utf-8 -*-
"""Pyinstaller hook for watchmaker standalone."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from PyInstaller.utils.hooks import (collect_data_files, collect_dynamic_libs,
                                     collect_submodules, copy_metadata)
import platform

datas = [
    # ("/Users/nikita/.pyenv/versions/3.10.12/envs/OCRAS/lib/python3.10/site-packages/unidic_lite", "unidic_lite"),
    # ("/Users/nikita/.pyenv/versions/3.10.12/envs/OCRAS/lib/python3.10/site-packages/manga_ocr/assets", "assets"),
    # ("data", "data"),
]

binaries = []
hiddenimports = [
    "tqdm",
]
datas += copy_metadata("ocr_aggregator_server", recursive=True)
datas += collect_data_files("ocr_aggregator_server")
binaries += collect_dynamic_libs("ocr_aggregator_server")
hiddenimports += collect_submodules("ocr_aggregator_server")