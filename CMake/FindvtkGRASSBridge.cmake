#
# Find the native VTK_GRASS_BRIDGE includes and library
#
# This module defines
# VTK_GRASS_BRIDGE_INCLUDE_DIR, where to find the includes ...
# VTK_GRASS_BRIDGE_LIBRARIES, the libraries to link against
# VTK_GRASS_BRIDGE_LIBRARIES_PYTHON, the libraries to link against for Python support
# VTK_GRASS_BRIDGE_FOUND, If false, do not try to use VTK_GRASS_BRIDGE.

# Find the include path
FIND_PATH(VTK_GRASS_BRIDGE_INCLUDE_DIR vtkGRASSInit.h
	/usr/local/include
	/usr/include
	/usr/local/vtkGRASSBridge/include
	/home/soeren/soft/vtkGRASSBridge/include
)
# Find the library path
FIND_PATH(VTK_GRASS_BRIDGE_LIBRARY_DIR vtkGRASSBridgeCommon
	/usr/local/lib
	/usr/lib
	/usr/local/vtkGRASSBridge/lib
	/home/soeren/soft/vtkGRASSBridge/lib
)
# Find all nessessary libraries
IF(VTK_GRASS_BRIDGE_LIBRARY_DIR)
	FIND_LIBRARY(vtkGRASSBridgeCommon vtkGRASSBridgeCommon	${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeCommonPython vtkGRASSBridgeCommonPython ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeCommonPythonD vtkGRASSBridgeCommonPythonD ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeVector vtkGRASSBridgeVector	${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeVectorPython vtkGRASSBridgeVectorPython ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeVectorPythonD vtkGRASSBridgeVectorPythonD ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeRaster vtkGRASSBridgeRaster	${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeRasterPython vtkGRASSBridgeRasterPython ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeRasterPythonD vtkGRASSBridgeRasterPythonD ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeRaster3d vtkGRASSBridgeRaster3d	${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeRaster3dPython vtkGRASSBridgeRaster3dPython ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeRaster3dPythonD vtkGRASSBridgeRaster3dPythonD ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeIO vtkGRASSBridgeIO	${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeIOPython vtkGRASSBridgeIOPython ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
	FIND_LIBRARY(vtkGRASSBridgeIOPythonD vtkGRASSBridgeIOPythonD ${VTK_GRASS_BRIDGE_LIBRARY_DIR})
ENDIF(VTK_GRASS_BRIDGE_LIBRARY_DIR)

# In case everything is ok, set the variables
IF(VTK_GRASS_BRIDGE_INCLUDE_DIR)
	IF(VTK_GRASS_BRIDGE_LIBRARY_DIR)
        	SET(VTK_GRASS_BRIDGE_FOUND "YES")	
        	SET( VTK_GRASS_BRIDGE_LIBRARIES 
			${vtkGRASSBridgeCommon}
                        ${vtkGRASSBridgeVector}
                        ${vtkGRASSBridgeRaster}
                        ${vtkGRASSBridgeRaster3d}
                        ${vtkGRASSBridgeIO}
		)
        	SET( VTK_GRASS_BRIDGE_LIBRARIES_PYTHON
			${vtkGRASSBridgeCommonPython}
			${vtkGRASSBridgeCommonPythonD}
                        ${vtkGRASSBridgeVectorPython}
                        ${vtkGRASSBridgeVectorPythonD}
                        ${vtkGRASSBridgeRasterPython}
                        ${vtkGRASSBridgeRasterPythonD}
                        ${vtkGRASSBridgeRaster3dPython}
                        ${vtkGRASSBridgeRaster3dPythonD}
                        ${vtkGRASSBridgeIOPython}
                        ${vtkGRASSBridgeIOPythonD}
		)
	ENDIF(VTK_GRASS_BRIDGE_LIBRARY_DIR)
ENDIF(VTK_GRASS_BRIDGE_INCLUDE_DIR)

# Libraries should only set direct in advanced mode
MARK_AS_ADVANCED(
    vtkGRASSBridgeCommon
    vtkGRASSBridgeCommonPython
    vtkGRASSBridgeCommonPythonD
    vtkGRASSBridgeVector
    vtkGRASSBridgeVectorPython
    vtkGRASSBridgeVectorPythonD
    vtkGRASSBridgeRaster
    vtkGRASSBridgeRasterPython
    vtkGRASSBridgeRasterPythonD
    vtkGRASSBridgeRaster3d
    vtkGRASSBridgeRaster3dPython
    vtkGRASSBridgeRaster3dPythonD
    vtkGRASSBridgeIO
    vtkGRASSBridgeIOPython
    vtkGRASSBridgeIOPythonD
)
