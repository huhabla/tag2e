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

#include <vtkCommand.h>
#include <vtkCompositeDataPipeline.h>
#include <vtkDataSet.h>
#include <vtkPointData.h>
#include <vtkCellData.h>
#include <vtkIntArray.h>
#include <vtkDoubleArray.h>
#include <vtkStringArray.h>
#include <vtkTemporalDataSet.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkDataSetAttributes.h>

#include <vtkDataSetAlgorithm.h>
#include <vtkObjectFactory.h>
#include "vtkTAG2EWeightingModel.h"
#include "vtkTAG2EWeightingModelParameter.h"
#include "vtkTAG2EAbstractModelParameter.h"

vtkCxxRevisionMacro(vtkTAG2EWeightingModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EWeightingModel);

//----------------------------------------------------------------------------

vtkTAG2EWeightingModel::vtkTAG2EWeightingModel()
{
  this->WeightingModelParameter = NULL;
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
}

//----------------------------------------------------------------------------

vtkTAG2EWeightingModel::~vtkTAG2EWeightingModel()
{
  ;
}

//----------------------------------------------------------------------------

int vtkTAG2EWeightingModel::FillInputPortInformation(int vtkNotUsed(port),
    vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkDataSet");
  return 1;
}

//----------------------------------------------------------------------------
int vtkTAG2EWeightingModel::FillOutputPortInformation(int vtkNotUsed(port),
    vtkInformation* info)
{
  // now add our info
  info->Set(vtkDataObject::DATA_TYPE_NAME(), "vtkDataSet");
  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2EWeightingModel::SetModelParameter(
    vtkTAG2EAbstractModelParameter* modelParameter)
{
  this->Superclass::SetModelParameter(modelParameter);

  // Check if the ModelParameter is of correct type
  if (this->ModelParameter->IsA("vtkTAG2EWeightingModelParameter"))
    {
    this->WeightingModelParameter =
        static_cast<vtkTAG2EWeightingModelParameter *>(this->ModelParameter);
    } else
    {
    vtkErrorMacro(
        << "The ModelParameter is not of type vtkTAG2EWeightingModelParameter");
    this->SetModelParameter(NULL);
    return;
    }

  // Generate the internal representation
  this->WeightingModelParameter->GenerateInternalSchemeFromXML();

  this->Modified();
}

//----------------------------------------------------------------------------

int vtkTAG2EWeightingModel::RequestData(vtkInformation * vtkNotUsed(request),
    vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
  unsigned int i;
  double val, value;
  unsigned int id;
  int num = 0;
  vtkDataArray *scalars, *factors;
  vtkDataSetAttributes *attrData;

  // Check for model parameter
  if (this->ModelParameter == NULL)
    {
    vtkErrorMacro("Model parameter not set or invalid.");
    return -1;
    }

  // the internal parameter object for fast access
  Weighting &W = this->WeightingModelParameter->GetInternalScheme();

  vtkDataSet* input = vtkDataSet::GetData(inputVector[0]);
  vtkDataSet* output = vtkDataSet::GetData(outputVector);

  output->DeepCopy(input);

  // Result array
  vtkDoubleArray *result = vtkDoubleArray::New();
  result->SetNumberOfComponents(1);
  result->SetName(this->ResultArrayName);

  if (this->UseCellData)
    result->SetNumberOfTuples(input->GetNumberOfCells());
  else
    result->SetNumberOfTuples(input->GetNumberOfPoints());
  result->FillComponent(0, 0.0);

  if (this->UseCellData)
    {
    attrData = input->GetCellData();
    num = input->GetNumberOfCells();
    } else
    {
    attrData = input->GetPointData();
    num = input->GetNumberOfPoints();
    }

  scalars = attrData->GetScalars();
  if (attrData->HasArray(W.Factor.name.c_str()))
    {
    factors = attrData->GetArray(W.Factor.name.c_str());
    } else
    {
    if (this->UseCellData)
      {
      vtkErrorMacro(
          <<"Factor array " << W.Factor.name.c_str()
          << " does not exist in cell data of dataset");
      } else
      {
      vtkErrorMacro(
          <<"Factor array " << W.Factor.name.c_str()
          << " does not exist in point data of dataset");
      }
    return -1;
    }

  for (i = 0; i < num; i++)
    {
    val = scalars->GetTuple1(i);
    id = (int) factors->GetTuple1(i);
    if (val == this->NullValue || id < 0 || id > W.Weights.size())
      {
      result->SetValue(i, this->NullValue);
      continue;
      }
    value = W.Weights[id].value * val;
    //std::cout << "Factor " << i << " with id: " << id << " Weight: " <<  W.Weights[id].value <<
    //             " value " << val << " result: " << value<< std::endl;
    result->SetValue(i, value);
    }

  if (this->UseCellData)
    {
    output->GetCellData()->AddArray(result);
    output->GetCellData()->SetActiveScalars(result->GetName());
    } else
    {
    output->GetPointData()->AddArray(result);
    output->GetPointData()->SetActiveScalars(result->GetName());
    };
  result->Delete();

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2EWeightingModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}
