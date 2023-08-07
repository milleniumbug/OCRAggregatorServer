# -*- coding: utf-8 -*-
"""Pyinstaller hook for watchmaker standalone."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from PyInstaller.utils.hooks import (collect_data_files, collect_dynamic_libs,
                                     collect_submodules, copy_metadata)

datas = []
binaries = []
hiddenimports = []
datas += copy_metadata("manga_ocr", recursive=True)
datas += collect_data_files("manga_ocr")
binaries += collect_dynamic_libs("manga_ocr")
hiddenimports += collect_submodules("manga_ocr")