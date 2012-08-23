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
#include "vtkTAG2ERothCModel.h"
#include "vtkTAG2ERothCModelParameter.h"
#include "vtkTAG2EAbstractModelParameter.h"

vtkCxxRevisionMacro(vtkTAG2ERothCModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ERothCModel);

//----------------------------------------------------------------------------

vtkTAG2ERothCModel::vtkTAG2ERothCModel()
{
  this->RothCModelParameter = NULL;
  this->CPools = NULL;
  this->CPoolsInitiated = 0;
  this->AddCPoolsToOutput = 0;
  this->TemporalRatio = 1 / 12.0; // Default is monthly resolution
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
}

//----------------------------------------------------------------------------

vtkTAG2ERothCModel::~vtkTAG2ERothCModel()
{
  if (this->RothCModelParameter)
    this->RothCModelParameter->Delete();
  if (this->CPools)
    this->CPools->Delete();
}

//----------------------------------------------------------------------------

int vtkTAG2ERothCModel::FillInputPortInformation(int vtkNotUsed(port),
    vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkPolyData");
  return 1;
}

//----------------------------------------------------------------------------
int vtkTAG2ERothCModel::FillOutputPortInformation(int port,
    vtkInformation* info)
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

void vtkTAG2ERothCModel::SetModelParameter(
    vtkTAG2EAbstractModelParameter* modelParameter)
{
  this->Superclass::SetModelParameter(modelParameter);

  // Check if the ModelParameter is of correct type
  if (this->ModelParameter->IsA("vtkTAG2ERothCModelParameter"))
    {
    this->RothCModelParameter =
        static_cast<vtkTAG2ERothCModelParameter *>(this->ModelParameter);
    } else
    {
    vtkErrorMacro(
        << "The ModelParameter is not of type vtkTAG2ERothCModelParameter");
    this->SetModelParameter(NULL);
    return;
    }

  // Generate the internal representation
  this->RothCModelParameter->GenerateInternalSchemeFromXML();

  this->Modified();
}

//----------------------------------------------------------------------------

int vtkTAG2ERothCModel::RequestData(vtkInformation * vtkNotUsed(request),
    vtkInformationVector **inputVector, vtkInformationVector *outputVector)
{
  vtkIdType i;
  vtkIdType cellId;
  bool hasInputPools = true;

  // Check for model parameter
  if (this->ModelParameter == NULL)
    {
    vtkErrorMacro("Model parameter not set or invalid.");
    return -1;
    }

  // the internal parameter object for fast access
  RothC &R = this->RothCModelParameter->GetInternalScheme();

  vtkPolyData* input = vtkPolyData::GetData(inputVector[0]);
  vtkPolyData* output = vtkPolyData::GetData(outputVector);

  // Check if the input has the C pools
  if (!input->GetCellData()->GetArray(ROTHC_POOL_NAME_DPM)
      || !input->GetCellData()->GetArray(ROTHC_POOL_NAME_RPM)
      || !input->GetCellData()->GetArray(ROTHC_POOL_NAME_BIO)
      || !input->GetCellData()->GetArray(ROTHC_POOL_NAME_HUM)
      || !input->GetCellData()->GetArray(ROTHC_POOL_NAME_IOM))
    hasInputPools = false;

  // Initiate the C pools
  if ((this->CPools == NULL || this->CPoolsInitiated == 0)
      && hasInputPools == false)
    {
    // Check for initial carbon array in the input

    if (!input->GetCellData()->GetArray(ROTHC_INPUT_NAME_INITIAL_CARBON))
      {
      vtkErrorMacro("Initial soil carbon is missing in input dataset");
      return -1;
      }

    this->CreateCPools(input);
    }

  // Allocate the pool structure if empty or if it has different
  // number of points/cells
  if (this->CPools == NULL
      || this->CPools->GetNumberOfCells() != input->GetNumberOfCells()
      || this->CPools->GetNumberOfCells() != input->GetNumberOfCells())
    {
    if (this->CPools)
      this->CPools->Delete();
    this->CPools = vtkPolyData::New();
    this->CPools->CopyStructure(input);
    }

  // Copy the arrays from input to the pools
  if (hasInputPools)
    {
    for (i = 0; i < this->CPools->GetCellData()->GetNumberOfArrays(); i++)
      this->CPools->GetCellData()->RemoveArray(i);

    this->CPools->GetCellData()->AddArray(
        input->GetCellData()->GetArray(ROTHC_POOL_NAME_DPM));
    this->CPools->GetCellData()->AddArray(
        input->GetCellData()->GetArray(ROTHC_POOL_NAME_RPM));
    this->CPools->GetCellData()->AddArray(
        input->GetCellData()->GetArray(ROTHC_POOL_NAME_BIO));
    this->CPools->GetCellData()->AddArray(
        input->GetCellData()->GetArray(ROTHC_POOL_NAME_HUM));
    this->CPools->GetCellData()->AddArray(
        input->GetCellData()->GetArray(ROTHC_POOL_NAME_IOM));
    }

  // Copy geometry from input
  output->CopyStructure(input);

  // Result array
  vtkDoubleArray *result = vtkDoubleArray::New();
  result->SetNumberOfComponents(1);
  result->SetName(this->ResultArrayName);
  result->SetNumberOfTuples(output->GetNumberOfCells());

  // ###########################################################################
  // ####################### RothC Computation Start ###########################
  // ###########################################################################

  // Get array pointer for easy access
  vtkDataArray *dpmArray = this->CPools->GetCellData()->GetArray(
      ROTHC_POOL_NAME_DPM);
  vtkDataArray *rpmArray = this->CPools->GetCellData()->GetArray(
      ROTHC_POOL_NAME_RPM);
  vtkDataArray *bioArray = this->CPools->GetCellData()->GetArray(
      ROTHC_POOL_NAME_BIO);
  vtkDataArray *humArray = this->CPools->GetCellData()->GetArray(
      ROTHC_POOL_NAME_HUM);
  vtkDataArray *clayArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_CLAY);
  vtkDataArray *meanTempArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_MEAN_TEMPERATURE);
  vtkDataArray *soilCoverArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_SOILCOVER);
  vtkDataArray *resRootsArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_RESIDUALS_ROOTS);
  vtkDataArray *resSurfArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_RESIDUALS_SURFACE);
  vtkDataArray *plantIdArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_PLANT_ID);
  vtkDataArray *fertIdArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_FERTILIZER_ID);
  vtkDataArray *soilMArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_SOIL_MOISTURE);
  vtkDataArray *fieldCArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_FIELD_CAPACITY);
  vtkDataArray *fertCArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_FERTILIZER_CARBON);

  vtkIdList *pointIds = vtkIdList::New();
  vtkIdType pointId;

  double a, b, c, k; // rate modifiers
  double a1, a2, a3; // raster modifier a parameter
  double b1, b2, b3, b4, b5, b6, b7;
  double dpm, rpm, bio, hum; // Pools
  double meanTemp, fertC, fieldC, soilM, soilCover, resRoots, resSurf, clay;
  int fertId, plantId;

  for (cellId = 0; cellId < input->GetNumberOfCells(); cellId++)
    {
    double lineLength;
    double *p1;
    double *p2;
    bool isSurface = false;

    // Check cell type, we support only lines
    if (input->GetCellType(cellId) != VTK_LINE)
      {
      vtkErrorMacro("Unsupported cell type.");
      return -1;
      }
    // We support only lines with two coordinates
    if (pointIds->GetNumberOfIds() != 2)
      {
      vtkErrorMacro("Unsupported line length.");
      return -1;
      }

    clay = clayArray->GetTuple1(cellId);
    meanTemp = meanTempArray->GetTuple1(cellId);
    soilCover = soilCoverArray->GetTuple1(cellId);
    resRoots = resRootsArray->GetTuple1(cellId);
    resSurf = resSurfArray->GetTuple1(cellId);
    plantId = (int) plantIdArray->GetTuple1(cellId);
    fertId = (int) fertIdArray->GetTuple1(cellId);
    soilM = soilMArray->GetTuple1(cellId);
    fieldC = fieldCArray->GetTuple1(cellId);
    fertC = fertCArray->GetTuple1(cellId);

    // Set the result to NULL in case some values are empty (NULL)
    if (clay == this->NullValue || meanTemp == this->NullValue
        || soilM == this->NullValue || fieldC == this->NullValue)
      {
      result->SetTuple1(cellId, this->NullValue);
      continue;
      }

    // Get array values

    // Compute length of the line in vertical direction
    input->GetCellPoints(cellId, pointIds);
    p1 = input->GetPoint(pointIds->GetId(0));
    p2 = input->GetPoint(pointIds->GetId(1));
    lineLength = fabs(p1[2] - p2[2]);

    a1 = R.a.a1.value;
    a2 = R.a.a2.value;
    a3 = R.a.a3.value;
    // a of (1 - e^(-abckt))
    a = a1 / (1.0 + exp(a2 / (meanTemp + a3)));

    if (soilCover == 0 || soilCover == this->NullValue)
      c = 1.0;
    else
      c = 0.6;

    dpm = rpm = bio = hum = 0;

    result->SetTuple1(cellId, dpm + rpm + bio + hum);

    dpmArray->SetTuple1(cellId, dpm);
    rpmArray->SetTuple1(cellId, rpm);
    bioArray->SetTuple1(cellId, bio);
    humArray->SetTuple1(cellId, hum);
    }

  pointIds->Delete();

  // ###########################################################################
  // ####################### RothC Computation End #############################
  // ###########################################################################

  output->GetCellData()->AddArray(result);

  if (this->AddCPoolsToOutput)
    {
    for (i = 0; i < this->CPools->GetCellData()->GetNumberOfArrays(); i++)
      output->GetCellData()->AddArray(this->CPools->GetCellData()->GetArray(i));
    }

  result->Delete();

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2ERothCModel::CreateCPools(vtkPolyData *input)
{
  vtkDoubleArray *dpmArray = vtkDoubleArray::New();
  vtkDoubleArray *rpmArray = vtkDoubleArray::New();
  vtkDoubleArray *bioArray = vtkDoubleArray::New();
  vtkDoubleArray *humArray = vtkDoubleArray::New();
  vtkDoubleArray *iomArray = vtkDoubleArray::New();
  vtkDataArray *initCArray = NULL;
  vtkIdType i;
  double dpm, rpm, bio, hum, iom, initC;

  // Set up the arrays
  dpmArray->SetName(ROTHC_POOL_NAME_DPM);
  dpmArray->SetNumberOfComponents(1);
  dpmArray->SetNumberOfTuples(input->GetNumberOfCells());

  // Copy the geometric structure from input
  if (this->CPools == NULL)
    {
    this->CPools = vtkPolyData::New();
    this->CPools->CopyStructure(input);
    }

  // For easy initial C access
  initCArray = input->GetCellData()->GetArray(ROTHC_INPUT_NAME_INITIAL_CARBON);

  for (i = 0; i < input->GetNumberOfCells(); i++)
    {
    initC = initCArray->GetTuple1(i);

    // Compute the pools
    dpm = rpm = bio = hum = iom = initC / 5.0;

    dpmArray->SetTuple1(i, dpm);
    rpmArray->SetTuple1(i, rpm);
    bioArray->SetTuple1(i, bio);
    humArray->SetTuple1(i, hum);
    iomArray->SetTuple1(i, iom);
    }

  // Add the pool arrays to the C pool dataset
  this->CPools->GetCellData()->AddArray(dpmArray);
  this->CPools->GetCellData()->AddArray(rpmArray);
  this->CPools->GetCellData()->AddArray(bioArray);
  this->CPools->GetCellData()->AddArray(humArray);
  this->CPools->GetCellData()->AddArray(iomArray);

  dpmArray->Delete();
  rpmArray->Delete();
  bioArray->Delete();
  humArray->Delete();
  iomArray->Delete();

  this->CPoolsInitiatedOn();
}

//----------------------------------------------------------------------------

void vtkTAG2ERothCModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}
