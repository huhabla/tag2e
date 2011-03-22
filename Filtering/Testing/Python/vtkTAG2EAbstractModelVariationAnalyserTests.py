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

# Test the abstract class of correct xml functionality
class vtkTAG2EAbstractModelVariationAnalyzerTests(unittest.TestCase):
       
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

    def testXMLDataDistributionDescription(self):
        
        self.ddd = vtkTAG2EAbstractModelParameter()
                
        norm = vtkXMLDataElement()
        norm.SetName("Norm")
        norm.SetDoubleAttribute("mean", 30.0)
        norm.SetDoubleAttribute("sd", 9.5)
        
        lnorm = vtkXMLDataElement()
        lnorm.SetName("Lnorm")
        lnorm.SetDoubleAttribute("meanlog", 1.2)
        lnorm.SetDoubleAttribute("sdlog", 0.50)
        
        var1 = vtkXMLDataElement()
        var1.SetName("Variable")
        var1.SetAttribute("name", "nrate")
        var1.SetAttribute("type", "norm")
        var1.AddNestedElement(norm)
        
        var2 = vtkXMLDataElement()
        var2.SetName("Variable")
        var2.SetAttribute("name", "sand")
        var2.SetAttribute("type", "lnorm")
        var2.AddNestedElement(lnorm)

        root  = vtk.vtkXMLDataElement()
        root.SetName("DataDistributionDescription")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/DataDistributionDescription")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/DataDistributionDescription http://tag2e.googlecode.com/files/DataDistributionDescription.xsd")
        root.SetAttribute("name", "Test1")
        root.AddNestedElement(var1)
        root.AddNestedElement(var2)
        
        self.ddd.SetFileName("/tmp/DataDistributionDescription1.xml")
        self.ddd.GetXMLRoot().DeepCopy(root)
        self.ddd.Write()
                
        analyser = vtkTAG2EAbstractModelVariationAnalyser()
        analyser.SetDataDistributionDescription(self.ddd)
        analyser.SetInputConnection(self.timesource.GetOutputPort())
        analyser.Update()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EAbstractModelVariationAnalyzerTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 

    
    