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

################################################################################
################################################################################
################################################################################

def CellSampling(dataset):

    return Sampling(dataset, "cell")

################################################################################
################################################################################
################################################################################

def PointSampling(dataset):

    return Sampling(dataset, "point")

################################################################################
################################################################################
################################################################################

def Sampling(dataset, type):

    selection = vtkSelection()
    selectionNode = vtkSelectionNode()
    extract = vtkExtractSelectedPolyDataIds()

    selectionNode.GetProperties().Set(vtkSelectionNode.CONTENT_TYPE(), vtkSelectionNode.INDICES)
    if type == "point":
        selectionNode.GetProperties().Set(vtkSelectionNode.FIELD_TYPE(), vtkSelectionNode.POINT)
    else:
        selectionNode.GetProperties().Set(vtkSelectionNode.FIELD_TYPE(), vtkSelectionNode.CELL)

    if type == "point":
        num = dataset.GetNumberOfPoints()
    else:
        num = dataset.GetNumberOfCells()
        
    ids = vtkIdTypeArray()
    ids.SetName("Selection")
    ids.SetNumberOfTuples(num)
    
    for i in range(num):
        id = random.randint(0, num - 1)
        ids.SetTuple1(i, id)

    selectionNode.SetSelectionList(ids)
    selection.AddNode(selectionNode)

    extract.SetInput(0, dataset)
    extract.SetInput(1, selection)
    extract.Update()

    if extract.GetOutput().GetNumberOfPoints() != dataset.GetNumberOfPoints():
        raise IOError("Error while bagging, number of points are different")

    if extract.GetOutput().GetNumberOfCells() != dataset.GetNumberOfCells():
        raise IOError("Error while bagging, number of cells are different")

    return extract.GetOutput()