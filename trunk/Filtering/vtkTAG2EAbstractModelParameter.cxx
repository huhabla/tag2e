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
#include "vtkTAG2EAbstractModelParameter.h"
#include <vtkXMLDataParser.h>

vtkCxxRevisionMacro(vtkTAG2EAbstractModelParameter, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EAbstractModelParameter);

//----------------------------------------------------------------------------

vtkTAG2EAbstractModelParameter::vtkTAG2EAbstractModelParameter()
{
  this->XMLRoot = vtkXMLDataElement::New();
}

//----------------------------------------------------------------------------

vtkTAG2EAbstractModelParameter::~vtkTAG2EAbstractModelParameter()
{
  this->XMLRoot->Delete();
}

//----------------------------------------------------------------------------

bool vtkTAG2EAbstractModelParameter::Read()
{
  vtkXMLDataParser *reader = vtkXMLDataParser::New();
  reader->SetFileName(this->FileName);
  if(0 == reader->Parse()) {
    vtkErrorMacro(<<"Unable to parse XML file " << this->FileName);
    return false;
  }
  
  this->XMLRoot->DeepCopy(reader->GetRootElement());

  reader->Delete();
  
  this->Modified();
  
  return true;
}


void vtkTAG2EAbstractModelParameter::Write()
{
  this->XMLRoot->PrintXML(this->FileName);
}