#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.
from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

from WFISGenerator import *
from MetropolisAlgorithm import *

################################################################################
################################################################################
################################################################################
  
class FuzzyCalibrator():
    
    def __init__(self):
        self.inputFile = "FuzzyCalibrationData.txt"
        self.factorNames = ["sand", "Paut", "Twin", "fertN"]
        self.measureName = "n2o"
        self.maxIterations = 1000
        self.Temperatur = 1
        self.errorBreak = 0.01
        self.outputName = "BestFit.xml"
        self.noData = 9999
        self.standardDeviation = 2
        self.minT = 1.005

    def _ReadTextData(self):
        
        file = open(self.inputFile)
        firstLine = file.readline()
        headerLine = file.readline()
        
        numberOfTimeSteps = int(firstLine)
        names = headerLine.split(',')
        
        nameArray = []
        for i in range(4, len(names)):
            nameArray.append(str(names[i]).rstrip('\r\n'))
                    
        points = vtkPoints()
        idataset = vtkIdList()
        
        dataArrays = vtkDataSetAttributes()
        
        for name in nameArray:
            array = vtkDoubleArray()
            array.SetName(name)
            dataArrays.AddArray(array)
        
        numberOfPoints = 0
        while True:
            
            line = file.readline()
            if line == "":
                break
            tmpArray = line.split(',')
                
            data = {}
            step = float(tmpArray[0])
            year = float(tmpArray[1])
            y = float(tmpArray[2])
            x = float(tmpArray[3])
            
            idataset.InsertNextId(points.InsertNextPoint(x, y, 0))
            
            count = 0
            for i in range(4, len(tmpArray)):
                data[nameArray[count]] = float(tmpArray[i])
                count += 1
            
            for key in data.keys():
                dataArrays.GetArray(key).InsertNextValue(data[key])
                
            numberOfPoints += 1
            

        file.close()
        
        self.dataset = vtkPolyData()
        self.dataset.Allocate(numberOfPoints,numberOfPoints)
        self.dataset.GetPointData().DeepCopy(dataArrays)
        self.dataset.SetPoints(points)
        self.dataset.InsertNextCell(vtk.VTK_POLY_VERTEX, idataset)
        
        # Create the temporal data
        # We have 1 time steps!
        time = 1

        # Generate the time steps
        timesteps = vtkDoubleArray()
        timesteps.SetNumberOfTuples(time)
        timesteps.SetNumberOfComponents(1)
        for i in range(time):
            timesteps.SetValue(i, 3600*24*i)

        # Create the spatio-temporal source
        self.timesource = vtkTemporalDataSetSource()
        self.timesource.SetTimeRange(0, 3600*24*time, timesteps)
        for i in range(time):
            self.timesource.SetInput(i, self.dataset)
        self.timesource.Update()

    def Run(self, type):
        
        self._ReadTextData()
        
        if type == 2:
            xmlRoot = BuildFuzzyXMLRepresentation2(self.factorNames, self.measureName, self.dataset, self.noData)
        if type == 3:
            xmlRoot = BuildFuzzyXMLRepresentation3(self.factorNames, self.measureName, self.dataset, self.noData)
        if type == 4:
            xmlRoot = BuildFuzzyXMLRepresentation4(self.factorNames, self.measureName, self.dataset, self.noData)
        if type == 5:
            xmlRoot = BuildFuzzyXMLRepresentation5(self.factorNames, self.measureName, self.dataset, self.noData)

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.GetXMLRoot().DeepCopy(xmlRoot)
        parameter.GenerateInternalSchemeFromXML()
            
        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(parameter)
                
        if True:
            caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
            caliModel.SetInputConnection(self.timesource.GetOutputPort())
            caliModel.SetModel(model)
            caliModel.SetModelParameter(parameter)
            caliModel.SetTargetArrayName(self.measureName)
            caliModel.SetMaxNumberOfIterations(self.maxIterations)
            caliModel.SetInitialT(self.Temperatur)
            caliModel.SetTMinimizer = self.minT
            caliModel.Update()
            
            caliModel.GetBestFitModelParameter().SetFileName(cal.outputName)
            caliModel.GetBestFitModelParameter().Write()
                    
            writer = vtkXMLPolyDataWriter()
            writer.SetFileName(self.resultFile)
            writer.SetInput(caliModel.GetOutput().GetTimeStep(0))
            writer.Write()
        else:
            SimulatedAnnealing(model, parameter, self.maxIterations, self.Temperatur, \
                               self.standardDeviation, self.errorBreak, model.GetResultArrayName(), \
                               self.measureName, self.outputName, self.minT)
                                               
            writer = vtkXMLPolyDataWriter()
            writer.SetFileName(self.resultFile)
            writer.SetInput(model.GetOutput().GetTimeStep(0))
            writer.Write()
        
if __name__ == "__main__":
    cal = FuzzyCalibrator()

    cal.inputFile = "FuzzyCalibrationData.txt"
    cal.resultFile = "BestFit.vtp"
    cal.factorNames = ["sand", "Paut", "Twin", "fertN"]
    cal.measureName = "n2o"
    cal.maxIterations = 50000
    cal.Temperatur = 1
    cal.errorBreak = 0.01
    cal.outputName = "BestFit.xml"
    cal.noData = 9999
    cal.standardDeviation = 0.5
    cal.minT = 1.005
    
    cal.Run(3)