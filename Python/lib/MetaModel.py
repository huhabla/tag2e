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
import random
from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *

class MetaModel():
    """This class will be used by the calibration algorithm to calibrate
       connected calibratable models, so called meta models. """
    def __init__(self):
        self.models = {}
        self.parameters = {}
        self.modificationNotice = {}
        self.identifier = []
        self.lastModifiedModelParameter = None
        self.lastModelInPipeline = None
        self.wasModified = 0
            
    def InsertModelParameter(self, model, parameter, modelName):
        self.models[modelName] = model
        self.parameters[modelName] = parameter
        self.identifier.append(modelName)
        
    def SetLastModelParameterInPipeline(self, model, parameter, modelName):
        self.InsertModelParameter(model, parameter, modelName)
        self.lastModelInPipeline = modelName
        
    def ModifyParameterRandomly(self, sd):
        # Choose a randomly selected model parameter
        # And call ModifyParameterRandomly(sd)
        # TODO: Weight the parameter selection
        pnum = len(self.identifier)
        r = random.randint(0, pnum - 1)
        key = self.identifier[r]
        self.parameters[key].ModifyParameterRandomly(sd)
        # Set the modification flag of the model to force an update in the pipeline
        self.models[key].Modified()
        self.lastModifiedModelParameter = key
        self.wasModified += 1
        
    def RestoreLastModifiedParameter(self):
        if self.wasModified > 0:
            self.parameters[self.lastModifiedModelParameter].RestoreLastModifiedParameter()
            self.wasModified -= 1
        
    def GetNumberOfParameters(self):
        num = 0
        for key in self.parameters.keys():
            num += parameters[key].GetNumberOfParameters()
        return num
    
    def SetTargetDataSet(self, dataSet):
        self.targetDataSet = dataSet
    
    def GetModelOutput(self):
        return self.models[self.lastModelInPipeline].GetOutput()
    
    def GetTargetDataSet(self):
        return self.targetDataSet
    
    def Run(self):
        self.models[self.lastModelInPipeline].Update()
    
    def GetXMLRepresentation(self, xml):
        root = vtkXMLDataElement()
        root.SetName("MetaModel")
        
        for key in self.parameters.keys():
            para = vtkXMLDataElement()
            self.parameters[key].GetXMLRepresentation(para)
            root.AddNestedElement(para)
            
        xml.DeepCopy(root)
        
    def WriteParameter(self, fileName):
        root = vtkXMLDataElement()
        self.GetXMLRepresentation(root)
        root.PrintXML(fileName)