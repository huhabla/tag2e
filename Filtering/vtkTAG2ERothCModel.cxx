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
#include "vtkTAG2ERothCDefines.h"
#include "vtkTAG2EDefines.h"

vtkCxxRevisionMacro(vtkTAG2ERothCModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ERothCModel);


#define DEFAULT_ROOTS 1

//----------------------------------------------------------------------------

vtkTAG2ERothCModel::vtkTAG2ERothCModel()
{
  this->RothCModelParameter = NULL;
  this->CPools = NULL;
  this->CPoolsInitiated = 0;
  this->AddCPoolsToOutput = 0;
  this->TemporalRatio = 1 / 12.0; // Default is monthly resolution
  this->EquilibriumRun = 0;
  this->SetResultArrayName(ROTHC_OUTPUT_NAME_SOIL_CARBON);
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
}

//----------------------------------------------------------------------------

vtkTAG2ERothCModel::~vtkTAG2ERothCModel()
{
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
                                    vtkInformationVector **inputVector,
                                    vtkInformationVector *outputVector)
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
  if (!input->GetCellData()->HasArray(ROTHC_POOL_NAME_DPM)
      || !input->GetCellData()->HasArray(ROTHC_POOL_NAME_RPM)
      || !input->GetCellData()->HasArray(ROTHC_POOL_NAME_BIO)
      || !input->GetCellData()->HasArray(ROTHC_POOL_NAME_HUM)
      || !input->GetCellData()->HasArray(ROTHC_POOL_NAME_IOM))
    hasInputPools = false;

  // Allocate the pool structure if empty or if it has different
  // number of points/cells
  if (this->CPools == NULL
      || this->CPools->GetNumberOfCells() != input->GetNumberOfCells()
      || this->CPools->GetNumberOfPoints() != input->GetNumberOfPoints())
    {
    if (this->CPools)
      this->CPools->Delete();
    this->CPools = vtkPolyData::New();
    this->CPools->CopyStructure(input);
    cout << "Allocating C-Pools" << endl;
    }

  // Copy the arrays from input to the pools
  if (hasInputPools && this->CPoolsInitiated == 0)
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
    cout << "Initializing C-Pools" << endl;
    this->CPoolsInitiatedOn();
    }

  // Initiate the C pools
  if (this->CPoolsInitiated == 0 && hasInputPools == false)
    {
    // Check for initial carbon array in the input
    if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_INITIAL_CARBON))
      {
      vtkErrorMacro("Initial soil carbon is missing in input dataset, assuming no initial carbon.");
      }

    this->CreateCPools(input);
    }
  // Check the array names

  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_CLAY))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_CLAY << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_MEAN_TEMPERATURE))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_MEAN_TEMPERATURE << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_SOILCOVER))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_SOILCOVER << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_SOIL_MOISTURE))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_SOIL_MOISTURE << "> is missing ");
    return -1;
    }
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_USABLE_FIELD_CAPACITY))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_USABLE_FIELD_CAPACITY << "> is missing ");
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
  vtkDataArray *dpmArray = this->CPools->GetCellData()->GetArray(
      ROTHC_POOL_NAME_DPM);
  vtkDataArray *rpmArray = this->CPools->GetCellData()->GetArray(
      ROTHC_POOL_NAME_RPM);
  vtkDataArray *bioArray = this->CPools->GetCellData()->GetArray(
      ROTHC_POOL_NAME_BIO);
  vtkDataArray *humArray = this->CPools->GetCellData()->GetArray(
      ROTHC_POOL_NAME_HUM);
  vtkDataArray *iomArray = this->CPools->GetCellData()->GetArray(
      ROTHC_POOL_NAME_IOM);
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
  vtkDataArray *soilMArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_SOIL_MOISTURE);
  vtkDataArray *usableFieldCArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_USABLE_FIELD_CAPACITY);
  vtkDataArray *fertCArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_FERTILIZER_CARBON);

  vtkDataArray *shootIdArray = input->GetCellData()->GetArray(ROTHC_INPUT_NAME_SHOOT_ID);
  vtkDataArray *rootIdArray = input->GetCellData()->GetArray(ROTHC_INPUT_NAME_ROOT_ID);
  vtkDataArray *fertIdArray = input->GetCellData()->GetArray(
        ROTHC_INPUT_NAME_FERTILIZER_ID);

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
#pragma omp parallel for private(cellId) shared(input, fertIdArray, shootIdArray,\
		fertCArray, usableFieldCArray, soilMArray, resSurfArray, soilCoverArray,\
		meanTempArray, clayArray, iomArray, humArray, bioArray, rpmArray, dpmArray,\
		result)
#endif
  for (cellId = 0; cellId < input->GetNumberOfCells(); cellId++)
    {
    double lineLength;
    double p1[3];
    double p2[3];
    double a, b, c; // rate modifiers
    double x1, x2, x3, x4;
    double a1, a2, a3; // rate modifier parameter
    double b1, b2, b3;
    double efficiency; // fraction of degraded C that remains
    double allocFractionbio, allocFractionhum;
    double dpm, rpm, bio, hum, iom; // Pools
    double dpm_old, rpm_old, bio_old, hum_old; //old_pools
    double meanTemp, fertC, usableFieldCapacity, soilMoisture, soilCover,
        resRoots, resSurf, clay;
    double fertId, shootId, rootId;

    vtkIdList *pointIds = vtkIdList::New();
    input->GetCellPoints(cellId, pointIds);

    // Check cell type, we support only lines
    if (input->GetCellType(cellId) != VTK_LINE)
      {
      vtkErrorMacro("Unsupported cell type.");
#ifndef OMP_PARALLELIZED
      return -1;
#else
      continue;
#endif
      }

    // We support only lines with two coordinates
    if (pointIds->GetNumberOfIds() != 2)
      {
      vtkErrorMacro("Unsupported line length.");
#ifndef OMP_PARALLELIZED
      return -1;
#else
      continue;
#endif
      }

    // We set them 0 if no residuals are provided
    if(resRootsArray)
      resRootsArray->GetTuple(cellId, &resRoots); // [ tC /ha/layer]
    else
      resRoots = 0.0;
    if(resSurfArray)
      resSurfArray->GetTuple(cellId, &resSurf); // [ tC /ha/layer]
    else
      resSurf = 0.0;

    clayArray->GetTuple(cellId, &clay);
    meanTempArray->GetTuple(cellId, &meanTemp);
    soilCoverArray->GetTuple(cellId, &soilCover); // 0 or 1 ?
    soilMArray->GetTuple(cellId, &soilMoisture); //[mm]
    usableFieldCArray->GetTuple(cellId, &usableFieldCapacity); // [mm]?

    if(!fertCArray || this->EquilibriumRun)
      fertC = 0.0;
    else
      fertCArray->GetTuple(cellId, &fertC); // [ tC /ha/layer]

    dpmArray->GetTuple(cellId, &dpm);
    rpmArray->GetTuple(cellId, &rpm);
    bioArray->GetTuple(cellId, &bio);
    humArray->GetTuple(cellId, &hum);
    iomArray->GetTuple(cellId, &iom);
    dpm_old = dpm;
    rpm_old = rpm;
    bio_old = bio;
    hum_old = hum;

    /*
    cout << "resRoots " << resRoots << " resSurf " << resSurf
         << " clay " << clay << " meanTemp " << meanTemp << " soilCover " << soilCover
         << " soilMoisture " << soilMoisture << " usableFieldCapacity " << usableFieldCapacity
         << " fertC " << fertC << endl;
  */

    // Set the result to NULL in case some values are empty (NULL)
    if (clay == this->NullValue || meanTemp == this->NullValue
        || soilMoisture == this->NullValue
        || usableFieldCapacity == this->NullValue || dpm == this->NullValue
        || rpm == this->NullValue || bio == this->NullValue
        || hum == this->NullValue || iom == this->NullValue)
      {
      result->SetTuple1(cellId, this->NullValue);
      continue;
      }

    // Root index 0 is the default value
    if (rootIdArray)
      {
      rootIdArray->GetTuple(cellId, &rootId);
      if ((int)rootId == this->NullValue)
        rootId = 0;
      }
    else
      {
      rootId = 0;
      }

    // Shoot index 0 is the default value
    if (shootIdArray)
      {
      shootIdArray->GetTuple(cellId, &shootId);
      if ((int)shootId == this->NullValue)
        shootId = 0;
      }
    else
      {
      shootId = 0;
      }

    if (fertIdArray)
      {
      fertIdArray->GetTuple(cellId, &fertId);
      if ((int)fertId == this->NullValue)
        fertId = 0;
      }
    else
      {
      fertId = 0;
      }

    // Compute length of the line in vertical direction
    input->GetPoint(pointIds->GetId(0), p1);
    input->GetPoint(pointIds->GetId(1), p2);
    lineLength = fabs(p1[2] - p2[2]);

    a1 = R.a.a1.value;
    a2 = R.a.a2.value;
    a3 = R.a.a3.value;

    // a of (1 - e^(-abckt)) (Temperature Response)
    a = a1 / (1.0 + exp(a2 / (meanTemp + a3)));

    // b (moistureResponse)
    b1 = R.b.b1.value;
    b2 = R.b.b2.value;
    b3 = R.b.b3.value;

    if (soilMoisture > usableFieldCapacity * b3)
      b = 1;
    else
      b = b1 + (b2 - b1) * soilMoisture / (usableFieldCapacity * b3);

    // c (soilcover_factor)
    if(this->EquilibriumRun)
      {
      c = 0.6;
      }
    else
      {
      if (soilCover == 0 || soilCover == this->NullValue)
        c = 1.0;
      else
        c = 0.6;
      }

    // efficiency , that describes how much of degraded C remains in the system
    // and is not blown out as CO2

    x1 = R.x.x1.value;
    x2 = R.x.x2.value;
    x3 = R.x.x3.value;
    x4 = R.x.x4.value;

    efficiency = x1 * (x2 + x3 * exp(x4 * clay));
    efficiency = 1 / (1 + efficiency);
    allocFractionhum = 0.54;
    allocFractionbio = 0.46;

    if (R.PlantFractions.size() <= shootId || R.PlantFractions.size() <= rootId)
      {
      vtkErrorMacro("Shoot/root ids out of plant fraction vector boundaries");
#ifndef OMP_PARALLELIZED
      return -1;
#else
      continue;
#endif
      }
#ifdef DEFAULT_ROOTS
    double dpmRootsFraction = R.PlantFractions[rootId]->DPM.value;
    double rpmRootsFraction = R.PlantFractions[rootId]->RPM.value;
    double humRootsFraction = R.PlantFractions[rootId]->HUM.value;
#else
    /* Work around, values from a mean calibration */
    double dpmRootsFraction = 0.2656288362015;
    double rpmRootsFraction = 0.7343711637985;
    double humRootsFraction = 0;
#endif
    double dpmSurfFraction = R.PlantFractions[shootId]->DPM.value;
    double rpmSurfFraction = R.PlantFractions[shootId]->RPM.value;
    double humSurfFraction = R.PlantFractions[shootId]->HUM.value;

    if (R.FertilizerFractions.size() <= fertId)
      {
      vtkErrorMacro(
          "Fertilizer id is out of fertilizer fraction vector boundaries");
#ifndef OMP_PARALLELIZED
      return -1;
#else
      continue;
#endif
      }

    double dpmFertFraction = R.FertilizerFractions[fertId]->DPM.value;
    double rpmFertFraction = R.FertilizerFractions[fertId]->RPM.value;
    double humFertFraction = R.FertilizerFractions[fertId]->HUM.value;

    // CPool computation
    // 1. Add residues from crop and fertilization
    dpm_old = dpm_old + dpmRootsFraction * resRoots + dpmSurfFraction * resSurf
        + dpmFertFraction * fertC;
    rpm_old = rpm_old + rpmRootsFraction * resRoots + rpmSurfFraction * resSurf
        + rpmFertFraction * fertC;
    hum_old = hum_old + humRootsFraction * resRoots + humSurfFraction * resSurf
        + humFertFraction * fertC;

    // Degradation
    double degradedC = 0;
    double dpm_k, rpm_k, hum_k, bio_k;
    dpm_k = R.k.DPM.value;
    rpm_k = R.k.RPM.value;
    hum_k = R.k.HUM.value;
    bio_k = R.k.BIO.value;

    // cout << "a " << a << " b " << b << " c " << c << " dpmRootsFraction "
    //     << dpmRootsFraction << " dpmSurfFraction " << dpmSurfFraction
    //     << " dpmFertFraction " << dpmFertFraction << endl;

    dpm = dpm_old * exp(-1.0 * dpm_k * a * b * c * this->TemporalRatio);
    degradedC = degradedC + (dpm_old - dpm);

    rpm = rpm_old * exp(-1.0 * rpm_k * a * b * c * this->TemporalRatio);
    degradedC = degradedC + (rpm_old - rpm);

    hum = hum_old * exp(-1.0 * hum_k * a * b * c * this->TemporalRatio);
    degradedC = degradedC + (hum_old - hum);

    bio = bio_old * exp(-1.0 * bio_k * a * b * c * this->TemporalRatio);
    degradedC = degradedC + (bio_old - bio);

    // cout << "dpm_old " << dpm_old << " rpm_old " << rpm_old << " hum_old "
    //     << hum_old << " bio_old " << bio_old << " dpm " << dpm << " rpm " << rpm
    //     << " hum " << hum << " bio " << bio << endl;

    // Adding all that is not CO2 to bio and hum
    hum = hum + degradedC * efficiency * allocFractionhum;
    bio = bio + degradedC * efficiency * allocFractionbio;

    // cout << "bio_new: " << bio << " degradedC  " << degradedC << " efficiency  "
    //     << efficiency << endl;

    result->SetTuple1(cellId, dpm + rpm + bio + hum + iom);

    dpmArray->SetTuple1(cellId, dpm);
    rpmArray->SetTuple1(cellId, rpm);
    bioArray->SetTuple1(cellId, bio);
    humArray->SetTuple1(cellId, hum);

    pointIds->Delete();
    }

  if(input->GetCellData()->HasArray("Layer"))
    output->GetCellData()->AddArray(input->GetCellData()->GetArray("Layer"));
  output->GetCellData()->AddArray(result);
  output->GetCellData()->SetActiveScalars(result->GetName());

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

  cout << "CreateCPools from initial carbon" << endl;

  // Set up the arrays
  dpmArray->SetName(ROTHC_POOL_NAME_DPM);
  dpmArray->SetNumberOfComponents(1);
  dpmArray->SetNumberOfTuples(input->GetNumberOfCells());
  rpmArray->SetName(ROTHC_POOL_NAME_RPM);
  rpmArray->SetNumberOfComponents(1);
  rpmArray->SetNumberOfTuples(input->GetNumberOfCells());
  bioArray->SetName(ROTHC_POOL_NAME_BIO);
  bioArray->SetNumberOfComponents(1);
  bioArray->SetNumberOfTuples(input->GetNumberOfCells());
  humArray->SetName(ROTHC_POOL_NAME_HUM);
  humArray->SetNumberOfComponents(1);
  humArray->SetNumberOfTuples(input->GetNumberOfCells());
  iomArray->SetName(ROTHC_POOL_NAME_IOM);
  iomArray->SetNumberOfComponents(1);
  iomArray->SetNumberOfTuples(input->GetNumberOfCells());

  // Copy the geometric structure from input
  if (this->CPools == NULL)
    {
    this->CPools = vtkPolyData::New();
    this->CPools->CopyStructure(input);
    }

  // For easy initial C access
  initCArray = input->GetCellData()->GetArray(ROTHC_INPUT_NAME_INITIAL_CARBON);


#ifdef OMP_PARALLELIZED
#pragma omp parallel for private(i) shared(initCArray)
#endif
  for (i = 0; i < input->GetNumberOfCells(); i++)
    {
    double dpm, rpm, bio, hum, iom, initC;
    // In case the array is not provided, 0.0 is assumed
    if(initCArray)
      initCArray->GetTuple(i, &initC);
    else
      initC = 0.0;

    if(initC == this->NullValue)
      {
      iom = this->NullValue;
      dpm = this->NullValue;
      rpm = this->NullValue;
      bio = this->NullValue;
      hum = this->NullValue;
      }
    else
      {
      // Compute the pools
      // IOM with Falloon equation
      iom = 0.049 * pow(initC, 1.139);
      dpm = 0.01 * (initC - iom);
      rpm = 0.12 * (initC - iom);
      bio = 0.02 * (initC - iom);
      hum = 0.85 * (initC - iom);
      }

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
