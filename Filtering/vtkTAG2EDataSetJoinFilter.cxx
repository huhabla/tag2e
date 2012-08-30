/*
 *  Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
 *
 * Authors: Soeren Gebbert, soeren.gebbert@vti.bund.de
 *          Rene Dechow, rene.dechow@vti.bund.de
 *
 * Copyright:
 *
 * Johann Heinrich von Thünen-Institut
 * Institut für Agrarrelevante Klimaforschung
 *
 * Phone: +49 (0)531 596 2601
 *
 * Fax:+49 (0)531 596 2699
 *
 * Mail: ak@vti.bund.de
 *
 * Bundesallee 50
 * 38116 Braunschweig
 * Germany
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */

#include <vtkObjectFactory.h>

#include <vtkDataSet.h>
#include <vtkPointData.h>
#include <vtkCellData.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include "vtkTAG2EDataSetJoinFilter.h"

vtkCxxRevisionMacro(vtkTAG2EDataSetJoinFilter, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EDataSetJoinFilter);

//----------------------------------------------------------------------------

vtkTAG2EDataSetJoinFilter::vtkTAG2EDataSetJoinFilter()
{
  // At least on input is needed
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
}

//----------------------------------------------------------------------------

vtkTAG2EDataSetJoinFilter::~vtkTAG2EDataSetJoinFilter()
{
  ;
}

//----------------------------------------------------------------------------

int vtkTAG2EDataSetJoinFilter::FillInputPortInformation(
  int,
  vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkDataSet");
  info->Set(vtkAlgorithm::INPUT_IS_REPEATABLE(), 1);
  return 1;
}

//----------------------------------------------------------------------------

int vtkTAG2EDataSetJoinFilter::FillOutputPortInformation(
  int vtkNotUsed(port), vtkInformation* info)
{
  // now add our info
  info->Set(vtkDataObject::DATA_TYPE_NAME(), "vtkDataSet");
  return 1;
}

//----------------------------------------------------------------------------

int vtkTAG2EDataSetJoinFilter::RequestData(vtkInformation * vtkNotUsed(request),
    vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
  int i, j;

  vtkDataSet* firstInput = vtkDataSet::GetData(inputVector[0], 0);
  vtkDataSet* output = vtkDataSet::GetData(outputVector);

  // We copy the structure of the first input
  output->CopyStructure(firstInput);

  // Now we add the data arrays from all inputs to the output
  for(i = 0; i < inputVector[0]->GetNumberOfInformationObjects(); i++)
    {
    vtkDataSet* input = vtkDataSet::GetData(inputVector[0], i);

    if(firstInput->GetNumberOfCells() != input->GetNumberOfCells())
      {
      vtkErrorMacro("The number of cells is different between the first input"
          " and the " << i << " input ");
      return -1;
      }

    if(firstInput->GetNumberOfPoints() != input->GetNumberOfPoints())
      {
      vtkErrorMacro("The number of points is different between the first input"
          " and the " << i << " input ");
      return -1;
      }

    for(j = 0; j < input->GetCellData()->GetNumberOfArrays(); j++)
      {
      output->GetCellData()->AddArray(input->GetCellData()->GetArray(j));
      }

    for(j = 0; j < input->GetPointData()->GetNumberOfArrays(); j++)
      {
      output->GetPointData()->AddArray(input->GetPointData()->GetArray(j));
      }
    }

  return 1;
}













