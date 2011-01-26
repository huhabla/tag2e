#SUBDIRS(Testing)

#
# Source files
#
# Here is where you can add the name of your local unsorted classes.
#

SET (Common_SRCS
vtkTAG2EAlternativeN2OPredictionModules.cxx
vtkTAG2EModelParameterCollection.cxx
vtkKeyValueMap.cxx
)

SET (Common_H
vtkTAG2EAlternativeN2OPredictionModules.h
vtkTAG2ECommonWin32Header.h
vtkTAG2EModelParameterCollection.h
vtkTAG2EDefines.h
vtkKeyValueMap.h
)

# --------------------------------------------------------------------------
# You probably do not need to modify anything below this line

# Create the vtkTAG2ECommon C++ library.
ADD_LIBRARY (vtkTAG2ECommon ${Common_SRCS}  ${Common_H})
TARGET_LINK_LIBRARIES(vtkTAG2ECommon vtkCommon ${VTK_GRASS_BRIDGE_LIBRARIES})


# Create the vtkTAG2ECommon Python library.
IF (VTK_WRAP_PYTHON AND VTK_TAG2E_WRAP_PYTHON)
  VTK_WRAP_PYTHON3 (vtkTAG2ECommonPython CommonPython_SRCS "${Common_SRCS}")
  ADD_LIBRARY (vtkTAG2ECommonPythonD ${CommonPython_SRCS})
  ADD_LIBRARY (vtkTAG2ECommonPython MODULE vtkTAG2ECommonPythonInit.cxx)
  TARGET_LINK_LIBRARIES(vtkTAG2ECommonPythonD vtkTAG2ECommon vtkCommonPythonD ${VTK_GRASS_BRIDGE_LIBRARIES_PYTHON})
  TARGET_LINK_LIBRARIES(vtkTAG2ECommonPython vtkTAG2ECommonPythonD)

  INSTALL_TARGETS(/lib vtkTAG2ECommonPythonD vtkTAG2ECommonPython)
ENDIF (VTK_WRAP_PYTHON AND VTK_TAG2E_WRAP_PYTHON)

IF (VTK_USE_HYBRID)
  TARGET_LINK_LIBRARIES (vtkTAG2ECommon vtkHybrid)
ENDIF (VTK_USE_HYBRID)

IF (VTK_USE_PARALLEL)
  TARGET_LINK_LIBRARIES (vtkTAG2ECommon vtkParallel)
ENDIF (VTK_USE_PARALLEL)

IF (VTK_USE_PATENTED)
  TARGET_LINK_LIBRARIES (vtkTAG2ECommon vtkPatented)
ENDIF (VTK_USE_PATENTED)

IF (VTK_USE_RENDERING)
  TARGET_LINK_LIBRARIES (vtkTAG2ECommon vtkRendering)
ENDIF (VTK_USE_RENDERING)

INSTALL_FILES(/include .h ${Common_H})
INSTALL_TARGETS(/lib vtkTAG2ECommon)
