cmake_minimum_required(VERSION 3.21)
project(aoc_cpp_y2019 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Enforce GCC (user has GCC 16.1) — but do not hard-fail if another compiler is used.
if(NOT CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message(WARNING "Expected GCC, found ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
endif()

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(aoc_cpp_y2019 src/day1.cpp)
target_compile_features(aoc_cpp_y2019 PRIVATE cxx_std_20)
target_compile_options(aoc_cpp_y2019 PRIVATE -Wall -Wextra -O3)

# The compiled extension lands at the project root with the right SONAME.
install(TARGETS aoc_cpp_y2019 LIBRARY DESTINATION .)
