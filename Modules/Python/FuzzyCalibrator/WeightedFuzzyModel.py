#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
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
from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeTemporalPython import *
from libvtkGRASSBridgeCommonPython import *

import CSVDataReader

################################################################################
################################################################################
################################################################################
  
class WeightedFuzzyModel():
    
    def __init__(self):
        self.inputFile = "FuzzyCalibrationData.txt"
        self.resultFile = "Model.vtp"
        self.factorNames = ["sand", "Paut", "Twin", "fertN"]
        self.targetArrayName = "n2o"
        self.parameterFile = "BestFit.xml"

    def Run(self):
        
        self.dataset, self.timesource = CSVDataReader.ReadTextData(self.inputFile, self.targetArrayName, False)

        reader = vtkXMLDataParser()
        reader.SetFileName(self.parameterFile)
        reader.Parse()

        xmlRoot = vtkXMLDataElement()
        xmlRootFIS = vtkXMLDataElement()
        xmlRootW = vtkXMLDataElement()

        xmlRoot.DeepCopy(reader.GetRootElement())

        if xmlRoot.GetName() != "MetaModel":
            print "Wrong input XML file. Missing MetaModel element."
            return 1

        xmlRootFIS.DeepCopy(xmlRoot.FindNestedElementWithName("FuzzyInferenceScheme"))

        if xmlRootFIS.GetName() != "FuzzyInferenceScheme":
            print "Wrong input XML file. Missing FuzzyInferenceScheme element."
            return 1

        xmlRootW.DeepCopy(xmlRoot.FindNestedElementWithName("Weighting"))

        if xmlRootW.GetName() != "Weighting":
            print "Wrong input XML file. Missing Weighting element."
            return 1

        # Set up the parameter and the model
        parameterFIS = vtkTAG2EFuzzyInferenceModelParameter()
        parameterFIS.SetXMLRepresentation(xmlRootFIS)
            
        modelFIS = vtkTAG2EFuzzyInferenceModel()
        modelFIS.SetInputConnection(self.timesource.GetOutputPort())
        modelFIS.SetModelParameter(parameterFIS)
        modelFIS.UseCellDataOn()
        
        parameterW = vtkTAG2EWeightingModelParameter()
        parameterW.SetXMLRepresentation(xmlRootW)
            
        modelW = vtkTAG2EWeightingModel()
        modelW.SetInputConnection(modelFIS.GetOutputPort())
        modelW.SetModelParameter(parameterW)
        modelW.UseCellDataOn()
        modelW.Update()

        Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(modelW.GetOutput(), self.timesource.GetOutput(), modelW.GetUseCellData(), 0)
        print "Finished with error", Error

        writer = vtkXMLPolyDataWriter()
        writer.SetFileName(self.resultFile)
        writer.SetInput(modelW.GetOutput().GetTimeStep(0))
        writer.Write()
        
if __name__ == "__main__":
    model = WeightedFuzzyModel()
    model.inputFile = "FuzzyCalibrationData.txt"
    model.resultFile = "Model.vtp"
    model.factorNames = ["sand", "Paut", "Twin", "fertN"]
    model.targetArrayName = "n2o"
    model.parameterFile = "BestFit.xml"
    model.Run()
