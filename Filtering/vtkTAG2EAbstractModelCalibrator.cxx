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
#include <vtkDataArray.h>
#include <vtkPointData.h>
#include <vtkDoubleArray.h>
#include <vtkCellData.h>
#include <vtkTemporalDataSet.h>
#include <vtkFieldData.h>
#include "vtkTAG2EAbstractModelCalibrator.h"

vtkCxxRevisionMacro(vtkTAG2EAbstractModelCalibrator, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EAbstractModelCalibrator);

//----------------------------------------------------------------------------

vtkTAG2EAbstractModelCalibrator::vtkTAG2EAbstractModelCalibrator()
{
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
  this->Model = NULL;
  this->ModelParameter = NULL;
  this->TargetArrayName = NULL;
}

//----------------------------------------------------------------------------

vtkTAG2EAbstractModelCalibrator::~vtkTAG2EAbstractModelCalibrator()
{
  if (this->TargetArrayName)
    delete [] this->TargetArrayName;
  ;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::CompareTemporalDataSets(vtkTemporalDataSet *tds1,
  vtkTemporalDataSet *tds2,
  bool useCellData, bool verbose)
{
  double result;
  unsigned int timeStep, id;
  double variance;
  double squareSum;
  unsigned int numberOfValues = 0;
  vtkDataArray *array1;
  vtkDataArray *array2;
  vtkDoubleArray *allMeasure = vtkDoubleArray::New();
  allMeasure->SetNumberOfComponents(1);

  squareSum = 0.0;

  if (tds1->GetNumberOfTimeSteps() != tds2->GetNumberOfTimeSteps()) {
    std::cerr << "Number of timesteps or input temporal data sets are different" << std::endl;
    return -1;
  }

  for (timeStep = 0; timeStep < tds1->GetNumberOfTimeSteps(); timeStep++) {
    vtkDataSet *ds1 = vtkDataSet::SafeDownCast(tds1->GetTimeStep(timeStep));
    vtkDataSet *ds2 = vtkDataSet::SafeDownCast(tds2->GetTimeStep(timeStep));

    if (!useCellData) {
      array1 = ds1->GetPointData()->GetScalars();
      array2 = ds2->GetPointData()->GetScalars();
    } else {
      array1 = ds1->GetCellData()->GetScalars();
      array2 = ds2->GetCellData()->GetScalars();
    }

    for (id = 0; id < array1->GetNumberOfTuples(); id++) {
      if (verbose)
        cout << array1->GetName() << " " << array1->GetTuple1(id) << "  " << array2->GetName() << " " << array2->GetTuple1(id) << endl;

      squareSum += (array2->GetTuple1(id) - array1->GetTuple1(id)) *
        (array2->GetTuple1(id) - array1->GetTuple1(id));
      allMeasure->InsertNextTuple1(array2->GetTuple1(id));
      numberOfValues++;
    }
  }

  variance = vtkTAG2EAbstractModelCalibrator::Variance(array2);

  result = squareSum / (numberOfValues * variance);

  allMeasure->Delete();

  return result;
}


//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::CompareTemporalDataSets(vtkTemporalDataSet *tds,
  const char *ModelResultArrayName,
  const char *TargetArrayName,
  bool useCellData, bool verbose)
{
  double result;
  unsigned int timeStep, id;
  double variance;
  double squareSum;
  unsigned int numberOfValues = 0;
  vtkDataArray *array1;
  vtkDataArray *array2;
  vtkDoubleArray *allMeasure = vtkDoubleArray::New();
  allMeasure->SetNumberOfComponents(1);

  squareSum = 0.0;

  for (timeStep = 0; timeStep < tds->GetNumberOfTimeSteps(); timeStep++) {
    vtkDataSet *ds = vtkDataSet::SafeDownCast(tds->GetTimeStep(timeStep));

    if (!useCellData) {

      if (ds->GetPointData()->HasArray(ModelResultArrayName) &&
        ds->GetPointData()->HasArray(TargetArrayName)) {
        array1 = ds->GetPointData()->GetArray(ModelResultArrayName);
        array2 = ds->GetPointData()->GetArray(TargetArrayName);
      } else {
        std::cerr << "Point data arrays not found in datasets at time step " << timeStep << std::endl;
        return -1;
      }
    } else {
      if (ds->GetCellData()->HasArray(ModelResultArrayName) &&
        ds->GetCellData()->HasArray(TargetArrayName)) {
        array1 = ds->GetCellData()->GetArray(ModelResultArrayName);
        array2 = ds->GetCellData()->GetArray(TargetArrayName);
      } else {
        std::cerr << "Cell data arrays not found in datasets at times tep " << timeStep << std::endl;
        return -1;
      }
    }

    for (id = 0; id < array1->GetNumberOfTuples(); id++) {
      if (verbose)
        cout << array1->GetName() << " " << array1->GetTuple1(id) << "  " << array2->GetName() << " " << array2->GetTuple1(id) << endl;

      squareSum += (array2->GetTuple1(id) - array1->GetTuple1(id)) *
        (array2->GetTuple1(id) - array1->GetTuple1(id));
      allMeasure->InsertNextTuple1(array2->GetTuple1(id));
      numberOfValues++;
    }
  }

  variance = vtkTAG2EAbstractModelCalibrator::Variance(array2);

  result = squareSum / (numberOfValues * variance);

  allMeasure->Delete();

  return result;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::StandardDeviation(vtkDataArray *data)
{
  double val = sqrt(Variance(data));
  return val;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::Variance(vtkDataArray *data)
{
  double result = 0.0;
  int i;
  int num = data->GetNumberOfTuples();
  double mean;

  mean = vtkTAG2EAbstractModelCalibrator::ArithmeticMean(data);

  for (i = 0; i < num; i++) {
    result += (mean - data->GetTuple1(i)) * (mean - data->GetTuple1(i));
  }

  result = result / (num - 1);

  return result;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::ArithmeticMean(vtkDataArray *data)
{
  double result = 0.0;
  int i;
  int num = data->GetNumberOfTuples();

  for (i = 0; i < num; i++) {
    result += data->GetTuple1(i);
  }

  result = result / (double) num;

  return result;
}