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

#ifndef VTKTAG2ESIMULATEDANNEALINGFILTER_H
#define	VTKTAG2ESIMULATEDANNEALINGFILTER_H

#include <vtkDataSetAlgorithm.h>
#include <assert.h>
#include "vtkTAG2EAbstractCalibrationParameter.h"
#include "vtkTAG2ECalibrationParameterCollection.h"

class vtkTAG2ESimulatedAnnealingFilter : public vtkDataSetAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2ESimulatedAnnealingFilter, vtkDataSetAlgorithm);
    static vtkTAG2ESimulatedAnnealingFilter *New(); 
protected:
    vtkTAG2ESimulatedAnnealingFilter();
    virtual ~vtkTAG2ESimulatedAnnealingFilter();
private:
    vtkTAG2ESimulatedAnnealingFilter(const vtkTAG2ESimulatedAnnealingFilter& orig);

};

#endif	/* VTKTAG2ESIMULATEDANNEALINGFILTER_H */

