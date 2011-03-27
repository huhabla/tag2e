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
 * \brief This class uses a weighted fuzzy inference scheme to process
 * the point data of the temporal input data sets. The weighted fuzzy inference 
 * must be provided as as XML model parameter representation which is of type
 * vtkTAG2EFuzzyInferenceModelParameter. 
 */

#ifndef vtkTAG2EWeightedFuzzyInferenceModel_H
#define	vtkTAG2EWeightedFuzzyInferenceModel_H

#include "vtkTAG2EAbstractCalibratableModel.h"

class vtkIntArray;
class vtkStringArray;
class vtkTAG2EFuzzyInferenceModelParameter;
class WeightedFuzzyInferenceScheme;

class vtkTAG2EWeightedFuzzyInferenceModel : public vtkTAG2EAbstractCalibratableModel {
public:
    vtkTypeRevisionMacro(vtkTAG2EWeightedFuzzyInferenceModel, vtkTAG2EAbstractModel);
    
    void PrintSelf(ostream& os, vtkIndent indent);
    static vtkTAG2EWeightedFuzzyInferenceModel *New(); 
     
    virtual double GetModelAssessmentFactor(){;}
    
    //!\brief Set the model parameter which must be of type vtkTAG2EFuzzyInferenceModelParameter
    //! This XML model parameter describes the fuzzy inference scheme which is used to compute 
    //! the input point data.
    void SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter);
    
    // Verify the FIS comutation with simple test cases. No inputs required.
    bool TestFISComputation();
    
protected:
    vtkTAG2EWeightedFuzzyInferenceModel();
    ~vtkTAG2EWeightedFuzzyInferenceModel();
    
    //!\brief This method computes the rule code matrix which is used to compute the 
    //! the deegree of membership of an input factor for each rule
    //!\param RuleCodeMatrix The matrix of coded rules
    //!\param numberOfRules Number of rules
    //!\param WFIS The internal representation of the weighted fuzzy inference scheme
    //!\return true in case of success

    virtual bool ComputeRuleCodeMatrixEntries(std::vector< std::vector<int> > &RuleCodeMatrix, 
                         int numberOfRules, WeightedFuzzyInferenceScheme &WFIS);
    //!\brief Compute the deegree of fullfillment of a single point for a single rule
    //!\param The factor input vector of a single point at a single time step
    //!\param rule The index of a single rule (index of row in the RuleCodeMatrix)
    //!\param RuleCodeMatrix The matrix of coded rules
    //!\param WFIS The internal representation of the weighted fuzzy inference scheme
    //!\return The deegree of fullfillment of a single rule
    virtual double ComputeDOF(double *Input, int rule, std::vector< std::vector<int> > &RuleCodeMatrix, WeightedFuzzyInferenceScheme &WFIS);

    //!\brief Compute the weighted fuzzy inference scheme result for a single point  
    //!\param The factor input vector of a single point at a single time step
    //!\param numberOfRules Number of rules
    //!\param RuleCodeMatrix The matrix of coded rules
    //!\param WFIS The internal representation of the weighted fuzzy inference scheme
    //!\return The result of the fuzzy inference scheme computation
    virtual double ComputeFISResult(double *Input, int numberOfRules, std::vector< std::vector<int> > &RuleCodeMatrix, WeightedFuzzyInferenceScheme &WFIS);

   //!\brief Interpolate the y value of a standard normal distribution and position x
    virtual double InterpolatePointInNormDist (double x);
    
    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
    virtual int FillInputPortInformation(int port, vtkInformation* info);
    virtual int RequestUpdateExtent(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
        
    vtkTAG2EFuzzyInferenceModelParameter *FuzzyModelParameter;
    vtkIntArray *InputPorts;
    vtkStringArray *ArrayNames;
    
private:
    vtkTAG2EWeightedFuzzyInferenceModel(const vtkTAG2EWeightedFuzzyInferenceModel& orig); // Not implemented.
    void operator=(const vtkTAG2EWeightedFuzzyInferenceModel&); // Not implemented.
};

#endif	/* vtkTAG2EWeightedFuzzyInferenceModel_H */
