cmake_minimum_required(VERSION 3.21)
project(SkyrimUnrealBridge LANGUAGES CXX VERSION 0.1.0)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL")
set(BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(ENABLE_SKYRIM_VR OFF CACHE BOOL "" FORCE)
set(ENABLE_SKYRIM_SE OFF CACHE BOOL "" FORCE)

add_subdirectory(deps/CommonLibSSE-NG)
include(deps/CommonLibSSE-NG/cmake/CommonLibSSE.cmake)

add_commonlibsse_plugin(SkyrimUnrealBridge
	AUTHOR "Aidan"
	VERSION 0.1.0
	USE_ADDRESS_LIBRARY
	SOURCES plugin/src/main.cpp)

target_compile_features(SkyrimUnrealBridge PRIVATE cxx_std_23)
target_precompile_headers(SkyrimUnrealBridge PRIVATE
	plugin/src/PCH.h)
