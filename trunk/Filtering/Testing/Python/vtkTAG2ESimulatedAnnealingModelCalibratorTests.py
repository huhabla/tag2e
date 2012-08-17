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
import math

from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeTemporalPython import *
from libvtkGRASSBridgeCommonPython import *

################################################################################
################################################################################
################################################################################

class vtkTAG2ESimulatedAnnealingModelCalibratorTests(unittest.TestCase):
  
    def setUp(self):
        
        # Create the point data
        xext = 100
        yext = 1
        num = xext*yext
                
        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)
        
        self.model = vtkDoubleArray()
        self.model.SetNumberOfTuples(num)
        self.model.SetName("model")
        
        self.measure = vtkDoubleArray()
        self.measure.SetNumberOfTuples(num)
        self.measure.SetName("measure")
        
        # Point ids for poly vertex cell
        points = vtkPoints()
        
        count = 0
        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()                
                ids.InsertNextId(points.InsertNextPoint(i, j, 0))
                # Data range [1:100] -> linear function x
                self.model.SetValue(count, count + 1)
                self.measure.SetValue(count, count + 1)   
                self.ds.InsertNextCell(vtk.VTK_VERTEX, ids)
                count += 1

        self.ds.GetCellData().AddArray(self.measure)
        self.ds.GetCellData().AddArray(self.model)
        self.ds.GetCellData().SetActiveScalars(self.measure.GetName())
        self.ds.SetPoints(points) 
        
        self._BuildXML()
        
    def _BuildXML(self):
        
        self.root  = vtk.vtkXMLDataElement()
        
        fss1 = vtkXMLDataElement()
        fs1 = vtkXMLDataElement()
        fs2 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr2 = vtkXMLDataElement()
        resp = vtkXMLDataElement()
        
# Triangular test shape layout
# ____    ____
#     \  /
#      \/ 
#      /\ 
#     /  \
#0  30 50 70  100
#
# - 1 -  - 3 - 
#
# 1: left = 101 center = 30 right = 40
# 2: left = 40  center = 70 right = 101
#       
        
        tr1.SetName("Triangular")
        tr1.SetDoubleAttribute("center", 30)
        tr1.SetDoubleAttribute("left",   101)
        tr1.SetDoubleAttribute("right",  40)
                
        tr2.SetName("Triangular")
        tr2.SetDoubleAttribute("center",  70)
        tr2.SetDoubleAttribute("left",    40)
        tr2.SetDoubleAttribute("right",   101)
        
        fs1.SetName("FuzzySet")
        fs1.SetAttribute("type", "Triangular")
        fs1.SetIntAttribute("priority", 0)
        fs1.SetIntAttribute("const", 0)
        fs1.SetAttribute("position", "left")
        fs1.AddNestedElement(tr1)
        
        fs2.SetName("FuzzySet")
        fs2.SetAttribute("type", "Triangular")
        fs2.SetIntAttribute("priority", 0)
        fs2.SetIntAttribute("const", 0)
        fs2.SetAttribute("position", "right")
        fs2.AddNestedElement(tr2)
        
        # A single factor
        fss1.SetName("Factor")
        fss1.SetIntAttribute("portId", 0)
        fss1.SetAttribute("name", "model")
        fss1.SetDoubleAttribute("min", 0.0)
        fss1.SetDoubleAttribute("max", 100.0)
        fss1.AddNestedElement(fs1)
        fss1.AddNestedElement(fs2)
                
        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 120)
        
        rval1 = vtkXMLDataElement()
        rval1.SetName("Response")
        rval1.SetIntAttribute("const", 0)
        rval1.SetIntAttribute("sd", 1)
        rval1.SetCharacterData(str(5), 6)
                
        rval2 = vtkXMLDataElement()
        rval2.SetName("Response")
        rval2.SetIntAttribute("const", 0)
        rval2.SetIntAttribute("sd", 1)
        rval2.SetCharacterData(str(5), 6)
        
        resp.AddNestedElement(rval1)
        resp.AddNestedElement(rval2)
                
        self.root.SetName("FuzzyInferenceScheme")
        self.root.AddNestedElement(fss1)
        self.root.AddNestedElement(resp)
        self.root.SetAttribute("name", "Test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/FuzzyInferenceScheme http://tag2e.googlecode.com/files/FuzzyInferenceScheme.xsd")
        
    def test1(self):

        self._BuildXML()

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.DebugOff()
        parameter.SetXMLRepresentation(self.root)

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInput(self.ds)
        model.SetModelParameter(parameter)
        model.UseCellDataOn()

        caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
        caliModel.SetInput(self.ds)
        caliModel.SetModel(model)
        caliModel.SetModelParameter(parameter)
        caliModel.SetMaxNumberOfIterations(100)
        caliModel.Update()

        caliModel.GetBestFitModelParameter().SetFileName("/tmp/vtkTAG2ESimulatedAnnealingModelCalibratorTests.xml")
        caliModel.GetBestFitModelParameter().Write()
        
################################################################################
################################################################################
################################################################################

class vtkTAG2ESimulatedAnnealingModelCalibratorTestsComplex(unittest.TestCase):

    def setUp(self):

        # Create the point data
        xext = 10000
        yext = 1
        num = xext*yext

        self.xarray = vtkDoubleArray()
        self.xarray.SetNumberOfTuples(num)
        self.xarray.SetName("x")

        self.yarray = vtkDoubleArray()
        self.yarray.SetNumberOfTuples(num)
        self.yarray.SetName("y")

        self.measure = vtkDoubleArray()
        self.measure.SetNumberOfTuples(num)
        self.measure.SetName("measure")

        # Point ids for poly vertex cell
        ids = vtkIdList()
        points = vtkPoints()

        count = 0
        for i in range(xext):
            for j in range(yext):
                points.InsertNextPoint(i, j, 0)
                ids.InsertNextId(count)

                x = count/100.0
                y = count/100.0
                fx = math.fabs(math.sin((x - 50)*(x - 50)/300.0) + (x - 50)/10.0)
                fy = math.fabs(math.sin((y - 50)*(y - 50)/300.0) + (y - 50)/10.0)

                # Data x and y range [-100:100]
                # Function
                self.xarray.SetValue(count,  x)
                self.yarray.SetValue(count, y)
                self.measure.SetValue(count, fx + fy)
                count += 1

        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)
        self.ds.GetPointData().SetScalars(self.measure)
        self.ds.GetPointData().AddArray(self.xarray)
        self.ds.GetPointData().AddArray(self.yarray)
        self.ds.SetPoints(points)
        self.ds.InsertNextCell(vtk.VTK_POLY_VERTEX, ids)


    def _BuildXML(self):

        self.root  = vtk.vtkXMLDataElement()

        fss1 = vtkXMLDataElement()
        fss2 = vtkXMLDataElement()
        fs11 = vtkXMLDataElement()
        fs12 = vtkXMLDataElement()
        fs13 = vtkXMLDataElement()
        tr11 = vtkXMLDataElement()
        tr12 = vtkXMLDataElement()
        tr13 = vtkXMLDataElement()

        fs21 = vtkXMLDataElement()
        fs22 = vtkXMLDataElement()
        fs23 = vtkXMLDataElement()
        tr21 = vtkXMLDataElement()
        tr22 = vtkXMLDataElement()
        tr23 = vtkXMLDataElement()

        resp = vtkXMLDataElement()

# Triangular test shape layout
#   ____        ____
#       \  /\  /
#        \/  \/
#        /\  /\
#       /  \/  \
#  0  25   50   75  100
#
#   - 1 -   2   - 3 -
#
# 1: left = 101 center = -50 right = 50
# 2: left = 50  center = 0 right = 50
# 2: left = 50  center = 50 right = 101

        tr11.SetName("Triangular")
        tr11.SetDoubleAttribute("center", 25)
        tr11.SetDoubleAttribute("left",   101)
        tr11.SetDoubleAttribute("right",  25)

        tr12.SetName("Triangular")
        tr12.SetDoubleAttribute("center",  50)
        tr12.SetDoubleAttribute("left",    25)
        tr12.SetDoubleAttribute("right",   25)

        tr13.SetName("Triangular")
        tr13.SetDoubleAttribute("center",  75)
        tr13.SetDoubleAttribute("left",    25)
        tr13.SetDoubleAttribute("right",   101)

        fs11.SetName("FuzzySet")
        fs11.SetAttribute("type", "Triangular")
        fs11.SetIntAttribute("priority", 0)
        fs11.SetIntAttribute("const", 0)
        fs11.SetAttribute("position", "left")
        fs11.AddNestedElement(tr11)

        fs12.SetName("FuzzySet")
        fs12.SetAttribute("type", "Triangular")
        fs12.SetIntAttribute("priority", 0)
        fs12.SetIntAttribute("const", 0)
        fs12.SetAttribute("position", "intermediate")
        fs12.AddNestedElement(tr12)

        fs13.SetName("FuzzySet")
        fs13.SetAttribute("type", "Triangular")
        fs13.SetIntAttribute("priority", 0)
        fs13.SetIntAttribute("const", 0)
        fs13.SetAttribute("position", "right")
        fs13.AddNestedElement(tr13)

        tr21.SetName("Triangular")
        tr21.SetDoubleAttribute("center", 25)
        tr21.SetDoubleAttribute("left",   101)
        tr21.SetDoubleAttribute("right",  25)

        tr22.SetName("Triangular")
        tr22.SetDoubleAttribute("center",  50)
        tr22.SetDoubleAttribute("left",    25)
        tr22.SetDoubleAttribute("right",   25)

        tr23.SetName("Triangular")
        tr23.SetDoubleAttribute("center",  75)
        tr23.SetDoubleAttribute("left",    25)
        tr23.SetDoubleAttribute("right",   101)

        fs21.SetName("FuzzySet")
        fs21.SetAttribute("type", "Triangular")
        fs21.SetIntAttribute("priority", 0)
        fs21.SetIntAttribute("const", 0)
        fs21.SetAttribute("position", "left")
        fs21.AddNestedElement(tr21)

        fs22.SetName("FuzzySet")
        fs22.SetAttribute("type", "Triangular")
        fs22.SetIntAttribute("priority", 0)
        fs22.SetIntAttribute("const", 0)
        fs22.SetAttribute("position", "intermediate")
        fs22.AddNestedElement(tr22)

        fs23.SetName("FuzzySet")
        fs23.SetAttribute("type", "Triangular")
        fs23.SetIntAttribute("priority", 0)
        fs23.SetIntAttribute("const", 0)
        fs23.SetAttribute("position", "right")
        fs23.AddNestedElement(tr23)

        # Two factors
        fss1.SetName("Factor")
        fss1.SetIntAttribute("portId", 0)
        fss1.SetAttribute("name", "x")
        fss1.SetDoubleAttribute("min", 0.0)
        fss1.SetDoubleAttribute("max",  100.0)
        fss1.AddNestedElement(fs11)
        fss1.AddNestedElement(fs12)
        fss1.AddNestedElement(fs13)

        fss2.SetName("Factor")
        fss2.SetIntAttribute("portId", 0)
        fss2.SetAttribute("name", "y")
        fss2.SetDoubleAttribute("min", 0.0)
        fss2.SetDoubleAttribute("max",  100.0)
        fss2.AddNestedElement(fs21)
        fss2.AddNestedElement(fs22)
        fss2.AddNestedElement(fs23)

        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 12)

        for i in range(9):
            rval = vtkXMLDataElement()
            rval.SetName("Response")
            rval.SetIntAttribute("const", 0)
            rval.SetIntAttribute("sd", 1)
            rval.SetCharacterData(str(0), 6)

            resp.AddNestedElement(rval)

        self.root.SetName("FuzzyInferenceScheme")
        self.root.AddNestedElement(fss1)
        self.root.AddNestedElement(fss2)
        self.root.AddNestedElement(resp)

        self.root.SetAttribute("name", "Test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/FuzzyInferenceScheme http://tag2e.googlecode.com/files/FuzzyInferenceScheme.xsd")

    def test1(self):

        self._BuildXML()

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetXMLRepresentation(self.root)

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInput(self.ds)
        model.SetModelParameter(parameter)
        
        caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
        caliModel.SetInput(self.ds)
        caliModel.SetModel(model)
        caliModel.SetModelParameter(parameter)
        caliModel.SetMaxNumberOfIterations(100)
        caliModel.Update()

        caliModel.GetBestFitModelParameter().SetFileName("/tmp/vtkTAG2ESimulatedAnnealingModelCalibratorTestscomplex.xml")
        caliModel.GetBestFitModelParameter().Write()
        
################################################################################
################################################################################
################################################################################

class vtkTAG2ESimulatedAnnealingModelCalibratorTestsBenchmark(unittest.TestCase):

    def setUp(self):

        # Create the point data
        xext = 160
        yext = 1
        num = xext*yext

        self.warray = vtkDoubleArray()
        self.warray.SetNumberOfTuples(num)
        self.warray.SetName("w")

        self.xarray = vtkDoubleArray()
        self.xarray.SetNumberOfTuples(num)
        self.xarray.SetName("x")

        self.yarray = vtkDoubleArray()
        self.yarray.SetNumberOfTuples(num)
        self.yarray.SetName("y")

        self.zarray = vtkDoubleArray()
        self.zarray.SetNumberOfTuples(num)
        self.zarray.SetName("z")

        self.measure = vtkDoubleArray()
        self.measure.SetNumberOfTuples(num)
        self.measure.SetName("measure")

        # Point ids for poly vertex cell
        ids = vtkIdList()
        points = vtkPoints()

        count = 0
        for i in range(xext):
            for j in range(yext):
                points.InsertNextPoint(i, j, 0)
                ids.InsertNextId(count)

                w = count/1.6
                x = count/1.6
                y = count/1.6
                z = count/1.6
                fw = math.fabs(math.sin((w)*(w)/300.0) + (w)/10.0)
                fx = math.fabs(math.sin((x)*(x)/300.0) + (x)/10.0)
                fy = math.fabs(math.sin((y)*(y)/300.0) + (y)/10.0)
                fz = math.fabs(math.sin((z)*(z)/300.0) + (z)/10.0)

                # Data x and y range [-100:100]
                # Function
                self.warray.SetValue(count, w)
                self.xarray.SetValue(count, x)
                self.yarray.SetValue(count, y)
                self.zarray.SetValue(count, z)
                self.measure.SetValue(count, fw + fx + fy + fz)
                count += 1

        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)
        self.ds.GetPointData().SetScalars(self.measure)
        self.ds.GetPointData().AddArray(self.warray)
        self.ds.GetPointData().AddArray(self.xarray)
        self.ds.GetPointData().AddArray(self.yarray)
        self.ds.GetPointData().AddArray(self.zarray)
        self.ds.SetPoints(points)
        self.ds.InsertNextCell(vtk.VTK_POLY_VERTEX, ids)

    def _BuildXML(self):

        self.root  = vtk.vtkXMLDataElement()
        resp = vtkXMLDataElement()



# Triangular test shape layout
#   ____    ____
#       \  /
#        \/
#        /\ 
#       /  \
#  0  25 50 75  100
#
#   - 1 -   2   - 3 -
#
# 1: left = 101 center = -50 right = 50
# 2: left = 50  center = 0 right = 50
# 2: left = 50  center = 50 right = 101


        names = []
        names.append("w")
        names.append("x")
        names.append("y")
        names.append("z")

        for i in range(4):

            fs1 = vtkXMLDataElement()
            fs2 = vtkXMLDataElement()
            fs3 = vtkXMLDataElement()
            tr1 = vtkXMLDataElement()
            tr2 = vtkXMLDataElement()
            tr3 = vtkXMLDataElement()
            fss = vtkXMLDataElement()

            tr1.SetName("Triangular")
            tr1.SetDoubleAttribute("center", 25)
            tr1.SetDoubleAttribute("left",   101)
            tr1.SetDoubleAttribute("right",  50)

            tr3.SetName("Triangular")
            tr3.SetDoubleAttribute("center",  75)
            tr3.SetDoubleAttribute("left",    50)
            tr3.SetDoubleAttribute("right",   101)

            fs1.SetName("FuzzySet")
            fs1.SetAttribute("type", "Triangular")
            fs1.SetIntAttribute("priority", 0)
            fs1.SetIntAttribute("const", 0)
            fs1.SetAttribute("position", "left")
            fs1.AddNestedElement(tr1)

            fs3.SetName("FuzzySet")
            fs3.SetAttribute("type", "Triangular")
            fs3.SetIntAttribute("priority", 0)
            fs3.SetIntAttribute("const", 0)
            fs3.SetAttribute("position", "right")
            fs3.AddNestedElement(tr3)

            fss.SetName("Factor")
            fss.SetIntAttribute("portId", 0)
            fss.SetAttribute("name", names[i])
            fss.SetDoubleAttribute("min", 0.0)
            fss.SetDoubleAttribute("max",  100.0)
            fss.AddNestedElement(fs1)
            fss.AddNestedElement(fs3)

            self.root.AddNestedElement(fss)

        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 45)

        for i in range(16):
            rval = vtkXMLDataElement()
            rval.SetName("Response")
            rval.SetIntAttribute("const", 0)
            rval.SetIntAttribute("sd", 1)
            rval.SetCharacterData(str(0), 6)

            resp.AddNestedElement(rval)
            
        self.root.AddNestedElement(resp)
        self.root.SetName("FuzzyInferenceScheme")
        self.root.SetAttribute("name", "Test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/FuzzyInferenceScheme http://tag2e.googlecode.com/files/FuzzyInferenceScheme.xsd")


    def test1(self):

        self._BuildXML()

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetXMLRepresentation(self.root)

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInput(self.ds)
        model.SetModelParameter(parameter)

        caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
        caliModel.SetInput(self.ds)
        caliModel.SetModel(model)
        caliModel.SetModelParameter(parameter)
        caliModel.SetMaxNumberOfIterations(100)
        caliModel.Update()
        
        caliModel.GetBestFitModelParameter().SetFileName("/tmp/vtkTAG2ESimulatedAnnealingModelCalibratorTestsBenchmark.xml")
        caliModel.GetBestFitModelParameter().Write()
        
################################################################################
################################################################################
################################################################################

class vtkTAG2ESimulatedAnnealingModelCalibratorTestsHuge(unittest.TestCase):

    def setUp(self):

        # Create the point data
        xext = 100
        yext = 1
        num = xext*yext

        self.uarray = vtkDoubleArray()
        self.uarray.SetNumberOfTuples(num)
        self.uarray.SetName("u")

        self.varray = vtkDoubleArray()
        self.varray.SetNumberOfTuples(num)
        self.varray.SetName("v")

        self.warray = vtkDoubleArray()
        self.warray.SetNumberOfTuples(num)
        self.warray.SetName("w")

        self.xarray = vtkDoubleArray()
        self.xarray.SetNumberOfTuples(num)
        self.xarray.SetName("x")

        self.yarray = vtkDoubleArray()
        self.yarray.SetNumberOfTuples(num)
        self.yarray.SetName("y")

        self.zarray = vtkDoubleArray()
        self.zarray.SetNumberOfTuples(num)
        self.zarray.SetName("z")

        self.measure = vtkDoubleArray()
        self.measure.SetNumberOfTuples(num)
        self.measure.SetName("measure")

        # Point ids for poly vertex cell
        ids = vtkIdList()
        points = vtkPoints()

        count = 0
        for i in range(xext):
            for j in range(yext):
                points.InsertNextPoint(i, j, 0)
                ids.InsertNextId(count)

                u = count
                v = count
                w = count
                x = count
                y = count
                z = count
                fu = math.fabs(math.sin((u - 50)*(u - 50)/300.0) + (u - 50)/10.0)
                fv = math.fabs(math.sin((v - 50)*(v - 50)/300.0) + (v - 50)/10.0)
                fw = math.fabs(math.sin((w - 50)*(w - 50)/300.0) + (w - 50)/10.0)
                fx = math.fabs(math.sin((x - 50)*(x - 50)/300.0) + (x - 50)/10.0)
                fy = math.fabs(math.sin((y - 50)*(y - 50)/300.0) + (y - 50)/10.0)
                fz = math.fabs(math.sin((z - 50)*(z - 50)/300.0) + (z - 50)/10.0)

                # Data x and y range [-100:100]
                # Function
                self.uarray.SetValue(count, u)
                self.varray.SetValue(count, v)
                self.warray.SetValue(count, w)
                self.xarray.SetValue(count, x)
                self.yarray.SetValue(count, y)
                self.zarray.SetValue(count, z)

                self.measure.SetValue(count, fu + fv + fw + fx + fy + fz)
                count += 1

        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)
        self.ds.GetPointData().SetScalars(self.measure)
        self.ds.GetPointData().AddArray(self.uarray)
        self.ds.GetPointData().AddArray(self.varray)
        self.ds.GetPointData().AddArray(self.warray)
        self.ds.GetPointData().AddArray(self.xarray)
        self.ds.GetPointData().AddArray(self.yarray)
        self.ds.GetPointData().AddArray(self.zarray)
        self.ds.SetPoints(points)
        self.ds.InsertNextCell(vtk.VTK_POLY_VERTEX, ids)

    def _BuildXML(self):

        self.root  = vtk.vtkXMLDataElement()
        resp = vtkXMLDataElement()

# Triangular test shape layout
#   ____        ____
#       \  /\  /
#        \/  \/
#        /\  /\
#       /  \/  \
#  0  25   50   75  100
#
#   - 1 -   2   - 3 -
#
# 1: left = 101 center = -50 right = 50
# 2: left = 50  center = 0 right = 50
# 2: left = 50  center = 50 right = 101

        names = []
        names.append("u")
        names.append("v")
        names.append("w")
        names.append("x")
        names.append("y")
        names.append("z")
        
        for i in range(6):

            fs1 = vtkXMLDataElement()
            fs2 = vtkXMLDataElement()
            fs3 = vtkXMLDataElement()
            tr1 = vtkXMLDataElement()
            tr2 = vtkXMLDataElement()
            tr3 = vtkXMLDataElement()
            fss = vtkXMLDataElement()

            tr1.SetName("Triangular")
            tr1.SetDoubleAttribute("center", 25)
            tr1.SetDoubleAttribute("left",   101)
            tr1.SetDoubleAttribute("right",  25)

            tr2.SetName("Triangular")
            tr2.SetDoubleAttribute("center",  50)
            tr2.SetDoubleAttribute("left",    25)
            tr2.SetDoubleAttribute("right",   25)

            tr3.SetName("Triangular")
            tr3.SetDoubleAttribute("center",  75)
            tr3.SetDoubleAttribute("left",    25)
            tr3.SetDoubleAttribute("right",   101)

            fs1.SetName("FuzzySet")
            fs1.SetAttribute("type", "Triangular")
            fs1.SetIntAttribute("priority", 0)
            fs1.SetIntAttribute("const", 0)
            fs1.SetAttribute("position", "left")
            fs1.AddNestedElement(tr1)

            fs2.SetName("FuzzySet")
            fs2.SetAttribute("type", "Triangular")
            fs2.SetIntAttribute("priority", 0)
            fs2.SetIntAttribute("const", 0)
            fs2.SetAttribute("position", "intermediate")
            fs2.AddNestedElement(tr2)

            fs3.SetName("FuzzySet")
            fs3.SetAttribute("type", "Triangular")
            fs3.SetIntAttribute("priority", 0)
            fs3.SetIntAttribute("const", 0)
            fs3.SetAttribute("position", "right")
            fs3.AddNestedElement(tr3)

            fss.SetName("Factor")
            fss.SetIntAttribute("portId", 0)
            fss.SetAttribute("name", names[i])
            fss.SetDoubleAttribute("min", 0.0)
            fss.SetDoubleAttribute("max",  100.0)
            fss.AddNestedElement(fs1)
            fss.AddNestedElement(fs2)
            fss.AddNestedElement(fs3)

            self.root.AddNestedElement(fss)

        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 35)

        for i in range(729):
            rval = vtkXMLDataElement()
            rval.SetName("Response")
            rval.SetIntAttribute("const", 0)
            rval.SetIntAttribute("sd", 1)
            rval.SetCharacterData(str(0), 6)

            resp.AddNestedElement(rval)
            
        self.root.AddNestedElement(resp)
        self.root.SetName("FuzzyInferenceScheme")
        self.root.SetAttribute("name", "Test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/FuzzyInferenceScheme http://tag2e.googlecode.com/files/FuzzyInferenceScheme.xsd")

    def test1(self):

        self._BuildXML()

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetXMLRepresentation(self.root)
        parameter.DebugOff()

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInput(self.ds)
        model.SetModelParameter(parameter)
        model.UseCellDataOff()

        caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
        caliModel.SetInput(self.ds)
        caliModel.SetModel(model)
        caliModel.SetModelParameter(parameter)
        caliModel.SetMaxNumberOfIterations(100)
        caliModel.Update()
        
        caliModel.GetBestFitModelParameter().SetFileName("/tmp/vtkTAG2ESimulatedAnnealingModelCalibratorTestsHuge.xml")
        caliModel.GetBestFitModelParameter().Write()
  
################################################################################
################################################################################
################################################################################

class vtkTAG2ESimulatedAnnealingModelCalibratorTestsWeighting(unittest.TestCase):
  
    def setUp(self):

        # Create the point data
        xext = 7
        yext = 1
        num = xext*yext

        self.ds1 = vtkPolyData()
        self.ds1.Allocate(xext,yext)
        
        self.ds2 = vtkPolyData()
        self.ds2.Allocate(xext,yext)

        self.model = vtkDoubleArray()
        self.model.SetNumberOfTuples(num)
        self.model.SetName("model")

        self.factor = vtkDoubleArray()
        self.factor.SetNumberOfTuples(num)
        self.factor.SetName("factor")

        self.target = vtkDoubleArray()
        self.target.SetNumberOfTuples(num)
        self.target.SetName("target")
        self.target.FillComponent(0, 1.0)

        # Point ids for poly vertex cell
        points = vtkPoints()

        count = 0
        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()
                ids.InsertNextId(points.InsertNextPoint(i, j, 0))
                # Data range [1:100] -> linear function x
                self.model.SetValue(count, count + 1)
                self.factor.SetValue(count, count)
                self.ds1.InsertNextCell(vtk.VTK_VERTEX, ids)
                self.ds2.InsertNextCell(vtk.VTK_VERTEX, ids)
                count += 1

        self.ds1.GetCellData().AddArray(self.factor)
        self.ds1.GetCellData().AddArray(self.model)
        self.ds1.GetCellData().SetActiveScalars(self.model.GetName())
        self.ds1.SetPoints(points)
        
        self.ds2.GetCellData().AddArray(self.target)
        self.ds2.GetCellData().SetActiveScalars(self.target.GetName())
        self.ds2.SetPoints(points)
                        
        self._BuildXML()

    def _BuildXML(self):

        self.root  = vtk.vtkXMLDataElement()
        
        factor = vtkXMLDataElement()
        factor.SetName("Factor")
        factor.SetAttribute("name", "factor")
        
        weights = vtkXMLDataElement()
        weights.SetName("Weights")

        for i in range(7):
            weight = vtkXMLDataElement()
            weight.SetName("Weight")
            weight.SetIntAttribute("id", i)
            weight.SetIntAttribute("const", 0)
            weight.SetIntAttribute("active", 1)
            weight.SetDoubleAttribute("min", 0)
            weight.SetDoubleAttribute("max", 1)
            weight.SetCharacterData(str(0), 6)
            weights.AddNestedElement(weight)
        
        self.root.SetName("Weighting")
        self.root.AddNestedElement(factor)
        self.root.AddNestedElement(weights)
        self.root.SetAttribute("name", "test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/Weighting")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/Weighting http://tag2e.googlecode.com/files/Weighting.xsd")
        
    def test1Model(self):

        self._BuildXML()
        # We expect as result the following weights:
        # 1, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7

        # Set up the parameter and the model
        parameter = vtkTAG2EWeightingModelParameter()
        parameter.SetXMLRepresentation(self.root)
        parameter.SetFileName("/tmp/vtkTAG2ESimulatedAnnealingModelCalibratorTestsWeighting0.xml")
        parameter.Write()

        model = vtkTAG2EWeightingModel()
        model.SetInput(self.ds1)
        model.SetModelParameter(parameter)
        model.UseCellDataOn()

        caliModel = vtkTAG2ESimulatedAnnealingModelCalibrator()
        caliModel.SetInput(self.ds2)
        caliModel.SetModel(model)
        caliModel.SetModelParameter(parameter)
        caliModel.SetMaxNumberOfIterations(1000)
        caliModel.SetStandardDeviation(0.1)
        caliModel.SetBreakCriteria(0.001)
        caliModel.Update()
        
        caliModel.GetBestFitModelParameter().SetFileName("/tmp/vtkTAG2ESimulatedAnnealingModelCalibratorTestsWeighting1.xml")
        caliModel.GetBestFitModelParameter().Write()
  
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ESimulatedAnnealingModelCalibratorTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
    suite2 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ESimulatedAnnealingModelCalibratorTestsComplex)
    unittest.TextTestRunner(verbosity=2).run(suite2) 
    suite3 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ESimulatedAnnealingModelCalibratorTestsBenchmark)
    unittest.TextTestRunner(verbosity=2).run(suite3) 
    suite4 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ESimulatedAnnealingModelCalibratorTestsHuge)
    unittest.TextTestRunner(verbosity=2).run(suite4) 
    suite5 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ESimulatedAnnealingModelCalibratorTestsWeighting)
    unittest.TextTestRunner(verbosity=2).run(suite5)     
    