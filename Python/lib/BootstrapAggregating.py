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

def CellSampling(dataset, typeArray=None):

    return Sampling(dataset, "cell", typeArray)

################################################################################
################################################################################
################################################################################

def PointSampling(dataset, typeArray=None):

    return Sampling(dataset, "point", typeArray)

################################################################################
################################################################################
################################################################################

def Sampling(dataset, type_, typeArray=None):

    selection = vtkSelection()
    selectionNode = vtkSelectionNode()
    extract = vtkExtractSelectedPolyDataIds()

    selectionNode.GetProperties().Set(vtkSelectionNode.CONTENT_TYPE(), vtkSelectionNode.INDICES)
    if type_ == "point":
        selectionNode.GetProperties().Set(vtkSelectionNode.FIELD_TYPE(), vtkSelectionNode.POINT)
    else:
        print "CELLS"
        selectionNode.GetProperties().Set(vtkSelectionNode.FIELD_TYPE(), vtkSelectionNode.CELL)

    if type_ == "point":
        num = dataset.GetNumberOfPoints()
    else:
        num = dataset.GetNumberOfCells()
        
    ids = vtkIdTypeArray()
    ids.SetName("Selection")
    ids.SetNumberOfTuples(num)

    # In case the typeArray is set, the sampling probability is weighted by the 
		# inverse of the number of data in each type 
    # --> each type is sampled with the same probability
    if typeArray:
        types = {}
        # Get the array with the numerical types
        if type_ == "point":
            array = dataset.GetPointData().GetArray(typeArray)
        else:
            array = dataset.GetCellData().GetArray(typeArray)
            if not array:
                raise IOError("Type array not found in input dataset")
        # We extract for each type the cell ids and save this in a nested dict-list
        for i in range(num):
            id_ = int(array.GetTuple1(i))
            if id_ in types:
                types[id_].append(i)
            else:
                types[id_] = []
                types[id_].append(i)
                
        # Store the keys in a list for index access
        key_list = []
        for key in types.keys():
            key_list.append(key)
        # Select the cell ids randomly
        for i in range(num):
            num2 = len(key_list)
            # Select the type specific cell id array randomly
            key_id = random.randint(0, num2 - 1)
            # print "Select type: ", key_list[key_id]
            num2 = len(types[key_list[key_id]])
            # Select a cell id from the type array randomly
            cell_id = random.randint(0, num2 - 1)
            id_ = types[key_list[key_id]][cell_id]
            # print "Selected cell/point id: ", id_
            # Save the id to sellect the cells from the input dataset
            ids.SetTuple1(i, id_)
    else:
        for i in range(num):
            id_ = random.randint(0, num - 1)
            ids.SetTuple1(i, id_)

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
