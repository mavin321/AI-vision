cmake_minimum_required(VERSION 3.14)
project(vision_ext LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)
find_package(OpenCV REQUIRED)

pybind11_add_module(vision pybind_wrapper.cpp vision.cpp)

target_link_libraries(vision PRIVATE ${OpenCV_LIBS})

target_include_directories(vision PRIVATE ${OpenCV_INCLUDE_DIRS})

set_target_properties(vision PROPERTIES OUTPUT_NAME "vision")
