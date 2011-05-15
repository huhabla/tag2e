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
#include "vtkTAG2EAbstractCalibratableModelParameter.h"
#include <stdlib.h>

vtkCxxRevisionMacro(vtkTAG2EAbstractCalibratableModelParameter, "$Revision: 1.0 $");

#define MAX_CHANGE_PARAMETER_RUNS 10000

//----------------------------------------------------------------------------

static int irand(int a, int e)
{
  double r = e - a + 1;
  return a + (int) (r * rand() / (RAND_MAX + 1.0));
}

//----------------------------------------------------------------------------

static double norm_dist(double mean, double sd)
{
  double u1, u2, x1, x2;
  u1 = (double) rand() / (double) (RAND_MAX);
  u2 = (double) rand() / (double) (RAND_MAX);
  x1 = sqrt(-2 * log(1.0 - u1)) * cos(2.0 * M_PI * u2);
  x2 = sqrt(-2 * log(1.0 - u1)) * sin(2.0 * M_PI * u2);
  return x1 * sd - mean;
}


vtkTAG2EAbstractCalibratableModelParameter::vtkTAG2EAbstractCalibratableModelParameter()
{
  this->NumberOfCalibratableParameter = 0;
  this->ParameterId = -1;
  this->ParameterValue = 0.0;

  // Initiate the random number generator with the current time
  srand(time(0));
}

vtkTAG2EAbstractCalibratableModelParameter::~vtkTAG2EAbstractCalibratableModelParameter()
{
  ;
}

//----------------------------------------------------------------------------

bool vtkTAG2EAbstractCalibratableModelParameter::ModifyParameterRandomly(double sd)
{
  bool check = false;
  int count = 0;

  // Change a randomly selected parameter till a valid configuration is found
  while (!check) {

    // Avoid endless loops
    count++;
    if (count > MAX_CHANGE_PARAMETER_RUNS) {
      vtkErrorMacro( << "Maximum number of parameter runs reached");
      return false;
    }

    // Select randomly a uniform distributed index
    int index = irand(0, this->ParameterIndex.size() - 1);

    // Change the Parameter
    check = this->ModifyParameter(index, sd);
  }

  return check;
}

//----------------------------------------------------------------------------

bool vtkTAG2EAbstractCalibratableModelParameter::ModifyParameter(int index, double sd)
{
  // Get min and max values for parameter range check
  double min = this->ParameterMinMax[index][0];
  double max = this->ParameterMinMax[index][1];
  // We need the current value of the selected parameter 
  // which is the base of the change
  double value = this->ParameterValues[index];
  // The range of the selected parameter
  double range = max - min;
  // A normal-distributed random number [0.0;1.0]
  double rvalue = norm_dist(0.0, sd);
  // The new parameter value 
  value = value + rvalue*range;

  // The generated value must be in range
  if (value < min || value > max) {
    vtkDebugMacro(<< "Parameter " << index << " Value " << value << " is out of range [" << min << ":" << max << "]");
    return false;
  }

  // Set the Parameter. This method must be overwritten in the subclasses
  bool check = this->SetParameter(index, value);
  
  // Revert the change in case the modified parametrer result in wrong fuzzy sets
  if (check == false)
    this->RestoreLastModifiedParameter();
  
  return check;
}

//----------------------------------------------------------------------------

bool vtkTAG2EAbstractCalibratableModelParameter::RestoreLastModifiedParameter()
{
  vtkDebugMacro(<< "Restore last parameter " << this->ParameterId << " to " << this->ParameterValue);
  double value = this->ParameterValue;
  bool check = this->SetParameter(this->ParameterId, this->ParameterValue);
  // Make sure the correct last parameter value is set
  this->ParameterValue = value;
    
  return check;
}

//----------------------------------------------------------------------------

void vtkTAG2EAbstractCalibratableModelParameter::UpdateParameterState(unsigned int index, double old_value, double new_value)
{

  vtkDebugMacro(<< "Index " << index << " old value " << old_value << " new value " << new_value);

  // Safe the last parameter for restauration
  this->ParameterValue = old_value;
  // Safe the last index for restauration
  this->ParameterId = index;
  // Modify the value array too 
  this->ParameterValues[index] = new_value;
}

//----------------------------------------------------------------------------

void vtkTAG2EAbstractCalibratableModelParameter::AppendParameterState(unsigned int index, double value, double min, double max)
{

  vtkDebugMacro( << "Index " << index << " Value " << value);

  // Save the parameter index
  this->ParameterIndex.push_back(index);
  // Save the current value of the parameter for random number generation
  this->ParameterValues.push_back(value);
  // We store the min and max values for each parameter, redundancy is intention 
  std::vector<double> mm;
  mm.push_back(min);
  mm.push_back(max);
  this->ParameterMinMax.push_back(mm);
}

//----------------------------------------------------------------------------

bool vtkTAG2EAbstractCalibratableModelParameter::GetXMLRepresentation(vtkXMLDataElement *root)
{
  this->GenerateXMLFromInternalScheme();
  
  if(!this->XMLRoot)
    return false;
  
  if(!root)
    return false;
  
  root->DeepCopy(this->XMLRoot);
    
  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EAbstractCalibratableModelParameter::SetXMLRepresentation(vtkXMLDataElement *root)
{
  if(!this->XMLRoot)
    return false;
  
  if(!root)
    return false;
 
  this->XMLRoot->DeepCopy(root);
  
  this->GenerateInternalSchemeFromXML();
  
  this->Modified();
  
  return true;
}