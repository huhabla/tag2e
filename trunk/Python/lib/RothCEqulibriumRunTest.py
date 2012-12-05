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
from libvtkGRASSBridgeCommonPython import *

from RothCEqulibriumRun import *

class RothCEquilibriumRunTest(unittest.TestCase):

    def test1(self):
        
        
        # Create the point data
        xext = 10
        yext = 10
        num = xext*yext
        
        GlobalRadiationArray = vtkDoubleArray()
        GlobalRadiationArray.SetNumberOfTuples(num)
        GlobalRadiationArray.SetName("GlobalRadiation")
        GlobalRadiationArray.FillComponent(0, 400)
        
        MeanTemperatureArray = vtkDoubleArray()
        MeanTemperatureArray.SetNumberOfTuples(num)
        MeanTemperatureArray.SetName("MeanTemperature")
        MeanTemperatureArray.FillComponent(0, 8.3)
        
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
        ClayArray.FillComponent(0, 3)
        
        SoilCarbonArray = vtkDoubleArray()
        SoilCarbonArray.SetNumberOfTuples(num)
        SoilCarbonArray.SetName("SoilCarbon")
        SoilCarbonArray.FillComponent(0, 25.0)
        
        InitialSoilCarbonArray = vtkDoubleArray()
        InitialSoilCarbonArray.SetNumberOfTuples(num)
        InitialSoilCarbonArray.SetName("InitialCarbon")
        InitialSoilCarbonArray.FillComponent(0, 25.0)
        
        ResidualsArray = vtkDoubleArray()
        ResidualsArray.SetNumberOfTuples(num)
        ResidualsArray.SetName("Residuals")
        ResidualsArray.FillComponent(0, 1)
        
        type_ = vtkIntArray()
        type_.SetNumberOfTuples(num)
        type_.SetName("type")
        
        # Point ids for poly vertex cell
        points = vtkPoints()
        
        Input = vtkPolyData()
        Input.Allocate(xext,yext)
        
        Residuals = vtkPolyData()
        Residuals.Allocate(xext,yext)
        
        SoilCarbon = vtkPolyData()
        SoilCarbon.Allocate(xext,yext)
        
        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()
                ids.InsertNextId(points.InsertNextPoint(i, j, 0))
                ids.InsertNextId(points.InsertNextPoint(i, j, 0.23))
                Input.InsertNextCell(vtk.VTK_LINE, ids)
                Residuals.InsertNextCell(vtk.VTK_LINE, ids)
                SoilCarbon.InsertNextCell(vtk.VTK_LINE, ids)
        
        Input.GetCellData().AddArray(GlobalRadiationArray)
        Input.GetCellData().AddArray(MeanTemperatureArray)
        Input.GetCellData().AddArray(PrecipitationArray)
        Input.GetCellData().AddArray(SoilCoverArray)
        Input.GetCellData().AddArray(ClayArray)
        Input.GetCellData().AddArray(InitialSoilCarbonArray) 
        Input.SetPoints(points)    
        
        Residuals.GetCellData().SetScalars(ResidualsArray)
        Residuals.SetPoints(points)    
        
        SoilCarbon.GetCellData().SetScalars(SoilCarbonArray)
        SoilCarbon.SetPoints(points)   
        
        Inputs = []
        ResidualsInput = Residuals
        SoilCarbonInput = SoilCarbon
        
        for month in range(0, 12):
          Inputs.append(Input)
        
        new_ds = RothCEquilibriumRun(Inputs=Inputs, ResidualsInput=ResidualsInput, 
                                     SoilCarbonInput=SoilCarbonInput, Years=300,
                                     NumberOfRuns=10)
        
        writer = vtkPolyDataWriter()
        writer.SetInput(new_ds)
        writer.SetFileName("/tmp/RothCEqulibirumTest1.vtk")
        writer.Write()

if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(RothCEquilibriumRunTest)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
