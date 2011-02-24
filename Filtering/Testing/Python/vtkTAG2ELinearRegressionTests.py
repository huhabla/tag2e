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

        self.ds1 = vtkPolyData()
        self.ds1.Allocate(5,5)
        self.ds1.GetPointData().SetScalars(data)
        
        self.ds2 = vtkPolyData()
        self.ds2.Allocate(5,5)
        self.ds2.GetPointData().SetScalars(data)

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
                
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test1_LR_result1.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(0))
        writer.Write()
        
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test1_LR_result2.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(1))
        writer.Write()
        
        #result must be exactly 5
        
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
        
        self.ds11 = vtkPolyData()
        self.ds11.Allocate(5,5)
        self.ds11.GetPointData().SetScalars(data1)
        
        self.ds12 = vtkPolyData()
        self.ds12.Allocate(5,5)
        self.ds12.GetPointData().SetScalars(data1)

        self.ds21 = vtkPolyData()
        self.ds21.Allocate(5,5)
        self.ds21.GetPointData().SetScalars(data2)
        
        self.ds22 = vtkPolyData()
        self.ds22.Allocate(5,5)
        self.ds22.GetPointData().SetScalars(data2)
        
        self.ds31 = vtkPolyData()
        self.ds31.Allocate(5,5)
        self.ds31.GetPointData().SetScalars(data3)
        
        self.ds32 = vtkPolyData()
        self.ds32.Allocate(5,5)
        self.ds32.GetPointData().SetScalars(data3)

        self.ds11.SetPoints(self.points)    
        self.ds12.SetPoints(self.points)   
        self.ds21.SetPoints(self.points)    
        self.ds22.SetPoints(self.points)   
        self.ds31.SetPoints(self.points)    
        self.ds32.SetPoints(self.points)     
        
        # We have two time stamps
        timesteps = vtkDoubleArray()
        timesteps.SetNumberOfTuples(2)
        timesteps.SetNumberOfComponents(1)
        timesteps.SetValue(0, 0.5)
        timesteps.SetValue(1, 1.5)

        # Use the temporal data source to create the temporal datasets
        self.timesource1 = vtkTemporalDataSetSource()
        self.timesource1.SetTimeRange(0, 2, timesteps)
        self.timesource1.SetInput(0, self.ds11)
        self.timesource1.SetInput(1, self.ds12)

        self.timesource2 = vtkTemporalDataSetSource()
        self.timesource2.SetTimeRange(0, 2, timesteps)
        self.timesource2.SetInput(0, self.ds21)
        self.timesource2.SetInput(1, self.ds22)

        self.timesource3 = vtkTemporalDataSetSource()
        self.timesource3.SetTimeRange(0, 2, timesteps)
        self.timesource3.SetInput(0, self.ds31)
        self.timesource3.SetInput(1, self.ds32)
 
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
        self.lrs.GetXMLRoot().DeepCopy(root)
        self.lrs.Write()
        
    def testComplexLinearModel(self):
        
        # We need to set the pipeline structure to composite rather then demand driven
        prototype = vtkCompositeDataPipeline()
        vtkAlgorithm.SetDefaultExecutivePrototype(prototype)
        
        model = vtkTAG2ELinearRegressionModel()
        model.SetModelParameter(self.lrs)
        model.SetInputConnection(0, self.timesource1.GetOutputPort())
        model.SetInputConnection(1, self.timesource2.GetOutputPort())
        model.SetInputConnection(2, self.timesource3.GetOutputPort())
        model.Update()   
        
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test2_LR_result1.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(0))
        writer.Write()
        
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test2_LR_result2.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(1))
        writer.Write()
        
        # Result must be exactly 127
       

# Test a more complex multi-linear regression scheme
class vtkTAG2EDLinearRegressionModelTestComplexInterpol(unittest.TestCase):
    
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
        
        self.ds11 = vtkPolyData()
        self.ds11.Allocate(5,5)
        self.ds11.GetPointData().SetScalars(data1)
        
        self.ds12 = vtkPolyData()
        self.ds12.Allocate(5,5)
        self.ds12.GetPointData().SetScalars(data1)
        
        self.ds13 = vtkPolyData()
        self.ds13.Allocate(5,5)
        self.ds13.GetPointData().SetScalars(data1)
        
        self.ds14 = vtkPolyData()
        self.ds14.Allocate(5,5)
        self.ds14.GetPointData().SetScalars(data1)

        self.ds21 = vtkPolyData()
        self.ds21.Allocate(5,5)
        self.ds21.GetPointData().SetScalars(data2)
        
        self.ds22 = vtkPolyData()
        self.ds22.Allocate(5,5)
        self.ds22.GetPointData().SetScalars(data2)
        
        self.ds31 = vtkPolyData()
        self.ds31.Allocate(5,5)
        self.ds31.GetPointData().SetScalars(data3)
        
        self.ds32 = vtkPolyData()
        self.ds32.Allocate(5,5)
        self.ds32.GetPointData().SetScalars(data3)

        self.ds11.SetPoints(self.points)    
        self.ds12.SetPoints(self.points)  
        self.ds13.SetPoints(self.points)    
        self.ds14.SetPoints(self.points)   
        self.ds21.SetPoints(self.points)    
        self.ds22.SetPoints(self.points)   
        self.ds31.SetPoints(self.points)    
        self.ds32.SetPoints(self.points)     
        
        # We have four time stamps
        timesteps = vtkDoubleArray()
        timesteps.SetNumberOfTuples(4)
        timesteps.SetNumberOfComponents(1)
        timesteps.SetValue(0, 0.5)
        timesteps.SetValue(1, 1.5)
        timesteps.SetValue(2, 2.5)
        timesteps.SetValue(3, 3.5)
        
        # We have two time stamps
        timestepsShort = vtkDoubleArray()
        timestepsShort.SetNumberOfTuples(2)
        timestepsShort.SetNumberOfComponents(1)
        timestepsShort.SetValue(0, 0.5)
        timestepsShort.SetValue(1, 3.5)

        # Use the temporal data source to create the temporal datasets
        self.timesource1 = vtkTemporalDataSetSource()
        self.timesource1.SetTimeRange(0, 4, timesteps)
        self.timesource1.SetInput(0, self.ds11)
        self.timesource1.SetInput(1, self.ds12)
        self.timesource1.SetInput(2, self.ds13)
        self.timesource1.SetInput(3, self.ds14)

        self.timesource2 = vtkTemporalDataSetSource()
        self.timesource2.SetTimeRange(0, 4, timestepsShort)
        self.timesource2.SetInput(0, self.ds21)
        self.timesource2.SetInput(1, self.ds22)

        self.timesource3 = vtkTemporalDataSetSource()
        self.timesource3.SetTimeRange(0, 4, timestepsShort)
        self.timesource3.SetInput(0, self.ds31)
        self.timesource3.SetInput(1, self.ds32)
 
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
        
        self.lrs.SetFileName("/tmp/LinearRegressionSchemeTest3.xml")
        self.lrs.GetXMLRoot().DeepCopy(root)
        self.lrs.Write()
        
    def testComplexLinearModel(self):
        
        # We need to set the pipeline structure to composite rather then demand driven
        prototype = vtkCompositeDataPipeline()
        vtkAlgorithm.SetDefaultExecutivePrototype(prototype)
        
        # Interpolate the data sets between the time steps of the first input
        interpol1 = vtkTemporalInterpolator()
        interpol1.SetInputConnection(self.timesource2.GetOutputPort())
        interpol2 = vtkTemporalInterpolator()
        interpol2.SetInputConnection(self.timesource3.GetOutputPort())
        
        model = vtkTAG2ELinearRegressionModel()
        model.SetModelParameter(self.lrs)
        model.SetInputConnection(0, self.timesource1.GetOutputPort())
        model.SetInputConnection(1, interpol1.GetOutputPort())
        model.SetInputConnection(2, interpol2.GetOutputPort())
        model.Update()   
        
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test3_LR_result1.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(0))
        writer.Write()
        
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test3_LR_result2.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(1))
        writer.Write()
        
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test3_LR_result3.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(2))
        
        writer.Write()
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test3_LR_result4.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(3))
        writer.Write()
        
        # Result must be exactly 127
       
        
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
        lrs.GetXMLRoot().DeepCopy(root)
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
    suite4 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDLinearRegressionModelTestComplexInterpol)
    unittest.TextTestRunner(verbosity=2).run(suite4) 
    
    