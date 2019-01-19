# Compile tests
cd tests/

echo "Compiling C++ Tests"
g++ -std=c++11 test_graph.cpp

echo "Running C++ Tests"
./a.out
rm *.out

echo "Running Python Tests"
cd ..
py.test --ignore=xayah --doctest-cython

# echo "Running JavaScript Tests"
