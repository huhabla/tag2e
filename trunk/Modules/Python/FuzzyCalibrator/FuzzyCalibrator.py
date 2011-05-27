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

import XMLFuzzyInferenceGenerator
import MetropolisAlgorithm
import CSVDataReader

################################################################################
################################################################################
################################################################################
  
class FuzzyCalibrator():
    
    def __init__(self):
        self.inputFile = "FuzzyCalibrationData.txt"
        self.factorNames = ["sand", "Paut", "Twin", "fertN"]
        self.targetArrayName = "n2o"
        self.maxNumberOfIterations = 1000
        self.initialT = 1
        self.breakCriteria = 0.01
        self.outputName = "BestFit.xml"
        self.noData = 9999
        self.standardDeviation = 2
        self.TMinimizer = 1.005

    def Run(self, type):
        
        self.dataset, self.timesource = CSVDataReader.ReadTextData(self.inputFile, self.targetArrayName)
        
        if type == 2:
            xmlRoot = XMLFuzzyInferenceGenerator.BuildXML2(self.factorNames, self.targetArrayName, self.dataset, self.noData, True)
        if type == 3:
            xmlRoot = XMLFuzzyInferenceGenerator.BuildXML3(self.factorNames, self.targetArrayName, self.dataset, self.noData, True)
        if type == 4:
            xmlRoot = XMLFuzzyInferenceGenerator.BuildXML4(self.factorNames, self.targetArrayName, self.dataset, self.noData, True)
        if type == 5:
            xmlRoot = XMLFuzzyInferenceGenerator.BuildXML5(self.factorNames, self.targetArrayName, self.dataset, self.noData, True)

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetXMLRepresentation(xmlRoot)
            
        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(parameter)
        model.UseCellDataOn()
                
        caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
        caliModel.SetInputConnection(self.timesource.GetOutputPort())
        caliModel.SetModel(model)
        caliModel.SetModelParameter(parameter)
        caliModel.SetMaxNumberOfIterations(self.maxNumberOfIterations)
        caliModel.SetInitialT(self.initialT)
        caliModel.SetTMinimizer(self.TMinimizer)
        caliModel.SetStandardDeviation(self.standardDeviation)
        caliModel.SetBreakCriteria(self.breakCriteria)
        caliModel.Update()

        caliModel.GetBestFitModelParameter().SetFileName(cal.outputName)
        caliModel.GetBestFitModelParameter().Write()

        writer = vtkXMLPolyDataWriter()
        writer.SetFileName(self.resultFile)
        writer.SetInput(caliModel.GetOutput().GetTimeStep(0))
        writer.Write()
        
if __name__ == "__main__":
    cal = FuzzyCalibrator()

    cal.inputFile = "FuzzyCalibrationData.txt"
    cal.resultFile = "BestFit.vtp"
    cal.factorNames = ["sand", "Paut", "Twin", "fertN"]
    cal.targetArrayName = "n2o"
    cal.maxNumberOfIterations = 20000
    cal.initialT = 1
    cal.breakCriteria = 0.01
    cal.outputName = "BestFit.xml"
    cal.noData = 9999
    cal.standardDeviation = 0.5
    cal.TMinimizer = 1.005
    cal.Run(2)
