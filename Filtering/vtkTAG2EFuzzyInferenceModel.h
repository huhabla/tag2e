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
 * \brief This class uses a  fuzzy inference scheme to process
 * the point data of the temporal input data sets. The  fuzzy inference 
 * must be provided as as XML model parameter representation which is of type
 * vtkTAG2EFuzzyInferenceModelParameter. 
 */

#ifndef vtkTAG2EFuzzyInferenceModel_H
#define	vtkTAG2EFuzzyInferenceModel_H

#include "vtkTAG2EAbstractCalibratableModel.h"
#include "tag2eFIS.h"

class vtkIntArray;
class vtkStringArray;
class vtkTAG2EFuzzyInferenceModelParameter;
class FuzzyInferenceScheme;

class vtkTAG2EFuzzyInferenceModel : public vtkTAG2EAbstractCalibratableModel {
public:
    vtkTypeRevisionMacro(vtkTAG2EFuzzyInferenceModel, vtkTAG2EAbstractCalibratableModel);
    
    void PrintSelf(ostream& os, vtkIndent indent);
    static vtkTAG2EFuzzyInferenceModel *New(); 
     
    virtual double GetModelAssessmentFactor(){return this->ModelAssessmentFactor;}
    
    //! Set the the desired lower limit for the applicability of the rules (0 - 100), default are 2%
    //! 0 - rule to 0% in use, 100 - rule to 100% in use
    //! This value affect directly the computation of the model assessment factor
    vtkSetMacro(ApplicabilityRuleLimit, double);
    vtkGetMacro(ApplicabilityRuleLimit, double);
    
    //!\brief Set the model parameter which must be of type vtkTAG2EFuzzyInferenceModelParameter
    //! This XML model parameter describes the fuzzy inference scheme which is used to compute 
    //! the input point data.
    void SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter);
    
    // Verify the FIS comutation with simple test cases. No inputs required.
    bool TestFISComputation(){return tag2eFIS::TestFISComputation();}

protected:
    vtkTAG2EFuzzyInferenceModel();
    ~vtkTAG2EFuzzyInferenceModel();
    
    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
    virtual int FillInputPortInformation(int port, vtkInformation* info);
    virtual int RequestUpdateExtent(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
        
    vtkTAG2EFuzzyInferenceModelParameter *FuzzyModelParameter;
    vtkIntArray *InputPorts;
    vtkStringArray *ArrayNames;
    double ModelAssessmentFactor;
    double ApplicabilityRuleLimit;
    
private:
    vtkTAG2EFuzzyInferenceModel(const vtkTAG2EFuzzyInferenceModel& orig); // Not implemented.
    void operator=(const vtkTAG2EFuzzyInferenceModel&); // Not implemented.
};

#endif	/* vtkTAG2EFuzzyInferenceModel_H */
