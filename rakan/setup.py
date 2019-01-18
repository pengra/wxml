from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='Rakan API Toolkit',
    ext_modules=cythonize('rakan.pyx', annotate=True, gdb_debug=True),
)