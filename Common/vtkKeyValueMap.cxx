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

#include "vtkKeyValueMap.h"
#include "vtkObjectFactory.h"

vtkCxxRevisionMacro(vtkKeyValueMap, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkKeyValueMap);

//----------------------------------------------------------------------------

double vtkKeyValueMap::GetValue(unsigned int idx) {
  unsigned int count;
  std::map<const char*, double>::iterator it;
  
  if(idx >= this->KeyVals.size()) {
    vtkErrorMacro(<< "Index is out of range");
    return 0.0;
  }
  count = 0;
  for(it = this->KeyVals.begin(); it != this->KeyVals.end(); it++)
  {
    if(idx == count)
      return (*it).second;
    count++;
  }
  return 0.0;
}
    
//----------------------------------------------------------------------------

const char* vtkKeyValueMap::GetKey(unsigned int idx) {
  unsigned int count;
  std::map<const char*, double>::iterator it;
  
  if(idx >= this->KeyVals.size()) {
    vtkErrorMacro(<< "Index is out of range");
    return NULL;
  }
  count = 0;
  for(it = this->KeyVals.begin(); it != this->KeyVals.end(); it++)
  {
    if(idx == count)
      return (*it).first;
    count++;
  }
  return NULL;
}
   //----------------------------------------------------------------------------
void vtkKeyValueMap::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);
  std::map<const char*, double>::iterator it;
  
  for(it = this->KeyVals.begin(); it != this->KeyVals.end(); it++)
  {

      os << indent << "key: " << (*it).first << "  value: " << (*it).second << endl;

  }
}
