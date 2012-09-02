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

class vtkTAG2ERothCModelTests(unittest.TestCase):
  
    def setUp(self):

        # Create the point data
        xext = 10
        yext = 10
        num = xext*yext

        self.ds1 = vtkPolyData()
        self.ds1.Allocate(xext,yext)
        
        self.ds2 = vtkPolyData()
        self.ds2.Allocate(xext,yext)
        
        self.ds3 = vtkPolyData()
        self.ds3.Allocate(xext,yext)

        Clay = vtkDoubleArray()
        Clay.SetNumberOfTuples(num)
        Clay.SetName("Clay")
        Clay.FillComponent(0, 20)
        
        # ETpot
        MeanTemperature = vtkDoubleArray()
        MeanTemperature.SetNumberOfTuples(num)
        MeanTemperature.SetName("MeanTemperature")
        MeanTemperature.FillComponent(0, 12)

        GlobalRadiation = vtkDoubleArray()
        GlobalRadiation.SetNumberOfTuples(num)
        GlobalRadiation.SetName("GlobalRadiation")
        GlobalRadiation.FillComponent(0, 1)
        
        # Water Budget
        Precipitation = vtkDoubleArray()
        Precipitation.SetNumberOfTuples(num)
        Precipitation.SetName("Precipitation")
        Precipitation.FillComponent(0, 12)

        SoilCover = vtkDoubleArray()
        SoilCover.SetNumberOfTuples(num)
        SoilCover.SetName("SoilCover")
        SoilCover.FillComponent(0, 1)

        UsableWaterContent = vtkDoubleArray()
        UsableWaterContent.SetNumberOfTuples(num)
        UsableWaterContent.SetName("UsableWaterContent")
        UsableWaterContent.FillComponent(0, 0.7)
        
        # RothC
        SoilCover = vtkDoubleArray()
        SoilCover.SetNumberOfTuples(num)
        SoilCover.SetName("SoilCover")
        SoilCover.FillComponent(0, 1)

        ResidualsRoots = vtkDoubleArray()
        ResidualsRoots.SetNumberOfTuples(num)
        ResidualsRoots.SetName("ResidualsRoots")
        ResidualsRoots.FillComponent(0, 0.3)

        ResidualsSurface = vtkDoubleArray()
        ResidualsSurface.SetNumberOfTuples(num)
        ResidualsSurface.SetName("ResidualsSurface")
        ResidualsSurface.FillComponent(0, 0.7)

        PlantID = vtkDoubleArray()
        PlantID.SetNumberOfTuples(num)
        PlantID.SetName("PlantID")
        PlantID.FillComponent(0, 0)

        FertilizerID = vtkDoubleArray()
        FertilizerID.SetNumberOfTuples(num)
        FertilizerID.SetName("FertilizerID")
        FertilizerID.FillComponent(0, 0)

        FieldCapacity = vtkDoubleArray()
        FieldCapacity.SetNumberOfTuples(num)
        FieldCapacity.SetName("UsableFieldCapacity")
        FieldCapacity.FillComponent(0, 0.5)

        FertilizerCarbon = vtkDoubleArray()
        FertilizerCarbon.SetNumberOfTuples(num)
        FertilizerCarbon.SetName("FertilizerCarbon")
        FertilizerCarbon.FillComponent(0, 0.5)

        InitialCarbon = vtkDoubleArray()
        InitialCarbon.SetNumberOfTuples(num)
        InitialCarbon.SetName("InitialCarbon")
        InitialCarbon.FillComponent(0, 40)

        # Point ids for poly vertex cell
        points = vtkPoints()

        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()
                ids.InsertNextId(points.InsertNextPoint(i, j, 0))
                ids.InsertNextId(points.InsertNextPoint(i, j, 0.23))
                self.ds1.InsertNextCell(vtk.VTK_LINE, ids)
                self.ds2.InsertNextCell(vtk.VTK_LINE, ids)
                self.ds3.InsertNextCell(vtk.VTK_LINE, ids)

        self.ds1.SetPoints(points)
        self.ds2.SetPoints(points)
        self.ds3.SetPoints(points)
        
        self.ds1.GetCellData().AddArray(Clay)
        self.ds1.GetCellData().AddArray(MeanTemperature)
        self.ds1.GetCellData().AddArray(SoilCover)
        self.ds1.GetCellData().AddArray(ResidualsRoots)
        self.ds1.GetCellData().AddArray(ResidualsSurface)
        self.ds1.GetCellData().AddArray(PlantID)
        self.ds1.GetCellData().AddArray(FertilizerID)
        self.ds1.GetCellData().AddArray(FieldCapacity)
        self.ds1.GetCellData().AddArray(FertilizerCarbon)
        self.ds1.GetCellData().AddArray(InitialCarbon)
        
        self.ds2.GetCellData().AddArray(Precipitation)
        self.ds2.GetCellData().AddArray(SoilCover)
        self.ds2.GetCellData().AddArray(UsableWaterContent)
        
        self.ds3.GetCellData().AddArray(MeanTemperature)
        self.ds3.GetCellData().AddArray(GlobalRadiation)
        
    def test1Model(self):
        
        # Compute potential evapo-transpiration
        ETpot = vtkTAG2ETurcETPotModel()
        ETpot.SetInput(self.ds3)
        
        # Soil moisture input
        dc1 = vtkTAG2EDataSetJoinFilter()
        dc1.AddInputConnection(ETpot.GetOutputPort())
        dc1.AddInput(self.ds2)
        
        # Soil moisture computation
        SoilMoisture = vtkTAG2ERothCWaterBudgetModel()
        SoilMoisture.SetInputConnection(dc1.GetOutputPort())
        
        # RothC input
        dc2 = vtkTAG2EDataSetJoinFilter()
        dc2.AddInputConnection(SoilMoisture.GetOutputPort())
        dc2.AddInput(self.ds1)
        
        
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2ERothCModelTestsInput.vtp")
        pwriter.SetInputConnection(dc2.GetOutputPort())
        pwriter.Write()
        
        # RothC model computation
        rp = vtkTAG2ERothCModelParameter()

        RothC = vtkTAG2ERothCModel()
        RothC.SetModelParameter(rp)
        RothC.AddCPoolsToOutputOn()
        RothC.CPoolsInitiatedOn()
        RothC.SetInputConnection(dc2.GetOutputPort())
        RothC.Update()
        
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2ERothCModelTestsResult.vtp")
        pwriter.SetInputConnection(RothC.GetOutputPort())
        pwriter.Write()
        
        print RothC.GetOutput()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ERothCModelTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
