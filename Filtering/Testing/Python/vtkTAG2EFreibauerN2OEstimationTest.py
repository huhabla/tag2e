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

from libvtkFilteringPython import *
from libvtkIOPython import *
from libvtkImagingPython import *
from libvtkCommonPython import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *

class vtkTAG2EDImageDataN2OFilterFreibauerTest(unittest.TestCase):
    def setUp(self):

        size = 499

        self.nrate = vtkImageData()
        self.nrate.SetExtent(0, size, 0, size, 0, 0)
        self.nrate.AllocateScalars ()
        self.nrate.GetPointData().GetScalars().FillComponent(0,500)

        self.sand = vtkImageData()
        self.sand.SetExtent(0, size, 0, size, 0, 0)
        self.sand.AllocateScalars ()
        self.sand.GetPointData().GetScalars().FillComponent(0,20)

        self.soilC = vtkImageData()
        self.soilC.SetExtent(0, size, 0, size, 0, 0)
        self.soilC.AllocateScalars ()
        self.soilC.GetPointData().GetScalars().FillComponent(0,20)

        self.soilN = vtkImageData()
        self.soilN.SetExtent(0, size, 0, size, 0, 0)
        self.soilN.AllocateScalars ()
        self.soilN.GetPointData().GetScalars().FillComponent(0,20)

        self.croptype = vtkImageData()
        self.croptype.SetExtent(0, size, 0, size, 0, 0)
        self.croptype.AllocateScalars ()
        self.croptype.GetPointData().GetScalars().FillComponent(0,1)

        self.climate = vtkImageData()
        self.climate.SetExtent(0, size, 0, size, 0, 0)
        self.climate.AllocateScalars ()
        self.climate.GetPointData().GetScalars().FillComponent(0,1)

        print "Number of points", self.climate.GetNumberOfPoints()
        print "Data dimension: ", self.climate.GetDataDimension()

    def testSmoke(self):

        model = vtkTAG2EDImageDataN2OFilterFreibauer()
        model.SetNitrogenRate(self.nrate)
        model.SetSandFraction(self.sand)
        model.SetSoilOrganicCorbon(self.soilC)
        model.SetSoilNitrogen(self.soilN)
        model.SetCropType(self.croptype)
        model.SetClimateType(self.climate)
        model.SetNumberOfThreads(6)
        model.Update()

        print model.GetOutput()
        print model.GetOutput().GetPointData().GetScalars().GetRange()

class vtkTAG2EDataSetN2OFilterFreibauerTest(unittest.TestCase):
    def setUp(self):

        xt = 500
        yt = 500
        tuples = xt * yt

        self.nrate = vtkDoubleArray()
        self.nrate.SetNumberOfTuples(tuples)
        self.nrate.SetName("nrate")
        self.nrate.FillComponent(0,500)

        self.sand = vtkDoubleArray()
        self.sand.SetNumberOfTuples(tuples)
        self.sand.SetName("sand")
        self.sand.FillComponent(0,20)

        self.soilC = vtkDoubleArray()
        self.soilC.SetNumberOfTuples(tuples)
        self.soilC.SetName("soilC")
        self.soilC.FillComponent(0,20)

        self.soilN = vtkDoubleArray()
        self.soilN.SetNumberOfTuples(tuples)
        self.soilN.SetName("soilN")
        self.soilN.FillComponent(0,20)

        self.croptype = vtkDoubleArray()
        self.croptype.SetNumberOfTuples(tuples)
        self.croptype.SetName("croptype")
        self.croptype.FillComponent(0,1)
        
        self.climate = vtkDoubleArray()
        self.climate.SetNumberOfTuples(tuples)
        self.climate.SetName("climate")
        self.climate.FillComponent(0,1)

        self.cats = vtkIntArray()
        self.cats.SetNumberOfTuples(tuples)
        self.cats.SetName("cats")
        self.cats.FillComponent(0,0)

        self.data = vtkPolyData()
        self.data.Allocate(5,5)
        self.data.GetPointData().AddArray(self.nrate)
        self.data.GetPointData().AddArray(self.soilC)
        self.data.GetPointData().AddArray(self.soilN)
        self.data.GetPointData().AddArray(self.sand)
        self.data.GetPointData().AddArray(self.croptype)
        self.data.GetPointData().AddArray(self.climate)
        self.data.GetPointData().AddArray(self.cats)

        self.points = vtkPoints()
        
        count = 0
        for i in range(xt):
            for j in range(yt):
                self.points.InsertNextPoint(i, j, 0)
                self.cats.InsertValue(count, i*j + 5000)
                count = count + 1

        self.data.SetPoints(self.points)

        print "Number of points", self.data.GetNumberOfPoints()

    def testSmoke(self):

        model = vtkTAG2EDataSetN2OFilterFreibauer()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSandFractionArrayName(self.sand.GetName())
        model.SetSoilOrganicCorbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeArrayName(self.croptype.GetName())
        model.SetClimateTypeArrayName(self.climate.GetName())
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput()
        print model.GetOutput().GetPointData().GetScalars().GetRange()

        #writer = vtkPolyDataWriter()
        #writer.SetFileName("/tmp/1.vtk")
        #writer.SetInput(model.GetOutput())
        #writer.Write()


if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDImageDataN2OFilterFreibauerTest)
    suite2= unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDataSetN2OFilterFreibauerTest)
    unittest.TextTestRunner(verbosity=2).run(suite1)
    unittest.TextTestRunner(verbosity=2).run(suite2)
