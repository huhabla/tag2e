PROJECT (VTK_TAG2E)

# Minimale Version von cmake
cmake_minimum_required(VERSION 2.4)
if(COMMAND cmake_policy)
  cmake_policy(SET CMP0003 NEW)
endif(COMMAND cmake_policy)

SET (PROJECT_CAN_BUILD 1)

INCLUDE (${PROJECT_SOURCE_DIR}/CMakeOptions.cmake)

IF (PROJECT_CAN_BUILD)

  SUBDIRS (
    Common
    Filtering
    Modules
  )

  INCLUDE_DIRECTORIES (${PROJECT_BINARY_DIR})
  INCLUDE_DIRECTORIES (${PROJECT_SOURCE_DIR}/Common)
  INCLUDE_DIRECTORIES (${PROJECT_SOURCE_DIR}/Filtering)
  INCLUDE_DIRECTORIES (${VTK_GRASS_BRIDGE_INCLUDE_DIR})

  CONFIGURE_FILE(
    ${PROJECT_SOURCE_DIR}/vtkTAG2EConfigure.h.in
    ${PROJECT_BINARY_DIR}/vtkTAG2EConfigure.h
  )

  # Install the configure file
  INSTALL_FILES(/include .h ${PROJECT_BINARY_DIR}/vtkTAG2EConfigure.h)

ENDIF (PROJECT_CAN_BUILD)
