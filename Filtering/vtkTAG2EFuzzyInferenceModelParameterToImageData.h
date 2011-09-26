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
 * vtkTAG2EFuzzyInferenceModelParameterToImageDataParameter. 
 */

#ifndef vtkTAG2EFuzzyInferenceModelParameterToImageData_H
#define	vtkTAG2EFuzzyInferenceModelParameterToImageData_H

#include <vtkImageAlgorithm.h>
#include "vtkTAG2EFuzzyInferenceModelParameter.h"
#include "tag2eFIS.h"

class vtkIntArray;
class vtkStringArray;
class vtkTAG2EFuzzyInferenceModelParameterToImageDataParameter;
class FuzzyInferenceScheme;

class vtkTAG2EFuzzyInferenceModelParameterToImageData : public vtkImageAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2EFuzzyInferenceModelParameterToImageData, vtkImageAlgorithm);
    
    void PrintSelf(ostream& os, vtkIndent indent);
    static vtkTAG2EFuzzyInferenceModelParameterToImageData *New(); 
    
    //!\brief Set the model parameter which must be of type vtkTAG2EFuzzyInferenceModelParameter
    //! This XML model parameter describes the fuzzy inference scheme which is used to compute 
    //! the input point data.
    vtkSetObjectMacro(FuzzyModelParameter, vtkTAG2EFuzzyInferenceModelParameter);
    
    vtkSetMacro(XAxisExtent, unsigned int);
    vtkSetMacro(YAxisExtent, unsigned int);
    vtkSetMacro(ZAxisExtent, unsigned int);

    vtkGetMacro(XAxisExtent, unsigned int);
    vtkGetMacro(YAxisExtent, unsigned int);
    vtkGetMacro(ZAxisExtent, unsigned int);

protected:
    vtkTAG2EFuzzyInferenceModelParameterToImageData();
    ~vtkTAG2EFuzzyInferenceModelParameterToImageData();
    
  virtual int RequestInformation(vtkInformation* request,
                                 vtkInformationVector** inputVector,
                                 vtkInformationVector* outputVector);
    
  virtual int RequestData(vtkInformation *,
                          vtkInformationVector **,
                          vtkInformationVector *);
    
    vtkTAG2EFuzzyInferenceModelParameter *FuzzyModelParameter;
    unsigned int XAxisExtent;
    unsigned int YAxisExtent;
    unsigned int ZAxisExtent;
    
private:
    vtkTAG2EFuzzyInferenceModelParameterToImageData(const vtkTAG2EFuzzyInferenceModelParameterToImageData& orig); // Not implemented.
    void operator=(const vtkTAG2EFuzzyInferenceModelParameterToImageData&); // Not implemented.
};

#endif	/* vtkTAG2EFuzzyInferenceModelParameterToImageData_H */
