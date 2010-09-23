#SUBDIRS(Testing)

#
# Source files
#
# Here is where you can add the name of your local unsorted classes.
#

SET (Filtering_SRCS
vtkTAG2EDImageDataN2OFilterFreibauer.cxx
vtkTAG2EDataSetN2OFilterFreibauer.cxx
)

SET (Filtering_H
vtkTAG2EFilteringWin32Header.h
vtkTAG2EDImageDataN2OFilterFreibauer.h
vtkTAG2EDataSetN2OFilterFreibauer.h
)

# --------------------------------------------------------------------------
# You probably do not need to modify anything below this line

# Create the vtkTAG2EFiltering C++ library.
ADD_LIBRARY (vtkTAG2EFiltering ${Filtering_SRCS}  ${Filtering_H})
TARGET_LINK_LIBRARIES(vtkTAG2EFiltering vtkTAG2ECommon vtkFiltering ${VTK_GRASS_BRIDGE_LIBRARIES})


# Create the vtkTAG2EFiltering Python library.
IF (VTK_WRAP_PYTHON AND VTK_TAG2E_WRAP_PYTHON)
  VTK_WRAP_PYTHON3 (vtkTAG2EFilteringPython FilteringPython_SRCS "${Filtering_SRCS}")
  ADD_LIBRARY (vtkTAG2EFilteringPythonD ${FilteringPython_SRCS})
  ADD_LIBRARY (vtkTAG2EFilteringPython MODULE vtkTAG2EFilteringPythonInit.cxx)
  TARGET_LINK_LIBRARIES(vtkTAG2EFilteringPythonD vtkTAG2EFiltering vtkTAG2ECommonPythonD vtkFilteringPythonD ${VTK_GRASS_BRIDGE_LIBRARIES_PYTHON})
  TARGET_LINK_LIBRARIES(vtkTAG2EFilteringPython vtkTAG2EFilteringPythonD)

  INSTALL_TARGETS(/lib vtkTAG2EFilteringPythonD vtkTAG2EFilteringPython)
ENDIF (VTK_WRAP_PYTHON AND VTK_TAG2E_WRAP_PYTHON)

IF (VTK_USE_HYBRID)
  TARGET_LINK_LIBRARIES (vtkTAG2EFiltering vtkHybrid)
ENDIF (VTK_USE_HYBRID)

IF (VTK_USE_PARALLEL)
  TARGET_LINK_LIBRARIES (vtkTAG2EFiltering vtkParallel)
ENDIF (VTK_USE_PARALLEL)

IF (VTK_USE_PATENTED)
  TARGET_LINK_LIBRARIES (vtkTAG2EFiltering vtkPatented)
ENDIF (VTK_USE_PATENTED)

IF (VTK_USE_RENDERING)
  TARGET_LINK_LIBRARIES (vtkTAG2EFiltering vtkRendering)
ENDIF (VTK_USE_RENDERING)

INSTALL_FILES(/include .h ${Filtering_H})
INSTALL_TARGETS(/lib vtkTAG2EFiltering)