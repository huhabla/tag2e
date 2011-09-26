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

class vtkTAG2EDFuzzyTest(unittest.TestCase):
  
    def setUp(self):
        
        # Create the point data
        xext = 20
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
        
        self._BuildXML()
        
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
        
        
# Triangular test shape layout first Factor 0.0 - 10.0
# ____        ____
#     \  /\  /
#      \/  \/
#      /\  /\
#     /  \/  \
# 0 3000 5000 7000  10000
#
# - 1 - - 2 - - 3 - 
#
# 1: left = 11000 center = 3000 right = 2000
# 2: left = 2000  center = 5000 right = 2000
# 3: left = 2000  center = 7000 right = 11000
#       
               
# Triangular test shape layout second Factor 0.0 - 150
# ____        ____
#     \  /\  /
#      \/  \/
#      /\  /\
#     /  \/  \
# 0  50  75  100  150
#
# - 1 - - 2 - - 3 - 
#
# 1: left = 151 center = 50 right = 25
# 2: left = 25  center = 75 right = 25
# 3: left = 25  center = 100 right = 151
#        
        tr11.SetName("Triangular")
        tr11.SetDoubleAttribute("center", 3000)
        tr11.SetDoubleAttribute("left",   11000)
        tr11.SetDoubleAttribute("right",  2000)
        
        tr12.SetName("Triangular")
        tr12.SetDoubleAttribute("center", 5000)
        tr12.SetDoubleAttribute("left",   2000)
        tr12.SetDoubleAttribute("right",  2000)
        
        tr13.SetName("Triangular")
        tr13.SetDoubleAttribute("center",  7000)
        tr13.SetDoubleAttribute("left",    2000)
        tr13.SetDoubleAttribute("right",   11000)
        
        
        tr21.SetName("Triangular")
        tr21.SetDoubleAttribute("center", 50)
        tr21.SetDoubleAttribute("left",   151)
        tr21.SetDoubleAttribute("right",  25)
        
        tr22.SetName("Triangular")
        tr22.SetDoubleAttribute("center", 75)
        tr22.SetDoubleAttribute("left",   25)
        tr22.SetDoubleAttribute("right",  25)
        
        tr23.SetName("Triangular")
        tr23.SetDoubleAttribute("center",  100)
        tr23.SetDoubleAttribute("left",    25)
        tr23.SetDoubleAttribute("right",   151)
        
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
        fss1.SetAttribute("name", "pH")
        fss1.SetDoubleAttribute("min", 0.0)
        fss1.SetDoubleAttribute("max", 10000.0)
        fss1.AddNestedElement(fs11)
        fss1.AddNestedElement(fs12)
        fss1.AddNestedElement(fs13)
        
        fss2.SetName("Factor")
        fss2.SetIntAttribute("portId", 0)
        fss2.SetAttribute("name", "nmin")
        fss2.SetDoubleAttribute("min", 0.0)
        fss2.SetDoubleAttribute("max", 150)
        fss2.AddNestedElement(fs21)
        fss2.AddNestedElement(fs22)
        fss2.AddNestedElement(fs23)
        
        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 1)
        
        for i in range(9):
            rval1 = vtkXMLDataElement()
            rval1.SetName("Response")
            rval1.SetIntAttribute("const", 0)
            rval1.SetIntAttribute("sd", 1)
            rval1.SetCharacterData(str(i * 0.1), 6)
            resp.AddNestedElement(rval1)
                
        self.root.SetName("FuzzyInferenceScheme")
        self.root.AddNestedElement(fss1)
        self.root.AddNestedElement(fss2)
        self.root.AddNestedElement(resp)
                
        self.root.SetAttribute("name", "N2OEmission_V20101111")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/FuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/FuzzyInferenceScheme http://tag2e.googlecode.com/files/FuzzyInferenceScheme.xsd")
        
    def test1Self(self):
        """Performe the self test"""
        model = vtkTAG2EFuzzyInferenceModel()
        model.TestFISComputation()
        
    def test2FuzzyXML(self):
        
        fisc = vtkTAG2EFuzzyInferenceModelParameter()
        fisc.SetXMLRepresentation(self.root)
        
        model = vtkTAG2EFuzzyInferenceModel()
        model.SetModelParameter(fisc)
        model.SetInputConnection(self.timesource.GetOutputPort())
        
        for i in range(1000):
            fisc.ModifyParameterRandomly(5)
            
            model.Modified()
            model.Update()
            
            fisc.GetXMLRepresentation(self.root)
            fisc.SetFileName("/tmp/vtkTAG2EFuzzyInferenceModelParameterTest_" + str(i) + ".xml")
            fisc.Write()
            fisc.Read()
            
        fim = vtkTAG2EFuzzyInferenceModelParameterToImageData()
        fim.SetFuzzyModelParameter(fisc)
        fim.SetXAxisExtent(50)
        fim.SetYAxisExtent(50)
        fim.SetZAxisExtent(50)
        fim.Update()
        
        pwriter = vtkXMLImageDataWriter()
        pwriter.SetFileName("/tmp/vtkTAG2EFuzzyInferenceModelParameterTest.vti")
        pwriter.SetInput(fim.GetOutput())
        pwriter.Write()
        
        print(fim.GetOutput())
            
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDFuzzyTest)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
