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
from libvtkGRASSBridgeTemporalPython import *
from libvtkGRASSBridgeCommonPython import *
import BootstrapAggregating as ba 

class BootstrapAggregationTest(unittest.TestCase):
  
    def setUp(self):
        
        # Create the point data
        xext = 5
        yext = 4
        num = xext*yext
                
        pH = vtkDoubleArray()
        pH.SetNumberOfTuples(num)
        pH.SetName("pH")
        
        type_ = vtkIntArray()
        type_.SetNumberOfTuples(num)
        type_.SetName("type")
        
        # Point ids for poly vertex cell
        points = vtkPoints()
 
        self.ds1 = vtkPolyData()
        self.ds1.Allocate(xext,yext)
  
        self.ds2 = vtkPolyData()
        self.ds2.Allocate(xext,yext)
      
        count = 0
        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()
                id_ = points.InsertNextPoint(i + j, j, 0)
                ids.InsertNextId(id_)
                type_.SetTuple1(count, i)
                pH.SetTuple1(count, count)
                self.ds1.InsertNextCell(vtk.VTK_VERTEX, ids)
                self.ds2.InsertNextCell(vtk.VTK_VERTEX, ids)
                count += 1

        self.ds1.GetCellData().SetScalars(pH)
        self.ds1.GetCellData().AddArray(type_)
        self.ds1.SetPoints(points)    

        self.ds2.GetPointData().SetScalars(pH)
        self.ds2.GetPointData().AddArray(type_)
        self.ds2.SetPoints(points)    

        writer = vtkPolyDataWriter()
        writer.SetInput(self.ds1)
        writer.SetFileName("/tmp/ba_1a.vtk")
        writer.Write()
 
        writer = vtkPolyDataWriter()
        writer.SetInput(self.ds2)
        writer.SetFileName("/tmp/ba_1b.vtk")
        writer.Write()
        
       
    def test1(self):

      new_ds = ba.CellSampling(self.ds1)

      writer = vtkPolyDataWriter()
      writer.SetInput(new_ds)
      writer.SetFileName("/tmp/ba_2a.vtk")
      writer.Write()
        
    def otest2(self):

      new_ds = ba.PointSampling(self.ds2)

      writer = vtkPolyDataWriter()
      writer.SetInput(new_ds)
      writer.SetFileName("/tmp/ba_2b.vtk")
      writer.Write()
        
    def test3(self):

      new_ds = ba.CellSampling(self.ds1, "type")

      writer = vtkPolyDataWriter()
      writer.SetInput(new_ds)
      writer.SetFileName("/tmp/ba_3a.vtk")
      writer.Write()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(BootstrapAggregationTest)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
