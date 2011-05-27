#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: r.fuzzy.calibrator
#
# Purpose: Calibrate a (weighted) fuzzy inference model parameter based on vector data
#
# Authors: Soeren Gebbert, soeren.gebbert@vti.bund.de
#          Rene Dechow, rene.dechow@vti.bund.de
#
# Copyright:
#
# Johann Heinrich von Thuenen-Institut
# Institut fuer Agrarrelevante Klimaforschung
#
# Phone: +49 (0)531 596 2601
#
# Fax:+49 (0)531 596 2699
#
# Mail: ak@vti.bund.de
#
# Bundesallee 50
# 38116 Braunschweig
# Germany
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import sys

#include the VTK and vtkGRASSBridge Python libraries
from vtk import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *
from libvtkGRASSBridgeTemporalPython import *

import XMLWeightingGenerator
import XMLFuzzyInferenceGenerator
import BootstrapAggregating
import MetaModel
import Calibration

################################################################################
################################################################################
################################################################################

def main():
    # Initiate GRASS
    init = vtkGRASSInit()
    init.Init("v.fuzzy.calibrator")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Calibrate a fuzzy inference model parameter based on vector data")
    module.AddKeyword("vector")

    input = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorInputType())

    feature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorFeatureType())
    feature.SetDefaultOptions("point,centroid,area")
    feature.SetDefaultAnswer("point")
    feature.MultipleOff()
    
    factors = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "factors")
    factors.SetDescription("Names of the table columns of the fuzzy factors")

    target = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "target")
    target.SetDescription("Name of the table column of the target variable")

    weightingFactor = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "weightfactor")
    weightingFactor.SetDescription("Name of the table column of the weighting variable")
    weightingFactor.RequiredOff()

    iterations = vtkGRASSOption()
    iterations.SetKey("iterations")
    iterations.MultipleOff()
    iterations.RequiredOff()
    iterations.SetDefaultAnswer("5000")
    iterations.SetDescription("The maximum number of iterations")
    iterations.SetTypeToInteger()

    fuzzysets = vtkGRASSOption()
    fuzzysets.SetKey("fuzzysets")
    fuzzysets.MultipleOff()
    fuzzysets.RequiredOff()
    fuzzysets.SetDefaultAnswer("3")
    fuzzysets.SetDefaultOptions("2,3,4,5")
    fuzzysets.SetDescription("The number of fuzzy sets to be used for calibration")
    fuzzysets.SetTypeToInteger()

    sd = vtkGRASSOption()
    sd.SetKey("sd")
    sd.MultipleOff()
    sd.RequiredOff()
    sd.SetDefaultAnswer("1")
    sd.SetDescription("The standard deviation used to modify the fuzzy inference model")
    sd.SetTypeToDouble()

    breakcrit = vtkGRASSOption()
    breakcrit.SetKey("breakcrit")
    breakcrit.MultipleOff()
    breakcrit.RequiredOff()
    breakcrit.SetDefaultAnswer("0.01")
    breakcrit.SetDescription("The break criteria")
    breakcrit.SetTypeToDouble()

    weightNum = vtkGRASSOption()
    weightNum.SetKey("weightnum")
    weightNum.MultipleOff()
    weightNum.RequiredOff()
    weightNum.SetDefaultAnswer("6")
    weightNum.SetDescription("The number of weights used for calibration")
    weightNum.SetTypeToInteger()

    null = vtkGRASSOption()
    null.SetKey("null")
    null.MultipleOff()
    null.RequiredOff()
    null.SetDefaultAnswer("9999")
    null.SetDescription("The value used fo no data")
    null.SetTypeToDouble()

    bagging = vtkGRASSFlag()
    bagging.SetDescription("Use bagging for input data selection")
    bagging.SetKey('b')

    weighting = vtkGRASSFlag()
    weighting.SetDescription("Use weighting for input data calibration")
    weighting.SetKey('w')

    paramXML = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "parameter")
    paramXML.SetDescription("Output name of the calibrated XML (weighted) fuzzy inference parameter file")

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorOutputType())
    output.SetDescription("The best fitted model result as vector map and VTK XML poly data output (.vtp added)")

    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1

    messages = vtkGRASSMessagingInterface()

    # Check for weighting support
    if weighting.GetAnswer() == True:
        if not weightingFactor.GetAnswer():
            messages.FatalError("The name of the weighting column name must be provided")

    # Create the names for the vector import and the (weighted) fuzzy inference scheme generation
    columns = vtkStringArray()
    factors.GetAnswers(columns)

    names = []
    for i in range(columns.GetNumberOfValues()):
        names.append(columns.GetValue(i))

    columns.InsertNextValue(target.GetAnswer())
    
    if weighting.GetAnswer() == True:
        columns.InsertNextValue(weightingFactor.GetAnswer())

    messages.Message("Reading vector map into memory")
    
    # Reader
    reader = vtkGRASSVectorTopoPolyDataReader()
    reader.SetVectorName(input.GetAnswer())
    reader.SetColumnNames(columns)
    if feature.GetAnswer() == "point":
        reader.SetFeatureTypeToPoint()
    if feature.GetAnswer() == "centroid" or feature.GetAnswer() == "area":
        reader.SetFeatureTypeToCentroid()
    reader.Update()

    polyData = vtkPolyData()
    
    if bagging.GetAnswer() == True:
        polyData.ShallowCopy(BootstrapAggregating.CellSampling(reader.GetOutput()))
    else:
        polyData.ShallowCopy(reader.GetOutput())

    # Set the active scalar array to target variable. The calibration algorithm
    # compares the active scalars to compute the best fit
    polyData.GetCellData().SetActiveScalars(target.GetAnswer())

    # Generate the time steps
    timesteps = vtkDoubleArray()
    timesteps.SetNumberOfTuples(1)
    timesteps.SetNumberOfComponents(1)
    timesteps.SetValue(0, 3600*24)

    # Create the spatio-temporal source
    timesource = vtkTemporalDataSetSource()
    timesource.SetTimeRange(0, 3600*24, timesteps)
    timesource.SetInput(0, polyData)

    type = int(fuzzysets.GetAnswer())

    if type == 2:
        xmlRootFIS = XMLFuzzyInferenceGenerator.BuildXML2(names, target.GetAnswer(), polyData, float(null.GetAnswer()), True)
    if type == 3:
        xmlRootFIS = XMLFuzzyInferenceGenerator.BuildXML3(names, target.GetAnswer(), polyData, float(null.GetAnswer()), True)
    if type == 4:
        xmlRootFIS = XMLFuzzyInferenceGenerator.BuildXML4(names, target.GetAnswer(), polyData, float(null.GetAnswer()), True)
    if type == 5:
        xmlRootFIS = XMLFuzzyInferenceGenerator.BuildXML5(names, target.GetAnswer(), polyData, float(null.GetAnswer()), True)

    outputTDS = vtkTemporalDataSet()

    if weighting.GetAnswer():

        xmlRootW = XMLWeightingGenerator.BuildXML(weightingFactor.GetAnswer(), int(weightNum.GetAnswer()), 0, 10)

        # Set up the parameter and the model of the meta model
        parameterFIS = vtkTAG2EFuzzyInferenceModelParameter()
        parameterFIS.SetXMLRepresentation(xmlRootFIS)
        parameterFIS.DebugOff()

        modelFIS = vtkTAG2EFuzzyInferenceModel()
        modelFIS.SetInputConnection(timesource.GetOutputPort())
        modelFIS.SetModelParameter(parameterFIS)
        modelFIS.UseCellDataOn()

        parameterW = vtkTAG2EWeightingModelParameter()
        parameterW.SetXMLRepresentation(xmlRootW)
        parameterW.DebugOff()

        modelW = vtkTAG2EWeightingModel()
        modelW.SetInputConnection(modelFIS.GetOutputPort())
        modelW.SetModelParameter(parameterW)
        modelW.UseCellDataOn()

        meta = MetaModel.MetaModel()
        meta.InsertModelParameter(modelFIS, parameterFIS, "vtkTAG2EFuzzyInferenceModel")
        meta.InsertModelParameter(modelW, parameterW, "vtkTAG2EWeightingModel")
        meta.SetLastModelParameterInPipeline(modelW, parameterW, "vtkTAG2EWeightingModel")
        meta.SetTargetDataSet(timesource.GetOutput())

        bestFitParameter, bestFitOutput, = Calibration.MetaModelSimulatedAnnealingImproved(
                                           meta, int(iterations.GetAnswer()),\
                                           1, float(sd.GetAnswer()),
                                           float(breakcrit.GetAnswer()), 1.001,\
                                           1.001)

        bestFitParameter.PrintXML(paramXML.GetAnswer())

        outputTDS.ShallowCopy(bestFitOutput)

    else:
        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetXMLRepresentation(xmlRootFIS)

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInputConnection(timesource.GetOutputPort())
        model.SetModelParameter(parameter)
        model.UseCellDataOn()

        caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
        caliModel.SetInputConnection(timesource.GetOutputPort())
        caliModel.SetModel(model)
        caliModel.SetModelParameter(parameter)
        caliModel.SetMaxNumberOfIterations(int(iterations.GetAnswer()))
        caliModel.SetInitialT(1)
        caliModel.SetTMinimizer(1.001)
        caliModel.SetStandardDeviation(float(sd.GetAnswer()))
        caliModel.SetBreakCriteria(float(breakcrit.GetAnswer()))
        caliModel.Update()

        caliModel.GetBestFitModelParameter().SetFileName(paramXML.GetAnswer())
        caliModel.GetBestFitModelParameter().Write()

        outputTDS.ShallowCopy(caliModel.GetOutput())

    messages.Message("Writing result vector map")
    
    # Areas must be treated in a specific way to garant correct topology
    if feature.GetAnswer() == "area":
        columns = vtkStringArray()
        columns.InsertNextValue("cat")
        # Read the centroids
        boundaries = vtkGRASSVectorTopoPolyDataReader()
        boundaries.SetVectorName(input.GetAnswer())
        boundaries.SetColumnNames(columns)
        boundaries.SetFeatureTypeToBoundary()
        boundaries.Update()
        
        writer = vtkGRASSVectorPolyDataAreaWriter()
        writer.SetInput(0, boundaries.GetOutput())
        writer.SetInput(1, outputTDS.GetTimeStep(0))
        writer.SetVectorName(output.GetAnswer())
        writer.BuildTopoOn()
        writer.Update()     
    else:
        # Write the result as vector map
        writer = vtkGRASSVectorPolyDataWriter()
        writer.SetInput(outputTDS.GetTimeStep(0))
        writer.SetVectorName(output.GetAnswer())
        writer.BuildTopoOn()
        writer.Update()
        
    # Create the poly data output for paraview analysis
    pwriter = vtkXMLPolyDataWriter()
    pwriter.SetFileName(output.GetAnswer() + ".vtp")
    pwriter.SetInput(outputTDS.GetTimeStep(0))
    pwriter.Write()

################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()
