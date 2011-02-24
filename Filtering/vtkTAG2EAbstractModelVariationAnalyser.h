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

#ifndef vtkTAG2EAbstractModelVariationAnalyser_H
#define	vtkTAG2EAbstractModelVariationAnalyser_H

#include <vtkTemporalDataSetAlgorithm.h>
#include <assert.h>
#include "vtkTAG2EAbstractModel.h"


// The supported distribution functions (df) which are used to create 
// random number variables 
#define TAG2E_R_DF_NORM 0
#define TAG2E_R_DF_LNORM 1
#define TAG2E_R_DF_UNIF 2
#define TAG2E_R_DF_BINOM 3
#define TAG2E_R_DF_CHISQ 4

class vtkStringArray;
class vtkIntArray;
class vtkDoubleArray;

class vtkTAG2EAbstractModelVariationAnalyser : public vtkTemporalDataSetAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractModelVariationAnalyser, vtkTemporalDataSetAlgorithm);
    static vtkTAG2EAbstractModelVariationAnalyser *New(); 
    
    //!\brief Set the model which should be analyzed
    vtkSetObjectMacro(Model, vtkTAG2EAbstractModel);
    vtkGetObjectMacro(Model, vtkTAG2EAbstractModel);
    
    //!\brief Set the data distribution description which should be used for analyze
    vtkSetObjectMacro(DataDistributionDescription, vtkTAG2EAbstractModelParameter);
    vtkGetObjectMacro(DataDistributionDescription, vtkTAG2EAbstractModelParameter);

    vtkGetMacro(MaxNumberOfIterations, int);
    
protected:
    vtkTAG2EAbstractModelVariationAnalyser();
    ~vtkTAG2EAbstractModelVariationAnalyser();

    vtkGetMacro(NumberOfTimeSteps, int);
    vtkSetMacro(NumberOfTimeSteps, int);
    vtkSetMacro(MaxNumberOfIterations, int);
    
    virtual int RequestInformation(vtkInformation *request, vtkInformationVector **inputVector, vtkInformationVector *outputVector);
    virtual int RequestUpdateExtent(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *) {
        this->BuildDataDistributionDescriptionArrays();
        vtkErrorMacro(<<"RequestData must be implemented in a subclass");
        return -1;
    }
    
    virtual bool BuildDataDistributionDescriptionArrays();

    vtkTAG2EAbstractModel *Model;
    vtkTAG2EAbstractModelParameter *DataDistributionDescription;
    
    vtkStringArray *VariableName;
    vtkIntArray *VariableDistributionType;
    vtkDoubleArray *DistributionParameter;

    int NumberOfTimeSteps;
    int MaxNumberOfIterations;
    double *TimeSteps;
    
private:
    vtkTAG2EAbstractModelVariationAnalyser(const vtkTAG2EAbstractModelVariationAnalyser& orig); // Not implemented.
    void operator=(const vtkTAG2EAbstractModelVariationAnalyser&); // Not implemented.
};

#endif	/* vtkTAG2EAbstractModelVariationAnalyser_H */
