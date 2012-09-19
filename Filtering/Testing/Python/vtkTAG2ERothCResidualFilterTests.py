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
from libvtkGRASSBridgeTemporalPython import *
from libvtkGRASSBridgeCommonPython import *

class vtkTAG2ERothCResidualFilterTests(unittest.TestCase):
  
    def setUp(self):

        # Create the point data
        xext = 2
        yext = 2
        zext = 5
        num = xext*yext*zext

        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)

        RootDepth = vtkDoubleArray()
        RootDepth.SetNumberOfTuples(num)
        RootDepth.SetName("RootDepth")
        RootDepth.FillComponent(0, 1)
        
        Residuals = vtkDoubleArray()
        Residuals.SetNumberOfTuples(num)
        Residuals.SetName("Residuals")
        Residuals.FillComponent(0, 2)

        Layer = vtkIntArray()
        Layer.SetName("Layer")
        Layer.FillComponent(0, 0)
        
        # Point ids for poly vertex cell
        points = vtkPoints()

        for i in range(xext):
            for j in range(yext):
                lastId = 0
                for k in range(zext):
                    ids = vtkIdList()
                    if k == 0:                    
                        id = points.InsertNextPoint(i, j, k/5.0)
                        ids.InsertNextId(id)
                        id = points.InsertNextPoint(i, j, -1*(k + 1)/5.0)
                        ids.InsertNextId(id)
                        lastId = id
                    else:
                        ids.InsertNextId(lastId)
                        id = points.InsertNextPoint(i, j, -1*(k + 1)/5.0)
                        ids.InsertNextId(id)
                        lastId = id
                    Layer.InsertNextValue(k)
                    
                    self.ds.InsertNextCell(vtk.VTK_LINE, ids)

        self.ds.GetCellData().AddArray(Layer)
        self.ds.GetCellData().AddArray(RootDepth)
        self.ds.GetCellData().AddArray(Residuals)
        self.ds.SetPoints(points)
        
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2ERothCResidualFilterTestsInput.vtp")
        pwriter.SetInput(self.ds)
        pwriter.Write()
        
    def test1Model(self):
        
        model = vtkTAG2ERothCResidualFilter()
        model.SetInput(self.ds)
        model.Update()
        
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2ERothCResidualFilterTests.vtp")
        pwriter.SetInputConnection(model.GetOutputPort())
        pwriter.Write()
        
        print model.GetOutput()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ERothCResidualFilterTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
