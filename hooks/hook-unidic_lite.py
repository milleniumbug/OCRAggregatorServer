# -*- coding: utf-8 -*-
"""Pyinstaller hook for watchmaker standalone."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from PyInstaller.utils.hooks import (collect_data_files, collect_dynamic_libs,
                                     collect_submodules, copy_metadata)

datas = []
binaries = []
hiddenimports = []
datas += copy_metadata("unidic_lite", recursive=True)
datas += collect_data_files("unidic_lite")
binaries += collect_dynamic_libs("unidic_lite")
hiddenimports += collect_submodules("unidic_lite")