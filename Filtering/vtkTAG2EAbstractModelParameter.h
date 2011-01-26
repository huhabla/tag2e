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
 * \brief This abstract class is the base class for all classes which define 
 * specific model parameter.
 *
 * Model parameter are textual and numerical description of satistical or 
 * numerical formulars. A model is the generalization of a statistical or
 * numerical method for spatio-temporal data processing, like linear or 
 * non-linear regression. The specific parameter of these models are desribed in this
 * class using the XML.
 * 
 * Example:
 * A concrete model class implements a generalized linear regression model. Because 
 * there are so many different specific lineare regression models the parameter 
 * of the generalized linear regression must be defined somewhere, i.e: temp = 0.5 + 3prec.
 * 
 * In this case a simple linear regression model which connects the precipitation
 * with the temperatur specifies a concrete linear regression model. 
 * The parameter "temp", "0.5", "3" and "prec" are specified in a subclass of 
 * this class using XML elements and attributes to describe the model parameter.
 *  
 * Because the handling of the XML description is similar in each subclass several
 * methods are implemented for convenience in this base class. So you can 
 * specify the input/output filename, read and write XML files and return the 
 * content as vtkXMLDataElement.
 * 
 */

#ifndef vtkTAG2EAbstractModelParameter_H
#define	vtkTAG2EAbstractModelParameter_H

#include <vtkObject.h>
#include <vtkXMLDataElement.h>
#include <assert.h>
#include "vtkObject.h"

class vtkKeyValueMap;

class vtkTAG2EAbstractModelParameter : public vtkObject {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractModelParameter, vtkObject);

    void PrintSelf(ostream& os, vtkIndent indent) {
        ;
    }
    
    static vtkTAG2EAbstractModelParameter *New();
    
    //!\brief Read the XML file with model parameter definitions specified by FileName
    virtual bool Read();
    //!\brief Write the XML file with model parameter definitions as file specified by FileName
    virtual void Write();
    //\brief filename of the XML model parameter definitions which should be read or written
    vtkSetStringMacro(FileName);
    //\brief filename of the XML model parameter definitions which should be read or written
    vtkGetStringMacro(FileName);
    //!\brief Get the XML representation of the model parameter definitions
    vtkGetObjectMacro(XMLRoot, vtkXMLDataElement);
    
protected:
    
    char *FileName;
    vtkXMLDataElement *XMLRoot;
        
    vtkTAG2EAbstractModelParameter();
    virtual ~vtkTAG2EAbstractModelParameter();
private:
    vtkTAG2EAbstractModelParameter(const vtkTAG2EAbstractModelParameter& orig);
    void operator=(const vtkTAG2EAbstractModelParameter&); // Not implemented.
};

#endif	/* vtkTAG2EAbstractModelParameter_H */
