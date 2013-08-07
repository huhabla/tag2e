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
#include "vtkTAG2ETurcETPotModel.h"
#include "vtkTAG2ERothCDefines.h"
#include "vtkTAG2EDefines.h"

vtkCxxRevisionMacro(vtkTAG2ETurcETPotModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ETurcETPotModel);

//----------------------------------------------------------------------------

vtkTAG2ETurcETPotModel::vtkTAG2ETurcETPotModel()
{
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
  this->SetResultArrayName(ROTHC_INPUT_NAME_ETPOT);
  this->TimeInterval = 1; // Default a single day
  this->RadiationInWatt = 1;
}

//----------------------------------------------------------------------------

vtkTAG2ETurcETPotModel::~vtkTAG2ETurcETPotModel()
{
  ;
}

//----------------------------------------------------------------------------

int vtkTAG2ETurcETPotModel::FillInputPortInformation(int vtkNotUsed(port),
                                                    vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkDataSet");
  return 1;
}

//----------------------------------------------------------------------------
int vtkTAG2ETurcETPotModel::FillOutputPortInformation(int port,
                                                     vtkInformation* info)
{
  if (!this->Superclass::FillOutputPortInformation(port, info))
    {
    return 0;
    }

  // now add our info
  info->Set(vtkDataObject::DATA_TYPE_NAME(), "vtkDataSet");
  return 1;
}

//----------------------------------------------------------------------------

int vtkTAG2ETurcETPotModel::RequestData(vtkInformation * vtkNotUsed(request),
                                       vtkInformationVector **inputVector,
                                       vtkInformationVector *outputVector)
{
  vtkIdType cellId;

  vtkDataSet* input = vtkDataSet::GetData(inputVector[0]);
  vtkDataSet* output = vtkDataSet::GetData(outputVector);


  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_GLOBAL_RADIATION))
    {
    vtkErrorMacro(<<"Cell data array <" << ROTHC_INPUT_NAME_GLOBAL_RADIATION
                  << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_MEAN_TEMPERATURE))
    {
    vtkErrorMacro(<<"Cell data array <" << ROTHC_INPUT_NAME_MEAN_TEMPERATURE
                  << "> is missing ");
    return -1;
    }

  // Copy geometry from input
  output->CopyStructure(input);

  // Result array
  vtkDoubleArray *result = vtkDoubleArray::New();
  result->SetNumberOfComponents(1);
  result->SetName(this->ResultArrayName);
  result->SetNumberOfTuples(output->GetNumberOfCells());

  // Get array pointer for easy access
  vtkDataArray *globalRadiationArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_GLOBAL_RADIATION);
  vtkDataArray *meanTemperatureArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_MEAN_TEMPERATURE);

  // Parallelize with OpenMP
#ifdef OMP_PARALLELIZED
#pragma omp parallel for private(cellId) shared(input, result,\
		globalRadiationArray, meanTemperatureArray)
#endif
  for (cellId = 0; cellId < input->GetNumberOfCells(); cellId++)
    {
    double globalRadiation;
    globalRadiationArray->GetTuple(cellId, &globalRadiation);
    double meanTemperature;
    meanTemperatureArray->GetTuple(cellId, &meanTemperature);

    // Jump over NULL values
    if(globalRadiation == this->NullValue || meanTemperature == this->NullValue)
      {
      result->SetTuple1(cellId, this->NullValue);
      continue;
      }

    // The global radiation can be in J/(cm^2*s) or in W/m^2
    // Here we compute J/(cm^2 * s) from w/m^2
    if(this->RadiationInWatt == 1)
      globalRadiation = globalRadiation *36.0 * 24.0/100.0;

    double etp = 0.0031 *
                ((meanTemperature / (meanTemperature + 15.0)) *
                (globalRadiation + 209.0));

    if (etp < 0.0)
      etp = 0.0;

    else if (etp > 7.0)
      etp = 7.0;

    result->SetTuple1(cellId, etp * this->TimeInterval);
    }

  output->GetCellData()->AddArray(result);
  output->GetCellData()->SetActiveScalars(result->GetName());
  result->Delete();

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2ETurcETPotModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}
