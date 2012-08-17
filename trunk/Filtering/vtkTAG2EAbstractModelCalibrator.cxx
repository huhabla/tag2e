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
#include <vtkDataSet.h>
#include <vtkFieldData.h>
#include "vtkTAG2EAbstractModelCalibrator.h"

extern "C" {
#include <math.h>
}

vtkCxxRevisionMacro(vtkTAG2EAbstractModelCalibrator, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EAbstractModelCalibrator);

//----------------------------------------------------------------------------

vtkTAG2EAbstractModelCalibrator::vtkTAG2EAbstractModelCalibrator()
{
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
  this->Model = NULL;
  this->ModelParameter = NULL;
}

//----------------------------------------------------------------------------

vtkTAG2EAbstractModelCalibrator::~vtkTAG2EAbstractModelCalibrator()
{
  ;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::CompareDataSets(vtkDataSet *ds1,
  vtkDataSet *ds2,
  bool useCellData, bool verbose)
{
  double result;
  int method = TDS_COMPARE_METHOD_NO_SCALED;
  int id;
  double variance;
  double squareSum;
  double val1, val2;
  double shift = 10000;
  unsigned int numberOfValues = 0;
  vtkDataArray *array1;
  vtkDataArray *array2;
  vtkDoubleArray *allMeasure = vtkDoubleArray::New();
  allMeasure->SetNumberOfComponents(1);

  squareSum = 0.0;

    if (!useCellData) {
      array1 = ds1->GetPointData()->GetScalars();
      array2 = ds2->GetPointData()->GetScalars();
    } else {
      array1 = ds1->GetCellData()->GetScalars();
      array2 = ds2->GetCellData()->GetScalars();
    }

    for (id = 0; id < array1->GetNumberOfTuples(); id++) {
      if (verbose)
        cout << array1->GetName() << " " << array1->GetTuple1(id) << "  "
             << array2->GetName() << " " << array2->GetTuple1(id) << endl;

      val1 = array1->GetTuple1(id);
      val2 = array2->GetTuple1(id);
          
      if(method == TDS_COMPARE_METHOD_LOG_SCALED) {
          val1 = log(shift + val1);
          val2 = log(shift + val2);
      }else if(method == TDS_COMPARE_METHOD_SQRT_SCALED) {
          val1 = sqrt(shift + val1);
          val2 = sqrt(shift + val2);
      } 
      
      squareSum += (val2 - val1) * (val2 - val1);
      allMeasure->InsertNextTuple1(val2);
      numberOfValues++;
    }

  variance = vtkTAG2EAbstractModelCalibrator::Variance(allMeasure);

  if(variance != 0)
    result = squareSum / (numberOfValues * variance);
  else
    result = squareSum / (numberOfValues);

  allMeasure->Delete();

  return result;
}


//----------------------------------------------------------------------------

bool vtkTAG2EAbstractModelCalibrator::ComputeDataSetsResiduals(vtkDataSet *ds1,
  vtkDataSet *ds2,
  bool useCellData, vtkDataArray *residuals)
{
  int id;
  double val1, val2;

  vtkDataArray *array1;
  vtkDataArray *array2;
  
  if(residuals == NULL)
      return false;
  
  residuals->Initialize();
  residuals->SetName("Residuals");
  residuals->SetNumberOfComponents(1);

    if (!useCellData) {
      array1 = ds1->GetPointData()->GetScalars();
      array2 = ds2->GetPointData()->GetScalars();
    } else {
      array1 = ds1->GetCellData()->GetScalars();
      array2 = ds2->GetCellData()->GetScalars();
    }

    for (id = 0; id < array1->GetNumberOfTuples(); id++) {

      val1 = array1->GetTuple1(id);
      val2 = array2->GetTuple1(id);

      residuals->InsertNextTuple1(val2 - val1);
    }

  return true;
}


//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::CompareDataSets(vtkDataSet *ds,
  const char *ModelResultArrayName,
  const char *TargetArrayName,
  bool useCellData, bool verbose)
{
  double result;
  int id;
  int method = TDS_COMPARE_METHOD_NO_SCALED;
  double variance;
  double squareSum;
  double val1, val2;
  double shift = 10000;
  unsigned int numberOfValues = 0;
  vtkDataArray *array1;
  vtkDataArray *array2;
  vtkDoubleArray *allMeasure = vtkDoubleArray::New();
  allMeasure->SetNumberOfComponents(1);

  squareSum = 0.0;

    if (!useCellData) {

      if (ds->GetPointData()->HasArray(ModelResultArrayName) &&
        ds->GetPointData()->HasArray(TargetArrayName)) {
        array1 = ds->GetPointData()->GetArray(ModelResultArrayName);
        array2 = ds->GetPointData()->GetArray(TargetArrayName);
      } else {
        std::cerr << "Point data arrays not found in datasets " << std::endl;
        return -1;
      }
    } else {
      if (ds->GetCellData()->HasArray(ModelResultArrayName) &&
        ds->GetCellData()->HasArray(TargetArrayName)) {
        array1 = ds->GetCellData()->GetArray(ModelResultArrayName);
        array2 = ds->GetCellData()->GetArray(TargetArrayName);
      } else {
        std::cerr << "Cell data arrays not found in datasets" << std::endl;
        return -1;
      }
    }

    for (id = 0; id < array1->GetNumberOfTuples(); id++) {
      if (verbose)
        cout << array1->GetName() << " "
             << array1->GetTuple1(id)
             << "  " << array2->GetName() << " "
             << array2->GetTuple1(id) << endl;

      val1 = array1->GetTuple1(id);
      val2 = array2->GetTuple1(id);
          
      if(method = TDS_COMPARE_METHOD_LOG_SCALED) {
          val1 = log(shift + val1);
          val2 = log(shift + val2);
      }else if(method = TDS_COMPARE_METHOD_SQRT_SCALED) {
          val1 = sqrt(shift + val1);
          val2 = sqrt(shift + val2);
      } 
      
      squareSum += (val2 - val1) * (val2 - val1);
      allMeasure->InsertNextTuple1(val2);
      numberOfValues++;
    }

  variance = vtkTAG2EAbstractModelCalibrator::Variance(allMeasure);

  if(variance != 0)
    result = squareSum / (numberOfValues * variance);
  else
    result = squareSum / (numberOfValues);

  cout << "Dataset difference measure: " << result << endl;
  
  allMeasure->Delete();

  return result;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::StandardDeviation(vtkDataSet *ds,
  const char *ArrayName, bool useCellData)
{
    double sd;
    vtkDataArray *array;

    if (!useCellData) {
      array = ds->GetPointData()->GetArray(ArrayName);
    } else {
      array = ds->GetCellData()->GetArray(ArrayName);
    }
    
    sd = vtkTAG2EAbstractModelCalibrator::StandardDeviation(array);
    array->Delete();
    return sd;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::StandardDeviation(vtkDataArray *data)
{
  double val = sqrt(Variance(data));
  return val;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::Variance(vtkDataSet *ds,
  const char *ArrayName, bool useCellData)
{
    double v;
    vtkDataArray *array;

    if (!useCellData) {
      array = ds->GetPointData()->GetArray(ArrayName);
    } else {
      array = ds->GetCellData()->GetArray(ArrayName);
    }
    
    v = vtkTAG2EAbstractModelCalibrator::Variance(array);
    array->Delete();
    return v;
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
