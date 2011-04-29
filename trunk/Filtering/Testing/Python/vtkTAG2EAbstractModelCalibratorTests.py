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
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

class vtkTAG2EAbstractModelCalibratorTests(unittest.TestCase):
  
    def setUp(self):
        
        # Create the point data
        xext = 7
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
#0  .4 .5 .6  1
#
# - 1 -  - 3 - 
#
# 1: left = 2222 center = 0.3 right = 0.4
# 2: left = 0.4  center = 0.7 right = 2222
#       
        
        tr1.SetName("Triangular")
        tr1.SetDoubleAttribute("center", 0.3)
        tr1.SetDoubleAttribute("left",   2222)
        tr1.SetDoubleAttribute("right",  0.4)
                
        tr2.SetName("Triangular")
        tr2.SetDoubleAttribute("center",  0.7)
        tr2.SetDoubleAttribute("left",    0.4)
        tr2.SetDoubleAttribute("right",   2222)
        
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
        
        # Two factors 
        fss1.SetName("Factor")
        fss1.SetIntAttribute("portId", 0)
        fss1.SetAttribute("name", "model")
        fss1.SetDoubleAttribute("min", 1.0)
        fss1.SetDoubleAttribute("max", 7.0)
        fss1.AddNestedElement(fs1)
        fss1.AddNestedElement(fs2)
                
        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 20)
        
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
        self.root.SetAttribute("name", "N2OEmission_V20101111")
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
        
        print vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(self.timesource.GetOutput(), "model", "measure", 1, 1)
        
    def test2(self):
        # Set up the parameter and the model
        fisc = vtkTAG2EFuzzyInferenceModelParameter()
        fisc.GetXMLRoot().DeepCopy(self.root)
        fisc.GenerateInternalSchemeFromXML();

        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(fisc)
        model.Update()
        
        firstError = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), "result", "measure", 1, 0)
        
        count = 0
        
        for i in range(10000):
            if (i + 1) % 1000 == 1:
                print "Iteration " + str(i)          
            
            fisc.ModifyParameterRandomly(0.001) 
            model = vtkTAG2EWeightedFuzzyInferenceModel()
            model.SetInputConnection(self.timesource.GetOutputPort())
            model.SetModelParameter(fisc)
            model.Update()
            
            # Measure the difference
            if i == 0:
                oldError = firstError
                
            Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), "result", "measure", 1, 0)
              
            # print "Error " + str(Error)
            diff = oldError - Error
            
            # The error must be reduced
            if diff < 0.000001:
                fisc.RestoreLastModifiedParameter()
            else:
                oldError = Error
                print "Old Error " + str(oldError) + "Error " + str(Error) + " Diff " + str(diff)
                "Accept a worse result ... "
                if (i) % 500 == 1:
                    oldError = oldError * 10
                    print "New error " + str(oldError)
            
            count += 1
        
            if Error < 0.01:
                break
                
        print "Finished after " + str(count) + " Iterations"
        
        fisc.SetFileName("/tmp/vtkTAG2EAbstractModelCalibratorTestsFinal.xml")
        fisc.Write()
        
        # Show the result
        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.SetModelParameter(fisc)
        model.Update()
            
        Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), "result", "measure", 1, 1)
              
  
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EAbstractModelCalibratorTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
