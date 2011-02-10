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

#include the VTK and vtkGRASSBridge Python libraries
import unittest

from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

class vtkTAG2EDLinearRegressionModel(unittest.TestCase):
    
    def setUp(self):
        
        # Set up the temporal dataset
        data = vtkDoubleArray()
        data.SetNumberOfTuples(25)
        data.SetName("data")
        data.FillComponent(0,3)

        self.ds1 = vtkPolyData()
        self.ds1.Allocate(5,5)
        self.ds1.GetPointData().SetScalars(data)
        
        self.ds2 = vtkPolyData()
        self.ds2.Allocate(5,5)
        self.ds2.GetPointData().SetScalars(data)

        self.points = vtkPoints()
        
        count = 0
        for i in range(5):
            for j in range(5):
                self.points.InsertNextPoint(i, j, 0)

        self.ds1.SetPoints(self.points)    
        self.ds2.SetPoints(self.points)     
        
        timesteps = vtkDoubleArray()
        timesteps.SetNumberOfTuples(2)
        timesteps.SetNumberOfComponents(1)
        timesteps.SetValue(0, 0.5)
        timesteps.SetValue(1, 1.5)

        # Use the temporal data source to create the temporal dataset
        self.timesource = vtkTemporalDataSetSource()
        self.timesource.SetTimeRange(0, 2, timesteps)
        self.timesource.SetInput(0, self.ds1)
        self.timesource.SetInput(1, self.ds2)

 
        ########################################################################
        # Set up the model parameter
        
        self.lrs = vtkTAG2EAbstractModelParameter()
        
        root  = vtk.vtkXMLDataElement()
        
        intercept = vtkXMLDataElement()
        coefficient = vtkXMLDataElement()
        
        intercept.SetName("Intercept")
        intercept.SetCharacterData("0.5", 5)
        
        coefficient.SetName("Coefficient")
        coefficient.SetIntAttribute("portId", 0)
        coefficient.SetAttribute("name", "data")
        coefficient.SetDoubleAttribute("power", 2)
        coefficient.SetCharacterData("0.5", 3)

        root.SetName("LinearRegressionScheme")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/LinearRegressionScheme")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/LinearRegressionScheme http://tag2e.googlecode.com/files/LinearRegressionScheme.xsd")
        root.SetAttribute("name", "Test1")
        root.SetIntAttribute("numberOfCoefficients", 3)
        root.SetIntAttribute("hasIntercept", 1)
        root.AddNestedElement(intercept)
        root.AddNestedElement(coefficient)
        root.SetCharacterDataWidth(0)  
        
        self.lrs.SetFileName("LinearRegressionSchemeTest1.xml")
        self.lrs.GetXMLRoot().DeepCopy(root)
        self.lrs.Write()
        
    def testSimpleLinearModel(self):
        
        # We need to set the pipeline structure to composite rather then demand driven
        prototype = vtkCompositeDataPipeline()
        vtkAlgorithm.SetDefaultExecutivePrototype(prototype)
        
        model = vtkTAG2ELinearRegressionModel()
        model.SetModelParameter(self.lrs)
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.Update()   
        
        #print model
        #print model.GetOutput()
        
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test_LR_result1.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(0))
        writer.Write()
        
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test_LR_result2.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(1))
        writer.Write()
        

class vtkTAG2EDLinearRegressionParameter(unittest.TestCase): 
    
    def testXML(self):
        
        lrs = vtkTAG2EAbstractModelParameter()
        
        root  = vtk.vtkXMLDataElement()
        
        intercept = vtkXMLDataElement()
        coefficient1 = vtkXMLDataElement()
        coefficient2 = vtkXMLDataElement()
        coefficient3 = vtkXMLDataElement()
        coefficient4 = vtkXMLDataElement()
        
        intercept.SetName("Intercept")
        intercept.SetCharacterData("0.6", 5)
        
        coefficient1.SetName("Coefficient")
        coefficient1.SetIntAttribute("portId", 0)
        coefficient1.SetAttribute("name", "nrate")
        coefficient1.SetDoubleAttribute("power", 1)
        coefficient1.SetCharacterData("0.002", 5)
        
        coefficient2.SetName("Coefficient")
        coefficient2.SetIntAttribute("portId", 0)
        coefficient2.SetAttribute("name", "sand")
        coefficient2.SetDoubleAttribute("power", 1)
        coefficient2.SetCharacterData("0.024", 5)
        
        coefficient3.SetName("Coefficient")
        coefficient3.SetIntAttribute("portId", 0)
        coefficient3.SetAttribute("name", "csoil")
        coefficient3.SetDoubleAttribute("power", 1)
        coefficient3.SetCharacterData("1.27", 5)
        
        coefficient4.SetName("Coefficient")
        coefficient4.SetIntAttribute("portId", 0)
        coefficient4.SetAttribute("name", "nsoil")
        coefficient4.SetDoubleAttribute("power", 1)
        coefficient4.SetCharacterData("28", 5)
        
        root.SetName("LinearRegressionScheme")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/LinearRegressionScheme")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/LinearRegressionScheme http://tag2e.googlecode.com/files/LinearRegressionScheme.xsd")
        root.SetAttribute("name", "Freibauer")
        root.SetIntAttribute("numberOfCoefficients", 3)
        root.SetIntAttribute("hasIntercept", 1)
        root.AddNestedElement(intercept)
        root.AddNestedElement(coefficient1)
        root.AddNestedElement(coefficient2)
        root.AddNestedElement(coefficient3)
        root.AddNestedElement(coefficient4)
        root.SetCharacterDataWidth(0)  
        
        lrs.SetFileName("LinearRegressionSchemeFreibauer1.xml")
        lrs.GetXMLRoot().DeepCopy(root)
        lrs.Write()
        # Read it again
        lrs.Read();
        lrs.SetFileName("LinearRegressionSchemeFreibauer2.xml")
        lrs.Write()


        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDLinearRegressionParameter)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
    suite2 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDLinearRegressionModel)
    unittest.TextTestRunner(verbosity=2).run(suite2) 