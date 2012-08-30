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
 * \brief This class is designed to join several datasets into
 * a single dataset. The idea is to use the structure of the fist input
 * and simply add the data arrays of the following inputs to it. Hence,
 * all provided inputs must have identical structures.
 * 
 * This class will only check that the number of points and cells
 * is equal between the datasets. The topology is and spatial location
 * will not checked.
 * 
 * In case arrays with the same names appear in the input datasets the last
 * found array will be used.
 *
 * Use this filter as follows (Python):
 * 
 * dsjoin = vtkTAG2EADataSetJoinFilter()
 * 
 * dsjoin.AddInput(ds1)
 * dsjoin.AddInput(ds2)
 * dsjoin.AddInput(ds3)
 * dsjoin.Update()
 * 
 */

#ifndef vtkTAG2EDataSetJoinFilter_H
#define	vtkTAG2EDataSetJoinFilter_H

#include <vtkDataSetAlgorithm.h>

class vtkTAG2EDataSetJoinFilter : public vtkDataSetAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2EDataSetJoinFilter, vtkDataSetAlgorithm);
    static vtkTAG2EDataSetJoinFilter *New();

protected:
    vtkTAG2EDataSetJoinFilter();
    ~vtkTAG2EDataSetJoinFilter();
    
    virtual int RequestData(vtkInformation *, vtkInformationVector **,
    		vtkInformationVector *);
    virtual int FillInputPortInformation(int port, vtkInformation* info);
    virtual int FillOutputPortInformation(int port, vtkInformation* info);

private:
    vtkTAG2EDataSetJoinFilter(const vtkTAG2EDataSetJoinFilter& orig); // Not implemented.
    void operator=(const vtkTAG2EDataSetJoinFilter&); // Not implemented.
};

#endif	/* vtkTAG2EDataSetJoinFilter_H */
