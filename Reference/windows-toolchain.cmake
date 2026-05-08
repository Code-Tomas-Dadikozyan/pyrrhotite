# configure for Windows
set(CMAKE_SYSTEM_NAME Windows)

# configure mingw-w64
set(CMAKE_C_COMPILER x86_64-w64-mingw32-gcc)
set(CMAKE_CXX_COMPILER x86_64-w64-mingw32-g++)

# prevent 'file too big' assembler error
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wa,-mbig-obj")
# set GUI application
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mwindows")

# indicate where to find headers and libraries
set(CMAKE_FIND_ROOT_PATH /usr/x86_64-w64-mingw32 ${CMAKE_CURRENT_SOURCE_DIR}/lib/boost-mingw-w64-x86-64-posix ${CMAKE_CURRENT_SOURCE_DIR}/lib/qtbase-mingw-w64-x86-64-posix ${CMAKE_CURRENT_SOURCE_DIR}/lib/nlohmann-json-mingw-w64-x86-64-posix ${CMAKE_CURRENT_SOURCE_DIR}/lib/freetype-mingw-w64-x86-64-posix)

# only search for headers and libraries in the above paths
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)

# only search for programs on the host
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

# configure resources file
set(RESOURCES_WINDOWS "${CMAKE_CURRENT_SOURCE_DIR}/resources.rc")
