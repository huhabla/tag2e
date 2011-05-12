#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.
from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

import FISGenerator
import WeightGenerator
import MetropolisAlgorithm
import DataReader
import Calibration
import MetaModel

################################################################################
################################################################################
################################################################################
  
class FuzzyCalibrator():
    
    def __init__(self):
        self.inputFile = "FuzzyCalibrationData.txt"
        self.factorNames = ["sand", "Paut", "Twin", "fertN"]
        self.targetArrayName = "n2o"
        self.weightFactorName = "croptype"
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
            xmlRootFIS = FISGenerator.BuildFuzzyXMLRepresentation2(self.factorNames, self.targetArrayName, self.dataset, self.noData)
        if type == 3:
            xmlRootFIS = FISGenerator.BuildFuzzyXMLRepresentation3(self.factorNames, self.targetArrayName, self.dataset, self.noData)
        if type == 4:
            xmlRootFIS = FISGenerator.BuildFuzzyXMLRepresentation4(self.factorNames, self.targetArrayName, self.dataset, self.noData)
        if type == 5:
            xmlRootFIS = FISGenerator.BuildFuzzyXMLRepresentation5(self.factorNames, self.targetArrayName, self.dataset, self.noData)

        xmlRootW = WeightGenerator.BuildXML(self.weightFactorName, 6, 0, 10)

        # Set up the parameter and the model
        parameterFIS = vtkTAG2EFuzzyInferenceModelParameter()
        parameterFIS.SetXMLRepresentation(xmlRootFIS)
            
        modelFIS = vtkTAG2EFuzzyInferenceModel()
        modelFIS.SetInputConnection(self.timesource.GetOutputPort())
        modelFIS.SetModelParameter(parameterFIS)
        
        parameterW = vtkTAG2EWeightingModelParameter()
        parameterW.SetXMLRepresentation(xmlRootW)
            
        modelW = vtkTAG2EWeightingModel()
        modelW.SetInputConnection(modelFIS.GetOutputPort())
        modelW.SetModelParameter(parameterW)
        
        meta = MetaModel.MetaModel()
        meta.InsertModelParameter(modelFIS, parameterFIS, "vtkTAG2EFuzzyInferenceModel")
        meta.SetLastModelParameterInPipeline(modelW, parameterW, "vtkTAG2EWeightingModel")
        meta.SetTargetDataSet(self.timesource.GetOutput())
    
        Calibration.MetaModelSimulatedAnnealing(meta, self.maxNumberOfIterations,\
                           self.initialT, self.standardDeviation, self.breakCriteria, \
                           self.outputName, self.TMinimizer)

        writer = vtkXMLPolyDataWriter()
        writer.SetFileName(self.resultFile)
        writer.SetInput(meta.GetModelOutput().GetTimeStep(0))
        writer.Write()
        
if __name__ == "__main__":
    cal = FuzzyCalibrator()

    cal.inputFile = "FuzzyCalibrationData.txt"
    cal.resultFile = "BestFit.vtp"
    cal.factorNames = ["sand", "Paut", "Twin", "fertN"]
    cal.weightFactorName = "croptype"
    cal.targetArrayName = "n2o"
    cal.maxNumberOfIterations = 20000
    cal.initialT = 1
    cal.breakCriteria = 0.01
    cal.outputName = "BestFit.xml"
    cal.noData = 9999
    cal.standardDeviation = 0.5
    cal.TMinimizer = 1.005
    cal.Run(2)
