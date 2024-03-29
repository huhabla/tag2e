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

/**
 * \brief This is the fuzzy inference model parameter class
 * 
 * \TODO Instead of normalized fuzzy set positions, use real values and normailze at runtime
 */

#ifndef vtkTAG2EFuzzyInferenceModelParameter_H
#define	vtkTAG2EFuzzyInferenceModelParameter_H

#include <vtkObject.h>
#include <vtkXMLDataElement.h>
#include "vtkTAG2EAbstractCalibratableModelParameter.h"
#include <vector>
#include <map>
#include "tag2eFIS.h"

class vtkXMLDataElement;

class vtkTAG2EFuzzyInferenceModelParameter : public vtkTAG2EAbstractCalibratableModelParameter {
public:
    vtkTypeRevisionMacro(vtkTAG2EFuzzyInferenceModelParameter,
    		vtkTAG2EAbstractCalibratableModelParameter);

    void PrintSelf(ostream& os, vtkIndent indent) {
        ;
    }
    static vtkTAG2EFuzzyInferenceModelParameter *New();

    virtual bool GenerateInternalSchemeFromXML();
    virtual bool GenerateXMLFromInternalScheme();
    
    vtkGetMacro(NumberOfRules, int);
    vtkGetMacro(NumberOfFactors, int);
    
    //BTX
    FuzzyInferenceScheme &GetInternalScheme() {
        return this->FIS;
    }
    //ETX

protected:

    vtkTAG2EFuzzyInferenceModelParameter();
    ~vtkTAG2EFuzzyInferenceModelParameter();

    bool ParseFactors(vtkXMLDataElement *FuzzyInferenceScheme);
    bool ParseResponses(vtkXMLDataElement *FuzzyInferenceScheme);
    bool ParseFuzzyInferenceScheme(vtkXMLDataElement *FuzzyInferenceScheme);
    bool ParseFuzzySets(FuzzyFactor &Factor, vtkXMLDataElement *XMLFactor);
    virtual bool CreateParameterIndex();
    virtual bool SetParameter(unsigned int index, double value);
    
    // BTX
    FuzzyInferenceScheme FIS;
    // ETX

    unsigned int NumberOfRules;
    unsigned int NumberOfFactors;
    
private:
    vtkTAG2EFuzzyInferenceModelParameter(const vtkTAG2EFuzzyInferenceModelParameter& orig);
    void operator=(const vtkTAG2EFuzzyInferenceModelParameter&); // Not implemented.
};


#endif	/* vtkTAG2EFuzzyInferenceModelParameter_H */
