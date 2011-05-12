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
import random

from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

class vtkTAG2EWeightingModelTests(unittest.TestCase):
  
    def setUp(self):

        # Create the point data
        xext = 100
        yext = 1
        num = xext*yext

        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)

        self.model = vtkDoubleArray()
        self.model.SetNumberOfTuples(num)
        self.model.SetName("model")

        self.factor = vtkDoubleArray()
        self.factor.SetNumberOfTuples(num)
        self.factor.SetName("factor")

        # Point ids for poly vertex cell
        points = vtkPoints()

        count = 0
        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()
                ids.InsertNextId(points.InsertNextPoint(i, j, 0))
                # Data range [1:100] -> linear function x
                self.model.SetValue(count, count + 1)
                r = random.randint(1, 9)
                self.factor.SetValue(count, r)
                self.ds.InsertNextCell(vtk.VTK_VERTEX, ids)
                count += 1

        self.ds.GetCellData().AddArray(self.factor)
        self.ds.GetCellData().AddArray(self.model)
        self.ds.GetCellData().SetActiveScalars(self.model.GetName())
        self.ds.SetPoints(points)

        # Create the temporal data

        # We have 10 time steps!
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
            self.timesource.SetInput(i, self.ds)
        self.timesource.Update()

        self._BuildXML()

    def _BuildXML(self):

        self.root  = vtk.vtkXMLDataElement()
        
        factor = vtkXMLDataElement()
        factor.SetName("Factor")
        factor.SetAttribute("name", "factor")
        
        weights = vtkXMLDataElement()
        weights.SetName("Weights")

        for i in range(9):
            weight = vtkXMLDataElement()
            weight.SetName("Weight")
            weight.SetIntAttribute("id", i)
            weight.SetIntAttribute("const", 0)
            weight.SetIntAttribute("active", 0)
            weight.SetDoubleAttribute("min", 0)
            weight.SetDoubleAttribute("max", 10)
            weight.SetCharacterData(str(i), 6)
            weights.AddNestedElement(weight)
        
        self.root.SetName("Weighting")
        self.root.AddNestedElement(factor)
        self.root.AddNestedElement(weights)
        self.root.SetAttribute("name", "test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/Weighting")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/Weighting http://tag2e.googlecode.com/files/Weighting.xsd")
        
    def test1Model(self):
        
        w = vtkTAG2EWeightingModelParameter()
        w.SetXMLRepresentation(self.root)

        model = vtkTAG2EWeightingModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(w)
        model.UseCellDataOn()
        model.Update()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EWeightingModelTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
