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
#include "vtkTAG2EModelParameterCollection.h"

class vtkTAG2EAbstractModelVariationAnalyser : public vtkTemporalDataSetAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractModelVariationAnalyser, vtkTemporalDataSetAlgorithm);
    static vtkTAG2EAbstractModelVariationAnalyser *New(); 
    
    //!\brief Set the model which should be analyzed
    vtkSetObjectMacro(Model, vtkTAG2EAbstractModel);
    vtkGetObjectMacro(Model, vtkTAG2EAbstractModel);

protected:
    vtkTAG2EAbstractModelVariationAnalyser();
    ~vtkTAG2EAbstractModelVariationAnalyser();

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *) {
        assert("RequestData must be implemented in a subclass");
    }

    vtkTAG2EAbstractModel *Model;

private:
    vtkTAG2EAbstractModelVariationAnalyser(const vtkTAG2EAbstractModelVariationAnalyser& orig); // Not implemented.
    void operator=(const vtkTAG2EAbstractModelVariationAnalyser&); // Not implemented.
};

#endif	/* vtkTAG2EAbstractModelVariationAnalyser_H */
