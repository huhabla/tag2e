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
#include "vtkTAG2ERothCModelParameter.h"
#include <vtkXMLDataParser.h>
#include <vtkXMLDataElement.h>
#include <sstream>

extern "C" {
#include <string.h>
}

vtkCxxRevisionMacro(vtkTAG2ERothCModelParameter, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ERothCModelParameter);

//----------------------------------------------------------------------------

vtkTAG2ERothCModelParameter::vtkTAG2ERothCModelParameter()
{
  // We initialize the RothC parameter with
  // default values from the RothC paper

  this->R.a.a1.value = this->R.a.a1.max = this->R.a.a1.min = 47.9;
  this->R.a.a1.constant = true;
  this->R.a.a2.value = this->R.a.a2.max = this->R.a.a2.min = 106.0;
  this->R.a.a2.constant = true;
  this->R.a.a3.value = this->R.a.a3.max = this->R.a.a3.min = 18.3;
  this->R.a.a3.constant = true;


  this->R.b.b1.value = this->R.b.b1.max = this->R.b.b1.min = 0.2;
  this->R.b.b1.constant = true;
  this->R.b.b2.value = this->R.b.b2.max = this->R.b.b2.min = 1;
  this->R.b.b2.constant = true;
  this->R.b.b3.value = this->R.b.b3.max = this->R.b.b3.min = 0.444;
  this->R.b.b3.constant = true;

  this->R.c.c1.value = this->R.c.c1.max = this->R.c.c1.min = 0.6;
  this->R.c.c1.constant = true;
  this->R.c.c2.value = this->R.c.c2.max = this->R.c.c2.min = 1.0;
  this->R.c.c2.constant = true;

  this->R.k.DPM.value = this->R.k.DPM.max = this->R.k.DPM.min = 10.2;
  this->R.k.DPM.constant = true;
  this->R.k.RPM.value = this->R.k.RPM.max = this->R.k.RPM.min = 0.3;
  this->R.k.RPM.constant = true;
  this->R.k.BIO.value = this->R.k.BIO.max = this->R.k.BIO.min = 0.66;
  this->R.k.BIO.constant = true;
  this->R.k.HUM.value = this->R.k.HUM.max = this->R.k.HUM.min = 0.02;
  this->R.k.HUM.constant = true;

  this->R.x.x1.value = this->R.x.x1.max = this->R.x.x1.min = 1.67;
  this->R.x.x1.constant = true;
  this->R.x.x2.value = this->R.x.x2.max = this->R.x.x2.min = 1.85;
  this->R.x.x2.constant = true;
  this->R.x.x3.value = this->R.x.x3.max = this->R.x.x3.min = 1.60;
  this->R.x.x3.constant = true;
  this->R.x.x4.value = this->R.x.x4.max = this->R.x.x4.min = -0.0786;
  this->R.x.x4.constant = true;

  // Plants
  RothCParameterFraction *pfrac = new RothCParameterFraction;
  pfrac->name = "default";
  pfrac->description =
      "The default ratio parameter for agricultural crops and grassland";
  pfrac->DPM.value = pfrac->DPM.max = pfrac->DPM.min = 0.59;
  pfrac->DPM.constant = true;
  pfrac->RPM.value = pfrac->RPM.max = pfrac->RPM.min = 0.41;
  pfrac->RPM.constant = true;
  pfrac->HUM.value = pfrac->HUM.max = pfrac->HUM.min = 0.0;
  pfrac->HUM.constant = true;
  this->R.PlantFractions.push_back(pfrac);

  // Fertilizer
  RothCParameterFraction *ffrac = new RothCParameterFraction;
  ffrac->name = "default";
  ffrac->description = "The default ratio parameter for farmyard manure";
  ffrac->DPM.value = ffrac->DPM.max = ffrac->DPM.min = 0.49;
  ffrac->DPM.constant = true;
  ffrac->RPM.value = ffrac->RPM.max = ffrac->RPM.min = 0.49;
  ffrac->RPM.constant = true;
  ffrac->HUM.value = ffrac->HUM.max = ffrac->HUM.min = 0.02;
  ffrac->HUM.constant = true;
  this->R.FertilizerFractions.push_back(ffrac);
}

//----------------------------------------------------------------------------

vtkTAG2ERothCModelParameter::~vtkTAG2ERothCModelParameter()
{
  ;
}

//----------------------------------------------------------------------------

bool vtkTAG2ERothCModelParameter::GenerateXMLFromInternalScheme()
{
  unsigned int i;

  vtkXMLDataElement *rc = vtkXMLDataElement::New();
  rc->SetName("RothC");
  rc->SetAttribute("xmlns", "http://tag2e.googlecode.com/files/RothC");
  rc->SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance");
  rc->SetAttribute("xsi:schemaLocation",
      "http://tag2e.googlecode.com/files/RothC http://tag2e.googlecode.com/files/RothC.xsd");

  vtkXMLDataElement *a = vtkXMLDataElement::New();
  a->SetName("a");
  vtkXMLDataElement *a1 = this->RothCParameterToXML(this->R.a.a1, "a1");
  a->AddNestedElement(a1);
  a1->Delete();
  vtkXMLDataElement *a2 = this->RothCParameterToXML(this->R.a.a2, "a2");
  a->AddNestedElement(a2);
  a2->Delete();
  vtkXMLDataElement *a3 = this->RothCParameterToXML(this->R.a.a3, "a3");
  a->AddNestedElement(a3);
  a3->Delete();
  rc->AddNestedElement(a);
  a->Delete();

  vtkXMLDataElement *b = vtkXMLDataElement::New();
  b->SetName("b");
  vtkXMLDataElement *b1 = this->RothCParameterToXML(this->R.b.b1, "b1");
  b->AddNestedElement(b1);
  b1->Delete();
  vtkXMLDataElement *b2 = this->RothCParameterToXML(this->R.b.b2, "b2");
  b->AddNestedElement(b2);
  b2->Delete();
  vtkXMLDataElement *b3 = this->RothCParameterToXML(this->R.b.b3, "b3");
  b->AddNestedElement(b3);
  b3->Delete();
  rc->AddNestedElement(b);
  b->Delete();

  vtkXMLDataElement *c = vtkXMLDataElement::New();
  c->SetName("c");
  vtkXMLDataElement *c1 = this->RothCParameterToXML(this->R.c.c1, "c1");
  c->AddNestedElement(c1);
  c1->Delete();
  vtkXMLDataElement *c2 = this->RothCParameterToXML(this->R.c.c2, "c2");
  c->AddNestedElement(c2);
  c2->Delete();
  rc->AddNestedElement(c);
  c->Delete();

  vtkXMLDataElement *k = vtkXMLDataElement::New();
  k->SetName("k");
  vtkXMLDataElement *DPM = this->RothCParameterToXML(this->R.k.DPM, "DPM");
  k->AddNestedElement(DPM);
  DPM->Delete();
  vtkXMLDataElement *RPM = this->RothCParameterToXML(this->R.k.RPM, "RPM");
  k->AddNestedElement(RPM);
  RPM->Delete();
  vtkXMLDataElement *BIO = this->RothCParameterToXML(this->R.k.BIO, "BIO");
  k->AddNestedElement(BIO);
  BIO->Delete();
  vtkXMLDataElement *HUM = this->RothCParameterToXML(this->R.k.HUM, "HUM");
  k->AddNestedElement(HUM);
  HUM->Delete();
  rc->AddNestedElement(k);
  k->Delete();

  vtkXMLDataElement *x = vtkXMLDataElement::New();
  x->SetName("x");
  vtkXMLDataElement *x1 = this->RothCParameterToXML(this->R.x.x1, "x1");
  x->AddNestedElement(x1);
  x1->Delete();
  vtkXMLDataElement *x2 = this->RothCParameterToXML(this->R.x.x2, "x2");
  x->AddNestedElement(x2);
  x2->Delete();
  vtkXMLDataElement *x3 = this->RothCParameterToXML(this->R.x.x3, "x3");
  x->AddNestedElement(x3);
  x3->Delete();
  vtkXMLDataElement *x4 = this->RothCParameterToXML(this->R.x.x4, "x4");
  x->AddNestedElement(x4);
  x4->Delete();
  rc->AddNestedElement(x);
  x->Delete();

  vtkXMLDataElement *plants = vtkXMLDataElement::New();
  plants->SetName("PlantFractions");
  for (i = 0; i < this->R.PlantFractions.size(); i++)
    {
    vtkXMLDataElement *plant = this->RothCParameterFractionToXML(
        this->R.PlantFractions[i], "PlantFraction", i);
    plants->AddNestedElement(plant);
    plant->Delete();
    }
  rc->AddNestedElement(plants);
  plants->Delete();

  vtkXMLDataElement *ferts = vtkXMLDataElement::New();
  ferts->SetName("FertilizerFractions");
  for (i = 0; i < this->R.FertilizerFractions.size(); i++)
    {
    vtkXMLDataElement *fert = this->RothCParameterFractionToXML(
        this->R.FertilizerFractions[i], "FertilizerFraction", i);
    ferts->AddNestedElement(fert);
    fert->Delete();
    }
  rc->AddNestedElement(ferts);
  ferts->Delete();

  this->XMLRoot->DeepCopy(rc);
  rc->Delete();

  return true;
}

//----------------------------------------------------------------------------

vtkXMLDataElement *vtkTAG2ERothCModelParameter::RothCParameterFractionToXML(
    RothCParameterFraction *p, const char *name, int id)
{
  vtkXMLDataElement *frac = vtkXMLDataElement::New();
  frac->SetName(name);
  frac->SetIntAttribute("id", (int) id);
  frac->SetAttribute("name", p->name.c_str());

  // Add the description
  vtkXMLDataElement *descr = vtkXMLDataElement::New();
  descr->SetName("description");
  descr->SetCharacterData(p->description.c_str(), p->description.size());
  frac->AddNestedElement(descr);
  descr->Delete();

  vtkXMLDataElement *DPM = RothCParameterToXML(p->DPM, "DPM");
  frac->AddNestedElement(DPM);
  DPM->Delete();

  vtkXMLDataElement *RPM = RothCParameterToXML(p->RPM, "RPM");
  frac->AddNestedElement(RPM);
  RPM->Delete();

  vtkXMLDataElement *HUM = RothCParameterToXML(p->HUM, "HUM");
  frac->AddNestedElement(HUM);
  HUM->Delete();

  return frac;
}

//----------------------------------------------------------------------------

vtkXMLDataElement *vtkTAG2ERothCModelParameter::RothCParameterToXML(
    RothCParameter &p, const char *name)
{
  vtkXMLDataElement *XMLRothCParameter = vtkXMLDataElement::New();
  XMLRothCParameter->SetName(name);
  XMLRothCParameter->SetIntAttribute("const", (int) p.constant);
  XMLRothCParameter->SetDoubleAttribute("max", p.max);
  XMLRothCParameter->SetDoubleAttribute("min", p.min);
  std::ostringstream value;
  value << setprecision(15) << p.value;
  XMLRothCParameter->SetCharacterData(value.str().c_str(), value.str().size());

  return XMLRothCParameter;
}

//----------------------------------------------------------------------------

bool vtkTAG2ERothCModelParameter::SetParameter(unsigned int index, double value)
{
  unsigned int count = 0;
  unsigned int i;

  // Parameter a
  if (this->R.a.a1.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.a.a1.value, value);
      this->R.a.a1.value = value;
      return true;
      }
    count++;
    }
  if (this->R.a.a2.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.a.a2.value, value);
      this->R.a.a2.value = value;
      return true;
      }
    count++;
    }
  if (this->R.a.a3.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.a.a3.value, value);
      this->R.a.a3.value = value;
      return true;
      }
    count++;
    }

  // Parameter b
  if (this->R.b.b1.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.b.b1.value, value);
      this->R.b.b1.value = value;
      return true;
      }
    count++;
    }
  if (this->R.b.b2.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.b.b2.value, value);
      this->R.b.b2.value = value;
      return true;
      }
    count++;
    }
  if (this->R.b.b3.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.b.b3.value, value);
      this->R.b.b3.value = value;
      return true;
      }
    count++;
    }

  // Parameter c
  if (this->R.c.c1.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.c.c1.value, value);
      this->R.c.c1.value = value;
      return true;
      }
    count++;
    }
  if (this->R.c.c2.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.c.c2.value, value);
      this->R.c.c2.value = value;
      return true;
      }
    count++;
    }

  // Parameter k
  if (this->R.k.DPM.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.k.DPM.value, value);
      this->R.k.DPM.value = value;
      return true;
      }
    count++;
    }
  if (this->R.k.RPM.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.k.RPM.value, value);
      this->R.k.RPM.value = value;
      return true;
      }
    count++;
    }
  if (this->R.k.BIO.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.k.BIO.value, value);
      this->R.k.BIO.value = value;
      return true;
      }
    count++;
    }
  if (this->R.k.HUM.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.k.HUM.value, value);
      this->R.k.HUM.value = value;
      return true;
      }
    count++;
    }

  // Parameter x
  if (this->R.x.x1.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.x.x1.value, value);
      this->R.x.x1.value = value;
      return true;
      }
    count++;
    }
  if (this->R.x.x2.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.x.x2.value, value);
      this->R.x.x2.value = value;
      return true;
      }
    count++;
    }
  if (this->R.x.x3.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.x.x3.value, value);
      this->R.x.x3.value = value;
      return true;
      }
    count++;
    }
  if (this->R.x.x4.constant == false)
    {
    if (count == index)
      {
      this->UpdateParameterState(index, this->R.x.x4.value, value);
      this->R.x.x4.value = value;
      return true;
      }
    count++;
    }

  // Plant fractions
  for (i = 0; i < this->R.PlantFractions.size(); i++)
    {
    RothCParameter &DPM = this->R.PlantFractions[i]->DPM;
    if (DPM.constant == false)
      {
      if (count == index)
        {
        this->UpdateParameterState(index, DPM.value, value);
        DPM.value = value;
        return true;
        }
      count++;
      }
    RothCParameter &RPM = this->R.PlantFractions[i]->RPM;
    if (RPM.constant == false)
      {
      if (count == index)
        {
        this->UpdateParameterState(index, RPM.value, value);
        RPM.value = value;
        return true;
        }
      count++;
      }
    RothCParameter &HUM = this->R.PlantFractions[i]->HUM;
    if (HUM.constant == false)
      {
      if (count == index)
        {
        this->UpdateParameterState(index, HUM.value, value);
        HUM.value = value;
        return true;
        }
      count++;
      }
    }

  // Fertilizer fractions
  for (i = 0; i < this->R.FertilizerFractions.size(); i++)
    {
    RothCParameter &DPM = this->R.FertilizerFractions[i]->DPM;
    if (DPM.constant == false)
      {
      if (count == index)
        {
        this->UpdateParameterState(index, DPM.value, value);
        DPM.value = value;
        return true;
        }
      count++;
      }
    RothCParameter &RPM = this->R.FertilizerFractions[i]->RPM;
    if (RPM.constant == false)
      {
      if (count == index)
        {
        this->UpdateParameterState(index, RPM.value, value);
        RPM.value = value;
        return true;
        }
      count++;
      }
    RothCParameter &HUM = this->R.FertilizerFractions[i]->HUM;
    if (HUM.constant == false)
      {
      if (count == index)
        {
        this->UpdateParameterState(index, HUM.value, value);
        HUM.value = value;
        return true;
        }
      count++;
      }
    }

  return false;
}

//----------------------------------------------------------------------------

bool vtkTAG2ERothCModelParameter::CreateParameterIndex()
{
  unsigned int i;
  unsigned int count = 0;

  // ATTENTION:
  // The count mechanism of CreateParameterIndex and SetParamter must be identical

  this->ParameterIndex.clear();

  // Parameter a
  if (this->R.a.a1.constant == false)
    {
    this->AppendParameterState(count, R.a.a1.value, R.a.a1.min, R.a.a1.max);
    count++;
    }
  if (this->R.a.a2.constant == false)
    {
    this->AppendParameterState(count, R.a.a2.value, R.a.a2.min, R.a.a2.max);
    count++;
    }
  if (this->R.a.a3.constant == false)
    {
    this->AppendParameterState(count, R.a.a3.value, R.a.a3.min, R.a.a3.max);
    count++;
    }

  // Parameter b
  if (this->R.b.b1.constant == false)
    {
    this->AppendParameterState(count, R.b.b1.value, R.b.b1.min, R.b.b1.max);
    count++;
    }
  if (this->R.b.b2.constant == false)
    {
    this->AppendParameterState(count, R.b.b2.value, R.b.b2.min, R.b.b2.max);
    count++;
    }
  if (this->R.b.b3.constant == false)
    {
    this->AppendParameterState(count, R.b.b3.value, R.b.b3.min, R.b.b3.max);
    count++;
    }

  // Parameter c
  if (this->R.c.c1.constant == false)
    {
    this->AppendParameterState(count, R.c.c1.value, R.c.c1.min, R.c.c1.max);
    count++;
    }
  if (this->R.c.c2.constant == false)
    {
    this->AppendParameterState(count, R.c.c2.value, R.c.c2.min, R.c.c2.max);
    count++;
    }

  // Parameter k
  if (this->R.k.DPM.constant == false)
    {
    this->AppendParameterState(count, R.k.DPM.value, R.k.DPM.min, R.k.DPM.max);
    count++;
    }
  if (this->R.k.RPM.constant == false)
    {
    this->AppendParameterState(count, R.k.RPM.value, R.k.RPM.min, R.k.RPM.max);
    count++;
    }
  if (this->R.k.BIO.constant == false)
    {
    this->AppendParameterState(count, R.k.BIO.value, R.k.BIO.min, R.k.BIO.max);
    count++;
    }
  if (this->R.k.HUM.constant == false)
    {
    this->AppendParameterState(count, R.k.HUM.value, R.k.HUM.min, R.k.HUM.max);
    count++;
    }

  // Parameter x
  if (this->R.x.x1.constant == false)
    {
    this->AppendParameterState(count, R.x.x1.value, R.x.x1.min, R.x.x1.max);
    count++;
    }
  if (this->R.x.x2.constant == false)
    {
    this->AppendParameterState(count, R.x.x2.value, R.x.x2.min, R.x.x2.max);
    count++;
    }
  if (this->R.x.x3.constant == false)
    {
    this->AppendParameterState(count, R.x.x3.value, R.x.x3.min, R.x.x3.max);
    count++;
    }
  if (this->R.x.x4.constant == false)
    {
    this->AppendParameterState(count, R.x.x4.value, R.x.x4.min, R.x.x4.max);
    count++;
    }

  // Plant fractions
  for (i = 0; i < this->R.PlantFractions.size(); i++)
    {
    RothCParameter &DPM = this->R.PlantFractions[i]->DPM;
    if (DPM.constant == false)
      {
      this->AppendParameterState(count, DPM.value, DPM.min, DPM.max);
      count++;
      }
    RothCParameter &RPM = this->R.PlantFractions[i]->RPM;
    if (RPM.constant == false)
      {
      this->AppendParameterState(count, RPM.value, RPM.min, RPM.max);
      count++;
      }
    RothCParameter &HUM = this->R.PlantFractions[i]->HUM;
    if (HUM.constant == false)
      {
      this->AppendParameterState(count, HUM.value, HUM.min, HUM.max);
      count++;
      }
    }

  // Fertilizer fractions
  for (i = 0; i < this->R.FertilizerFractions.size(); i++)
    {
    RothCParameter &DPM = this->R.FertilizerFractions[i]->DPM;
    if (DPM.constant == false)
      {
      this->AppendParameterState(count, DPM.value, DPM.min, DPM.max);
      count++;
      }
    RothCParameter &RPM = this->R.FertilizerFractions[i]->RPM;
    if (RPM.constant == false)
      {
      this->AppendParameterState(count, RPM.value, RPM.min, RPM.max);
      count++;
      }
    RothCParameter &HUM = this->R.FertilizerFractions[i]->HUM;
    if (HUM.constant == false)
      {
      this->AppendParameterState(count, HUM.value, HUM.min, HUM.max);
      count++;
      }
    }

  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2ERothCModelParameter::GenerateInternalSchemeFromXML()
{
  int i;
  vtkXMLDataElement *root = this->XMLRoot;

  if (root == NULL)
    {
    vtkErrorMacro( "XML root element for a valid RothC scheme not set");
    return false;
    }

  // Check for correct name
  if (strncasecmp(root->GetName(), "RothC", strlen("RothC")) != 0)
    {
    vtkErrorMacro( "The model parameter does not contain a valid RothC scheme");
    return false;
    }

  vtkXMLDataElement *a = root->FindNestedElementWithName("a");
  if (a != NULL)
    {
    vtkXMLDataElement *a1 = a->FindNestedElementWithName("a1");
    if (a1 != NULL)
      {
      this->ParseRothCParameter(a1, this->R.a.a1);
      }
    vtkXMLDataElement *a2 = a->FindNestedElementWithName("a2");
    if (a2 != NULL)
      {
      this->ParseRothCParameter(a2, this->R.a.a2);
      }
    vtkXMLDataElement *a3 = a->FindNestedElementWithName("a3");
    if (a3 != NULL)
      {
      this->ParseRothCParameter(a3, this->R.a.a3);
      }
    }

  vtkXMLDataElement *b = root->FindNestedElementWithName("b");
  if (b != NULL)
    {
    vtkXMLDataElement *b1 = b->FindNestedElementWithName("b1");
    if (b1 != NULL)
      {
      this->ParseRothCParameter(b1, this->R.b.b1);
      }
    vtkXMLDataElement *b2 = b->FindNestedElementWithName("b2");
    if (b2 != NULL)
      {
      this->ParseRothCParameter(b2, this->R.b.b2);
      }
    vtkXMLDataElement *b3 = b->FindNestedElementWithName("b3");
    if (b3 != NULL)
      {
      this->ParseRothCParameter(b3, this->R.b.b3);
      }
    }

  vtkXMLDataElement *c = root->FindNestedElementWithName("c");
  if (c != NULL)
    {
    vtkXMLDataElement *c1 = c->FindNestedElementWithName("c1");
    if (c1 != NULL)
      {
      this->ParseRothCParameter(c1, this->R.c.c1);
      }
    vtkXMLDataElement *c2 = c->FindNestedElementWithName("c2");
    if (c2 != NULL)
      {
      this->ParseRothCParameter(c2, this->R.c.c2);
      }
    }

  vtkXMLDataElement *k = root->FindNestedElementWithName("k");
  if (k != NULL)
    {
    vtkXMLDataElement *DPM = k->FindNestedElementWithName("DPM");
    if (DPM != NULL)
      {
      this->ParseRothCParameter(DPM, this->R.k.DPM);
      }
    vtkXMLDataElement *RPM = k->FindNestedElementWithName("RPM");
    if (RPM != NULL)
      {
      this->ParseRothCParameter(RPM, this->R.k.RPM);
      }
    vtkXMLDataElement *HUM = k->FindNestedElementWithName("HUM");
    if (HUM != NULL)
      {
      this->ParseRothCParameter(HUM, this->R.k.HUM);
      }
    vtkXMLDataElement *BIO = k->FindNestedElementWithName("BIO");
    if (BIO != NULL)
      {
      this->ParseRothCParameter(BIO, this->R.k.BIO);
      }
    }

  vtkXMLDataElement *x = root->FindNestedElementWithName("x");
  if (x != NULL)
    {
    vtkXMLDataElement *x1 = x->FindNestedElementWithName("x1");
    if (x1 != NULL)
      {
      this->ParseRothCParameter(x1, this->R.x.x1);
      }
    vtkXMLDataElement *x2 = x->FindNestedElementWithName("x2");
    if (x2 != NULL)
      {
      this->ParseRothCParameter(x2, this->R.x.x2);
      }
    vtkXMLDataElement *x3 = x->FindNestedElementWithName("x3");
    if (x3 != NULL)
      {
      this->ParseRothCParameter(x3, this->R.x.x3);
      }
    vtkXMLDataElement *x4 = x->FindNestedElementWithName("x4");
    if (x4 != NULL)
      {
      this->ParseRothCParameter(x4, this->R.x.x4);
      }
    }

  // Prase the plant fractions
  vtkXMLDataElement *plantsXML = root->FindNestedElementWithName(
      "PlantFractions");
  if (plantsXML != NULL)
    {
    this->R.PlantFractions.clear();
    for (i = 0; i < plantsXML->GetNumberOfNestedElements(); i++)
      {
      vtkXMLDataElement *plantXML = plantsXML->GetNestedElement(i);
      if (!plantXML->FindNestedElementWithName("DPM")
          || !plantXML->FindNestedElementWithName("RPM")
          || !plantXML->FindNestedElementWithName("HUM")
          || strncasecmp(plantXML->GetName(), "PlantFraction",
              strlen("PlantFraction") != 0))
        {
        vtkErrorMacro(
            "The model parameter does not contain a valid Plant Fraction scheme");
        return false;
        }
      RothCParameterFraction *plant = new RothCParameterFraction;
      // Set the name
      plant->name = plantXML->GetAttribute("name");
      // Get the description
      vtkXMLDataElement *descrXML = plantXML->FindNestedElementWithName(
          "description");
      if (descrXML != NULL)
        {
        plant->description = descrXML->GetCharacterData();
        }
      // Parse the parameter
      this->ParseRothCParameter(plantXML->FindNestedElementWithName("DPM"),
          plant->DPM);
      this->ParseRothCParameter(plantXML->FindNestedElementWithName("RPM"),
          plant->RPM);
      this->ParseRothCParameter(plantXML->FindNestedElementWithName("HUM"),
          plant->HUM);
      this->R.PlantFractions.push_back(plant);
      }
    }

  // Parse the fertilizer fractions
  vtkXMLDataElement *fertsXML = root->FindNestedElementWithName(
      "FertilizerFractions");
  if (fertsXML != NULL)
    {
    this->R.FertilizerFractions.clear();
    for (i = 0; i < fertsXML->GetNumberOfNestedElements(); i++)
      {
      vtkXMLDataElement *fertXML = fertsXML->GetNestedElement(i);
      if (!fertXML->FindNestedElementWithName("DPM")
          || !fertXML->FindNestedElementWithName("RPM")
          || !fertXML->FindNestedElementWithName("HUM")
          || strncasecmp(fertXML->GetName(), "FertilizerFraction",
              strlen("FertilizerFraction") != 0))
        {
        vtkErrorMacro(
            "The model parameter does not contain a valid Fertilizer Fraction scheme");
        return false;
        }
      RothCParameterFraction *fert = new RothCParameterFraction;      // Set the name
      fert->name = fertXML->GetAttribute("name");
      // Get the description
      vtkXMLDataElement *descrXML = fertXML->FindNestedElementWithName(
          "description");
      if (descrXML != NULL)
        {
        fert->description = descrXML->GetCharacterData();
        }
      this->ParseRothCParameter(fertXML->FindNestedElementWithName("DPM"),
          fert->DPM);
      this->ParseRothCParameter(fertXML->FindNestedElementWithName("RPM"),
          fert->RPM);
      this->ParseRothCParameter(fertXML->FindNestedElementWithName("HUM"),
          fert->HUM);
      this->R.PlantFractions.push_back(fert);
      }
    }

  // Create the calibratable parameter index
  this->CreateParameterIndex();

  this->SetNumberOfCalibratableParameter(this->ParameterIndex.size());

  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2ERothCModelParameter::ParseRothCParameter(
    vtkXMLDataElement *XMLRothCParameter, RothCParameter &p)
{
  int active;
  int constant = 0;
  active = 0;

  if (XMLRothCParameter == NULL)
    return false;

  if (XMLRothCParameter->GetAttribute("const") != NULL)
    {
    constant = atoi(XMLRothCParameter->GetAttribute("const"));
    if (constant == 0)
      p.constant = false;
    else
      p.constant = true;
    }

  if (XMLRothCParameter->GetAttribute("min") != NULL)
    {
    p.min = atof(XMLRothCParameter->GetAttribute("min"));
    }

  if (XMLRothCParameter->GetAttribute("max") != NULL)
    {
    p.max = atof(XMLRothCParameter->GetAttribute("max"));
    }

  if (XMLRothCParameter->GetCharacterData() != NULL)
    {
    p.value = atof(XMLRothCParameter->GetCharacterData());
    }
  return true;
}
