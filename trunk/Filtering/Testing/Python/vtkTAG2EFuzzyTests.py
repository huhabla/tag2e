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

class vtkTAG2EDFuzzyTest(unittest.TestCase):
  
    def setUp(self):
        
        # Create the point data
        xext = 10
        yext = 10
        num = xext*yext
                
        pH = vtkDoubleArray()
        pH.SetNumberOfTuples(num)
        pH.SetName("pH")
        pH.FillComponent(0, 5)
        
        nmin = vtkDoubleArray()
        nmin.SetNumberOfTuples(num)
        nmin.SetName("nmin")
        nmin.FillComponent(0, 75)
        
        # Point ids for poly vertex cell
        ids = vtkIdList()
        points = vtkPoints()
        
        count = 0
        for i in range(xext):
            for j in range(yext):
                points.InsertNextPoint(i, j, 0)
                ids.InsertNextId(count)
                count += 1

        ds = vtkPolyData()
        ds.Allocate(xext,yext)
        ds.GetPointData().SetScalars(pH)
        ds.GetPointData().AddArray(nmin)
        ds.SetPoints(points)    
        ds.InsertNextCell(vtk.VTK_POLY_VERTEX, ids)
        
        # Create the temporal data

        # We have 10 time steps!
        time = 2
        
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
            self.timesource.SetInput(i, ds)
        self.timesource.Update()
        
    def test1Self(self):
        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.TestFISComputation()
        
    def test2FuzzyXML(self):
        
        root  = vtk.vtkXMLDataElement()
        
        fuzzyRoot = vtkXMLDataElement()
        fss1 = vtkXMLDataElement()
        fss2 = vtkXMLDataElement()
        fs1 = vtkXMLDataElement()
        fs2 = vtkXMLDataElement()
        fs3 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr2 = vtkXMLDataElement()
        tr3 = vtkXMLDataElement()
        resp = vtkXMLDataElement()
        
        weight = vtkXMLDataElement()
        
# Triangular test shape layout
# ____        ____
#     \  /\  /
#      \/  \/
#      /\  /\
#     /  \/  \
# 0  0.3 0.5 0.7  1
#
# - 1 - - 2 - - 3 - 
#
# 1: left = 2222 center = 0.3 right = 0.2
# 2: left = 0.2  center = 0.5 right = 0.2
# 3: left = 0.2  center = 0.7 right = 2222
#       
        
        tr1.SetName("Triangular")
        tr1.SetDoubleAttribute("center", 0.3)
        tr1.SetDoubleAttribute("left",   2222)
        tr1.SetDoubleAttribute("right",  0.2)
        
        tr2.SetName("Triangular")
        tr2.SetDoubleAttribute("center", 0.5)
        tr2.SetDoubleAttribute("left",   0.2)
        tr2.SetDoubleAttribute("right",  0.2)
        
        tr3.SetName("Triangular")
        tr3.SetDoubleAttribute("center",  0.7)
        tr3.SetDoubleAttribute("left",    0.2)
        tr3.SetDoubleAttribute("right",   2222)
        
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
        
        # Two factors 
        fss1.SetName("Factor")
        fss1.SetIntAttribute("portId", 0)
        fss1.SetAttribute("name", "pH")
        fss1.SetDoubleAttribute("min", 0.0)
        fss1.SetDoubleAttribute("max", 10.0)
        fss1.AddNestedElement(fs1)
        fss1.AddNestedElement(fs2)
        fss1.AddNestedElement(fs3)
        
        fss2.SetName("Factor")
        fss2.SetIntAttribute("portId", 0)
        fss2.SetAttribute("name", "nmin")
        fss2.SetDoubleAttribute("min", 0.0)
        fss2.SetDoubleAttribute("max", 150)
        fss2.AddNestedElement(fs1)
        fss2.AddNestedElement(fs2)
        fss2.AddNestedElement(fs3)
        
        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 160)
        
        for i in range(9):
            rval1 = vtkXMLDataElement()
            rval1.SetName("Response")
            rval1.SetIntAttribute("const", 0)
            rval1.SetIntAttribute("sd", 1)
            rval1.SetCharacterData(str(i * 20), 6)
            resp.AddNestedElement(rval1)
                
        fuzzyRoot.SetName("FuzzyInferenceScheme")
        fuzzyRoot.AddNestedElement(fss1)
        fuzzyRoot.AddNestedElement(fss2)
        fuzzyRoot.AddNestedElement(resp)
        
        weight.SetName("Weight")
        weight.SetAttribute("name", "grass")
        weight.SetIntAttribute("active", 1)
        weight.SetIntAttribute("const", 0)
        weight.SetDoubleAttribute("min", 0)
        weight.SetDoubleAttribute("max", 10)
        weight.SetCharacterData("1", 1)
        
        root.SetName("WeightedFuzzyInferenceScheme")
        root.SetAttribute("name", "N2OEmission_V20101111")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
        root.AddNestedElement(fuzzyRoot)
        root.AddNestedElement(weight)
        
        fisc = vtkTAG2EFuzzyInferenceModelParameter()
        fisc.SetFileName("/tmp/FuzzyInferenceScheme1.xml")
        fisc.GetXMLRoot().DeepCopy(root)
        fisc.Write()
        # Read it again
        fisc.Read();
        # Change the name
        fisc.GetXMLRoot().SetAttribute("name", "CH4Emission_V20101111") 
        fisc.SetFileName("/tmp/FuzzyInferenceScheme2.xml")
        fisc.Write()
        fisc.GenerateInternalSchemeFromXML();
        fisc.GenerateXMLFromInternalScheme();
        fisc.SetFileName("/tmp/FuzzyInferenceScheme3.xml")
        fisc.Write()
        
        model = vtkTAG2EWeightedFuzzyInferenceModel()
        model.SetModelParameter(fisc)
        model.SetInputConnection(self.timesource.GetOutputPort())
        model.Update()
                
        writer = vtkPolyDataWriter()
        writer.SetFileName("/tmp/test1_FIS_result.vtk")
        writer.SetInput(model.GetOutput().GetTimeStep(0))
        writer.Write()
  
    def test3FuzzyXML(self):
        
        root  = vtk.vtkXMLDataElement()
        
        fuzzyRoot = vtkXMLDataElement()
        fss1 = vtkXMLDataElement()
        fss2 = vtkXMLDataElement()
        fs1 = vtkXMLDataElement()
        fs2 = vtkXMLDataElement()
        fs3 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr2 = vtkXMLDataElement()
        tr3 = vtkXMLDataElement()
        resp = vtkXMLDataElement()
        
        weight = vtkXMLDataElement()
        
# Triangular test shape layout
# ____        ____
#     \  /\  /
#      \/  \/
#      /\  /\
#     /  \/  \
# 0  0.3 0.5 0.7  1
#
# - 1 - - 2 - - 3 - 
#
# 1: left = 2222 center = 0.3 right = 0.2
# 2: left = 0.2  center = 0.5 right = 0.2
# 3: left = 0.2  center = 0.7 right = 2222
#       
        
        tr1.SetName("Triangular")
        tr1.SetDoubleAttribute("center", 0.3)
        tr1.SetDoubleAttribute("left",   2222)
        tr1.SetDoubleAttribute("right",  0.2)
        
        tr2.SetName("Triangular")
        tr2.SetDoubleAttribute("center", 0.5)
        tr2.SetDoubleAttribute("left",   0.2)
        tr2.SetDoubleAttribute("right",  0.2)
        
        tr3.SetName("Triangular")
        tr3.SetDoubleAttribute("center",  0.7)
        tr3.SetDoubleAttribute("left",    0.2)
        tr3.SetDoubleAttribute("right",   2222)
        
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
        fs3.SetIntAttribute("const", 1)
        fs3.SetAttribute("position", "right")
        fs3.AddNestedElement(tr3)
        
        # Two factors 
        fss1.SetName("Factor")
        fss1.SetIntAttribute("portId", 0)
        fss1.SetAttribute("name", "pH")
        fss1.SetDoubleAttribute("min", 0.0)
        fss1.SetDoubleAttribute("max", 10.0)
        fss1.AddNestedElement(fs1)
        fss1.AddNestedElement(fs2)
        fss1.AddNestedElement(fs3)
        
        fss2.SetName("Factor")
        fss2.SetIntAttribute("portId", 0)
        fss2.SetAttribute("name", "nmin")
        fss2.SetDoubleAttribute("min", 0.0)
        fss2.SetDoubleAttribute("max", 150)
        fss2.AddNestedElement(fs1)
        fss2.AddNestedElement(fs2)
        fss2.AddNestedElement(fs3)
        
        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 160)
        
        for i in range(9):
            rval1 = vtkXMLDataElement()
            rval1.SetName("Response")
            rval1.SetIntAttribute("const", 0)
            rval1.SetIntAttribute("sd", 1)
            rval1.SetCharacterData(str(i * 20), 6)
            resp.AddNestedElement(rval1)
                
        fuzzyRoot.SetName("FuzzyInferenceScheme")
        fuzzyRoot.AddNestedElement(fss1)
        fuzzyRoot.AddNestedElement(fss2)
        fuzzyRoot.AddNestedElement(resp)
        
        weight.SetName("Weight")
        weight.SetAttribute("name", "grass")
        weight.SetIntAttribute("active", 1)
        weight.SetIntAttribute("const", 0)
        weight.SetDoubleAttribute("min", 0)
        weight.SetDoubleAttribute("max", 10)
        weight.SetCharacterData("1", 1)
        
        root.SetName("WeightedFuzzyInferenceScheme")
        root.SetAttribute("name", "N2OEmission_V20101111")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
        root.AddNestedElement(fuzzyRoot)
        root.AddNestedElement(weight)
        
        fisc = vtkTAG2EFuzzyInferenceModelParameter()
        fisc.GetXMLRoot().DeepCopy(root)
        fisc.GenerateInternalSchemeFromXML();
        fisc.GenerateXMLFromInternalScheme();
        fisc.ChangeParameterRandomly()

  
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDFuzzyTest)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
