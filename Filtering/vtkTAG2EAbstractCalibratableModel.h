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
 * \brief This class is derived from vtkTAG2EAbstractModel and defines additionally 
 * an abstract method which computes an assessment factor of the model.
 * 
 * The assessment factor describes the quality of the model and is used by
 * calibration algorithms like simulated annealing.
 * 
 * Models which must be calibrated should be derived from this class and must
 * implement the the abstract method GetModelAssessmentFactor. The model
 * assessment factor must be 1 or greater. Factors of 1 indicates a model of high quality
 * while factors greater 1 indicates models of lower quality.
 * 
 */

#ifndef vtkTAG2EAbstractCalibratableModel_H
#define	vtkTAG2EAbstractCalibratableModel_H

#include <assert.h>
#include "vtkTAG2EAbstractModel.h"

class vtkTAG2EAbstractCalibratableModel : public vtkTAG2EAbstractModel {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractCalibratableModel, vtkTAG2EAbstractModel);
    
    //!\brief Return the model assessment factor [1, inf[
    virtual double GetModelAssessmentFactor() = 0;
    
protected:
    vtkTAG2EAbstractCalibratableModel();
    ~vtkTAG2EAbstractCalibratableModel();

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *) {
        assert("RequestData must be implemented in a subclass");
        return -1;
    }

private:
    vtkTAG2EAbstractCalibratableModel(const vtkTAG2EAbstractCalibratableModel& orig); // Not implemented.
    void operator=(const vtkTAG2EAbstractCalibratableModel&); // Not implemented.
};

#endif	/* vtkTAG2EAbstractCalibratableModel_H */
