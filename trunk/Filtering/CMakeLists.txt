#SUBDIRS(Testing)

#
# Source files
#
# Here is where you can add the name of your local unsorted classes.
#

SET (Filtering_SRCS
    vtkTAG2EImageDataN2OFilterFreibauer.cxx
    vtkTAG2EDataSetN2OFilterFreibauer.cxx
    vtkTAG2EDataSetN2OFilterStehfest.cxx
    vtkTAG2EDataSetN2OFilterRoelandt.cxx
    vtkTAG2EDataSetN2OFilterBouwman.cxx
    vtkTAG2EAbstractModel.cxx
    vtkTAG2EAbstractCalibratableModel.cxx
    vtkTAG2EAbstractModelParameter.cxx
    vtkTAG2EAbstractModelEstimator.cxx
    vtkTAG2EAbstractModelCalibrator.cxx
    vtkTAG2EAbstractModelVariationAnalyser.cxx
    vtkTAG2EAbstractCalibratableModelParameter.cxx
    vtkTAG2EFuzzyInferenceModelParameter.cxx
    vtkTAG2ELinearRegressionModel.cxx
    vtkTAG2EModelMonteCarloVariationAnalyser.cxx
    vtkTAG2EFuzzyInferenceModel.cxx
    vtkTAG2EFuzzyInferenceModelParameterToImageData.cxx
    vtkTAG2ESimulatedAnnealingModelCalibrator.cxx
#    vtkTAG2ERSpaceTimeModel.cxx
    vtkTAG2EWeightingModelParameter.cxx
    vtkTAG2EWeightingModel.cxx
    vtkTAG2ERothCModelParameter.cxx
)

SET (Filtering_H
    vtkTAG2EFilteringWin32Header.h
    vtkTAG2EImageDataN2OFilterFreibauer.h
    vtkTAG2EDataSetN2OFilterFreibauer.h
    vtkTAG2EDataSetN2OFilterStehfest.h
    vtkTAG2EDataSetN2OFilterRoelandt.h
    vtkTAG2EDataSetN2OFilterBouwman.h
    vtkTAG2EAbstractModel.h
    vtkTAG2EAbstractCalibratableModel.h
    vtkTAG2EAbstractModelParameter.h
    vtkTAG2EAbstractModelEstimator.h
    vtkTAG2EAbstractModelCalibrator.h
    vtkTAG2EAbstractModelVariationAnalyser.h
    vtkTAG2EAbstractCalibratableModelParameter.h
    vtkTAG2EFuzzyInferenceModelParameter.h
    vtkTAG2ELinearRegressionModel.h
    vtkTAG2EModelMonteCarloVariationAnalyser.h
    vtkTAG2EFuzzyInferenceModel.h
    vtkTAG2EFuzzyInferenceModelParameterToImageData.h
    vtkTAG2ESimulatedAnnealingModelCalibrator.h
#    vtkTAG2ERSpaceTimeModel.h
    vtkTAG2EWeightingModelParameter.h
    vtkTAG2EWeightingModel.h
    vtkTAG2ERothCModelParameter.h
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
