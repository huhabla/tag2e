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
 * \brief 
 * 
 */

#ifndef vtkTAG2EWeightedFuzzyInferenceModel_H
#define	vtkTAG2EWeightedFuzzyInferenceModel_H

#include "vtkTAG2EAbstractCalibratableModel.h"

class vtkDoubleArray;
class vtkStringArray;
class vtkTAG2EFuzzyInferenceModelParameter;
class vtkDataSetAttributes;
class WeightedFuzzyInferenceScheme;

class vtkTAG2EWeightedFuzzyInferenceModel : public vtkTAG2EAbstractCalibratableModel {
public:
    vtkTypeRevisionMacro(vtkTAG2EWeightedFuzzyInferenceModel, vtkTAG2EAbstractModel);
    
    void PrintSelf(ostream& os, vtkIndent indent);
    static vtkTAG2EWeightedFuzzyInferenceModel *New(); 
     
    virtual double GetModelAssessmentFactor(){;}
    
protected:
    vtkTAG2EWeightedFuzzyInferenceModel();
    ~vtkTAG2EWeightedFuzzyInferenceModel();
    
    virtual bool ComputeFIS(vtkDataSetAttributes *Data);
    virtual bool ComputeRuleCodeArrayEntries(int **RuleCodeArray, int numberOfRules, WeightedFuzzyInferenceScheme &WFIS);

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
    virtual int FillInputPortInformation(int port, vtkInformation* info);
    virtual int RequestUpdateExtent(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
        
    vtkTAG2EFuzzyInferenceModelParameter *FuzzyModelParameter;
    
private:
    vtkTAG2EWeightedFuzzyInferenceModel(const vtkTAG2EWeightedFuzzyInferenceModel& orig); // Not implemented.
    void operator=(const vtkTAG2EWeightedFuzzyInferenceModel&); // Not implemented.
};

#endif	/* vtkTAG2EWeightedFuzzyInferenceModel_H */
