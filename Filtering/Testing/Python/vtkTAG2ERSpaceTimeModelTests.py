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
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *
from libvtkGRASSBridgeGraphicsPython import *

class vtkTAG2ERSpaceTimeModelTests(unittest.TestCase):
    
    def setUp(self):
        
        # Create the point data
        xext = 50
        yext = 50
        num = xext*yext
                
        data1 = vtkDoubleArray()
        data1.SetNumberOfTuples(num)
        data1.SetName("data1")
        data2 = vtkDoubleArray()
        data2.SetNumberOfTuples(num)
        data2.SetName("data2")
        data3 = vtkDoubleArray()
        data3.SetNumberOfTuples(num)
        data3.SetName("data3")
        
        # Point ids for poly vertex cell
        ids = vtkIdList()
        points = vtkPoints()
        
        count = 0
        for i in range(xext):
            for j in range(yext):
                points.InsertNextPoint(i, j, 0)
                data1.SetValue(count, i)
                data2.SetValue(count, j)
                data3.SetValue(count, i*j)
                ids.InsertNextId(count)
                count += 1

        ds = vtkPolyData()
        ds.Allocate(xext,yext)
        ds.GetPointData().SetScalars(data1)
        ds.GetPointData().AddArray(data2)
        ds.GetPointData().AddArray(data3)
        ds.SetPoints(points)    
        ds.InsertNextCell(vtk.VTK_POLY_VERTEX, ids)
        
        # Create the temporal data

        # We have 10 time steps!
        time = 200
        
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
            self.timesource.SetInput(i, ds)
        self.timesource.Update()
        
        # Generate the XML descirption of the model parameter
        
        root  = vtkXMLDataElement()
        inputs = vtkXMLDataElement()
        outputs = vtkXMLDataElement()
        script = vtkXMLDataElement()
        inputname1 = vtkXMLDataElement()
        inputname2 = vtkXMLDataElement()
        inputname3 = vtkXMLDataElement()
        outputname1 = vtkXMLDataElement()

        # We have 3 input arrays named data1, data2 and data3
        # Which must be present in the input
        inputname1.SetName("ArrayName")
        inputname1.SetCharacterData("data1", 5)
        inputname2.SetName("ArrayName")
        inputname2.SetCharacterData("data2", 5)
        inputname3.SetName("ArrayName")
        inputname3.SetCharacterData("data3", 5)
        
        # A single output array named result should be read from the R session
        outputname1.SetName("ArrayName")
        outputname1.SetCharacterData("result", 6)

        inputs.SetName("InputArrays")
        inputs.AddNestedElement(inputname1)
        inputs.AddNestedElement(inputname2)
        inputs.AddNestedElement(inputname3)
        
        outputs.SetName("OutputArrays")
        outputs.AddNestedElement(outputname1)
        
        # This is a simple input script
        script.SetName("RScript")
        text = "result = rnorm(" + str(xext*yext*time) + ")"
        script.SetCharacterData(text, len(text))

        # Put it all together
        root.SetName("RSpaceTimeModelDescription")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/RSpaceTimeModelDescription")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/RSpaceTimeModelDescription http://tag2e.googlecode.com/files/RSpaceTimeModelDescription.xsd")
        root.SetAttribute("name", "test")
        root.AddNestedElement(inputs)
        root.AddNestedElement(outputs)
        root.AddNestedElement(script)
        
        self.modelparam = vtkTAG2EAbstractModelParameter()
        self.modelparam.SetFileName("/tmp/vtkTAG2ERSpaceTimeModelTests.xml")
        self.modelparam.SetXMLRepresentation(root)
        self.modelparam.Write()
        
    def test1(self):
        
        model = vtkTAG2ERSpaceTimeModel()
        model.SetModelParameter(self.modelparam)
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetStartDate("2007-12-25")
        model.Update()
        
        print model
                
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ERSpaceTimeModelTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
