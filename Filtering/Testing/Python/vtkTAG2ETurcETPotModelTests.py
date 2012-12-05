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
from libvtkGRASSBridgeCommonPython import *

class vtkTAG2ETurcETPotModelTests(unittest.TestCase):
  
    def setUp(self):

        # Create the point data
        xext = 10
        yext = 10
        num = xext*yext

        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)

        self.Clay = vtkDoubleArray()
        self.Clay.SetNumberOfTuples(num)
        self.Clay.SetName("Clay")
        self.Clay.FillComponent(0, 20)

        self.MeanTemperature = vtkDoubleArray()
        self.MeanTemperature.SetNumberOfTuples(num)
        self.MeanTemperature.SetName("MeanTemperature")
        self.MeanTemperature.FillComponent(0, 12)

        self.GlobalRadiation = vtkDoubleArray()
        self.GlobalRadiation.SetNumberOfTuples(num)
        self.GlobalRadiation.SetName("GlobalRadiation")
        self.GlobalRadiation.FillComponent(0, 1)

        # Point ids for poly vertex cell
        points = vtkPoints()

        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()
                ids.InsertNextId(points.InsertNextPoint(i, j, 0))
                ids.InsertNextId(points.InsertNextPoint(i, j, 0.23))
                self.ds.InsertNextCell(vtk.VTK_LINE, ids)

        self.ds.GetCellData().AddArray(self.Clay)
        self.ds.GetCellData().AddArray(self.MeanTemperature)
        self.ds.GetCellData().AddArray(self.GlobalRadiation)
        self.ds.SetPoints(points)
        
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2ETurcETPotModelTestsInput.vtp")
        pwriter.SetInput(self.ds)
        pwriter.Write()
        
    def test1Model(self):
        
        model = vtkTAG2ETurcETPotModel()
        model.SetInput(self.ds)
        model.Update()
        
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2ETurcETPotModelTestsResult.vtp")
        pwriter.SetInputConnection(model.GetOutputPort())
        pwriter.Write()
        
        print model.GetOutput()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ETurcETPotModelTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
