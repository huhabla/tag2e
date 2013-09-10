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
#include "vtkTAG2ERothCModelEquilibrium.h"
#include "vtkTAG2ERothCModelParameter.h"
#include "vtkTAG2EAbstractModelParameter.h"
#include "vtkTAG2EDefines.h"

vtkCxxRevisionMacro(vtkTAG2ERothCModelEquilibrium, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ERothCModelEquilibrium);

//----------------------------------------------------------------------------

vtkTAG2ERothCModelEquilibrium::vtkTAG2ERothCModelEquilibrium()
{
  this->RothCModelParameter = NULL;
  this->CPools = NULL;
  this->AddCPoolsToOutput = 0;
  this->TemporalResolution = 12; // Default is monthly resolution
  this->NumberOfYears = 300;
  this->SetResultArrayName(ROTHC_OUTPUT_NAME_SOIL_CARBON);
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
}

//----------------------------------------------------------------------------

vtkTAG2ERothCModelEquilibrium::~vtkTAG2ERothCModelEquilibrium()
{
  if (this->CPools)
    this->CPools->Delete();
}

//----------------------------------------------------------------------------

int vtkTAG2ERothCModelEquilibrium::FillInputPortInformation(
    int vtkNotUsed(port), vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkPolyData");
  info->Set(vtkAlgorithm::INPUT_IS_REPEATABLE(), 1);
  return 1;
}

//----------------------------------------------------------------------------
int vtkTAG2ERothCModelEquilibrium::FillOutputPortInformation(
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

void vtkTAG2ERothCModelEquilibrium::SetModelParameter(
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

int vtkTAG2ERothCModelEquilibrium::RequestData(
    vtkInformation * vtkNotUsed(request), vtkInformationVector **inputVector,
    vtkInformationVector *outputVector)
{
  vtkIdType i = 0, j = 0;
  vtkIdType cellId;
  bool hasInputPools = true;
  bool hasPlantId = true;
  bool hasFertilizerId = true;
  int numInputs = inputVector[0]->GetNumberOfInformationObjects();

  // Check for model parameter
  if (this->ModelParameter == NULL)
    {
    vtkErrorMacro("Model parameter not set or invalid.");
    return -1;
    }

  vtkPolyData* firstInput = vtkPolyData::GetData(inputVector[0], i);
  vtkPolyData* output = vtkPolyData::GetData(outputVector);
  
  // Check for initial carbon array in the input
  if (!firstInput)
  {
      vtkErrorMacro( "First input dataset is missing.");
      return -1;
  }
  
  // Check for initial carbon array in the input
  if (!firstInput->GetCellData()->HasArray(ROTHC_INPUT_NAME_INITIAL_CARBON))
    {
    vtkErrorMacro( "Initial soil carbon is missing in first input dataset.");
    return -1;
    }

  // Compute responses
  if (this->ComputeResponses(inputVector) == -1)
    {
    vtkErrorMacro("Unable to compute responses.");
    return -1;
    }

  // Create pools
  if (this->CPools)
    this->CPools->Delete();
  this->CPools = vtkPolyData::New();
  this->CPools->CopyStructure(firstInput);
  cout << "Allocating C-Pools" << endl;
  this->CreateCPools(firstInput);

  // the internal parameter object for fast access
  RothC &R = this->RothCModelParameter->GetInternalScheme();

  // Copy geometry from input
  output->CopyStructure(firstInput);

#ifdef OMP_PARALLELIZED
  // For line length computation
  for (i = 0; i < this->TemporalResolution; i++)
    {
    vtkPolyData* input = vtkPolyData::GetData(inputVector[0], i);
    // We must call the following method first in a single thread to
    // avoid race conditions
    if (input->GetNumberOfCells() > 0)
      {
      vtkIdList *tmp = vtkIdList::New();
      input->GetCellPoints(0, tmp);
      input->GetCellType(0);
      tmp->Delete();
      }
    }
#endif

  // Result array
  vtkDoubleArray *result = vtkDoubleArray::New();
  result->SetNumberOfComponents(1);
  result->SetName(this->ResultArrayName);
  result->SetNumberOfTuples(output->GetNumberOfCells());

  // Id's for plants taken from the first input
  vtkDataArray *plantIdArray = firstInput->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_PLANT_ID);

  cout << "Equilibrium run start" << endl;

  for (j = 0; j < this->NumberOfYears; j++)
    {
    for (i = 0; i < this->TemporalResolution; i++)
      {
      vtkPolyData* input = vtkPolyData::GetData(inputVector[0], i);
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

#ifdef OMP_PARALLELIZED
#pragma omp parallel for private(cellId)
#endif
      for (cellId = 0; cellId < firstInput->GetNumberOfCells(); cellId++)
        {
        double lineLength;
        double p1[3];
        double p2[3];
        double a_res, b_res, c_res; // rate modifiers
        double efficiency; // fraction of degraded C that remains
        double allocFractionbio, allocFractionhum;
        double dpm, rpm, bio, hum, iom; // Pools
        double dpm_old, rpm_old, bio_old, hum_old; //old_pools
        double meanTemp, fertC, usableFieldCapacity, soilMoisture, soilCover,
            resRoots, resSurf, clay;
        double plantId;

        // The line length is not needed yet
        /*
         vtkIdList *pointIds = vtkIdList::New();
         input->GetCellPoints(cellId, pointIds);

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

         // Compute length of the line in vertical direction
         input->GetPoint(pointIds->GetId(0), p1);
         input->GetPoint(pointIds->GetId(1), p2);
         lineLength = fabs(p1[2] - p2[2]);
         */

        dpmArray->GetTuple(cellId, &dpm);
        rpmArray->GetTuple(cellId, &rpm);
        bioArray->GetTuple(cellId, &bio);
        humArray->GetTuple(cellId, &hum);
        iomArray->GetTuple(cellId, &iom);
        dpm_old = dpm;
        rpm_old = rpm;
        bio_old = bio;
        hum_old = hum;

        // Index 0 is the default value
        if (plantIdArray)
          {
          plantIdArray->GetTuple(cellId, &plantId);
          if ((int) plantId == this->NullValue)
            plantId = 0;
          } else
          {
          plantId = 0;
          }

        // Get the responses
        a_res = (*this->a[i])[cellId];
        b_res = (*this->b[i])[cellId];
        efficiency = (*this->x[i])[cellId];
        resRoots = (*this->roots[i])[cellId];
        resSurf = (*this->surface[i])[cellId];

        // Constants
        // we assume soil cover in the equilibrium run
        c_res = 0.6;
        allocFractionhum = 0.54;
        allocFractionbio = 0.46;

        if (R.PlantFractions.size() <= plantId)
          {
          vtkErrorMacro("Plant id is out of plant fraction vector boundaries");
#ifndef OMP_PARALLELIZED
          return -1;
#else
          continue;
#endif
          }

        double dpmRootsFraction = R.PlantFractions[plantId]->DPM.value;
        double rpmRootsFraction = R.PlantFractions[plantId]->RPM.value;
        double humRootsFraction = R.PlantFractions[plantId]->HUM.value;

        double dpmSurfFraction = R.PlantFractions[plantId]->DPM.value;
        double rpmSurfFraction = R.PlantFractions[plantId]->RPM.value;
        double humSurfFraction = R.PlantFractions[plantId]->HUM.value;

        // CPool computation
        // 1. Add residues from crop and fertilization
        dpm_old = dpm_old + dpmRootsFraction * resRoots
            + dpmSurfFraction * resSurf;
        rpm_old = rpm_old + rpmRootsFraction * resRoots
            + rpmSurfFraction * resSurf;
        hum_old = hum_old + humRootsFraction * resRoots
            + humSurfFraction * resSurf;

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

        dpm = dpm_old
            * exp(
                -1.0 * dpm_k * a_res * b_res * c_res
                    / this->TemporalResolution);
        degradedC = degradedC + (dpm_old - dpm);

        rpm = rpm_old
            * exp(
                -1.0 * rpm_k * a_res * b_res * c_res
                    / this->TemporalResolution);
        degradedC = degradedC + (rpm_old - rpm);

        hum = hum_old
            * exp(
                -1.0 * hum_k * a_res * b_res * c_res
                    / this->TemporalResolution);
        degradedC = degradedC + (hum_old - hum);

        bio = bio_old
            * exp(
                -1.0 * bio_k * a_res * b_res * c_res
                    / this->TemporalResolution);
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

        //pointIds->Delete();
        }
      }
    }

  if (firstInput->GetCellData()->HasArray("Layer"))
    output->GetCellData()->AddArray(
        firstInput->GetCellData()->GetArray("Layer"));
  output->GetCellData()->AddArray(result);
  output->GetCellData()->SetActiveScalars(result->GetName());

  if (this->AddCPoolsToOutput)
    {
    for (i = 0; i < this->CPools->GetCellData()->GetNumberOfArrays(); i++)
      output->GetCellData()->AddArray(this->CPools->GetCellData()->GetArray(i));
    }

  result->Delete();

  cout << "Equilibrium run finished" << endl;

  return 1;
}

//----------------------------------------------------------------------------

int vtkTAG2ERothCModelEquilibrium::ComputeResponses(
    vtkInformationVector **inputVector)
{
  vtkIdType i = 0, j = 0;
  vtkIdType cellId;
  bool hasInputPools = true;
  bool hasPlantId = true;
  bool hasFertilizerId = true;
  int numInputs = inputVector[0]->GetNumberOfInformationObjects();

  cout << "Compute response functions" << endl;

  // Check the temporal resolution
  if (this->TemporalResolution == ROTHC_YEARLY
      || this->TemporalResolution == ROTHC_MONTHLY)
    {
    if (ROTHC_MONTHLY != numInputs)
      {
      vtkErrorMacro(
          <<"Incorrect number of inputs, expected " << ROTHC_MONTHLY << ", got " << numInputs);
      return -1;
      }
    } else
    {
    vtkErrorMacro( <<"Incorrect temporal resolution, expected 1 or 12");
    return -1;
    }

  // We need the first input
  vtkPolyData* firstInput = vtkPolyData::GetData(inputVector[0], i);

  // the internal parameter object for fast access
  RothC &R = this->RothCModelParameter->GetInternalScheme();

  // Now we add the data arrays from all inputs to the output
  for (i = 0; i < numInputs; i++)
    {
    vtkPolyData* input = vtkPolyData::GetData(inputVector[0], i);

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
    }

  // Now we add the data arrays from all inputs to the output
  for (i = 0; i < numInputs; i++)
    {
    vtkDataSet* input = vtkDataSet::GetData(inputVector[0], i);

    vtkDataArray *clayArray = input->GetCellData()->GetArray(
        ROTHC_INPUT_NAME_CLAY);
    vtkDataArray *meanTempArray = input->GetCellData()->GetArray(
        ROTHC_INPUT_NAME_MEAN_TEMPERATURE);
    vtkDataArray *soilMArray = input->GetCellData()->GetArray(
        ROTHC_INPUT_NAME_SOIL_MOISTURE);
    vtkDataArray *usableFieldCArray = input->GetCellData()->GetArray(
        ROTHC_INPUT_NAME_USABLE_FIELD_CAPACITY);
    vtkDataArray *fertCArray = input->GetCellData()->GetArray(
        ROTHC_INPUT_NAME_FERTILIZER_CARBON);

    // Residuals are optional
    vtkDataArray *resRootsArray = input->GetCellData()->GetArray(
        ROTHC_INPUT_NAME_RESIDUALS_ROOTS);
    vtkDataArray *resSurfArray = input->GetCellData()->GetArray(
        ROTHC_INPUT_NAME_RESIDUALS_SURFACE);

    std::vector<double> *a_resp = new std::vector<double>;
    std::vector<double> *b_resp = new std::vector<double>;
    std::vector<double> *x_resp = new std::vector<double>;
    std::vector<double> *roots_resp = new std::vector<double>;
    std::vector<double> *surf_resp = new std::vector<double>;

    for (cellId = 0; cellId < input->GetNumberOfCells(); cellId++)
      {
      double a, b, x; // rate modifiers
      double x1, x2, x3, x4;
      double a1, a2, a3; // rate modifier parameter
      double b1, b2, b3;
      double meanTemp, usableFieldCapacity, soilMoisture, clay, resRoots,
          resSurf;

      // We set them 0 if no residuals are provided
      if (resRootsArray)
        resRootsArray->GetTuple(cellId, &resRoots); // [ tC /ha/layer]
      else
        resRoots = 0.0;
      if (resSurfArray)
        resSurfArray->GetTuple(cellId, &resSurf); // [ tC /ha/layer]
      else
        resSurf = 0.0;

      roots_resp->push_back(resRoots);
      surf_resp->push_back(resSurf);

      clayArray->GetTuple(cellId, &clay);
      meanTempArray->GetTuple(cellId, &meanTemp);
      soilMArray->GetTuple(cellId, &soilMoisture); //[mm]
      usableFieldCArray->GetTuple(cellId, &usableFieldCapacity); // [mm]?

      a1 = R.a.a1.value;
      a2 = R.a.a2.value;
      a3 = R.a.a3.value;

      // a of (1 - e^(-abckt)) (Temperature Response)
      a = a1 / (1.0 + exp(a2 / (meanTemp + a3)));

      a_resp->push_back(a);

      // b (moistureResponse)
      b1 = R.b.b1.value;
      b2 = R.b.b2.value;
      b3 = R.b.b3.value;

      if (soilMoisture > usableFieldCapacity * b3)
        b = 1;
      else
        b = b1 + (b2 - b1) * soilMoisture / (usableFieldCapacity * b3);

      b_resp->push_back(b);

      // efficiency , that describes how much of degraded C remains in the system
      // and is not blown out as CO2

      x1 = R.x.x1.value;
      x2 = R.x.x2.value;
      x3 = R.x.x3.value;
      x4 = R.x.x4.value;

      x = x1 * (x2 + x3 * exp(x4 * clay));
      x = 1 / (1 + x);

      x_resp->push_back(x);
      }

    this->a.push_back(a_resp);
    this->b.push_back(b_resp);
    this->x.push_back(x_resp);
    this->roots.push_back(roots_resp);
    this->surface.push_back(surf_resp);
    }

  // We need to aggregate the arrays in case of yearly resolution
  // The first vector contains the arithmetic mean
  if (this->TemporalResolution == ROTHC_YEARLY)
    {
    for (i = 1; i < numInputs; i++)
      {
      vtkDataSet* input = vtkDataSet::GetData(inputVector[0], i);
      for (cellId = 0; cellId < input->GetNumberOfCells(); cellId++)
        {
        (*this->a[0])[cellId] += (*this->a[i])[cellId];
        (*this->b[0])[cellId] += (*this->b[i])[cellId];
        (*this->x[0])[cellId] += (*this->x[i])[cellId];
        // Roots and surface residuals are simply aggregated over time
        (*this->roots[0])[cellId] += (*this->roots[i])[cellId];
        (*this->surface[0])[cellId] += (*this->surface[i])[cellId];
        }
      }
    for (cellId = 0; cellId < firstInput->GetNumberOfCells(); cellId++)
      {
      (*this->a[0])[cellId] /= numInputs;
      (*this->b[0])[cellId] /= numInputs;
      (*this->x[0])[cellId] /= numInputs;
      }
    }

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2ERothCModelEquilibrium::CreateCPools(vtkPolyData *input)
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
    if (initCArray)
      initCArray->GetTuple(i, &initC);
    else
      initC = 0.0;

    if (initC == this->NullValue)
      {
      iom = this->NullValue;
      dpm = this->NullValue;
      rpm = this->NullValue;
      bio = this->NullValue;
      hum = this->NullValue;
      } else
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
}

//----------------------------------------------------------------------------

void vtkTAG2ERothCModelEquilibrium::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}
