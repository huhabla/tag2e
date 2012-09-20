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
import math


################################################################################
################################################################################
################################################################################
def MergeFuzzyInferenceSchemes(xmlRootFIS, names, fuzzySetNum, target, polyData, null):
        
    xmlRoot = vtkXMLDataElement()
    messages = vtkGRASSMessagingInterface()
    
    if xmlRootFIS and xmlRootFIS.GetName() == "FuzzyInferenceScheme":
        xmlFIS = XMLFuzzyInferenceGenerator.BuildXML(names, fuzzySetNum, target, polyData, null, True)
        # Save the factor XML elements
        oldElementList = []
        newElementList = []
        
        xmlRoot.DeepCopy(xmlFIS)
        xmlRoot.RemoveAllNestedElements()

        # Count the Factors from the file
        for id in range(xmlRootFIS.GetNumberOfNestedElements()):
            oldElement = xmlRootFIS.GetNestedElement(id)
            if oldElement.GetName() == "Factor":
                oldElementList.append(oldElement)
                
        # Count the generated Factors
        for id in range(xmlFIS.GetNumberOfNestedElements()):
            newElement = xmlFIS.GetNestedElement(id)
            if newElement.GetName() == "Factor":
                newElementList.append(newElement)
                
        # Remove Factors which are present in the init XML file from the generated ones
        for oel in oldElementList:
            for nel in newElementList:
                if oel.GetAttribute("name") == nel.GetAttribute("name"):
                    xmlFIS.RemoveNestedElement(nel)
                    messages.Message("Factor " + nel.GetAttribute("name") + " removed")
        
        # Add the Factors from the init XML file
        for oel in oldElementList:
            xmlRoot.AddNestedElement(oel)
            messages.Message("Factor " + oel.GetAttribute("name") + " added")

        # Add all generated Factors and Responses
        for id in range(xmlFIS.GetNumberOfNestedElements()):
            newElement = xmlFIS.GetNestedElement(id)
            xmlRoot.AddNestedElement(newElement)
            if newElement.GetName() == "Factor":
                messages.Message("Factor " + newElement.GetAttribute("name") + " added")
            else:
                messages.Message(newElement.GetName() + " added")
      
        xmlRootFIS.DeepCopy(xmlRoot)
    else:
        # FIS does not exists, so we create a new one
        xmlRootFIS = XMLFuzzyInferenceGenerator.BuildXML(names, fuzzySetNum, target, polyData, null, True)

    return xmlRootFIS
    
    
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

    initparamXML = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileInputType(), "initparameter")
    initparamXML.RequiredOff()
    initparamXML.SetDescription("The name of the initial XML (weighted) fuzzy inference parameter file, including factors (and weights) which are already calibrated.")

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
    fuzzysets.MultipleOn()
    fuzzysets.RequiredOn()
    fuzzysets.SetDescription("The number of fuzzy sets to be used for calibration for each factor: in case of 4 factors each 2 fuzzy sets: 2,2,2,2")
    fuzzysets.SetTypeToInteger()

    samplingFactor = vtkGRASSOption()
    samplingFactor.SetKey("samplingfactor")
    samplingFactor.MultipleOff()
    samplingFactor.RequiredOff()
    samplingFactor.SetDescription("The name of the column with ids for bootstrap aggregation selection")
    samplingFactor.SetTypeToString()

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
    
    treduce = vtkGRASSOption()
    treduce.SetKey("treduce")
    treduce.MultipleOff()
    treduce.RequiredOff()
    treduce.SetDefaultAnswer("1.01")
    treduce.SetDescription("This factor is used to reduce the annealing temperature each step")
    treduce.SetTypeToDouble()
    
    sdreduce = vtkGRASSOption()
    sdreduce.SetKey("sdreduce")
    sdreduce.MultipleOff()
    sdreduce.RequiredOff()
    sdreduce.SetDefaultAnswer("1.01")
    sdreduce.SetDescription("This factor is used to reduce the standard deviation each step")
    sdreduce.SetTypeToDouble()
    
    rulelimit = vtkGRASSOption()
    rulelimit.SetKey("rulelimit")
    rulelimit.MultipleOff()
    rulelimit.RequiredOff()
    rulelimit.SetDefaultAnswer("2")
    rulelimit.SetDescription("The rule limit specifies the minimum percentage of data that " + \
                             "should be located in a single rule. " + \
                             "This value affect directly the computation of the model assessment factor")
    rulelimit.SetTypeToDouble()
    
    bagging = vtkGRASSFlag()
    bagging.SetDescription("Use boostrap aggregation (bagging) for input data selection")
    bagging.SetKey('b')

    weighting = vtkGRASSFlag()
    weighting.SetDescription("Use weighting for input data calibration. A weightingfactor and the number of weights must be provided.")
    weighting.SetKey('w')

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorOutputType())
    output.RequiredOff()
    output.SetDescription("The best fitted model result as vector map")

    paramXML = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "parameter")
    paramXML.SetDescription("Output name of the calibrated XML (weighted) fuzzy inference parameter file")

    logfile = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "log")
    logfile.SetDescription("The name of the logfile to store the model error and AKAIKE criteria")

    outputvtk = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "vtkoutput")
    outputvtk.RequiredOff()
    outputvtk.SetDescription("The file name of the best fitted model result exported as VTK XML poly data output (.vtp)")

    fuzzyvtk = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "fuzzyvtk")
    fuzzyvtk.RequiredOff()
    fuzzyvtk.SetDescription("The file name of the best fitted fuzzy model exported as VTK XML image data output (.vti)")

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

    setnums = vtkStringArray()
    fuzzysets.GetAnswers(setnums)

    names = []
    for i in range(columns.GetNumberOfValues()):
        names.append(columns.GetValue(i))

    fuzzySetNum = []
    for i in range(setnums.GetNumberOfValues()):
        fuzzySetNum.append(int(setnums.GetValue(i)))

    if columns.GetNumberOfValues() != setnums.GetNumberOfValues():
        messages.FatalError("The number of factors must match the number of fuzzysets: factors=a,b,c fuzzysets=3,2,3")
    
    columns.InsertNextValue(target.GetAnswer())
 
    if samplingFactor.GetAnswer():
        columns.InsertNextValue(samplingFactor.GetAnswer())
   
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
        if samplingFactor.GetAnswer():
            polyData.ShallowCopy(BootstrapAggregating.CellSampling(reader.GetOutput(), samplingFactor.GetAnswer()))
        else:
            polyData.ShallowCopy(BootstrapAggregating.CellSampling(reader.GetOutput()))
    else:
        polyData.ShallowCopy(reader.GetOutput())

    # Set the active scalar array to target variable. The calibration algorithm
    # compares the active scalars to compute the best fit
    polyData.GetCellData().SetActiveScalars(target.GetAnswer())

    # In case an initial FIS or WFIS XML file is provided, add only the new factors
    # to the XML representation
    if initparamXML.GetAnswer():
        # Read the XML file
        reader = vtkXMLDataParser()
        reader.SetFileName(initparamXML.GetAnswer())
        reader.Parse()

        xmlRootFIS = vtkXMLDataElement()
        xmlRootW = vtkXMLDataElement()
        
        # in case weighting should be used, the meta model is required 
        if weighting.GetAnswer():        

            xmlRoot = vtkXMLDataElement()
            xmlRoot.DeepCopy(reader.GetRootElement())
            
            if xmlRoot.GetName() != "MetaModel":
                messages.FatalError("Wrong input XML file. Missing MetaModel element.")

            if xmlRoot.FindNestedElementWithName("FuzzyInferenceScheme"):
                xmlRootFIS.DeepCopy(xmlRoot.FindNestedElementWithName("FuzzyInferenceScheme"))
            else:
                xmlRootFIS = None

            # In case the FIS exists, add only the factors which are not already present
            xmlRootFIS = MergeFuzzyInferenceSchemes(xmlRootFIS, names, fuzzySetNum, target.GetAnswer(), polyData, float(null.GetAnswer()))

            if xmlRoot.FindNestedElementWithName("Weighting"):
                xmlRootW.DeepCopy(xmlRoot.FindNestedElementWithName("Weighting"))
            else:
                xmlRootW = None

            if xmlRootW and xmlRootW.GetName() == "Weighting":
                pass
            else:
                 xmlRootW = XMLWeightingGenerator.BuildXML(weightingFactor.GetAnswer(), int(weightNum.GetAnswer()), 0, 10)

            pass
        else:
            xmlRootFIS.DeepCopy(reader.GetRootElement())
            # In case the FIS exists, add only the factors which are not already present
            xmlRootFIS = MergeFuzzyInferenceSchemes(xmlRootFIS, names, fuzzySetNum, target.GetAnswer(), polyData, float(null.GetAnswer()))
    else:
        # Create the XML stuff in case no pinitial parameter is given
        xmlRootFIS = XMLFuzzyInferenceGenerator.BuildXML(names, fuzzySetNum, target.GetAnswer(), polyData, float(null.GetAnswer()), True)
 
        if weighting.GetAnswer():
            xmlRootW = XMLWeightingGenerator.BuildXML(weightingFactor.GetAnswer(), int(weightNum.GetAnswer()), 0, 10)

    # xmlRootFIS.PrintXML("xmlRootFIS.xml")
   
    # The output dataset
    outputDS = vtkPolyData()
    
    bestFitError = 999999
    AKAIKE = 999999 
    NumberOfModelParameter = 0
    ModelAssessmentFactor = 0

    if weighting.GetAnswer():

        # xmlRootW.PrintXML("xmlRootW.xml")
        
        # Set up the parameter and the model of the meta model
        parameterFIS = vtkTAG2EFuzzyInferenceModelParameter()
        parameterFIS.SetXMLRepresentation(xmlRootFIS)
        parameterFIS.DebugOff()
        
        NumberOfModelParameter = parameterFIS.GetNumberOfCalibratableParameter()

        modelFIS = vtkTAG2EFuzzyInferenceModel()
        modelFIS.SetInput(polyData)
        modelFIS.SetModelParameter(parameterFIS)
        modelFIS.SetApplicabilityRuleLimit(float(rulelimit.GetAnswer()))
        modelFIS.UseCellDataOn()

        parameterW = vtkTAG2EWeightingModelParameter()
        parameterW.SetXMLRepresentation(xmlRootW)
        parameterW.DebugOff()
        
        NumberOfModelParameter = NumberOfModelParameter + parameterW.GetNumberOfCalibratableParameter()
        
        modelW = vtkTAG2EWeightingModel()
        modelW.SetInputConnection(modelFIS.GetOutputPort())
        modelW.SetModelParameter(parameterW)
        modelW.UseCellDataOn()

        meta = MetaModel.MetaModel()
        meta.InsertModelParameter(modelFIS, parameterFIS, "vtkTAG2EFuzzyInferenceModel")
        meta.InsertModelParameter(modelW, parameterW, "vtkTAG2EWeightingModel")
        meta.SetLastModelParameterInPipeline(modelW, parameterW, "vtkTAG2EWeightingModel")
        meta.SetTargetDataSet(polyData)

        bestFitParameter, bestFitOutput, bestFitError, ModelAssessmentFactor = \
                                           Calibration.MetaModelSimulatedAnnealingImproved(\
                                           meta, int(iterations.GetAnswer()),\
                                           1, float(sd.GetAnswer()),
                                           float(breakcrit.GetAnswer()), float(treduce.GetAnswer()),\
                                           float(sdreduce.GetAnswer()))

        bestFitParameter.PrintXML(paramXML.GetAnswer())
        
        outputDS.ShallowCopy(bestFitOutput)

    else:
        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetXMLRepresentation(xmlRootFIS)
        
        NumberOfModelParameter = parameter.GetNumberOfCalibratableParameter()

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInput(polyData)
        model.SetModelParameter(parameter)
        model.SetApplicabilityRuleLimit(float(rulelimit.GetAnswer()))
        model.UseCellDataOn()

        caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
        caliModel.SetInput(polyData)
        caliModel.SetModel(model)
        caliModel.SetModelParameter(parameter)
        caliModel.SetMaxNumberOfIterations(int(iterations.GetAnswer()))
        caliModel.SetInitialT(1)
        caliModel.SetTMinimizer(float(treduce.GetAnswer()))
        caliModel.SetStandardDeviation(float(sd.GetAnswer()))
        caliModel.SetBreakCriteria(float(breakcrit.GetAnswer()))
        caliModel.Update()

        caliModel.GetBestFitModelParameter().SetFileName(paramXML.GetAnswer())
        caliModel.GetBestFitModelParameter().Write()
        
        bestFitError = caliModel.GetBestFitError()
        
        ModelAssessmentFactor = caliModel.GetBestFitModelAssessmentFactor()

        outputDS.ShallowCopy(caliModel.GetOutput())

    
    if output.GetAnswer():
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
        
    # Compute the AKAIKE criteria
    residuals = vtkDoubleArray()
    vtkTAG2EAbstractModelCalibrator.ComputeDataSetsResiduals(polyData, outputDS, 1, residuals)
                
    vresiduals = vtkTAG2EAbstractModelCalibrator.Variance(residuals)
    
    AKAIKE = 2 * NumberOfModelParameter + residuals.GetNumberOfTuples() * math.log(residuals.GetNumberOfTuples() * vresiduals)
    # We use the model assessment factor to fit the akaike criteria
    AKAIKE = AKAIKE * ModelAssessmentFactor
    
    # Write the logfile
    log = open(logfile.GetAnswer(), "w")
    log.write(str(bestFitError))
    log.write(str("\n"))
    log.write(str(AKAIKE))
    log.write(str("\n"))
    log.write(str(ModelAssessmentFactor))
    log.close()
    
    # Create the poly data output for paraview analysis
    if outputvtk.GetAnswer():
        messages.Message("Writing result VTK poly data")
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName(outputvtk.GetAnswer() + ".vtp")
        pwriter.SetInput(outputDS)
        pwriter.Write()
    
    # Create the poly data output for paraview analysis
    if fuzzyvtk.GetAnswer() and not weighting.GetAnswer():
        messages.Message("Writing Fuzzy Inference Scheme XML represenation as VTK image data")
        
        fim = vtkTAG2EFuzzyInferenceModelParameterToImageData()
        fim.SetFuzzyModelParameter(parameter)
        fim.SetXAxisExtent(50)
        fim.SetYAxisExtent(50)
        fim.SetZAxisExtent(50)
        fim.Update()
        
        iwriter = vtkXMLImageDataWriter()
        iwriter.SetFileName(fuzzyvtk.GetAnswer() + ".vti")
        iwriter.SetInput(fim.GetOutput())
        iwriter.Write()
    
    messages.Message("Finished calibration with best fit " + str(bestFitError) + \
                     " and AKAIKE criteria " + str(AKAIKE))

################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()
