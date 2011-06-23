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
import XMLWeightingGenerator
import CSVDataReader
import Calibration
import MetaModel

################################################################################
################################################################################
################################################################################
  
class FuzzyCalibrator():
    
    def __init__(self):
        self.inputFile = "FuzzyCalibrationData.txt"
        self.factorNames = ["sand", "Paut", "Twin", "fertN"]
        self.fuzzySetNum = [2,3,3,2]
        self.targetArrayName = "n2o"
        self.weightFactorName = "croptype"
        self.maxNumberOfIterations = 1000
        self.initialT = 1
        self.breakCriteria = 0.01
        self.outputName = "BestFit.xml"
        self.noData = 9999
        self.standardDeviation = 2
        self.TMinimizer = 1.005
        self.SdMinimizer = 1.005
        self.numberOfWeights = 6
        self.enableBagging = True

    def Run(self):
        
        self.dataset, self.timesource = CSVDataReader.ReadTextData(self.inputFile, self.targetArrayName, self.enableBagging)

        xmlRootFIS = XMLFuzzyInferenceGenerator.BuildXML(self.factorNames, self.fuzzySetNum, self.targetArrayName, self.dataset, self.noData, True)

        xmlRootW = XMLWeightingGenerator.BuildXML(self.weightFactorName, self.numberOfWeights, 0, 10)

        # Set up the parameter and the model
        parameterFIS = vtkTAG2EFuzzyInferenceModelParameter()
        parameterFIS.SetXMLRepresentation(xmlRootFIS)
        parameterFIS.DebugOff()
            
        modelFIS = vtkTAG2EFuzzyInferenceModel()
        modelFIS.SetInputConnection(self.timesource.GetOutputPort())
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
        meta.SetLastModelParameterInPipeline(modelW, parameterW, "vtkTAG2EWeightingModel")
        meta.SetTargetDataSet(self.timesource.GetOutput())

        bestFitParameter, bestFitOutput, = Calibration.MetaModelSimulatedAnnealingImproved(
                                           meta, self.maxNumberOfIterations,\
                                           self.initialT, self.standardDeviation, 
                                           self.breakCriteria, self.TMinimizer,\
                                           self.SdMinimizer)

        bestFitParameter.PrintXML(self.outputName)

        writer = vtkXMLPolyDataWriter()
        writer.SetFileName(self.resultFile)
        writer.SetInput(bestFitOutput.GetTimeStep(0))
        writer.Write()
        
################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    cal = FuzzyCalibrator()

    cal.inputFile = "FuzzyCalibrationData.txt"
    cal.resultFile = "BestFit.vtp"
    cal.factorNames = ["sand", "Paut", "Twin", "fertN"]
    cal.fuzzySetNum = [2,3,3,2]
    cal.weightFactorName = "croptype"
    cal.targetArrayName = "n2o"
    cal.maxNumberOfIterations = 20000
    cal.initialT = 1
    cal.breakCriteria = 0.01
    cal.outputName = "BestFit.xml"
    cal.noData = 9999
    cal.standardDeviation = 1
    cal.TMinimizer = 1.002
    cal.SdMinimizer = 1.0001
    cal.numberOfWeights = 6
    cal.enableBagging = False
    cal.Run()
