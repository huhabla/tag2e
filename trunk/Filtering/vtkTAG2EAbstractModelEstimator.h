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
 * \brief This is the abstract base class for algorithms which are used to estimate 
 * statistical models like linear or non-linear regression.
 * 
 * The model and the model parameter must be set as well as the input data.
 * 
 */

#ifndef vtkTAG2EAbstractModelEstimator_H
#define	vtkTAG2EAbstractModelEstimator_H

#include <vtkTemporalDataSetAlgorithm.h>
#include <assert.h>
#include "vtkTAG2EAbstractModelParameter.h"
#include "vtkTAG2EAbstractModel.h"

class vtkTAG2EAbstractModelEstimator : public vtkTemporalDataSetAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractModelEstimator, vtkTemporalDataSetAlgorithm);
    static vtkTAG2EAbstractModelEstimator *New(); 
    
    vtkSetObjectMacro(Model, vtkTAG2EAbstractModel);
    vtkGetObjectMacro(Model, vtkTAG2EAbstractModel);
    
    vtkSetObjectMacro(ModelParameter, vtkTAG2EAbstractModelParameter);
    vtkGetObjectMacro(ModelParameter, vtkTAG2EAbstractModelParameter);
    
protected:
    vtkTAG2EAbstractModelEstimator();
    ~vtkTAG2EAbstractModelEstimator();

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *) {
        assert("RequestData must be implemented in a subclass");
    }

    vtkTAG2EAbstractModel *Model;
    vtkTAG2EAbstractModelParameter *ModelParameter;

private:
    vtkTAG2EAbstractModelEstimator(const vtkTAG2EAbstractModelEstimator& orig); // Not implemented.
    void operator=(const vtkTAG2EAbstractModelEstimator&); // Not implemented.
};

#endif	/* vtkTAG2EAbstractModelEstimator */
