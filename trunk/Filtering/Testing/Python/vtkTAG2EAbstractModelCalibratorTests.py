import math
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
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

################################################################################
################################################################################
################################################################################

class vtkTAG2EAbstractModelCalibratorTests(unittest.TestCase):
  
    def setUp(self):
        
        # Create the point data
        xext = 100
        yext = 1
        num = xext*yext
                
        self.model = vtkDoubleArray()
        self.model.SetNumberOfTuples(num)
        self.model.SetName("model")
        
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
                # Data range [1:100] -> linear function x
                self.model.SetValue(count, count + 1)
                self.measure.SetValue(count, count + 1)
                count += 1

        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)
        self.ds.GetPointData().SetScalars(self.model)
        self.ds.GetPointData().AddArray(self.measure)
        self.ds.SetPoints(points)    
        self.ds.InsertNextCell(vtk.VTK_POLY_VERTEX, ids)
        
        # Create the temporal data

        # We have 10 time steps!
        time = 1
        
        # Generate the time steps
        timesteps = vtkDoubleArray()
        timesteps.SetNumberOfTuples(time)
        timesteps.SetNumberOfComponents(1)
        for i in range(time):
            timesteps.SetValue(i, 3600*24*i)

        # Create the spatio-temporal source
        self.timesource = vtkTemporalDataSetSource()
        self.timesource.SetTimeRange(0, 3600*24*time, timesteps)
        for i in range(time):
            self.timesource.SetInput(i, self.ds)
        self.timesource.Update()
        
        self._BuildXML()
        
    def _BuildXML(self):
        
        self.root  = vtk.vtkXMLDataElement()
        
        fuzzyRoot = vtkXMLDataElement()
        fss1 = vtkXMLDataElement()
        fs1 = vtkXMLDataElement()
        fs2 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr2 = vtkXMLDataElement()
        resp = vtkXMLDataElement()
        
        weight = vtkXMLDataElement()
        
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
                
        fuzzyRoot.SetName("FuzzyInferenceScheme")
        fuzzyRoot.AddNestedElement(fss1)
        fuzzyRoot.AddNestedElement(resp)
        
        weight.SetName("Weight")
        weight.SetAttribute("name", "grass")
        weight.SetIntAttribute("active", 1)
        weight.SetIntAttribute("const", 1)
        weight.SetDoubleAttribute("min", 0)
        weight.SetDoubleAttribute("max", 10)
        weight.SetCharacterData("1", 1)
        
        self.root.SetName("WeightedFuzzyInferenceScheme")
        self.root.SetAttribute("name", "Test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
        self.root.AddNestedElement(fuzzyRoot)
        self.root.AddNestedElement(weight)
        
        
    def test1(self):
        
        print vtkTAG2EAbstractModelCalibrator.ArithmeticMean(self.model)
        print vtkTAG2EAbstractModelCalibrator.ArithmeticMean(self.measure)
        
        print vtkTAG2EAbstractModelCalibrator.Variance(self.model)
        print vtkTAG2EAbstractModelCalibrator.Variance(self.measure)
        
        print vtkTAG2EAbstractModelCalibrator.StandardDeviation(self.model)
        print vtkTAG2EAbstractModelCalibrator.StandardDeviation(self.measure)
        
        print vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(self.timesource.GetOutput(), "model", "measure", 0, 1)
        
    def test2(self):

        self._BuildXML()

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.GetXMLRoot().DeepCopy(self.root)
        parameter.GenerateInternalSchemeFromXML()

        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(parameter)

        MetropolisCalibrator(model, parameter, 5000, 1, 2, 0.0001, "result", "measure", "simple")

################################################################################
################################################################################
################################################################################

class vtkTAG2EAbstractModelCalibratorTestsComplex(unittest.TestCase):

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

        # Create the temporal data

        # We have 10 time steps!
        time = 1

        # Generate the time steps
        timesteps = vtkDoubleArray()
        timesteps.SetNumberOfTuples(time)
        timesteps.SetNumberOfComponents(1)
        for i in range(time):
            timesteps.SetValue(i, 3600*24*i)

        # Create the spatio-temporal source
        self.timesource = vtkTemporalDataSetSource()
        self.timesource.SetTimeRange(0, 3600*24*time, timesteps)
        for i in range(time):
            self.timesource.SetInput(i, self.ds)
        self.timesource.Update()


    def _BuildXML(self):

        self.root  = vtk.vtkXMLDataElement()

        fuzzyRoot = vtkXMLDataElement()
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

        weight = vtkXMLDataElement()



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

        fuzzyRoot.SetName("FuzzyInferenceScheme")
        fuzzyRoot.AddNestedElement(fss1)
        fuzzyRoot.AddNestedElement(fss2)
        fuzzyRoot.AddNestedElement(resp)

        weight.SetName("Weight")
        weight.SetAttribute("name", "grass")
        weight.SetIntAttribute("active", 1)
        weight.SetIntAttribute("const", 1)
        weight.SetDoubleAttribute("min", 0)
        weight.SetDoubleAttribute("max", 10)
        weight.SetCharacterData("1", 1)

        self.root.SetName("WeightedFuzzyInferenceScheme")
        self.root.SetAttribute("name", "Test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
        self.root.AddNestedElement(fuzzyRoot)
        self.root.AddNestedElement(weight)

    def test1(self):

        self._BuildXML()

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.GetXMLRoot().DeepCopy(self.root)
        parameter.GenerateInternalSchemeFromXML()

        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(parameter)

        MetropolisCalibrator(model, parameter, 5000, 1, 2, 0.01, "result", "measure", "complex")


################################################################################
################################################################################
################################################################################

class vtkTAG2EAbstractModelCalibratorTestsBenchmark(unittest.TestCase):

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

        # Create the temporal data

        # We have 10 time steps!
        time = 1

        # Generate the time steps
        timesteps = vtkDoubleArray()
        timesteps.SetNumberOfTuples(time)
        timesteps.SetNumberOfComponents(1)
        for i in range(time):
            timesteps.SetValue(i, 3600*24*i)

        # Create the spatio-temporal source
        self.timesource = vtkTemporalDataSetSource()
        self.timesource.SetTimeRange(0, 3600*24*time, timesteps)
        for i in range(time):
            self.timesource.SetInput(i, self.ds)
        self.timesource.Update()



    def _BuildXML(self):

        self.root  = vtk.vtkXMLDataElement()
        resp = vtkXMLDataElement()
        weight = vtkXMLDataElement()



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


        fuzzyRoot = vtkXMLDataElement()
        fuzzyRoot.SetName("FuzzyInferenceScheme")
        
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

            fuzzyRoot.AddNestedElement(fss)

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
            
        fuzzyRoot.AddNestedElement(resp)

        weight.SetName("Weight")
        weight.SetAttribute("name", "grass")
        weight.SetIntAttribute("active", 1)
        weight.SetIntAttribute("const", 0)
        weight.SetDoubleAttribute("min", 0)
        weight.SetDoubleAttribute("max", 10)
        weight.SetCharacterData("1", 1)

        self.root.SetName("WeightedFuzzyInferenceScheme")
        self.root.SetAttribute("name", "Test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
        self.root.AddNestedElement(fuzzyRoot)
        self.root.AddNestedElement(weight)


    def test1(self):

        self._BuildXML()

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.GetXMLRoot().DeepCopy(self.root)
        parameter.GenerateInternalSchemeFromXML()

        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(parameter)

        MetropolisCalibrator(model, parameter, 5000, 1, 2, 0.01, "result", "measure", "bench")

################################################################################
################################################################################
################################################################################

class vtkTAG2EAbstractModelCalibratorTestsHuge(unittest.TestCase):

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

        # Create the temporal data

        # We have 10 time steps!
        time = 1

        # Generate the time steps
        timesteps = vtkDoubleArray()
        timesteps.SetNumberOfTuples(time)
        timesteps.SetNumberOfComponents(1)
        for i in range(time):
            timesteps.SetValue(i, 3600*24*i)

        # Create the spatio-temporal source
        self.timesource = vtkTemporalDataSetSource()
        self.timesource.SetTimeRange(0, 3600*24*time, timesteps)
        for i in range(time):
            self.timesource.SetInput(i, self.ds)
        self.timesource.Update()


    def _BuildXML(self):

        self.root  = vtk.vtkXMLDataElement()
        resp = vtkXMLDataElement()
        weight = vtkXMLDataElement()



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


        fuzzyRoot = vtkXMLDataElement()
        fuzzyRoot.SetName("FuzzyInferenceScheme")

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

            fuzzyRoot.AddNestedElement(fss)

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
            
        fuzzyRoot.AddNestedElement(resp)

        weight.SetName("Weight")
        weight.SetAttribute("name", "grass")
        weight.SetIntAttribute("active", 1)
        weight.SetIntAttribute("const", 1)
        weight.SetDoubleAttribute("min", 0)
        weight.SetDoubleAttribute("max", 10)
        weight.SetCharacterData("1", 1)

        self.root.SetName("WeightedFuzzyInferenceScheme")
        self.root.SetAttribute("name", "Test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
        self.root.AddNestedElement(fuzzyRoot)
        self.root.AddNestedElement(weight)

    def test1(self):

        self._BuildXML()

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.GetXMLRoot().DeepCopy(self.root)
        parameter.GenerateInternalSchemeFromXML()

        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(parameter)

        MetropolisCalibrator(model, parameter, 5000, 1, 2, 0.01, "result", "measure", "huge")

################################################################################
################################################################################
################################################################################

def MetropolisCalibrator(model, parameter, maxiter, maxFactor, sd, errorBreak, modelArray, measureArray, prefix):

    model.Update()

    firstError = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), modelArray, measureArray, 0, 0)

    count = 0

    T = maxFactor

    for i in range(maxiter):
        if (i + 1) % 100 == 1:
            print "######### Iteration " + str(i) + " #########"
            
        sdNew = sd/((maxFactor - T)/maxFactor + 1)

        parameter.ModifyParameterRandomly(sdNew)
        model.Modified()
        model.Update()

        if i == 0:
            oldError = firstError

        # Measure the difference between old and new error
        Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), modelArray, measureArray, 0, 0)

        diff = Error - oldError

        # Accept the new parameter
        if diff <= 0:
            oldError = Error
        else:
            # Create a random number
            r = random.uniform(1.0, 0.0)
            pa = math.exp(-1.0*diff/T)
            if pa > 1:
                pa = 1

            # restore the last parameter if the random variable is larger then the error
            if r > pa:
                parameter.RestoreLastModifiedParameter()
            else:
                oldError = Error
                print "Not restored"
                T = T/1.005
                print "Error ", oldError, "diff ", diff, "Pa ", pa, " R ", r, "T ", T, "sd ", sdNew

        count += 1
        
        # Save an intermediate state
        if i % 1000 == 1:
            print "Save XML state"
            Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), modelArray, measureArray, 0, 1)
            print "Error ", Error
            parameter.GenerateXMLFromInternalScheme()
            parameter.SetFileName("/tmp/vtkTAG2EAbstractModelCalibratorTestsComplexIteration_" + str(i) + "_" + prefix + ".xml")
            parameter.Write()

        if Error < errorBreak:
            break

    print "Finished after " + str(count) + " Iterations"

    parameter.GenerateXMLFromInternalScheme()
    parameter.SetFileName("/tmp/vtkTAG2EAbstractModelCalibratorTestsComplexFinal" + "_" + prefix + ".xml")
    parameter.Write()
    model.Modified()
    model.Update()

    Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), modelArray, measureArray, 0, 1)
    print "Error ", Error

################################################################################
################################################################################
################################################################################
  
  
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EAbstractModelCalibratorTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
    suite2 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EAbstractModelCalibratorTestsComplex)
    unittest.TextTestRunner(verbosity=2).run(suite2) 
    suite3 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EAbstractModelCalibratorTestsBenchmark)
    unittest.TextTestRunner(verbosity=2).run(suite3) 
    suite4 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EAbstractModelCalibratorTestsHuge)
    unittest.TextTestRunner(verbosity=2).run(suite4) 