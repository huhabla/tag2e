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
import math

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
    init.Init("v.fuzzy.model")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Compute a (weighted) fuzzy inference model based on vector data")
    module.AddKeyword("vector")
    module.AddKeyword("fuzzy")

    input = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorInputType())
    
    mcol = vtkGRASSOption()
    mcol.SetKey("mcol")
    mcol.SetDescription("The column name with measurements")
    mcol.RequiredOff()

    feature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorFeatureType())
    feature.SetDefaultOptions("point,centroid,area")
    feature.SetDefaultAnswer("point")
    feature.MultipleOff()
    
    paramXML = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileInputType(), "parameter")
    paramXML.SetDescription("Name of the XML (weighted) fuzzy inference parameter file")
 
    sigparamXML = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "sigparameter")
    sigparamXML.SetDescription("Compute the rule specific sigma and store it in this xml file")
    sigparamXML.RequiredOff()

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorOutputType())
    output.SetDescription("The model result")

    sigma = vtkGRASSFlag()
    sigma.SetDescription("Compute the rule specific sigma.")
    sigma.SetKey('s')

    weighting = vtkGRASSFlag()
    weighting.SetDescription("Input is weighted fuzzy inference scheme")
    weighting.SetKey('w')

    vtkout = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "vtkout")
    vtkout.RequiredOff()
    vtkout.SetDescription("The file name of the best fitted model result exported as VTK poly data output (.vtp is added automatically)")

    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1

    messages = vtkGRASSMessagingInterface()

    if sigparamXML.GetAnswer() and not mcol.GetAnswer():
        messages.FatalError("You need to specifiy the measument column name of the input vector map")

    messages.Message("Reading vector map into memory")
    # Reader
    dataset = vtkGRASSVectorTopoPolyDataReader()
    dataset.SetVectorName(input.GetAnswer())
    if feature.GetAnswer() == "point":
        dataset.SetFeatureTypeToPoint()
    if feature.GetAnswer() == "centroid" or feature.GetAnswer() == "area":
        dataset.SetFeatureTypeToCentroid()
    dataset.Update()

    outputDS = vtkPolyData()

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
        modelFIS.SetInputConnection(dataset.GetOutputPort())
        modelFIS.SetModelParameter(parameterFIS)
        if sigma.GetAnswer():
            modelFIS.ComputeSigmaOn()
        if sigparamXML.GetAnswer():
            modelFIS.CreateDOFArrayOn()
        modelFIS.UseCellDataOn()

        parameterW = vtkTAG2EWeightingModelParameter()
        parameterW.SetXMLRepresentation(xmlRootW)
        parameterW.DebugOff()

        modelW = vtkTAG2EWeightingModel()
        modelW.SetInputConnection(modelFIS.GetOutputPort())
        modelW.SetModelParameter(parameterW)
        modelW.UseCellDataOn()
        modelW.Update()

        outputDS.ShallowCopy(modelW.GetOutput())

    else:
        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetFileName(paramXML.GetAnswer())
        parameter.Read()

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInputConnection(dataset.GetOutputPort())
        model.SetModelParameter(parameter)
        if sigma.GetAnswer():
            model.ComputeSigmaOn()
        if sigparamXML.GetAnswer():
            model.CreateDOFArrayOn()
        model.UseCellDataOn()
        model.Update()

        outputDS.ShallowCopy(model.GetOutput())

    # Compute the rule specific standard deviation
    if sigparamXML.GetAnswer():
        numRules = parameter.GetNumberOfRules()
        numCells = outputDS.GetNumberOfCells()
        dofDev = [0]*numRules
        dof = [0]*numRules
        sig = [0]*numRules
        values = [0]*numRules

        inputArray = dataset.GetOutput().GetCellData().GetArray(mcol.GetAnswer())
        modelArray = outputDS.GetCellData().GetArray(model.GetResultArrayName())

        dofArray = outputDS.GetCellData().GetArray("DOF")
        for id in xrange(numCells):

            m = inputArray.GetTuple1(id)
            i = modelArray.GetTuple1(id)

            dev = (m - i)*(m - i)
            dofArray.GetTupleValue(id, values)

            for rule in xrange(numRules):
                dofDev[rule] += values[rule] * dev
                dof[rule] += values[rule]

        for rule in xrange(numRules):
            sig[rule] = math.sqrt(dofDev[rule] / dof[rule])
            print "Rule %i has a standard deviation of %.5f"%(rule, sig[rule])

        p = vtkTAG2EFuzzyInferenceModelParameter()
        p.SetFileName(paramXML.GetAnswer())
        p.Read()

        # Lets create the output XML representation
        paramXML = vtkXMLDataElement()
        p.GetXMLRepresentation(paramXML)

        responses = paramXML.FindNestedElementWithName("Responses")
        for rule in xrange(numRules):
            response = responses.GetNestedElement(rule)
            response.SetDoubleAttribute("sd", sig[rule])

        p.SetXMLRepresentation(paramXML)
        p.SetFileName(sigparamXML.GetAnswer())
        p.Write()

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
        writer.SetInput(1, outputDS)
        writer.SetVectorName(output.GetAnswer())
        writer.BuildTopoOn()
        writer.Update()     
    else:
        # Write the result as vector map
        writer = vtkGRASSVectorPolyDataWriter()
        writer.SetInput(outputDS)
        writer.SetVectorName(output.GetAnswer())
        writer.BuildTopoOn()
        writer.Update()

    messages.Message("Writing result VTK poly data")
    
    # Create the poly data output for paraview analysis
    if vtkout.GetAnswer():
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName(vtkout.GetAnswer() + ".vtp")
        pwriter.SetInput(outputDS)
        pwriter.Write()
    
################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()
