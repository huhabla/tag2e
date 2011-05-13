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
from vtk import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

import random

# Implement bagging and cross validation using this code
# from VTK test TestExtractSelection.cxx:
#  32   vtkSelection* sel = vtkSelection::New();
#  33   vtkSelectionNode* node = vtkSelectionNode::New();
#  34   sel->AddNode(node);
#  35   node->GetProperties()->Set(
#  36     vtkSelectionNode::CONTENT_TYPE(), vtkSelectionNode::INDICES);
#  37   node->GetProperties()->Set(
#  38     vtkSelectionNode::FIELD_TYPE(), vtkSelectionNode::CELL);
#  39   
#  40   // list of cells to be selected
#  41   vtkIdTypeArray* arr = vtkIdTypeArray::New();
#  42   arr->SetNumberOfTuples(4);
#  43   arr->SetTuple1(0, 2);
#  44   arr->SetTuple1(1, 4);
#  45   arr->SetTuple1(2, 5);
#  46   arr->SetTuple1(3, 8);
#  47 
#  48   node->SetSelectionList(arr);
#  49   arr->Delete();
#  50 
#  51   vtkSphereSource* sphere = vtkSphereSource::New();
#  52 
#  53   vtkExtractSelectedPolyDataIds* selFilter = 
#  54     vtkExtractSelectedPolyDataIds::New();
#  55   selFilter->SetInput(1, sel);
#  56   selFilter->SetInputConnection(0,sphere->GetOutputPort());
#  57   sel->Delete();
#  58   node->Delete();

def ReadTextData(inputFile, scalarName, bagging = True):

    file = open(inputFile)
    headerLine = file.readline()
    names = headerLine.split(',')

    nameArray = []
    for i in range(0, len(names)):
        nameArray.append(str(names[i]).rstrip('\r\n'))

    dataset = vtkPolyData()
    dataset.Allocate(1,1)

    points = vtkPoints()

    dataArrays = vtkDataSetAttributes()

    for name in nameArray:
        array = vtkDoubleArray()
        array.SetName(name)
        dataArrays.AddArray(array)

    while True:

        line = file.readline()
        if line == "":
            break
        tmpArray = line.split(',')

        data = {}
        year = float(tmpArray[0])
        y = float(tmpArray[1])
        x = float(tmpArray[2])

        ids = vtkIdList()
        ids.InsertNextId(points.InsertNextPoint(x, y, 0))

        dataset.InsertNextCell(vtk.VTK_VERTEX, ids)

        count = 0
        for i in range(0, len(tmpArray)):
            data[nameArray[count]] = float(tmpArray[i])
            count += 1

        for key in data.keys():
            dataArrays.GetArray(key).InsertNextValue(data[key])

    file.close()

    dataset.GetCellData().DeepCopy(dataArrays)
    dataset.SetPoints(points)

    if dataset.GetCellData().HasArray(scalarName):
        dataset.GetCellData().SetActiveScalars(scalarName)
        
    selection = vtkSelection()
    selectionNode = vtkSelectionNode()
    extract = vtkExtractSelectedPolyDataIds()
        
    if bagging == True:
        selectionNode.GetProperties().Set(vtkSelectionNode.CONTENT_TYPE(), vtkSelectionNode.INDICES)
        selectionNode.GetProperties().Set(vtkSelectionNode.FIELD_TYPE(), vtkSelectionNode.CELL)

        num = dataset.GetNumberOfCells()
        liste = {}
        ids = vtkIdTypeArray()
        ids.SetName("Selection")
        ids.SetNumberOfTuples(num)
        for i in range(num):
            id = random.randint(0, num)
            liste[id] = id
            ids.SetTuple1(i, id)
            
        selectionNode.SetSelectionList(ids)
        selection.AddNode(selectionNode)
        
        print len(liste)
        
        extract.SetInput(1, selection)
        extract.SetInput(0, dataset)
        extract.Update()
        
        print extract.GetOutput()
        
    time = 1

    # Generate the time steps
    timesteps = vtkDoubleArray()
    timesteps.SetNumberOfTuples(time)
    timesteps.SetNumberOfComponents(1)
    for i in range(time):
        timesteps.SetValue(i, 3600*24*i)

    # Create the spatio-temporal source
    timesource = vtkTemporalDataSetSource()
    timesource.SetTimeRange(0, 3600*24*time, timesteps)
    for i in range(time):
        if bagging == True:
            timesource.SetInput(i, extract.GetOutput())
        else:
            timesource.SetInput(i, dataset)
    timesource.Update()
    
    return dataset, timesource

