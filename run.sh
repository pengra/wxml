rm -rf rakan/build/
rm -rf rakan/cython_debug/
rm -r rakan/*.*o
rm -rf rakan/__pycache__/
rm -r rakan/*.html
rm -r rakan/rakan.cpp
cd rakan
touch rakan.pyx
touch rakan.pxd
python setup.py build_ext --inplace
cd ..
python rakan/