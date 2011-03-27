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
from libvtkGRASSBridgeGraphicsPython import *

# test a simple linear regression scheme with monte carlo analysis
class vtkTAG2EModelMonteCarloVariationAnalyserTests(unittest.TestCase):
       
    def setUp(self):
        
        # Set up the linear regression scheme
        # y = 0.5 + 0.5 * x^2 
        
        self.lrs = vtkTAG2EAbstractModelParameter()
        
        root  = vtk.vtkXMLDataElement()
        
        intercept = vtkXMLDataElement()
        coefficient = vtkXMLDataElement()
        
        intercept.SetName("Intercept")
        intercept.SetCharacterData("0.5", 5)
        
        coefficient.SetName("Coefficient")
        coefficient.SetIntAttribute("portId", 0)
        coefficient.SetAttribute("name", "data")
        coefficient.SetDoubleAttribute("power", 2)
        coefficient.SetCharacterData("0.5", 3)

        root.SetName("LinearRegressionScheme")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/LinearRegressionScheme")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/LinearRegressionScheme http://tag2e.googlecode.com/files/LinearRegressionScheme.xsd")
        root.SetAttribute("name", "Test1")
        root.SetIntAttribute("numberOfCoefficients", 3)
        root.SetIntAttribute("hasIntercept", 1)
        root.AddNestedElement(intercept)
        root.AddNestedElement(coefficient)
        root.SetCharacterDataWidth(0)  
        
        self.lrs.SetFileName("/tmp/MCComplexSimpleLinearRegressionScheme.xml")
        self.lrs.GetXMLRoot().DeepCopy(root)
        self.lrs.Write()
        
        # Set up the model
        self.Model = vtkTAG2ELinearRegressionModel()
        self.Model.SetModelParameter(self.lrs)

    def test1(self):
        
        self.ddd = vtkTAG2EAbstractModelParameter()
                
        norm = vtkXMLDataElement()
        norm.SetName("Norm")
        norm.SetDoubleAttribute("mean", 3.0)
        norm.SetDoubleAttribute("sd", 0.1)
        
        var1 = vtkXMLDataElement()
        var1.SetName("Variable")
        var1.SetAttribute("name", "data")
        var1.SetAttribute("type", "norm")
        var1.AddNestedElement(norm)
        
        root  = vtk.vtkXMLDataElement()
        root.SetName("DataDistributionDescription")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/DataDistributionDescription")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/DataDistributionDescription http://tag2e.googlecode.com/files/DataDistributionDescription.xsd")
        root.SetAttribute("name", "Test1")
        root.AddNestedElement(var1)
        
        self.ddd.SetFileName("/tmp/MCSimpleSimpleDataDistributionDescription1.xml")
        self.ddd.GetXMLRoot().DeepCopy(root)
        self.ddd.Write()
                
        analyser = vtkTAG2EModelMonteCarloVariationAnalyser()
        analyser.SetDataDistributionDescription(self.ddd)
        analyser.SetModel(self.Model)
        analyser.SetNumberOfRandomValues(50)
        analyser.SetNumberOfTimeSteps(5)
        analyser.Update()
        
        output = analyser.GetOutput()
        
        # Generate the output        
        num = output.GetNumberOfTimeSteps()
        
        writer = vtkXMLPolyDataWriter()
        
        for i in range(1):
            writer.SetFileName("/tmp/TAG2EMonteCarloTest_0_" + str(i) + ".vtp")
            writer.SetInput(output.GetTimeStep(i))
            writer.Write()
            

    def test2(self):
        
        self.ddd = vtkTAG2EAbstractModelParameter()
                
        norm = vtkXMLDataElement()
        norm.SetName("Lnorm")
        norm.SetDoubleAttribute("meanlog", 3.0)
        norm.SetDoubleAttribute("sdlog", 0.1)
        
        var1 = vtkXMLDataElement()
        var1.SetName("Variable")
        var1.SetAttribute("name", "data")
        var1.SetAttribute("type", "lnorm")
        var1.AddNestedElement(norm)
        
        root  = vtk.vtkXMLDataElement()
        root.SetName("DataDistributionDescription")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/DataDistributionDescription")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/DataDistributionDescription http://tag2e.googlecode.com/files/DataDistributionDescription.xsd")
        root.SetAttribute("name", "Test1")
        root.AddNestedElement(var1)
        
        self.ddd.SetFileName("/tmp/MCSimpleSimpleDataDistributionDescription2.xml")
        self.ddd.GetXMLRoot().DeepCopy(root)
        self.ddd.Write()
                
        analyser = vtkTAG2EModelMonteCarloVariationAnalyser()
        analyser.SetDataDistributionDescription(self.ddd)
        analyser.SetModel(self.Model)
        analyser.SetNumberOfRandomValues(50)
        analyser.SetNumberOfTimeSteps(5)
        analyser.Update()
        
        output = analyser.GetOutput()
        
        # Generate the output        
        num = output.GetNumberOfTimeSteps()
        
        writer = vtkXMLPolyDataWriter()
        
        for i in range(1):
            writer.SetFileName("/tmp/TAG2EMonteCarloTest_1_" + str(i) + ".vtp")
            writer.SetInput(output.GetTimeStep(i))
            writer.Write()
            

    def test3(self):
        
        self.ddd = vtkTAG2EAbstractModelParameter()
                
        norm = vtkXMLDataElement()
        norm.SetName("Unif")
        norm.SetDoubleAttribute("min", 2.5)
        norm.SetDoubleAttribute("max", 3.5)
        
        var1 = vtkXMLDataElement()
        var1.SetName("Variable")
        var1.SetAttribute("name", "data")
        var1.SetAttribute("type", "unif")
        var1.AddNestedElement(norm)
        
        root  = vtk.vtkXMLDataElement()
        root.SetName("DataDistributionDescription")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/DataDistributionDescription")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/DataDistributionDescription http://tag2e.googlecode.com/files/DataDistributionDescription.xsd")
        root.SetAttribute("name", "Test1")
        root.AddNestedElement(var1)
        
        self.ddd.SetFileName("/tmp/MCSimpleSimpleDataDistributionDescription3.xml")
        self.ddd.GetXMLRoot().DeepCopy(root)
        self.ddd.Write()
                
        analyser = vtkTAG2EModelMonteCarloVariationAnalyser()
        analyser.SetDataDistributionDescription(self.ddd)
        analyser.SetModel(self.Model)
        analyser.SetNumberOfRandomValues(50)
        analyser.SetNumberOfTimeSteps(5)
        analyser.Update()
        
        output = analyser.GetOutput()
        
        # Generate the output        
        num = output.GetNumberOfTimeSteps()
        
        writer = vtkXMLPolyDataWriter()
        
        for i in range(1):
            writer.SetFileName("/tmp/TAG2EMonteCarloTest_2_" + str(i) + ".vtp")
            writer.SetInput(output.GetTimeStep(i))
            writer.Write()
        

# test a complex linear regression scheme with monte carlo analysis
class vtkTAG2EModelMonteCarloVariationAnalyserTestsComplex(unittest.TestCase):
       
    def setUp(self):
        
        ########################################################################
        # Set up the model parameter
        # We build a linear regression scheme of type:
        # 0.5 + 9.0*data1 + 0.5*(data1)^2 + 2.0*(data2)^2 + 45.0*data3
        #
        # When data1 == 3 and data2 == 5 and data3 == 1 then result == 127
        
        # Start the interface
        self.riface = vtkRInterfaceSpatial()
        
        self.lrs = vtkTAG2EAbstractModelParameter()
        
        root  = vtk.vtkXMLDataElement()
        
        intercept = vtkXMLDataElement()
        intercept.SetName("Intercept")
        intercept.SetCharacterData("0.5", 5)
        
        coefficient0 = vtkXMLDataElement()
        coefficient0.SetName("Coefficient")
        coefficient0.SetIntAttribute("portId", 0)
        coefficient0.SetAttribute("name", "data1")
        coefficient0.SetDoubleAttribute("power", 1)
        coefficient0.SetCharacterData("9.0", 3)
        
        coefficient1 = vtkXMLDataElement()
        coefficient1.SetName("Coefficient")
        coefficient1.SetIntAttribute("portId", 0)
        coefficient1.SetAttribute("name", "data1")
        coefficient1.SetDoubleAttribute("power", 2)
        coefficient1.SetCharacterData("0.5", 3)

        coefficient2 = vtkXMLDataElement()
        coefficient2.SetName("Coefficient")
        coefficient2.SetIntAttribute("portId", 0)
        coefficient2.SetAttribute("name", "data2")
        coefficient2.SetDoubleAttribute("power", 2)
        coefficient2.SetCharacterData("2.0", 3)
        
        coefficient3 = vtkXMLDataElement()
        coefficient3.SetName("Coefficient")
        coefficient3.SetIntAttribute("portId", 0)
        coefficient3.SetAttribute("name", "data3")
        coefficient3.SetDoubleAttribute("power", 1)
        coefficient3.SetCharacterData("45.0", 4)
        
        
        root.SetName("LinearRegressionScheme")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/LinearRegressionScheme")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/LinearRegressionScheme http://tag2e.googlecode.com/files/LinearRegressionScheme.xsd")
        root.SetAttribute("name", "Test1")
        root.SetIntAttribute("numberOfCoefficients", 3)
        root.SetIntAttribute("hasIntercept", 1)
        root.AddNestedElement(intercept)
        root.AddNestedElement(coefficient0)
        root.AddNestedElement(coefficient1)
        root.AddNestedElement(coefficient2)
        root.AddNestedElement(coefficient3)
        root.SetCharacterDataWidth(0)  
        
        self.lrs.SetFileName("/tmp/MCComplexLinearRegressionSchemeTest1.xml")
        self.lrs.GetXMLRoot().DeepCopy(root)
        self.lrs.Write()

        # Set up the model
        self.Model = vtkTAG2ELinearRegressionModel()
        self.Model.SetModelParameter(self.lrs)
        
    def test1(self):
        
        self.ddd = vtkTAG2EAbstractModelParameter()
                
        df1 = vtkXMLDataElement()
        df1.SetName("Lnorm")
        df1.SetDoubleAttribute("meanlog", 1.098612)
        df1.SetDoubleAttribute("sdlog", 0.01)
        
        df2 = vtkXMLDataElement()
        df2.SetName("Unif")
        df2.SetDoubleAttribute("min", 4.5)
        df2.SetDoubleAttribute("max", 5.5)
        
        df3 = vtkXMLDataElement()
        df3.SetName("Norm")
        df3.SetDoubleAttribute("mean", 1.0)
        df3.SetDoubleAttribute("sd", 0.1)
        
        var1 = vtkXMLDataElement()
        var1.SetName("Variable")
        var1.SetAttribute("name", "data1")
        var1.SetAttribute("type", "lnorm")
        var1.AddNestedElement(df1)
        
        var2 = vtkXMLDataElement()
        var2.SetName("Variable")
        var2.SetAttribute("name", "data2")
        var2.SetAttribute("type", "unif")
        var2.AddNestedElement(df2)
        
        var3 = vtkXMLDataElement()
        var3.SetName("Variable")
        var3.SetAttribute("name", "data3")
        var3.SetAttribute("type", "norm")
        var3.AddNestedElement(df3)
        
        root  = vtk.vtkXMLDataElement()
        root.SetName("DataDistributionDescription")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/DataDistributionDescription")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/DataDistributionDescription http://tag2e.googlecode.com/files/DataDistributionDescription.xsd")
        root.SetAttribute("name", "Test1")
        root.AddNestedElement(var1)
        root.AddNestedElement(var2)
        root.AddNestedElement(var3)
        
        self.ddd.SetFileName("/tmp/MCLRComplexSimpleDataDistributionDescription1.xml")
        self.ddd.GetXMLRoot().DeepCopy(root)
        self.ddd.Write()
                
        analyser = vtkTAG2EModelMonteCarloVariationAnalyser()
        analyser.SetDataDistributionDescription(self.ddd)
        analyser.SetModel(self.Model)
        analyser.SetNumberOfRandomValues(10000)
        analyser.SetNumberOfTimeSteps(10)
        analyser.SetMaxNumberOfIterations(20000)
        analyser.SetBreakCriterion(0.001)
        analyser.Update()
        
        output = analyser.GetOutput()
        
        # Generate the output        
        num = output.GetNumberOfTimeSteps()
        
        writer = vtkXMLPolyDataWriter()
        
        for i in range(1):
            writer.SetFileName("/tmp/TAG2EMonteCarloLRComplexTest_1_" + str(i) + ".vtp")
            writer.SetInput(output.GetTimeStep(i))
            writer.Write()
            
        print output.GetFieldData().GetArray(self.Model.GetResultArrayName())
        print output.GetFieldData().GetArray(self.Model.GetResultArrayName()).GetRange()
        
        # make a statistical anlysis possible using R
        self.riface.AssignVTKDataArrayToRVariable(output.GetFieldData().GetArray(self.Model.GetResultArrayName()), self.Model.GetResultArrayName())
        
        # Save the workspace for testing
        script = "save(list = ls(all=TRUE), file = \"/home/soeren/MonteCarloTestLR\")"
        print script
        self.riface.EvalRscript(script, True)
    
# test a weighted fuzzy inference scheme with monte carlo analysis
class vtkTAG2EModelMonteCarloVariationAnalyserTestsWFIS(unittest.TestCase):
       
    def setUp(self):
        
        ########################################################################
        # Set up the model parameter
        # We build a weighted fuzzy inference scheme
        
        # Start the interface
        self.riface = vtkRInterfaceSpatial()
         
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
        fss1.SetDoubleAttribute("max", 14.0)
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
        resp.SetDoubleAttribute("min", 0.0)
        resp.SetDoubleAttribute("max", 120.0)
        
        for i in range(9):
            rval1 = vtkXMLDataElement()
            rval1.SetName("Response")
            rval1.SetIntAttribute("const", 0)
            rval1.SetIntAttribute("sd", 1)
            rval1.SetCharacterData(str(i*12), 6)
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
        weight.SetCharacterData("1.0", 5)
        
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
        
        # Set up the model
        self.Model = vtkTAG2EWeightedFuzzyInferenceModel()
        self.Model.SetModelParameter(fisc)
        
    def test1(self):
        
        self.ddd = vtkTAG2EAbstractModelParameter()
                
        df1 = vtkXMLDataElement()
        df1.SetName("norm")
        df1.SetDoubleAttribute("mean", 75)
        df1.SetDoubleAttribute("sd", 15)
        
        df2 = vtkXMLDataElement()
        df2.SetName("Norm")
        df2.SetDoubleAttribute("mean", 7.0)
        df2.SetDoubleAttribute("sd", 2)
        
        var1 = vtkXMLDataElement()
        var1.SetName("Variable")
        var1.SetAttribute("name", "nmin")
        var1.SetAttribute("type", "norm")
        var1.AddNestedElement(df1)
        
        var2 = vtkXMLDataElement()
        var2.SetName("Variable")
        var2.SetAttribute("name", "pH")
        var2.SetAttribute("type", "norm")
        var2.AddNestedElement(df2)
        
        root  = vtk.vtkXMLDataElement()
        root.SetName("DataDistributionDescription")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/DataDistributionDescription")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/DataDistributionDescription http://tag2e.googlecode.com/files/DataDistributionDescription.xsd")
        root.SetAttribute("name", "Test2")
        root.AddNestedElement(var1)
        root.AddNestedElement(var2)
        
        self.ddd.SetFileName("/tmp/MCWFISSimpleDataDistributionDescription1.xml")
        self.ddd.GetXMLRoot().DeepCopy(root)
        self.ddd.Write()
                
        analyser = vtkTAG2EModelMonteCarloVariationAnalyser()
        analyser.SetDataDistributionDescription(self.ddd)
        analyser.SetModel(self.Model)
        analyser.SetNumberOfRandomValues(1000)
        analyser.SetNumberOfTimeSteps(5)
        analyser.SetMaxNumberOfIterations(2000)
        analyser.SetBreakCriterion(0.001)
        analyser.Update()
        
        output = analyser.GetOutput()
        
        # Generate the output        
        num = output.GetNumberOfTimeSteps()
        
        writer = vtkXMLPolyDataWriter()
        
        for i in range(1):
            writer.SetFileName("/tmp/TAG2EMonteCarloWFISTest_1_" + str(i) + ".vtp")
            writer.SetInput(output.GetTimeStep(i))
            writer.Write()
            
        print output.GetFieldData().GetArray(self.Model.GetResultArrayName())
        print output.GetFieldData().GetArray(self.Model.GetResultArrayName()).GetRange()
        
        # make a statistical anlysis possible using R
        self.riface.AssignVTKDataArrayToRVariable(output.GetFieldData().GetArray(self.Model.GetResultArrayName()), self.Model.GetResultArrayName())
        
        # Save the workspace for testing
        script = "save(list = ls(all=TRUE), file = \"/home/soeren/MonteCarloTestWFIS\")"
        print script
        self.riface.EvalRscript(script, True)
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EModelMonteCarloVariationAnalyserTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
    suite2 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EModelMonteCarloVariationAnalyserTestsComplex)
    unittest.TextTestRunner(verbosity=2).run(suite2) 
    suite3 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EModelMonteCarloVariationAnalyserTestsWFIS)
    unittest.TextTestRunner(verbosity=2).run(suite3) 


    
    
