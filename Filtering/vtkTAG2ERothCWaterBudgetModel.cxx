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
#include "vtkTAG2EDefines.h"

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

  // Check the input arrays
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_ETPOT))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_ETPOT << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_PRECIPITATION))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_PRECIPITATION << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_SOILCOVER))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_SOILCOVER << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_CLAY))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_CLAY << "> is missing ");
    return -1;
    }

  // Copy geometry from input
  output->CopyStructure(input);
  input->BuildCells();

  // Result array usable Fieldcapacity
  vtkDoubleArray *resultUsableFieldCapacity = vtkDoubleArray::New();
  resultUsableFieldCapacity->SetNumberOfComponents(1);
  resultUsableFieldCapacity->SetName(ROTHC_INPUT_NAME_USABLE_FIELD_CAPACITY);
  resultUsableFieldCapacity->SetNumberOfTuples(input->GetNumberOfCells());

  // Result array WaterContentNew
  vtkDoubleArray *resultWaterContentNew = vtkDoubleArray::New();
  resultWaterContentNew->SetNumberOfComponents(1);
  resultWaterContentNew->SetName(this->ResultArrayName);
  resultWaterContentNew->SetNumberOfTuples(input->GetNumberOfCells());

  // Get array pointer for easy access
  vtkDataArray *etpotArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_ETPOT);
  vtkDataArray *precipitationArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_PRECIPITATION);
  vtkDataArray *soilCoverArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_SOILCOVER);
  vtkDataArray *waterContentArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_USABLE_WATER_CONTENT);
  vtkDataArray *clayArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_CLAY);

  int cellNum = input->GetNumberOfCells();

#ifdef OMP_PARALLELIZED
  // We must call the following method first in a single thread to
  // avoid race conditions
  if(input->GetNumberOfCells() > 0) {
    vtkIdList *tmp = vtkIdList::New();
    input->GetCellPoints(0, tmp);
    input->GetCellType(0);
    tmp->Delete();
  }
#endif

  // Parallelize with OpenMP
#ifdef OMP_PARALLELIZED
#pragma omp parallel for private(cellId) shared(input, etpotArray, \
    precipitationArray, soilCoverArray, clayArray, waterContentArray,\
    resultUsableFieldCapacity, resultWaterContentNew, cellNum)
#endif
  for (cellId = 0; cellId < cellNum; cellId++)
    {
    double lineLength, c;
    double p1[3];
    double p2[3];
    double etpot, precipitation, soilCover, waterContent, res;
    double waterContentNew;
    double usableFieldcapacity; //[cm³/cm³]
    double clay; //[%]

    vtkIdList *pointIds = vtkIdList::New();
    vtkIdType pointId;

    input->GetCellPoints(cellId, pointIds);

    // Check cell type, we support only lines
    if (input->GetCellType(cellId) != VTK_LINE)
      {
      vtkErrorMacro("Unsupported cell type: " << input->GetCellType(cellId));
#ifndef OMP_PARALLELIZED
      return -1;
#else
      continue;
#endif
      }

    // We support only lines with two coordinates
    if (pointIds->GetNumberOfIds() != 2)
      {
      vtkErrorMacro("Unsupported number of line coordinates: " << pointIds->GetNumberOfIds());
#ifndef OMP_PARALLELIZED
      return -1;
#else
      continue;
#endif
      }

    // Compute length of the line in vertical direction
    input->GetPoint(pointIds->GetId(0), p1);
    input->GetPoint(pointIds->GetId(1), p2);
    lineLength = fabs(p1[2] - p2[2]); //m

    etpotArray->GetTuple(cellId, &etpot);
    precipitationArray->GetTuple(cellId, &precipitation);
    soilCoverArray->GetTuple(cellId, &soilCover);
    clayArray->GetTuple(cellId, &clay);

    // compute the usable field capacity
    usableFieldcapacity = (20 + 1.3 * clay - 0.01 * clay * clay) / 230.0;

    if (waterContentArray != NULL)
      {
      waterContentArray->GetTuple(cellId, &waterContent);
      } else
      {
      waterContent = usableFieldcapacity;
      }
    /*  New RothC approach, disabled for comparison with old model
     if (soilCover == 0 || soilCover == this->NullValue)
     usableFieldcapacity /= 1.8;
     */
    // compute water budget for 1 horizon
    if ((precipitation - etpot) < 0)
      {
      waterContentNew = MAX(0, waterContent+(precipitation - etpot)/
          (lineLength*1000));
      } else
      {
      waterContentNew = MIN(usableFieldcapacity,waterContent +
          (precipitation - etpot)/(lineLength*1000));
      }
    /*
    cout << "ETpot " << etpot << " usableFieldcapacity " << usableFieldcapacity
        << " waterContentNew " << waterContentNew << " Precipitation "
        << precipitation << endl;
    */
    resultUsableFieldCapacity->SetTuple1(cellId, usableFieldcapacity);
    resultWaterContentNew->SetTuple1(cellId, waterContentNew);

    pointIds->Delete();
    }

  output->GetCellData()->AddArray(resultUsableFieldCapacity);
  output->GetCellData()->AddArray(etpotArray);
  output->GetCellData()->AddArray(resultWaterContentNew);
  output->GetCellData()->SetActiveScalars(resultWaterContentNew->GetName());

  resultUsableFieldCapacity->Delete();
  resultWaterContentNew->Delete();

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2ERothCWaterBudgetModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}
