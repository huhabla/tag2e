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
 * \brief 
 * 
 */

#ifndef vtkTAG2ERSpaceTimeModel_H
#define	vtkTAG2ERSpaceTimeModel_H

#include "vtkTAG2EAbstractModel.h"

class vtkDoubleArray;
class vtkStringArray;
class vtkIntArray;
class vtkRInterfaceSpaceTime;

class vtkTAG2ERSpaceTimeModel : public vtkTAG2EAbstractModel {
public:
    vtkTypeRevisionMacro(vtkTAG2ERSpaceTimeModel, vtkTAG2EAbstractModel);
    void PrintSelf(ostream& os, vtkIndent indent) ;   
    static vtkTAG2ERSpaceTimeModel *New();

    vtkSetStringMacro(StartDate);
    vtkGetStringMacro(StartDate);
    
  //!\brief Set the string which defines the coordiante reference system in proj4 format. This tring will be assigned
  //! to the created spatial objects in R.
  vtkSetStringMacro(Proj4String);
  //!\brief The string which defines the coordiante reference system in proj4 format
  vtkGetStringMacro(Proj4String);

protected:
    vtkTAG2ERSpaceTimeModel();
    ~vtkTAG2ERSpaceTimeModel();

    vtkSetStringMacro(RString);
    vtkGetStringMacro(RString);

    vtkSetStringMacro(RVariable);
    vtkGetStringMacro(RVariable);

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
    virtual int FillInputPortInformation(int port, vtkInformation* info);
    virtual int RequestUpdateExtent(vtkInformation *, vtkInformationVector **, vtkInformationVector *);

    virtual bool BuildArrays();

    vtkStringArray *InputArrayNames;
    vtkStringArray *OutputArrayNames;
    char *RString;
    char *RVariable;
    char *StartDate;
    vtkRInterfaceSpaceTime *RInterface;
    char *Proj4String;
    
private:
    vtkTAG2ERSpaceTimeModel(const vtkTAG2ERSpaceTimeModel& orig); // Not implemented.
    void operator=(const vtkTAG2ERSpaceTimeModel&); // Not implemented.
};

#endif	/* vtkTAG2ERSpaceTimeModel_H */
