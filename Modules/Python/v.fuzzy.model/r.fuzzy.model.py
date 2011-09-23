#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: r.fuzzy.model
#
# Purpose: Compute a weighted fuzzy inference model based on raster data
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
    init.Init("r.fuzzy.model")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Compute a (weighted) fuzzy inference model based on vector data")
    module.AddKeyword("raster")
    module.AddKeyword("fuzzy")

    input = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputsType())
    
    paramXML = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileInputType(), "parameter")
    paramXML.SetDescription("Name of the XML (weighted) fuzzy inference parameter file")

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    output.SetDescription("The model result")

    weighting = vtkGRASSFlag()
    weighting.SetDescription("Input is weighted fuzzy inference scheme")
    weighting.SetKey('w')

    vtkout = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "vtkout")
    vtkout.RequiredOff()
    vtkout.SetDescription("The file name of the best fitted model result exported as VTK image data output (.vtk)")

    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1

    messages = vtkGRASSMessagingInterface()

    messages.Message("Reading raster map into memory")
    
    raster_maps = vtkStringArray()
    input.GetAnswers(raster_maps)
    
    dataset = vtkImageData()
    
    # Read all raster maps into memory
    for count in range(raster_maps.GetNumberOfValues()):
        map_name = raster_maps.GetValue(count)
        map = vtkGRASSRasterImageReader()
        map.SetRasterName(map_name)
        map.UseCurrentRegion()
        map.SetNullValue(9999)
        map.UseNullValueOn()
        map.ReadMapAsDouble()
        map.Update()
        map.GetOutput().GetPointData().GetScalars().SetName(map_name)

        if count == 0:
            dataset.DeepCopy(map.GetOutput())
        else:
            dataset.GetPointData().AddArray(map.GetOutput().GetPointData().GetScalars())

    # Generate the time steps
    timesteps = vtkDoubleArray()
    timesteps.SetNumberOfTuples(1)
    timesteps.SetNumberOfComponents(1)
    timesteps.SetValue(0, 3600*24)

    # Create the spatio-temporal source
    timesource = vtkTemporalDataSetSource()
    timesource.SetTimeRange(0, 3600*24, timesteps)
    timesource.SetInput(0, dataset)

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
        modelFIS.UseCellDataOff()

        parameterW = vtkTAG2EWeightingModelParameter()
        parameterW.SetXMLRepresentation(xmlRootW)
        parameterW.DebugOff()

        modelW = vtkTAG2EWeightingModel()
        modelW.SetInputConnection(modelFIS.GetOutputPort())
        modelW.SetModelParameter(parameterW)
        modelW.UseCellDataOff()
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
        model.UseCellDataOff()
        model.Update()

        outputTDS.ShallowCopy(model.GetOutput())

    messages.Message("Writing first result raster map")

    # Write the result as vector map
    writer = vtkGRASSRasterImageWriter()
    writer.SetInput(outputTDS.GetTimeStep(0))
    writer.SetRasterName(output.GetAnswer())
    writer.Update()

    messages.Message("Writing result VTK poly data")
    
    # Create the poly data output for paraview analysis
    if vtkout.GetAnswer():
        pwriter = vtkXMLImageDataWriter()
        pwriter.SetFileName(vtkout.GetAnswer() + ".vti")
        pwriter.SetInput(outputTDS.GetTimeStep(0))
        pwriter.Write()
    
################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()
