#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.
from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

import WFISGenerator
import MetropolisAlgorithm
import DataReader

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
        
        self.dataset, self.timesource = DataReader.ReadTextData(self.inputFile, self.targetArrayName)
                    
        if type == 2:
            xmlRoot = WFISGenerator.BuildFuzzyXMLRepresentation2(self.factorNames, self.targetArrayName, self.dataset, self.noData)
        if type == 3:
            xmlRoot = WFISGenerator.BuildFuzzyXMLRepresentation3(self.factorNames, self.targetArrayName, self.dataset, self.noData)
        if type == 4:
            xmlRoot = WFISGenerator.BuildFuzzyXMLRepresentation4(self.factorNames, self.targetArrayName, self.dataset, self.noData)
        if type == 5:
            xmlRoot = WFISGenerator.BuildFuzzyXMLRepresentation5(self.factorNames, self.targetArrayName, self.dataset, self.noData)

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetXMLRepresentation(xmlRoot)
            
        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(parameter)
                
        if True:
            caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
            caliModel.SetInputConnection(self.timesource.GetOutputPort())
            caliModel.SetModel(model)
            caliModel.SetModelParameter(parameter)
            caliModel.SetTargetArrayName(self.targetArrayName)
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
        else:
            MetropolisAlgorithm.SimulatedAnnealing(model, parameter, self.maxNumberOfIterations, self.initialT, \
                               self.standardDeviation, self.breakCriteria, model.GetResultArrayName(), \
                               self.targetArrayName, self.outputName, self.TMinimizer)
                                               
            writer = vtkXMLPolyDataWriter()
            writer.SetFileName(self.resultFile)
            writer.SetInput(model.GetOutput().GetTimeStep(0))
            writer.Write()
        
if __name__ == "__main__":
    cal = FuzzyCalibrator()

    cal.inputFile = "FuzzyCalibrationData.txt"
    cal.resultFile = "BestFit.vtp"
    cal.factorNames = ["sand", "Paut", "Twin", "fertN"]
    cal.targetArrayName = "n2o"
    cal.maxNumberOfIterations = 2000
    cal.initialT = 1
    cal.breakCriteria = 0.01
    cal.outputName = "BestFit.xml"
    cal.noData = 9999
    cal.standardDeviation = 0.5
    cal.TMinimizer = 1.005
    cal.Run(2)
