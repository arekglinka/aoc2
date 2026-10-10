cmake_minimum_required(VERSION 3.28)
project(aoc_cpp_y2019 LANGUAGES CXX)

# Emit compile_commands.json so clangd / vscode-cpptools can resolve includes
# and flags for IntelliSense.
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Enforce GCC (GCC 16.2 in the lambda_cpp26-dev container, GCC 16.1 on host)
# — but do not hard-fail if another compiler is used.
if(NOT CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message(WARNING "Expected GCC, found ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
endif()

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Override pybind11_strip before pybind11_add_module: pybind11 3.x strips the
# .so unconditionally in Release builds — the no-op keeps DWARF for LLDB.
function(pybind11_strip)
endfunction()

pybind11_add_module(aoc_cpp_y2019 src/day1.cpp)
target_compile_features(aoc_cpp_y2019 PRIVATE cxx_std_26)
# -g must be on BOTH compile and link when LTO is active, or debug info is
# silently stripped at link time.
target_compile_options(aoc_cpp_y2019 PRIVATE -Wall -Wextra -O3 -g)
target_link_options(aoc_cpp_y2019 PRIVATE -g)

# The compiled extension lands at the project root with the right SONAME.
install(TARGETS aoc_cpp_y2019 LIBRARY DESTINATION .)
