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
from libvtkGRASSBridgeCommonPython import *

# test a simple linear regression scheme
class vtkTAG2EDLinearRegressionModelTestSimple(unittest.TestCase):
    
    def setUp(self):
        
        self.points = vtkPoints()
        
        for i in range(5):
            for j in range(5):
                self.points.InsertNextPoint(i, j, 0)

        # Set up the temporal dataset
        data = vtkDoubleArray()
        data.SetNumberOfTuples(25)
        data.SetName("data")
        data.FillComponent(0,3)

        self.ds = vtkPolyData()
        self.ds.Allocate(5,5)
        self.ds.GetPointData().SetScalars(data)
        self.ds.SetPoints(self.points)  

 
        ########################################################################
        # Set up the model parameter
        # A simple linear regression scheme
        # 0.5 + 0.5*(data1)^2
        # When data1 == 3 then result == 5
        
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
        
        self.lrs.SetFileName("/tmp/LinearRegressionSchemeTest1.xml")
        self.lrs.SetXMLRepresentation(root)
        self.lrs.Write()
        
    def testSimpleLinearModel(self):
        
        # We need to set the pipeline structure to composite rather then demand driven
        prototype = vtkCompositeDataPipeline()
        vtkAlgorithm.SetDefaultExecutivePrototype(prototype)
        
        model = vtkTAG2ELinearRegressionModel()
        model.SetModelParameter(self.lrs)
        model.SetInput(self.ds)
        model.Update()   
                
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test1_LR_result1.vtk")
        writer.SetInput(model.GetOutput())
        writer.Write()
        
        mean = vtkTAG2EAbstractModelCalibrator.ArithmeticMean(model.GetOutput().GetPointData().GetScalars())
        
        #result must be exactly 5
        if mean != 5.0:
            print "ERROR mean should be 5 but is", mean
        
# Test a more complex multi-linear regression scheme
class vtkTAG2EDLinearRegressionModelTestComplex(unittest.TestCase):
    
    def setUp(self):
        
        self.points = vtkPoints()
        for i in range(5):
            for j in range(5):
                self.points.InsertNextPoint(i, j, 0)
                
        data1 = vtkDoubleArray()
        data1.SetNumberOfTuples(25)
        data1.SetName("data1")
        data1.FillComponent(0,3)

        data2 = vtkDoubleArray()
        data2.SetNumberOfTuples(25)
        data2.SetName("data2")
        data2.FillComponent(0,5)
        
        data3 = vtkDoubleArray()
        data3.SetNumberOfTuples(25)
        data3.SetName("data3")
        data3.FillComponent(0,1)
        
        self.ds1 = vtkPolyData()
        self.ds1.Allocate(5,5)
        self.ds1.GetPointData().SetScalars(data1)
        
        self.ds2 = vtkPolyData()
        self.ds2.Allocate(5,5)
        self.ds2.GetPointData().SetScalars(data2)
        
        self.ds3 = vtkPolyData()
        self.ds3.Allocate(5,5)
        self.ds3.GetPointData().SetScalars(data3)

        self.ds1.SetPoints(self.points)   
        self.ds2.SetPoints(self.points)  
        self.ds3.SetPoints(self.points)    
         
        ########################################################################
        # Set up the model parameter
        # We build a linear regression scheme of type:
        # 0.5 + 9.0*data1 + 0.5*(data1)^2 + 2.0*(data2)^2 + 45.0*data3
        #
        # When data1 == 3 and data2 == 5 and data3 == 1 then result == 127
        
        
        self.lrs = vtkTAG2EAbstractModelParameter()
        
        root  = vtk.vtkXMLDataElement()
        
        intercept = vtkXMLDataElement()
        intercept.SetName("Intercept")
        intercept.SetCharacterData("0.5", 5)
        
        coefficient0 = vtkXMLDataElement()
        coefficient0.SetName("Coefficient")
        coefficient0.SetIntAttribute("portId", 0)
        coefficient0.SetAttribute("name", "data1")
        coefficient0.SetDoubleAttribute("power", 1)
        coefficient0.SetCharacterData("9.0", 3)
        
        coefficient1 = vtkXMLDataElement()
        coefficient1.SetName("Coefficient")
        coefficient1.SetIntAttribute("portId", 0)
        coefficient1.SetAttribute("name", "data1")
        coefficient1.SetDoubleAttribute("power", 2)
        coefficient1.SetCharacterData("0.5", 3)

        coefficient2 = vtkXMLDataElement()
        coefficient2.SetName("Coefficient")
        coefficient2.SetIntAttribute("portId", 1)
        coefficient2.SetAttribute("name", "data2")
        coefficient2.SetDoubleAttribute("power", 2)
        coefficient2.SetCharacterData("2.0", 3)
        
        coefficient3 = vtkXMLDataElement()
        coefficient3.SetName("Coefficient")
        coefficient3.SetIntAttribute("portId", 2)
        coefficient3.SetAttribute("name", "data3")
        coefficient3.SetDoubleAttribute("power", 1)
        coefficient3.SetCharacterData("45.0", 4)
        
        
        root.SetName("LinearRegressionScheme")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/LinearRegressionScheme")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/LinearRegressionScheme http://tag2e.googlecode.com/files/LinearRegressionScheme.xsd")
        root.SetAttribute("name", "Test1")
        root.SetIntAttribute("numberOfCoefficients", 3)
        root.SetIntAttribute("hasIntercept", 1)
        root.AddNestedElement(intercept)
        root.AddNestedElement(coefficient0)
        root.AddNestedElement(coefficient1)
        root.AddNestedElement(coefficient2)
        root.AddNestedElement(coefficient3)
        root.SetCharacterDataWidth(0)  
        
        self.lrs.SetFileName("/tmp/LinearRegressionSchemeTest2.xml")
        self.lrs.SetXMLRepresentation(root)
        self.lrs.Write()
        
    def testComplexLinearModel(self):
        
        # We need to set the pipeline structure to composite rather then demand driven
        prototype = vtkCompositeDataPipeline()
        vtkAlgorithm.SetDefaultExecutivePrototype(prototype)
        
        model = vtkTAG2ELinearRegressionModel()
        model.SetModelParameter(self.lrs)
        model.SetInput(0, self.ds1)
        model.SetInput(1, self.ds2)
        model.SetInput(2, self.ds3)
        model.Update()   
        
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test2_LR_result1.vtk")
        writer.SetInput(model.GetOutput())
        writer.Write()
        
        # Result must be exactly 127       
        
        mean = vtkTAG2EAbstractModelCalibrator.ArithmeticMean(model.GetOutput().GetPointData().GetScalars())
        
        #result must be exactly 5
        if mean != 127.0:
            print "ERROR mean should be 5 but is", mean
                
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
        
        lrs.SetFileName("/tmp/LinearRegressionSchemeFreibauer1.xml")
        lrs.SetXMLRepresentation(root)
        lrs.Write()
        # Read it again
        lrs.Read();
        lrs.SetFileName("/tmp/LinearRegressionSchemeFreibauer2.xml")
        lrs.Write()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDLinearRegressionParameter)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
    suite2 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDLinearRegressionModelTestSimple)
    unittest.TextTestRunner(verbosity=2).run(suite2) 
    suite3 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDLinearRegressionModelTestComplex)
    unittest.TextTestRunner(verbosity=2).run(suite3) 
    
    