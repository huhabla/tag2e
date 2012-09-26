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
#"""!Compute the RothC soil carbon equilibrium
#
#   @param ETpotInputs: A list of 12 inputs, each the long term parameter
#                      for ETpot computation.
#                      - Long term monthly temperature mean [°C]
#                      - Long term monthly global radiation [J/(cm² * day)]
#   
#   @param WaterBudgetInputs: A list of 12 inputs, each the long term 
#                      parameter for Water Budget computation.
#                      - Long term monthly accumulated precipitation [mm]
#                      - Long term monthly soil cover (0 or 1) [-]
#                      - Clay content in percent [%]
#   
#   param RothCInputs: A list of 12 vtkPolyData inputs, each the long term
#                      parameter of the RothC model
#                      - Clay content in percent [%]
#                      - Long term monthly soil cover (0 or 1) [-]
#                      - Long term monthly temperature mean [°C]
#                      - Long term monthly fertilizer carbon (should be 0)
#                      
#   param ResidualsInput: The initial residuals as vtkPolyData input
#                      for the the RothC model [tC/ha]
#                      
#   @param Years: The maximum number of Iterations (years) for a single run
#   @param NumberOfRuns: The maximum number of runs to find the equilibrium
#   @param RothCParameter: The parameter object for the RothC Model
#   @param NullValue: The Null value that represents unknown values
#   
#   @return A vtkPolyDataSet with RothC pools and initial Carbon
#"""  
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
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(BootstrapAggregationTest)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
