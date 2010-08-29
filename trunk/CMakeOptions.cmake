#
# Try to find VTK and include its settings (otherwise complain)
#
INCLUDE (${CMAKE_ROOT}/Modules/FindVTK.cmake)
# We need vtkGRASSBridge, so no option is defined
INCLUDE (CMake/FindvtkGRASSBridge.cmake)

IF (USE_VTK_FILE)
  INCLUDE (${USE_VTK_FILE})
ELSE (USE_VTK_FILE)
  SET (VTK_TAG2E_CAN_BUILD 0)
ENDIF (USE_VTK_FILE)

#
# Defaults to the same VTK setting.
#

IF (USE_VTK_FILE)
  # Standard CMake option for building libraries shared or static by default.
  OPTION(BUILD_SHARED_LIBS 
         "Build with shared libraries." 
         ${VTK_BUILD_SHARED_LIBS})
  # Copy the CMake option to a setting with VTK_TAG2E_ prefix for use in
  # our project.  This name is used in vtkTAG2EConfigure.h.in.
  SET(VTK_TAG2E_BUILD_SHARED_LIBS ${BUILD_SHARED_LIBS})

  #
  # Output path(s)
  #
  SET (LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib CACHE PATH
       "Single output directory for building all libraries.")

  SET (EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin CACHE PATH
       "Single output directory for building all executables.")

  MARK_AS_ADVANCED (
    LIBRARY_OUTPUT_PATH 
    EXECUTABLE_OUTPUT_PATH
  )

  # If this is a build tree, provide an option for putting
  # this project's executables and libraries in with VTK's.
  IF (EXISTS ${VTK_DIR}/bin)
    OPTION(USE_VTK_OUTPUT_PATHS
           "Use VTK's output directory for this project's executables and libraries."
           OFF)
    MARK_AS_ADVANCED (USE_VTK_OUTPUT_PATHS)
    IF (USE_VTK_OUTPUT_PATHS)
      SET (LIBRARY_OUTPUT_PATH ${VTK_DIR}/bin)
      SET (EXECUTABLE_OUTPUT_PATH ${VTK_DIR}/bin)
    ENDIF (USE_VTK_OUTPUT_PATHS)
  ENDIF (EXISTS ${VTK_DIR}/bin)

#
# Python Wrapping
#

IF (VTK_WRAP_PYTHON)

  OPTION(VTK_TAG2E_WRAP_PYTHON
         "Wrap classes into the Python interpreted language."
         ON)

  IF (VTK_TAG2E_WRAP_PYTHON)
    INCLUDE(${VTK_CMAKE_DIR}/vtkWrapPython.cmake)
    IF (WIN32)
      IF (NOT BUILD_SHARED_LIBS)
        MESSAGE(FATAL_ERROR "Python support requires BUILD_SHARED_LIBS to be ON.")
        SET (VTK_TAG2E_CAN_BUILD 0)
      ENDIF (NOT BUILD_SHARED_LIBS)
    ENDIF (WIN32)
  ENDIF (VTK_TAG2E_WRAP_PYTHON)

ELSE (VTK_WRAP_PYTHON)

  IF (VTK_TAG2E_WRAP_PYTHON)
    MESSAGE("Warning. VTK_TAG2E_WRAP_PYTHON is ON but the VTK version you have "
            "chosen has not support for Python (VTK_WRAP_PYTHON is OFF).  "
            "Please set VTK_TAG2E_WRAP_PYTHON to OFF.")
    SET (VTK_TAG2E_WRAP_PYTHON OFF)
  ENDIF (VTK_TAG2E_WRAP_PYTHON)

ENDIF (VTK_WRAP_PYTHON)

SET(VTK_WRAP_HINTS ${VTK_TAG2E_SOURCE_DIR}/Wrapping/hints)

ENDIF (USE_VTK_FILE)

