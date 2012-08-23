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

        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)

        self.Clay = vtkDoubleArray()
        self.Clay.SetNumberOfTuples(num)
        self.Clay.SetName("Clay")
        self.Clay.FillComponent(0, 45)

        self.MeanTemperature = vtkDoubleArray()
        self.MeanTemperature.SetNumberOfTuples(num)
        self.MeanTemperature.SetName("MeanTemperature")
        self.MeanTemperature.FillComponent(0, 12)

        self.SoilCover = vtkDoubleArray()
        self.SoilCover.SetNumberOfTuples(num)
        self.SoilCover.SetName("SoilCover")
        self.SoilCover.FillComponent(0, 1)

        self.ResidualsRoots = vtkDoubleArray()
        self.ResidualsRoots.SetNumberOfTuples(num)
        self.ResidualsRoots.SetName("ResidualsRoots")
        self.ResidualsRoots.FillComponent(0, 10)

        self.ResidualsSurface = vtkDoubleArray()
        self.ResidualsSurface.SetNumberOfTuples(num)
        self.ResidualsSurface.SetName("ResidualsSurface")
        self.ResidualsSurface.FillComponent(0, 20)

        self.PlantID = vtkDoubleArray()
        self.PlantID.SetNumberOfTuples(num)
        self.PlantID.SetName("PlantID")
        self.PlantID.FillComponent(0, 0)

        self.FertilizerID = vtkDoubleArray()
        self.FertilizerID.SetNumberOfTuples(num)
        self.FertilizerID.SetName("FertilizerID")
        self.FertilizerID.FillComponent(0, 0)

        self.SoilMoisture = vtkDoubleArray()
        self.SoilMoisture.SetNumberOfTuples(num)
        self.SoilMoisture.SetName("SoilMoisture")
        self.SoilMoisture.FillComponent(0, 30)

        self.FieldCapacity = vtkDoubleArray()
        self.FieldCapacity.SetNumberOfTuples(num)
        self.FieldCapacity.SetName("FieldCapacity")
        self.FieldCapacity.FillComponent(0, 0.5)

        self.FertilizerCarbon = vtkDoubleArray()
        self.FertilizerCarbon.SetNumberOfTuples(num)
        self.FertilizerCarbon.SetName("FertilizerCarbon")
        self.FertilizerCarbon.FillComponent(0, 50)

        self.InitialCarbon = vtkDoubleArray()
        self.InitialCarbon.SetNumberOfTuples(num)
        self.InitialCarbon.SetName("InitialCarbon")
        self.InitialCarbon.FillComponent(0, 10)

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
        self.ds.GetCellData().AddArray(self.SoilCover)
        self.ds.GetCellData().AddArray(self.ResidualsRoots)
        self.ds.GetCellData().AddArray(self.ResidualsSurface)
        self.ds.GetCellData().AddArray(self.PlantID)
        self.ds.GetCellData().AddArray(self.FertilizerID)
        self.ds.GetCellData().AddArray(self.SoilMoisture)
        self.ds.GetCellData().AddArray(self.FieldCapacity)
        self.ds.GetCellData().AddArray(self.FertilizerCarbon)
        self.ds.GetCellData().AddArray(self.InitialCarbon)
        self.ds.SetPoints(points)
        
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2ERothCModelTestsInput.vtp")
        pwriter.SetInput(self.ds)
        pwriter.Write()
        
        self._BuildXML()

    def _BuildXML(self):

        self.root  = vtk.vtkXMLDataElement()
        
        a = vtkXMLDataElement()
        a.SetName("a")

        # We generate the a Parameter and make them calibratable
        for i in range(1,4):
            an = vtkXMLDataElement()
            an.SetName("a%i"%i)
            an.SetIntAttribute("const", 0)
            an.SetDoubleAttribute("min", 0)
            an.SetDoubleAttribute("max", 10)
            a.AddNestedElement(an)
        
        self.root.SetName("RothC")
        self.root.AddNestedElement(a)
        self.root.SetAttribute("name", "test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/RothC")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/RothC http://tag2e.googlecode.com/files/RothC.xsd")
        
    def test1Model(self):
        
        w = vtkTAG2ERothCModelParameter()
        w.SetXMLRepresentation(self.root)

        model = vtkTAG2ERothCModel()
        model.SetInput(self.ds)
        model.SetModelParameter(w)
        model.AddCPoolsToOutputOn()
        model.CPoolsInitiatedOn()
        model.Update()
        
        pwriter = vtkXMLPolyDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2ERothCModelTestsResult.vtp")
        pwriter.SetInputConnection(model.GetOutputPort())
        pwriter.Write()
        
        print model.GetOutput()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ERothCModelTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
