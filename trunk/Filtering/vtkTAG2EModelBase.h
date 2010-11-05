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

#ifndef VTKTAG2EMODELBASE_H
#define	VTKTAG2EMODELBASE_H

#include <vtkDataSetAlgorithm.h>
#include <assert.h>
#include "vtkTAG2EAbstractCalibrationParameter.h"
#include "vtkTAG2ECalibrationParameterCollection.h"

class vtkTAG2EModelBase : public vtkDataSetAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2EModelBase, vtkDataSetAlgorithm);
    static vtkTAG2EModelBase *New(); 
    
    vtkSetObjectMacro(ParameterCollection, vtkTAG2ECalibrationParameterCollection);
    vtkGetObjectMacro(ParameterCollection, vtkTAG2ECalibrationParameterCollection);

protected:
    vtkTAG2EModelBase();
    ~vtkTAG2EModelBase();

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *) {
        assert("RequestData must be implemented in a subclass");
    }

    vtkTAG2ECalibrationParameterCollection *ParameterCollection;

private:
    vtkTAG2EModelBase(const vtkTAG2EModelBase& orig); // Not implemented.
    void operator=(const vtkTAG2EModelBase&); // Not implemented.
};

#endif	/* VTKTAG2EMODELBASE_H */
