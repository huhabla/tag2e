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
 * \brief RothC Parameter class
 *
 */

#ifndef vtkTAG2ERothCModelParameter_H
#define	vtkTAG2ERothCModelParameter_H

#include <vtkObject.h>
#include "vtkTAG2EAbstractCalibratableModelParameter.h"
#include <vector>
#include <string>

/**
 * \brief Parameter for calibration
 *
 * Set constant = True to avoid calibration
 */
class RothCParameter
{
public:
  bool constant;
  double min;
  double max;
  double value;
};

/**
 * \brief RothC parameter a from (1 - e^(-abckt))
 *
 * a is the rate modifying factor for temperature
 *
 * a = a1 / (1 + e^(a2/(T + a3)))
 *
 * Default:
 *
 * a1 = 47.9
 * a2 = 106.0
 * a3 = 18.3
 *
 * T: mean temperature
 *
 */
class RothCParameterA
{
public:
  RothCParameter a1;
  RothCParameter a2;
  RothCParameter a3;
};

/**
 * \brief RothC parameter b from (1 - e^(-abckt))
 *
 * b is the rate modifying factor for moisture
 *
 * maxTSMD = -(b1 + b2 * Clay - b3 * Clay^2)
 *
 * b = b1 + (b2 - b1) * (maxTSMD - accTSMD)/(maxTSMD - b3 * maxTSMD)
 *
 * Default:
 *
 * b1 = 0.2
 * b2 = 1.0
 * b3 = 0.444
 */
class RothCParameterB
{
public:

  RothCParameter b1;
  RothCParameter b2;
  RothCParameter b3;

};

/**
 * \brief RothC parameter c from (1 - e^(-abckt))
 *
 * c is the soil cover rate modifying factor
 *
 * if soilcover == True:
 *   c = c1
 * else:
 *   c = c2
 *
 * Default:
 *
 * c1 = 0.6
 * c2 = 1.0
 */
class RothCParameterC
{
public:
  RothCParameter c1;
  RothCParameter c2;
};

/**
 * \brief RothC parameter k from (1 - e^(-abckt))
 *
 * k is the decomposition rate constant for that compartment
 *
 * Compartments are :
 *   DPM - Decomposable Plant Material = 10.2
 *   RPM - Resistant Plant Material    = 0.3
 *   BIO - Microbial Biomass           = 0.66
 *   HUM - Humified organic matter     = 0.02
 *
 */
class RothCParameterK
{
public:
  RothCParameter DPM;
  RothCParameter RPM;
  RothCParameter BIO;
  RothCParameter HUM;
};

/**
 * \brief The CO2/(BIO + HUM) ratio
 *
 * x = x1 * (x2 + x3 * exp(x4 * Clay))
 *
 * Default:
 *   x1 = 1.67
 *   x2 = 1.85
 *   x3 = 1.60
 *   x4 = -0.0786
 */

class RothCParameterX
{
public:
  RothCParameter x1;
  RothCParameter x2;
  RothCParameter x3;
  RothCParameter x4;
};

/**
 * \brief These are plant and organic fertilization specific
 * fractions in %
 *
 * Examples:
 *
 * most crops and improved grass lands:
 *   DPM = 59
 *   RPM = 41
 *
 * tropical woodland:
 *   DPM = 20
 *   RPM = 80
 *
 * Farm Yard Manure:
 *   DPM = 49
 *   RPM = 49
 *   HUM = 2
 *
 */
class RothCParameterFraction
{
public:
  std::string name;
  std::string description;
  RothCParameter DPM;
  RothCParameter RPM;
  RothCParameter HUM;
};

/**
 * Parmeter of the RothC model: A model for the turnover of carbon in soil
 *
 */
class RothC
{
public:
  RothCParameterA a;
  RothCParameterB b;
  RothCParameterC c;
  RothCParameterK k;
  RothCParameterX x;
  std::vector<RothCParameterFraction*> PlantFractions;
  std::vector<RothCParameterFraction*> FertilizerFractions;
};

class vtkXMLDataElement;

class vtkTAG2ERothCModelParameter: public vtkTAG2EAbstractCalibratableModelParameter
{
public:
vtkTypeRevisionMacro(vtkTAG2ERothCModelParameter,
    vtkTAG2EAbstractCalibratableModelParameter);

  void PrintSelf(ostream& os, vtkIndent indent)
  {
    ;
  }
  static vtkTAG2ERothCModelParameter *New();

  /**
   * \brief Use the XML parameter description that has be already read in or
   *  was set as XMLRoot to generate
   *  its internal representation that is based on nested
   *  trivial classes for fast read access
   */
  virtual bool GenerateInternalSchemeFromXML();
  /**
   * \brief Transform the internal parameter representation into its XML
   *  equivalent
   */
  virtual bool GenerateXMLFromInternalScheme();

  //BTX
  RothC &GetInternalScheme()
  {
    return this->R;
  }
  //ETX

protected:

  vtkTAG2ERothCModelParameter();
  ~vtkTAG2ERothCModelParameter();

  vtkXMLDataElement *RothCParameterFractionToXML(RothCParameterFraction *p,
      const char *name, int id);
  vtkXMLDataElement *RothCParameterToXML(RothCParameter &p, const char *name);
  bool ParseRothCParameter(vtkXMLDataElement *XMLRothC, RothCParameter &p);
  virtual bool CreateParameterIndex();
  virtual bool SetParameter(unsigned int index, double value);

  // BTX
  RothC R;
  // ETX

private:
  vtkTAG2ERothCModelParameter(const vtkTAG2ERothCModelParameter& orig);
  void operator=(const vtkTAG2ERothCModelParameter&); // Not implemented.
};

#endif	/* vtkTAG2ERothCModelParameter_H */
