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

#ifndef vtkTAG2EFuzzyInferenceModelParameter_H
#define	vtkTAG2EFuzzyInferenceModelParameter_H

#include <vtkObject.h>
#include <vtkXMLDataElement.h>
#include <assert.h>
#include "vtkTAG2EAbstractCalibratableModelParameter.h"
#include <vector>
#include <map>

#define FUZZY_SET_POISITION_LEFT 0
#define FUZZY_SET_POISITION_INT 1
#define FUZZY_SET_POISITION_RIGHT 2
#define FUZZY_SET_TYPE_TRIANGULAR 0
#define FUZZY_SET_TYPE_CRISP 1
#define FUZZY_SET_TYPE_BELL_SHAPE 2

// The documentation of the following trivial classes
// is located in the WeightedFuzzyInferenceScheme.xsd
class FuzzyShapeTriangular{
public:
    double center;
    double left;
    double right;
};

class FuzzyShapeCrisp{
public:
    double left;
    double right;
};

class FuzzyShapeBell{
public:
    double center;
    double sdLeft;
    double sdRight;
};

class FuzzySet {
public:
    unsigned int type;
    unsigned int priority;
    unsigned int position;
    bool constant;
    FuzzyShapeTriangular Triangular;
    FuzzyShapeCrisp Crisp;
    FuzzyShapeBell BellShape;
};

class FuzzyFactor {
public:
    int portId;
    std::string name;
    double min;
    double max;
    std::vector<FuzzySet> Sets;
};

class FuzzyResponse{
public:
    bool constant;
    double value;
    double sd;
};

class FuzzyResponses{
public:
    double min;
    double max;
    std::vector<FuzzyResponse> Responses;
};

class FuzzyInferenceScheme {
public:
    std::string name;
    std::vector<FuzzyFactor> Factors;
    FuzzyResponses Responses;
};

class FuzzyWeight{
public:
    int portId;
    std::string name;
    bool active;
    bool constant;
    double value;
    double min;
    double max;
};

class FuzzyWeights{
public:
    bool active;
    std::vector<FuzzyWeight> Weights;
};

class WeightedFuzzyInferenceScheme {
public:
    std::string name;
    FuzzyInferenceScheme FIS;
    FuzzyWeights Weights;
};

class vtkXMLDataElement;

class vtkTAG2EFuzzyInferenceModelParameter : public vtkTAG2EAbstractCalibratableModelParameter {
public:
    vtkTypeRevisionMacro(vtkTAG2EFuzzyInferenceModelParameter, vtkTAG2EAbstractCalibratableModelParameter);

    void PrintSelf(ostream& os, vtkIndent indent) {
        ;
    }
    static vtkTAG2EFuzzyInferenceModelParameter *New();
    
    //!\brief Change arbritary a model parameter
    virtual void ChangeParameterRandomly(){;}
    //!\brief Restore the last randomly modified model parameter 
    virtual void RestoreParameter(){;}
    
    virtual bool GenerateInternalSchemeFromXML();
    virtual bool GenerateXMLFromInternalScheme();
    
    //BTX
    WeightedFuzzyInferenceScheme &GetInternalScheme(){return this->WFIS;}
    //ETX
    
protected:        

    vtkTAG2EFuzzyInferenceModelParameter();
    ~vtkTAG2EFuzzyInferenceModelParameter();
    
    bool ParseFactors(vtkXMLDataElement *FuzzyInferenceScheme);
    bool ParseResponses(vtkXMLDataElement *FuzzyInferenceScheme);
    bool ParseFuzzyInferenceScheme(vtkXMLDataElement *FuzzyInferenceScheme);
    bool ParseFuzzySets(FuzzyFactor &Factor, vtkXMLDataElement *XMLFactor);
    bool ParseWeights(vtkXMLDataElement *Weights);
    
    // BTX
    WeightedFuzzyInferenceScheme WFIS;
    // ETX
    
private:
    vtkTAG2EFuzzyInferenceModelParameter(const vtkTAG2EFuzzyInferenceModelParameter& orig);
    void operator=(const vtkTAG2EFuzzyInferenceModelParameter&); // Not implemented.
};


#endif	/* vtkTAG2EFuzzyInferenceModelParameter_H */
