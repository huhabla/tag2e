#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: r.fuzzy.model
#
# Purpose: Compute a weighted fuzzy inference model based on vector data
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

################################################################################
################################################################################
################################################################################

def main():
    # Initiate GRASS
    init = vtkGRASSInit()
    init.Init("v.fuzzy.model")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Compute a (weighted) fuzzy inference model based on vector data")
    module.AddKeyword("vector")
    module.AddKeyword("fuzzy")

    input = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorInputType())

    feature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorFeatureType())
    feature.SetDefaultOptions("point,centroid,area")
    feature.SetDefaultAnswer("point")
    feature.MultipleOff()
    
    paramXML = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileInputType(), "parameter")
    paramXML.SetDescription("Name of the XML (weighted) fuzzy inference parameter file")

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorOutputType())
    output.SetDescription("The model result")

    weighting = vtkGRASSFlag()
    weighting.SetDescription("Input is weighted fuzzy inference scheme")
    weighting.SetKey('w')

    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1

    messages = vtkGRASSMessagingInterface()

    messages.Message("Reading vector map into memory")
    # Reader
    dataset = vtkGRASSVectorTopoPolyDataReader()
    dataset.SetVectorName(input.GetAnswer())
    if feature.GetAnswer() == "point":
        dataset.SetFeatureTypeToPoint()
    if feature.GetAnswer() == "centroid" or feature.GetAnswer() == "area":
        dataset.SetFeatureTypeToCentroid()
    dataset.Update()

    # Generate the time steps
    timesteps = vtkDoubleArray()
    timesteps.SetNumberOfTuples(1)
    timesteps.SetNumberOfComponents(1)
    timesteps.SetValue(0, 3600*24)

    # Create the spatio-temporal source
    timesource = vtkTemporalDataSetSource()
    timesource.SetTimeRange(0, 3600*24, timesteps)
    timesource.SetInputConnection(0, dataset.GetOutputPort())

    outputTDS = vtkTemporalDataSet()

    if weighting.GetAnswer():

        reader = vtkXMLDataParser()
        reader.SetFileName(paramXML.GetAnswer())
        reader.Parse()

        xmlRoot = vtkXMLDataElement()
        xmlRootFIS = vtkXMLDataElement()
        xmlRootW = vtkXMLDataElement()

        xmlRoot.DeepCopy(reader.GetRootElement())

        if xmlRoot.GetName() != "MetaModel":
            messages.FatalError("Wrong input XML file. Missing MetaModel element.")
            
        xmlRootFIS.DeepCopy(xmlRoot.FindNestedElementWithName("FuzzyInferenceScheme"))

        if xmlRootFIS.GetName() != "FuzzyInferenceScheme":
            messages.FatalError("Wrong input XML file. Missing FuzzyInferenceScheme element.")

        xmlRootW.DeepCopy(xmlRoot.FindNestedElementWithName("Weighting"))

        if xmlRootW.GetName() != "Weighting":
            messages.FatalError("Wrong input XML file. Missing Weighting element.")

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
        modelW.Update()

        outputTDS.ShallowCopy(modelW.GetOutput())

    else:
        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetFileName(paramXML.GetAnswer())
        parameter.Read()

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInputConnection(timesource.GetOutputPort())
        model.SetModelParameter(parameter)
        model.UseCellDataOn()
        model.Update()

        outputTDS.ShallowCopy(model.GetOutput())

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

    messages.Message("Writing result VTK poly data")
    
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
