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
#include <vtk-5.9/vtkFieldData.h>
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
}

//----------------------------------------------------------------------------

vtkTAG2EAbstractModelCalibrator::~vtkTAG2EAbstractModelCalibrator()
{
  ;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::CompareTemporalDataSets(vtkTemporalDataSet *tds, 
                                        const char *ModelResultArrayName, 
                                        const char *MeasuredDataArrayname, 
                                        bool usePointData, bool verbose)
{
  double result;
  unsigned int timeStep, id;
  double variance;
  double squareSum;
  unsigned int numberOfValues = 0;
  vtkDataArray *model;
  vtkDataArray *measure;
  vtkDoubleArray *allMeasure = vtkDoubleArray::New();
  allMeasure->SetNumberOfComponents(1);
  
  squareSum = 0.0;
  
  for(timeStep = 0; timeStep < tds->GetNumberOfTimeSteps(); timeStep++)
  {
    vtkDataSet *ds = vtkDataSet::SafeDownCast(tds->GetTimeStep(timeStep));
    
    if(usePointData) {
      model = ds->GetPointData()->GetArray(ModelResultArrayName);
      measure = ds->GetPointData()->GetArray(MeasuredDataArrayname);
    } else  {
      model = ds->GetCellData()->GetArray(ModelResultArrayName);
      measure = ds->GetCellData()->GetArray(MeasuredDataArrayname);
    }
        
    for(id = 0; id < model->GetNumberOfTuples(); id++)
    {
      if(verbose)
        cout << model->GetName() << " " << model->GetTuple1(id) <<  "  " << measure->GetName() << " " << measure->GetTuple1(id) << endl;
      
      squareSum += (measure->GetTuple1(id) - model->GetTuple1(id)) * 
                   (measure->GetTuple1(id) - model->GetTuple1(id));
      allMeasure->InsertNextTuple1(measure->GetTuple1(id));
      numberOfValues++;
    }  
  }
  
  variance = vtkTAG2EAbstractModelCalibrator::StandardDeviation(measure);
  variance *= variance;
  
  result = squareSum/(numberOfValues * variance);
  
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
  
  for(i = 0; i < num; i++)
  {
    result += (mean - data->GetTuple1(i)) * (mean - data->GetTuple1(i));
  }
  
  result = result/(num - 1);
  
  return result;
}

//----------------------------------------------------------------------------

double vtkTAG2EAbstractModelCalibrator::ArithmeticMean(vtkDataArray *data)
{
  double result = 0.0;
  int i;
  int num = data->GetNumberOfTuples();
  
  for(i = 0; i < num; i++)
  {
    result += data->GetTuple1(i);
  }
  
  result = result/(double)num;
  
  return result;
}