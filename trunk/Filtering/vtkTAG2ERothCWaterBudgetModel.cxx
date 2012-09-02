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
#include <vtkCell.h>
#include <vtkMath.h>

extern "C" {
#include <math.h>
}

#include <vtkDataSetAlgorithm.h>
#include <vtkObjectFactory.h>
#include "vtkTAG2ERothCWaterBudgetModel.h"
#include "vtkTAG2ERothCDefines.h"

vtkCxxRevisionMacro(vtkTAG2ERothCWaterBudgetModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ERothCWaterBudgetModel);

//----------------------------------------------------------------------------

vtkTAG2ERothCWaterBudgetModel::vtkTAG2ERothCWaterBudgetModel()
{
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
  this->SetResultArrayName(ROTHC_INPUT_NAME_SOIL_MOISTURE);
}

//----------------------------------------------------------------------------

vtkTAG2ERothCWaterBudgetModel::~vtkTAG2ERothCWaterBudgetModel()
{
  ;
}

//----------------------------------------------------------------------------

int vtkTAG2ERothCWaterBudgetModel::FillInputPortInformation(
    int vtkNotUsed(port), vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkPolyData");
  return 1;
}

//----------------------------------------------------------------------------
int vtkTAG2ERothCWaterBudgetModel::FillOutputPortInformation(
    int port, vtkInformation* info)
{
  if (!this->Superclass::FillOutputPortInformation(port, info))
    {
    return 0;
    }

  // now add our info
  info->Set(vtkDataObject::DATA_TYPE_NAME(), "vtkPolyData");
  return 1;
}

//----------------------------------------------------------------------------

int vtkTAG2ERothCWaterBudgetModel::RequestData(
    vtkInformation * vtkNotUsed(request), vtkInformationVector **inputVector,
    vtkInformationVector *outputVector)
{
  vtkIdType i;
  vtkIdType cellId;
  bool hasInputPools = true;

  vtkPolyData* input = vtkPolyData::GetData(inputVector[0]);
  vtkPolyData* output = vtkPolyData::GetData(outputVector);

  // Copy geometry from input
  output->CopyStructure(input);

  // Result array
  vtkDoubleArray *result = vtkDoubleArray::New();
  result->SetNumberOfComponents(1);
  result->SetName(this->ResultArrayName);
  result->SetNumberOfTuples(input->GetNumberOfCells());

  // Check the input arrays
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_ETPOT))
    {
    vtkErrorMacro(<<"Cell data array <" << ROTHC_INPUT_NAME_ETPOT
                  << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_PRECIPITATION))
    {
    vtkErrorMacro(<<"Cell data array <" << ROTHC_INPUT_NAME_PRECIPITATION
                  << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_SOILCOVER))
    {
    vtkErrorMacro(<<"Cell data array <" << ROTHC_INPUT_NAME_SOILCOVER
                  << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_USABLE_WATER_CONTENT))
    {
    vtkErrorMacro(<<"Cell data array <" << ROTHC_INPUT_NAME_USABLE_WATER_CONTENT
                  << "> is missing ");
    return -1;
    }

  // Get array pointer for easy access
  vtkDataArray *etpotArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_ETPOT);
  vtkDataArray *precipitationArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_PRECIPITATION);
  vtkDataArray *soilCoverArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_SOILCOVER);
  vtkDataArray *waterContentArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_USABLE_WATER_CONTENT);

  // Parallelize with OpenMP
  for (cellId = 0; cellId < input->GetNumberOfCells(); cellId++)
    {
    double lineLength, c;
    double p1[3];
    double p2[3];
    double etpot, precipitation, soilCover, waterContent, res;
    double usableFieldcapacity; //[cm³/cm³]
    double clay; //[%]

    vtkIdList *pointIds = vtkIdList::New();
    vtkIdType pointId;

    // Check cell type, we support only lines
    if (input->GetCellType(cellId) != VTK_LINE)
      {
      vtkErrorMacro("Unsupported cell type.");
      return -1;
      }

    input->GetCellPoints(cellId, pointIds);
    // We support only lines with two coordinates
    if (pointIds->GetNumberOfIds() != 2)
      {
      vtkErrorMacro("Unsupported line length.");
      return -1;
      }
    // Compute length of the line in vertical direction
    input->GetPoint(pointIds->GetId(0), p1);
    input->GetPoint(pointIds->GetId(1), p2);
    lineLength = fabs(p1[2] - p2[2]);

    etpot = etpotArray->GetTuple1(cellId);
    precipitation = precipitationArray->GetTuple1(cellId);
    soilCover = soilCoverArray->GetTuple1(cellId);
    waterContent = waterContentArray->GetTuple1(cellId);

    // compute the usable field capacity
    usableFieldcapacity = -(20 + 1.3 * clay - 0.01 * clay * clay) / 230.0;
    if (soilCover == 0 || soilCover == this->NullValue)
      usableFieldcapacity /= 1.8;

    result->SetTuple1(cellId, usableFieldcapacity);

    pointIds->Delete();
    }

  output->GetCellData()->AddArray(result);
  output->GetCellData()->SetActiveScalars(result->GetName());
  result->Delete();

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2ERothCWaterBudgetModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}
