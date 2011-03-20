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

class vtkTAG2EDImageDataN2OFilterTest(unittest.TestCase):
    def setUp(self):

        size = 55

        self.nrate = vtkImageData()
        self.nrate.SetExtent(0, size, 0, size, 0, 0)
        self.nrate.AllocateScalars ()
        self.nrate.GetPointData().GetScalars().FillComponent(0,100)

        self.sand = vtkImageData()
        self.sand.SetExtent(0, size, 0, size, 0, 0)
        self.sand.AllocateScalars ()
        self.sand.GetPointData().GetScalars().FillComponent(0,20)

        self.silt = vtkImageData()
        self.silt.SetExtent(0, size, 0, size, 0, 0)
        self.silt.AllocateScalars ()
        self.silt.GetPointData().GetScalars().FillComponent(0,20)

        self.clay = vtkImageData()
        self.clay.SetExtent(0, size, 0, size, 0, 0)
        self.clay.AllocateScalars ()
        self.clay.GetPointData().GetScalars().FillComponent(0,20)

        self.soilC = vtkImageData()
        self.soilC.SetExtent(0, size, 0, size, 0, 0)
        self.soilC.AllocateScalars ()
        self.soilC.GetPointData().GetScalars().FillComponent(0,20)

        self.soilN = vtkImageData()
        self.soilN.SetExtent(0, size, 0, size, 0, 0)
        self.soilN.AllocateScalars ()
        self.soilN.GetPointData().GetScalars().FillComponent(0,20)

        self.T_win = vtkImageData()
        self.T_win.SetExtent(0, size, 0, size, 0, 0)
        self.T_win.AllocateScalars ()
        self.T_win.GetPointData().GetScalars().FillComponent(0,1)

        self.T_spring = vtkImageData()
        self.T_spring.SetExtent(0, size, 0, size, 0, 0)
        self.T_spring.AllocateScalars ()
        self.T_spring.GetPointData().GetScalars().FillComponent(0,10)

        self.P_sum = vtkImageData()
        self.P_sum.SetExtent(0, size, 0, size, 0, 0)
        self.P_sum.AllocateScalars ()
        self.P_sum.GetPointData().GetScalars().FillComponent(0,600)

        self.pH = vtkImageData()
        self.pH.SetExtent(0, size, 0, size, 0, 0)
        self.pH.AllocateScalars ()
        self.pH.GetPointData().GetScalars().FillComponent(0,7)

    def testFreibauerGrassTemperate(self):

        model = vtkTAG2EImageDataN2OFilterFreibauer()
        model.SetNitrogenRate(self.nrate)
        model.SetSandFraction(self.sand)
        model.SetSoilOrganicCarbon(self.soilC)
        model.SetSoilNitrogen(self.soilN)
        model.SetCropTypeToGrass()
        model.SetClimateTypeToTemperate()
        model.SetNumberOfThreads(6)
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testFreibauerGrassSubBoreal(self):

        model = vtkTAG2EImageDataN2OFilterFreibauer()
        model.SetNitrogenRate(self.nrate)
        model.SetSandFraction(self.sand)
        model.SetSoilOrganicCarbon(self.soilC)
        model.SetSoilNitrogen(self.soilN)
        model.SetCropTypeToGrass()
        model.SetClimateTypeToSubBoreal()
        model.SetNumberOfThreads(6)
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testFreibauerOtherSubBoreal(self):

        model = vtkTAG2EImageDataN2OFilterFreibauer()
        model.SetNitrogenRate(self.nrate)
        model.SetSandFraction(self.sand)
        model.SetSoilOrganicCarbon(self.soilC)
        model.SetSoilNitrogen(self.soilN)
        model.SetCropTypeToOther()
        model.SetClimateTypeToSubBoreal()
        model.SetNumberOfThreads(6)
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testFreibauerOtherTemperate(self):

        model = vtkTAG2EImageDataN2OFilterFreibauer()
        model.SetNitrogenRate(self.nrate)
        model.SetSandFraction(self.sand)
        model.SetSoilOrganicCarbon(self.soilC)
        model.SetSoilNitrogen(self.soilN)
        model.SetCropTypeToOther()
        model.SetClimateTypeToTemperate()
        model.SetNumberOfThreads(6)
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

class vtkTAG2EDataSetN2OFilterTest(unittest.TestCase):
    def setUp(self):

        xt = 60
        yt = 50
        tuples = xt * yt

        self.nrate = vtkDoubleArray()
        self.nrate.SetNumberOfTuples(tuples)
        self.nrate.SetName("nrate")
        self.nrate.FillComponent(0,100)

        self.sand = vtkDoubleArray()
        self.sand.SetNumberOfTuples(tuples)
        self.sand.SetName("sand")
        self.sand.FillComponent(0,20)

        self.silt = vtkDoubleArray()
        self.silt.SetNumberOfTuples(tuples)
        self.silt.SetName("silt")
        self.silt.FillComponent(0,20)

        self.clay = vtkDoubleArray()
        self.clay.SetNumberOfTuples(tuples)
        self.clay.SetName("clay")
        self.clay.FillComponent(0,20)

        self.T_win = vtkDoubleArray()
        self.T_win.SetNumberOfTuples(tuples)
        self.T_win.SetName("T_win")
        self.T_win.FillComponent(0,1)

        self.T_spring = vtkDoubleArray()
        self.T_spring.SetNumberOfTuples(tuples)
        self.T_spring.SetName("T_spring")
        self.T_spring.FillComponent(0,10)

        self.P_sum = vtkDoubleArray()
        self.P_sum.SetNumberOfTuples(tuples)
        self.P_sum.SetName("P_sum")
        self.P_sum.FillComponent(0,600)

        self.pH = vtkDoubleArray()
        self.pH.SetNumberOfTuples(tuples)
        self.pH.SetName("pH")
        self.pH.FillComponent(0,600)

        self.soilC = vtkDoubleArray()
        self.soilC.SetNumberOfTuples(tuples)
        self.soilC.SetName("soilC")
        self.soilC.FillComponent(0,20)

        self.soilN = vtkDoubleArray()
        self.soilN.SetNumberOfTuples(tuples)
        self.soilN.SetName("soilN")
        self.soilN.FillComponent(0,20)

        self.cats = vtkIntArray()
        self.cats.SetNumberOfTuples(tuples)
        self.cats.SetName("cats")
        self.cats.FillComponent(0,0)

        self.data = vtkPolyData()
        self.data.Allocate(5,5)
        self.data.GetPointData().AddArray(self.nrate)
        self.data.GetPointData().AddArray(self.silt)
        self.data.GetPointData().AddArray(self.clay)
        self.data.GetPointData().AddArray(self.T_win)
        self.data.GetPointData().AddArray(self.T_spring)
        self.data.GetPointData().AddArray(self.P_sum)
        self.data.GetPointData().AddArray(self.soilC)
        self.data.GetPointData().AddArray(self.soilN)
        self.data.GetPointData().AddArray(self.sand)
        self.data.GetPointData().AddArray(self.cats)
        self.data.GetPointData().AddArray(self.pH)

        self.points = vtkPoints()
        
        count = 0
        for i in range(xt):
            for j in range(yt):
                self.points.InsertNextPoint(i, j, 0)
                self.cats.InsertValue(count, i*j + 5000)
                count = count + 1

        self.data.SetPoints(self.points)

    def testFreibauerGrassTemperate(self):

        model = vtkTAG2EDataSetN2OFilterFreibauer()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSandFractionArrayName(self.sand.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToGrass()
        model.SetClimateTypeToTemperate()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testFreibauerGrassSubBoreal(self):

        model = vtkTAG2EDataSetN2OFilterFreibauer()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSandFractionArrayName(self.sand.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToGrass()
        model.SetClimateTypeToSubBoreal()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testFreibauerOtherTemperate(self):

        model = vtkTAG2EDataSetN2OFilterFreibauer()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSandFractionArrayName(self.sand.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToOther()
        model.SetClimateTypeToTemperate()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testFreibauerOtherSubBoreal(self):

        model = vtkTAG2EDataSetN2OFilterFreibauer()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSandFractionArrayName(self.sand.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToOther()
        model.SetClimateTypeToSubBoreal()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testRoelandtGrass(self):

        model = vtkTAG2EDataSetN2OFilterRoelandt()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetTempWinterArrayName(self.T_win.GetName())
        model.SetTempSpringArrayName(self.T_spring.GetName())
        model.SetPrecipitationSumArrayName(self.P_sum.GetName())
        model.SetCropTypeToGrass()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testRoelandtOther(self):

        model = vtkTAG2EDataSetN2OFilterRoelandt()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetTempWinterArrayName(self.T_win.GetName())
        model.SetTempSpringArrayName(self.T_spring.GetName())
        model.SetPrecipitationSumArrayName(self.P_sum.GetName())
        model.SetCropTypeToOther()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()
                
    def testStehfestGrassBoreal(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToGrass()
        model.SetClimateTypeToBoreal()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestGrassContinental(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToGrass()
        model.SetClimateTypeToContinental()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestGrassOceanic(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToGrass()
        model.SetClimateTypeToOceanic()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestGrassSubTropic(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToGrass()
        model.SetClimateTypeToSubTropic()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestGrassTropic(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToGrass()
        model.SetClimateTypeToTropic()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestGCerealsBoreal(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToCereals()
        model.SetClimateTypeToBoreal()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestFallowBoreal(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToFallow()
        model.SetClimateTypeToBoreal()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestLegumeBoreal(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToLegume()
        model.SetClimateTypeToBoreal()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestRootsBoreal(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToRoots()
        model.SetClimateTypeToBoreal()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestVegtBoral(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToVegetables()
        model.SetClimateTypeToBoreal()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testStehfestOtherBoreal(self):

        model = vtkTAG2EDataSetN2OFilterStehfest()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetSiltFractionArrayName(self.silt.GetName())
        model.SetClayFractionArrayName(self.clay.GetName())
        model.SetpHArrayName(self.pH.GetName())
        model.SetSoilOrganicCarbonArrayName(self.soilC.GetName())
        model.SetSoilNitrogenArrayName(self.soilN.GetName())
        model.SetCropTypeToOther()
        model.SetClimateTypeToBoreal()
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

    def testBouwman(self):

        model = vtkTAG2EDataSetN2OFilterBouwman()
        model.SetInput(self.data)
        model.SetNitrogenRateArrayName(self.nrate.GetName())
        model.SetCategoryArrayName(self.cats.GetName())
        model.UsePointDataOn()
        model.Update()

        print model.GetOutput().GetPointData().GetScalars().GetRange()

if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDImageDataN2OFilterTest)
    suite2= unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDataSetN2OFilterTest)
    unittest.TextTestRunner(verbosity=2).run(suite1)
    unittest.TextTestRunner(verbosity=2).run(suite2)
