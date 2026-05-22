#!/usr/bin/env python
from pathlib import Path

import nbformat
from nbformat.notebooknode import NotebookNode


JUPYTERLITE_PATCH = """# this is required to monkey patch any urllib requests to use urllib3/requests.
# urllib is not WASM compatible. Emscripten tries to automatically reroute any of its download
# requests to a ws:// websocket which fails with a "Mixed content" error on an https:// deployment.

import pyodide_http
pyodide_http.patch_all()  # Patch all libraries

import numpy as np
def fake_memmap(filename, dtype=np.uint8, mode=None, offset=0, shape=None, order=None):
    with open(filename, "rb") as f:
        f.seek(offset)
        data = np.fromfile(f, dtype=dtype)
    if shape is not None:
        data = data.reshape(shape)
    return data

np.memmap = fake_memmap
"""


root = Path("content")

for notebook_file in root.glob('**/*.ipynb'):
    # not sure if it's safe to just initialize this once.. so do it in loop to
    # be safe
    new_cell = {
        'cell_type': 'code',
        'metadata': {},
        'execution_count': None,
        'source': JUPYTERLITE_PATCH,
        'outputs': []}
    new_cell = NotebookNode(**new_cell)

    # optional how to read jupytext files
    # import jupytext
    # nb = jupytext.read("Python_Crash_Course_solution.py")

    nb = nbformat.read(str(notebook_file), as_version=nbformat.NO_CONVERT)

    # find the first code cell and insert before
    for i, cell in enumerate(nb.cells):
        if cell['cell_type'] == 'code':
            break
    # check if that cell already is what we would write (to not do the
    # addition twice) and skip if so
    if cell['source'] == new_cell['source']:
        print(f'skipping, patch already present: {notebook_file}')
        continue
    nb.cells.insert(i, new_cell)
    # write in place
    nbformat.write(nb, str(notebook_file))
    print(f'added patch in place: {notebook_file}')
