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
#include "vtkTAG2EFuzzyInferenceModelParameter.h"
#include <vtkXMLDataParser.h>

vtkCxxRevisionMacro(vtkTAG2EFuzzyInferenceModelParameter, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EFuzzyInferenceModelParameter);

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModelParameter::vtkTAG2EFuzzyInferenceModelParameter()
{
  ;
}

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModelParameter::~vtkTAG2EFuzzyInferenceModelParameter()
{
  ;
}

bool vtkTAG2EFuzzyInferenceModelParameter::GenerateXMLFromInternalScheme()
{
  unsigned int i, j; 
  
  cout << this->Scheme.name << endl;
  cout << this->Scheme.InferenceScheme.name << endl;
  
  for(i = 0; i < this->Scheme.InferenceScheme.Factors.size(); i++) {
    cout << " " << this->Scheme.InferenceScheme.Factors[i].name << endl;
    cout << " " << this->Scheme.InferenceScheme.Factors[i].min << endl;
    cout << " " << this->Scheme.InferenceScheme.Factors[i].max << endl;
    for(j = 0; j < this->Scheme.InferenceScheme.Factors[i].Sets.size(); j++) {
      cout << "  " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].constant << endl;
      cout << "  " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].position << endl;
      cout << "  " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].priority << endl;
      cout << "  " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].type << endl;
      if(this->Scheme.InferenceScheme.Factors[i].Sets[j].type == FUZZY_SET_TYPE_TRIANGULAR) {
        cout << "   " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].Triangular.center << endl;
        cout << "   " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].Triangular.left << endl;
        cout << "   " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].Triangular.right << endl;
      }
      if(this->Scheme.InferenceScheme.Factors[i].Sets[j].type == FUZZY_SET_TYPE_CRISP) {
        cout << "   " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].Crisp.left << endl;
        cout << "   " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].Crisp.right << endl;
      }
      if(this->Scheme.InferenceScheme.Factors[i].Sets[j].type == FUZZY_SET_TYPE_BELL_SHAPE) {
        cout << "   " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].BellShape.center << endl;
        cout << "   " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].BellShape.sdLeft << endl;
        cout << "   " <<  this->Scheme.InferenceScheme.Factors[i].Sets[j].BellShape.sdRight << endl;
      }
    }
  }
  
  cout << this->Scheme.InferenceScheme.Responses.min << endl;
  cout << this->Scheme.InferenceScheme.Responses.max << endl;
  
  for(i = 0; i < this->Scheme.InferenceScheme.Responses.Responses.size(); i++) {
    cout << " " << this->Scheme.InferenceScheme.Responses.Responses[i].constant << endl;
    cout << " " << this->Scheme.InferenceScheme.Responses.Responses[i].sd << endl;
    cout << " " << this->Scheme.InferenceScheme.Responses.Responses[i].value << endl;
  }
  
  cout << this->Scheme.Weights.active << endl;
  
  for(i = 0; i < this->Scheme.Weights.Weights.size(); i++) {
    cout << " " << this->Scheme.Weights.Weights[i].active << endl;
    cout << " " << this->Scheme.Weights.Weights[i].constant << endl;
    cout << " " << this->Scheme.Weights.Weights[i].max << endl;
    cout << " " << this->Scheme.Weights.Weights[i].min << endl;
    cout << " " << this->Scheme.Weights.Weights[i].name << endl;
    cout << " " << this->Scheme.Weights.Weights[i].portId << endl;
    cout << " " << this->Scheme.Weights.Weights[i].value << endl;
  }
  return true;
}

bool vtkTAG2EFuzzyInferenceModelParameter::GenerateInternalSchemeFromXML()
{
  vtkXMLDataElement *root = this->GetXMLRoot();

  // Check for correct name
  if (strncasecmp(root->GetName(), "WeightedFuzzyInferenceScheme", strlen("WeightedFuzzyInferenceScheme")) != 0) {
    vtkErrorMacro("The model parameter does not contain a valid weighted fuzzy inference scheme");
    return false;
  }

  if (root->GetAttribute("name") != NULL) {
    this->Scheme.name = root->GetAttribute("name");
  } else {
    vtkErrorMacro( << "Attribute \"name\" is missing in WeightedFuzzyInferenceScheme element");
    return false;
  }

  // Get the Fuzzy inference scheme
  vtkXMLDataElement *InferenceScheme = root->FindNestedElementWithName("FuzzyInferenceScheme");

  // Parse the Factors and the responses
  if (InferenceScheme != NULL) {

    if (InferenceScheme->GetAttribute("name") != NULL) {
      this->Scheme.InferenceScheme.name = InferenceScheme->GetAttribute("name");
    } else {
      vtkErrorMacro( << "Attribute \"name\" is missing in FuzzyInferenceScheme element");
      return false;
    }
    this->ParseFactors(InferenceScheme);

    vtkXMLDataElement *Responses = InferenceScheme->FindNestedElementWithName("Responces");
    if (Responses != NULL)
      this->ParseResponses(Responses);
  }

  // Get the Fuzzy inference scheme
  vtkXMLDataElement *Weights = root->FindNestedElementWithName("Weights");

  // Parse the Factors and the responses
  if (Weights != NULL) {

    if (Weights->GetAttribute("active") != NULL) {
      int active = atoi(Weights->GetAttribute("active"));
      if (active == 0)
        this->Scheme.Weights.active = false;
      else
        this->Scheme.Weights.active = true;
    } else {
      vtkErrorMacro( << "Attribute \"active\" is missing in Weights element");
      return false;
    }
    this->ParseWeights(Weights);
  }

  return true;
}

bool vtkTAG2EFuzzyInferenceModelParameter::ParseFactors(vtkXMLDataElement *InferenceScheme)
{
  int i;

  for (i = 0; i < InferenceScheme->GetNumberOfNestedElements(); i++) {
    vtkXMLDataElement *XMLFactor = InferenceScheme->GetNestedElement(i);

    if (strncasecmp(XMLFactor->GetName(), "Factor", strlen("Factor")) != 0) {
      continue;
    }

    FuzzyFactor Factor;

    if (XMLFactor->GetAttribute("name") != NULL) {
      Factor.name = XMLFactor->GetAttribute("name");
    } else {
      vtkErrorMacro( << "Attribute \"name\" is missing in Factor element: " << i);
      return false;
    }

    if (XMLFactor->GetAttribute("portId") != NULL) {
      Factor.portId = atoi(XMLFactor->GetAttribute("portId"));
    } else {
      vtkErrorMacro( << "Attribute \"portId\" is missing in Factor element: " << i);
      return false;
    }

    if (XMLFactor->GetAttribute("min") != NULL) {
      Factor.min = atof(XMLFactor->GetAttribute("min"));
    } else {
      vtkErrorMacro( << "Attribute \"min\" is missing in Factor element: " << i);
      return false;
    }

    if (XMLFactor->GetAttribute("max") != NULL) {
      Factor.max = atof(XMLFactor->GetAttribute("max"));
    } else {
      vtkErrorMacro( << "Attribute \"max\" is missing in Factor element: " << i);
      return false;
    }

    this->ParseFuzzySets(Factor, XMLFactor);

    cout << "Add Factor " << Factor.name << " with portId " << Factor.portId
      << " min  " << Factor.min << " max " << Factor.max << endl;

    this->Scheme.InferenceScheme.Factors.push_back(Factor);
  }

  return true;
}

bool vtkTAG2EFuzzyInferenceModelParameter::ParseFuzzySets(FuzzyFactor &Factor, vtkXMLDataElement *XMLFactor)
{

  int i;

  for (i = 0; i < XMLFactor->GetNumberOfNestedElements(); i++) {
    vtkXMLDataElement *XMLFuzzySet = XMLFactor->GetNestedElement(i);

    FuzzySet Set;

    if (XMLFuzzySet->GetAttribute("type") != NULL) {
      const char *type = XMLFuzzySet->GetAttribute("type");
      if (strncasecmp(type, "Triangular", strlen(type)) == 0)
        Set.type = FUZZY_SET_TYPE_TRIANGULAR;
      if (strncasecmp(type, "Crisp", strlen(type)) == 0)
        Set.type = FUZZY_SET_TYPE_CRISP;
      if (strncasecmp(type, "BellShape", strlen(type)) == 0)
        Set.type = FUZZY_SET_TYPE_BELL_SHAPE;
    } else {
      vtkErrorMacro( << "Attribute \"type\" is missing in FuzzySet element: " << i);
      return false;
    }

    if (XMLFuzzySet->GetAttribute("priority") != NULL) {
      Set.priority = atoi(XMLFuzzySet->GetAttribute("priority"));
    } else {
      vtkErrorMacro( << "Attribute \"priority\" is missing in FuzzySet element: " << i);
      return false;
    }

    if (XMLFuzzySet->GetAttribute("const") != NULL) {
      int val = atoi(XMLFuzzySet->GetAttribute("priority"));
      if (val == 0)
        Set.constant = false;
      else
        Set.constant = true;
    } else {
      vtkErrorMacro( << "Attribute \"const\" is missing in FuzzySet element: " << i);
      return false;
    }


    if (XMLFuzzySet->GetAttribute("position") != NULL) {
      const char *type = XMLFuzzySet->GetAttribute("position");
      if (strncasecmp(type, "left", strlen(type)) == 0)
        Set.position = FUZZY_SET_POISITION_LEFT;
      if (strncasecmp(type, "intermediate", strlen(type)) == 0)
        Set.position = FUZZY_SET_POISITION_INT;
      if (strncasecmp(type, "right", strlen(type)) == 0)
        Set.position = FUZZY_SET_POISITION_RIGHT;
    } else {
      vtkErrorMacro( << "Attribute \"position\" is missing in FuzzySet element: " << i);
      return false;
    }

    // Now fetch the Fuzzy shapes

    if (Set.type == FUZZY_SET_TYPE_TRIANGULAR) {
      vtkXMLDataElement *Triangular = XMLFuzzySet->FindNestedElementWithName("Triangular");

      if (Triangular != NULL) {
        if (Triangular->GetAttribute("left") != NULL) {
          Set.Triangular.left = atof(Triangular->GetAttribute("left"));
        } else {
          vtkErrorMacro( << "Attribute \"left\" is missing in Triangular element: " << i);
          return false;
        }
        if (Triangular->GetAttribute("right") != NULL) {
          Set.Triangular.right = atof(Triangular->GetAttribute("right"));
        } else {
          vtkErrorMacro( << "Attribute \"right\" is missing in Triangular element: " << i);
          return false;
        }
        if (Triangular->GetAttribute("center") != NULL) {
          Set.Triangular.center = atof(Triangular->GetAttribute("center"));
        } else {
          vtkErrorMacro( << "Attribute \"center\" is missing in Triangular element: " << i);
          return false;
        }
      } else {
        vtkErrorMacro( << "Element \"Triangular\" is missing in FuzzySet element: " << i);
        return false;
      }

      cout << "Added Trinagular center " << Set.Triangular.center << " left "
        << Set.Triangular.left << " right " << Set.Triangular.right << endl;
    }

    if (Set.type == FUZZY_SET_TYPE_CRISP) {
      vtkXMLDataElement *Crisp = XMLFuzzySet->FindNestedElementWithName("Crisp");

      if (Crisp != NULL) {
        if (Crisp->GetAttribute("left") != NULL) {
          Set.Crisp.left = atof(Crisp->GetAttribute("left"));
        } else {
          vtkErrorMacro( << "Attribute \"left\" is missing in Crisp element: " << i);
          return false;
        }
        if (Crisp->GetAttribute("right") != NULL) {
          Set.Crisp.right = atof(Crisp->GetAttribute("right"));
        } else {
          vtkErrorMacro( << "Attribute \"right\" is missing in Crisp element: " << i);
          return false;
        }
      } else {
        vtkErrorMacro( << "Element \"Crisp\" is missing in FuzzySet element: " << i);
        return false;
      }

      cout << "Added Crispt left " << Set.Crisp.left << " right " << Set.Crisp.right << endl;
    }


    if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE) {
      vtkXMLDataElement *BellShape = XMLFuzzySet->FindNestedElementWithName("BellShape");

      if (BellShape != NULL) {
        if (BellShape->GetAttribute("sdLeft") != NULL) {
          Set.BellShape.sdLeft = atof(BellShape->GetAttribute("sdLeft"));
        } else {
          vtkErrorMacro( << "Attribute \"sdLeft\" is missing in BellShape element: " << i);
          return false;
        }
        if (BellShape->GetAttribute("sdRight") != NULL) {
          Set.BellShape.sdRight = atof(BellShape->GetAttribute("sdRight"));
        } else {
          vtkErrorMacro( << "Attribute \"sdRight\" is missing in BellShape element: " << i);
          return false;
        }
        if (BellShape->GetAttribute("center") != NULL) {
          Set.BellShape.center = atof(BellShape->GetAttribute("center"));
        } else {
          vtkErrorMacro( << "Attribute \"center\" is missing in BellShape element: " << i);
          return false;
        }
      } else {
        vtkErrorMacro( << "Element \"BellShape\" is missing in FuzzySet element: " << i);
        return false;
      }

      cout << "Added BellShape center " << Set.Triangular.center << " left "
        << Set.Triangular.left << " right " << Set.Triangular.right << endl;
    }

    cout << "Add FuzzySet " << Set.type << " with priority " << Set.priority
      << " constant  " << Set.constant << " position " << Set.position << endl;

    // Add the FuzzySet to the Factor
    Factor.Sets.push_back(Set);
  }

  return true;
}

bool vtkTAG2EFuzzyInferenceModelParameter::ParseResponses(vtkXMLDataElement *XMLResponces)
{
  int i;

  if (XMLResponces->GetAttribute("min") != NULL) {
    this->Scheme.InferenceScheme.Responses.min = atof(XMLResponces->GetAttribute("min"));
  } else {
    vtkErrorMacro( << "Attribute \"min\" is missing in Responces element");
    return false;
  }

  if (XMLResponces->GetAttribute("max") != NULL) {
    this->Scheme.InferenceScheme.Responses.max = atof(XMLResponces->GetAttribute("max"));
  } else {
    vtkErrorMacro( << "Attribute \"max\" is missing in Responces element");
    return false;
  }

  for (i = 0; i < XMLResponces->GetNumberOfNestedElements(); i++) {
    vtkXMLDataElement *XMLResponce = XMLResponces->GetNestedElement(i);

    FuzzyResponse Responce;

    int constant;

    if (XMLResponce->GetAttribute("const") != NULL) {
      constant = atoi(XMLResponce->GetAttribute("const"));
      if(constant == 0)
        Responce.constant = false;
      else
        Responce.constant = true;
    } else {
      vtkErrorMacro( << "Attribute \"const\" is missing in Responce element: " << i);
      return false;
    }
    
    if (XMLResponce->GetAttribute("sd") != NULL) {
      Responce.sd = atof(XMLResponce->GetAttribute("sd"));
    } else {
      vtkErrorMacro( << "Attribute \"sd\" is missing in Responce element: " << i);
      return false;
    }
    
    if (XMLResponce->GetCharacterData() != NULL) {
      Responce.value = atof(XMLResponce->GetCharacterData());
    } else {
      vtkErrorMacro( << "Attribute \"sd\" is missing in Responce element: " << i);
      return false;
    }
    
    this->Scheme.InferenceScheme.Responses.Responses.push_back(Responce);
    
    cout << "Added Responce const " << Responce.constant << " sd " << Responce.sd
         << " value " << Responce.value << endl;
    
  }
  
  cout << "Added Responces min " << this->Scheme.InferenceScheme.Responses.min
       << " max " << this->Scheme.InferenceScheme.Responses.max << endl;


  return true;
}

bool vtkTAG2EFuzzyInferenceModelParameter::ParseWeights(vtkXMLDataElement *Weights)
{

  int i;
  int active;

  if (Weights->GetAttribute("active") != NULL) {
    active = atoi(Weights->GetAttribute("active"));
    if(active == 0)
      this->Scheme.Weights.active = false;
    else
      this->Scheme.Weights.active = true;
  } else {
    vtkErrorMacro( << "Attribute \"active\" is missing in Weights element");
    return false;
  }

  for (i = 0; i < Weights->GetNumberOfNestedElements(); i++) {
    vtkXMLDataElement *XMLWeight = Weights->GetNestedElement(i);

    FuzzyWeight Weight;

    int constant = 0;
    active = 0;

    if (XMLWeight->GetAttribute("const") != NULL) {
      constant = atoi(XMLWeight->GetAttribute("const"));
      if(constant == 0)
        Weight.constant = false;
      else
        Weight.constant = true;
    } else {
      vtkErrorMacro( << "Attribute \"const\" is missing in Weight element: " << i);
      return false;
    }
    
    if (XMLWeight->GetAttribute("active") != NULL) {
      active = atoi(XMLWeight->GetAttribute("active"));
      if(active == 0)
        Weight.active = false;
      else
        Weight.active = true;
    } else {
      vtkErrorMacro( << "Attribute \"active\" is missing in Weight element: " << i);
      return false;
    }
    
    if (XMLWeight->GetAttribute("name") != NULL) {
      Weight.name = XMLWeight->GetAttribute("name");
    } else {
      vtkErrorMacro( << "Attribute \"name\" is missing in Weight element: " << i);
      return false;
    }
    
    if (XMLWeight->GetAttribute("min") != NULL) {
      Weight.min = atof(XMLWeight->GetAttribute("min"));
    } else {
      vtkErrorMacro( << "Attribute \"min\" is missing in Weight element: " << i);
      return false;
    }
    
    if (XMLWeight->GetAttribute("max") != NULL) {
      Weight.max = atof(XMLWeight->GetAttribute("max"));
    } else {
      vtkErrorMacro( << "Attribute \"max\" is missing in Weight element: " << i);
      return false;
    }
    
    if (XMLWeight->GetCharacterData() != NULL) {
      Weight.value = atof(XMLWeight->GetCharacterData());
    } else {
      vtkErrorMacro( << "Attribute \"sd\" is missing in Weight element: " << i);
      return false;
    }
    
    this->Scheme.Weights.Weights.push_back(Weight);
    
    cout << "Added Weight const " << Weight.constant << " name " << Weight.name
         << " value " << Weight.value << " min " <<  Weight.min 
         << " max " << Weight.max << " active "  << Weight.active << endl;
    
  }
  
  cout << "Added Weight active " << this->Scheme.Weights.active << endl;


  return true;
}
