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

from RothCEqulibriumRun import *

class RothCEquilibriumRunTest(unittest.TestCase):

    def setUp(self):

   
        # Create the point data
        xext = 20
        yext = 20
        num = xext*yext
                
        GlobalRadiationArray = vtkDoubleArray()
        GlobalRadiationArray.SetNumberOfTuples(num)
        GlobalRadiationArray.SetName("GlobalRadiation")
        GlobalRadiationArray.FillComponent(0, 1)
        
        MeanTemperatureArray = vtkDoubleArray()
        MeanTemperatureArray.SetNumberOfTuples(num)
        MeanTemperatureArray.SetName("MeanTemperature")
        MeanTemperatureArray.FillComponent(0, 8)
        
        PrecipitationArray = vtkDoubleArray()
        PrecipitationArray.SetNumberOfTuples(num)
        PrecipitationArray.SetName("Precipitation")
        PrecipitationArray.FillComponent(0, 50)
        
        SoilCoverArray = vtkDoubleArray()
        SoilCoverArray.SetNumberOfTuples(num)
        SoilCoverArray.SetName("SoilCover")
        SoilCoverArray.FillComponent(0, 1)
        
        ClayArray = vtkDoubleArray()
        ClayArray.SetNumberOfTuples(num)
        ClayArray.SetName("Clay")
        ClayArray.FillComponent(0, 30)
        
        FertilizerCarbonArray = vtkDoubleArray()
        FertilizerCarbonArray.SetNumberOfTuples(num)
        FertilizerCarbonArray.SetName("FertilizerCarbon")
        FertilizerCarbonArray.FillComponent(0, 0.0)

        SoilCarbonArray = vtkDoubleArray()
        SoilCarbonArray.SetNumberOfTuples(num)
        SoilCarbonArray.SetName("SoilCarbon")
        SoilCarbonArray.FillComponent(0, 5)
        
        ResidualsArray = vtkDoubleArray()
        ResidualsArray.SetNumberOfTuples(num)
        ResidualsArray.SetName("Residuals")
        ResidualsArray.FillComponent(0, 0.4)
        
        type_ = vtkIntArray()
        type_.SetNumberOfTuples(num)
        type_.SetName("type")
        
        # Point ids for poly vertex cell
        points = vtkPoints()
 
        self.ETpot = vtkPolyData()
        self.ETpot.Allocate(xext,yext)
  
        self.WaterBudget = vtkPolyData()
        self.WaterBudget.Allocate(xext,yext)
        
        self.RothC = vtkPolyData()
        self.RothC.Allocate(xext,yext)
        
        self.Residuals = vtkPolyData()
        self.Residuals.Allocate(xext,yext)
        
        self.SoilCarbon = vtkPolyData()
        self.SoilCarbon.Allocate(xext,yext)
      
        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()
                ids.InsertNextId(points.InsertNextPoint(i, j, 0))
                ids.InsertNextId(points.InsertNextPoint(i, j, 0.23))
                self.ETpot.InsertNextCell(vtk.VTK_LINE, ids)
                self.WaterBudget.InsertNextCell(vtk.VTK_LINE, ids)
                self.RothC.InsertNextCell(vtk.VTK_LINE, ids)
                self.Residuals.InsertNextCell(vtk.VTK_LINE, ids)
                self.SoilCarbon.InsertNextCell(vtk.VTK_LINE, ids)

        self.ETpot.GetCellData().AddArray(GlobalRadiationArray)
        self.ETpot.GetCellData().AddArray(MeanTemperatureArray)
        self.ETpot.SetPoints(points)    
        
        self.WaterBudget.GetCellData().AddArray(PrecipitationArray)
        self.WaterBudget.GetCellData().AddArray(SoilCoverArray)
        self.WaterBudget.GetCellData().AddArray(ClayArray)
        self.WaterBudget.SetPoints(points) 
           
        self.RothC.GetCellData().AddArray(ClayArray) 
        self.RothC.GetCellData().AddArray(SoilCoverArray) 
        self.RothC.GetCellData().AddArray(MeanTemperatureArray)
        self.RothC.GetCellData().AddArray(FertilizerCarbonArray)
        self.RothC.SetPoints(points)    
        
        self.Residuals.GetCellData().SetScalars(ResidualsArray)
        self.Residuals.SetPoints(points)    
        
        self.SoilCarbon.GetCellData().SetScalars(SoilCarbonArray)
        self.SoilCarbon.SetPoints(points)    
        
    def test1(self):
        
      ETpotInputs = []
      WaterBudgetInputs = []
      RothCInputs = []
      ResidualsInput = self.Residuals
      SoilCarbonInput = self.SoilCarbon
      
      for month in range(0, 12):
          ETpotInputs.append(self.ETpot)
          WaterBudgetInputs.append(self.WaterBudget)
          RothCInputs.append(self.RothC)
      
      new_ds = RothCEquilibriumRun(ETpotInputs, WaterBudgetInputs, RothCInputs, 
                        ResidualsInput, SoilCarbonInput, 300, 100,
                        None, -99999)

      writer = vtkPolyDataWriter()
      writer.SetInput(new_ds)
      writer.SetFileName("/tmp/RothCEqulibirumTest.vtk")
      writer.Write()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(RothCEquilibriumRunTest)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
