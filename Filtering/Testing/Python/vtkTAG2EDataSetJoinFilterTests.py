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

class vtkTAG2EDataSetJoinFilterTests(unittest.TestCase):
  
    def _buildPolyDataSet(self, name, value):
        # Create the point data
        xext = 10
        yext = 10
        num = xext*yext

        ds = vtkPolyData()
        ds.Allocate(xext,yext)

        # Cell data
        array1 = vtkDoubleArray()
        array1.SetNumberOfTuples(num)
        array1.SetName(name)
        array1.FillComponent(0, value)
        # Point data
        array2 = vtkDoubleArray()
        array2.SetNumberOfTuples(num*2)
        array2.SetName(name)
        array2.FillComponent(0, value)

        points = vtkPoints()

        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()
                ids.InsertNextId(points.InsertNextPoint(i, j, 0))
                ids.InsertNextId(points.InsertNextPoint(i, j, 0.23))
                ds.InsertNextCell(vtk.VTK_LINE, ids)

        ds.GetCellData().AddArray(array1)
        ds.GetPointData().AddArray(array2)
        ds.SetPoints(points)
        
        return ds
        
    def test1(self):
        
        
        ds1 = self._buildPolyDataSet("A", 1)
        ds2 = self._buildPolyDataSet("B", 2)
        ds3 = self._buildPolyDataSet("C", 3)
        ds4 = self._buildPolyDataSet("D", 4)
        ds5 = self._buildPolyDataSet("E", 5)
        
        filter = vtkTAG2EDataSetJoinFilter()
        filter.AddInput(ds1)
        filter.AddInput(ds2)
        filter.AddInput(ds3)
        filter.AddInput(ds4)
        filter.AddInput(ds5)
        
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2EDataSetJoinFilterTestsResult.vtp")
        pwriter.SetInputConnection(filter.GetOutputPort())
        pwriter.Write()
        
        if not filter.GetOutput().GetPointData().HasArray("A"):
            print "ERROR: array A not present in point data"
        if not filter.GetOutput().GetPointData().HasArray("B"):
            print "ERROR: array B not present in point data"
        if not filter.GetOutput().GetPointData().HasArray("C"):
            print "ERROR: array C not present in point data"
        if not filter.GetOutput().GetPointData().HasArray("D"):
            print "ERROR: array D not present in point data"
        if not filter.GetOutput().GetPointData().HasArray("E"):
            print "ERROR: array E not present in point data"
        
        if not filter.GetOutput().GetCellData().HasArray("A"):
            print "ERROR: array A not present in cell data"
        if not filter.GetOutput().GetCellData().HasArray("B"):
            print "ERROR: array B not present in cell data"
        if not filter.GetOutput().GetCellData().HasArray("C"):
            print "ERROR: array C not GetCellData in cell data"
        if not filter.GetOutput().GetPointData().HasArray("D"):
            print "ERROR: array D not GetCellData in cell data"
        if not filter.GetOutput().GetPointData().HasArray("E"):
            print "ERROR: array E not GetCellData in cell data"
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDataSetJoinFilterTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
