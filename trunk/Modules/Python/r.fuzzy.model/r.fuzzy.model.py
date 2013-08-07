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

    alias = vtkGRASSOption()
    alias.SetKey("alias")
    alias.SetDescription("Alias name of the input raster maps in the XML fuzzy inference scheme file")
    alias.RequiredOff()
    alias.MultipleOn()
    alias.SetTypeToString()
    
    paramXML = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileInputType(), "parameter")
    paramXML.SetDescription("Name of the XML (weighted) fuzzy inference parameter file")

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    output.SetDescription("The model result")

    sd = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    sd.SetDescription("Compute the cell specific standard deviation based on the rule standard deviation specified in the XML input file")
    sd.RequiredOff()
    sd.SetKey('sd')

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

    messages.VerboseMessage("Reading raster maps into memory")
    
    raster_maps = vtkStringArray()
    input.GetAnswers(raster_maps)
     
    raster_alias = vtkStringArray()
    alias.GetAnswers(raster_alias)
    
    if raster_alias.GetNumberOfValues() > 0 and raster_alias.GetNumberOfValues() != raster_maps.GetNumberOfValues():
        messages.FatalError("The number of inputs and alias must be equal")
    
    # Use raster map names in case no alias is provided
    if raster_alias.GetNumberOfValues() == 0:
        input.GetAnswers(raster_alias)

    dataset = vtkImageData()
    nullValue = -999999
    
    # Read all raster maps into memory
    for count in range(raster_maps.GetNumberOfValues()):
        map_name = raster_maps.GetValue(count)
        alias_name = raster_alias.GetValue(count)
        map = vtkGRASSRasterImageReader()
        map.SetRasterName(map_name)
        map.UseCurrentRegion()
        map.SetNullValue(nullValue)
        map.UseNullValueOn()
        map.ReadMapAsDouble()
        map.Update()
        map.GetOutput().GetPointData().GetScalars().SetName(alias_name)

        if count == 0:
            dataset.DeepCopy(map.GetOutput())
        else:
            dataset.GetPointData().AddArray(map.GetOutput().GetPointData().GetScalars())

    outputDS = vtkImageData()

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
        modelFIS.SetInput(dataset)
        modelFIS.SetModelParameter(parameterFIS)
        modelFIS.UseCellDataOff()
        if sd.GetAnswer():
            modelFIS.ComputeSigmaOn()
        modelFIS.SetNullValue(nullValue)

        parameterW = vtkTAG2EWeightingModelParameter()
        parameterW.SetXMLRepresentation(xmlRootW)
        parameterW.DebugOff()

        modelW = vtkTAG2EWeightingModel()
        modelW.SetInputConnection(modelFIS.GetOutputPort())
        modelW.SetModelParameter(parameterW)
        modelW.UseCellDataOff()
        modelW.SetNullValue(nullValue)
        modelW.Update()

        outputDS.ShallowCopy(modelW.GetOutput())

    else:
        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetFileName(paramXML.GetAnswer())
        parameter.Read()

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInput(dataset)
        model.SetModelParameter(parameter)
        model.UseCellDataOff()
        if sd.GetAnswer():
            model.ComputeSigmaOn()
        model.SetNullValue(nullValue)
        model.Update()

        outputDS.ShallowCopy(model.GetOutput())

    messages.VerboseMessage("Writing first result raster map")

    # Write the result as image maps
    writer = vtkGRASSRasterImageWriter()
    writer.SetInput(outputDS)
    writer.SetRasterName(output.GetAnswer())
    writer.SetNullValue(nullValue)
    writer.Update()
 
    # Write the standard deviation as image maps
    if sd.GetAnswer():
        outputDS.GetPointData().SetActiveScalars("Sigma")
        writer = vtkGRASSRasterImageWriter()
        writer.SetInput(outputDS)
        writer.SetRasterName(sd.GetAnswer())
        writer.SetNullValue(nullValue)
        writer.Update()
       
    # Create the image data output for paraview analysis
    if vtkout.GetAnswer():
        messages.Message("Writing result VTK image data")
        pwriter = vtkXMLImageDataWriter()
        pwriter.SetFileName(vtkout.GetAnswer() + ".vti")
        pwriter.SetInput(outputDS)
        pwriter.Write()
    
################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()
