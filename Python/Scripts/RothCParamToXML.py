#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Authors: Soeren Gebbert, soeren.gebbert@vti.bund.de
#          Rene Dechow, rene.dechow@vti.bund.de
#
# Copyright:
#
# Johann Heinrich von Thuenen-Institut
# Institut fuer Agrarrelevante Klimaforschung
#
# Phone: +49 (0)531 596 2601
#
# Fax:+49 (0)531 596 2699
#
# Mail: ak@vti.bund.de
#
# Bundesallee 50
# 38116 Braunschweig
# Germany
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# This script is designed to transform RothC calibration parameter
# from an csv file into RothC Model Parameter files
#
# The column names of the csv are hard coded and must be changed
# in case the csv layout changes

from optparse import OptionParser
from datetime import datetime
from vtk import *
import os

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

# What to convert RothC factors:
# temp_response_Fakt1 -> R.a.a1.value
# temp_response_Fakt2 -> R.a.a2.value
# wfp_r_when_dry -> R.b.b1.value
# wfp_r_obere_schwelle -> R.b.b3.value
# mult_Co2_humbio ->  R.x.x1.value
# co2_humbio_f2 -> R.x.x3.value

class Parameter(object):
    """!This class specifies the  XML element,
       XML subelement and the value of a RothC 
       parameter 
    """
    def __init__(self, element, subelement, value):
        self.element = element
        self.subelement = subelement
        self.value = value

def create_parameter_xml(name, value):
    """!We create a RothC parameter object
       with name and value set
    """
    d = vtkXMLDataElement()
    d.SetName(name)
    d.SetIntAttribute("const", 1)
    d.SetDoubleAttribute("max", float(value))
    d.SetDoubleAttribute("min", float(value))
    string = str(value)
    d.SetCharacterData(string, len(string))

    return d

def create_fraction_xml(fraction, num, name, dpm, rpm, hum):
    """!Create a fraction XML element and fill it with 
       data
    """
    frac = vtkXMLDataElement()
    frac.SetName(fraction)
    frac.SetIntAttribute("id", int(num))
    frac.SetAttribute("name", name)

    descr = vtkXMLDataElement()
    descr.SetName("description")
    descr.SetCharacterData(name, len(name))
    frac.AddNestedElement(descr)

    d = create_parameter_xml("DPM", dpm)
    r = create_parameter_xml("RPM", rpm)
    h = create_parameter_xml("HUM", hum)

    frac.AddNestedElement(d)
    frac.AddNestedElement(r)
    frac.AddNestedElement(h)
    # Debug
    # frac.PrintXML(name + str(num) + ".xml")

    return frac

def parse_plant_fractions(root, identifier, content):
    """!Parse the plant parameter
    """
    # Identifier in the text file
    plant_ids = ["DPM_hum_ref","RPM_hum_ref","HUM_hum_ref"]

    plant_names = {}
    keys = ["cerials", "green", "root"]
    plant_names["cerials"] = [name + "_shoot_cer"   for name in plant_ids]
    plant_names["green"]   = [name + "_shoot_green" for name in plant_ids]
    plant_names["root"]    = [name + "_root"  for name in plant_ids]

    plant_xml = root.FindNestedElementWithName("PlantFractions")

    count = 0
    for key in keys:
        count += 1
        values = []
        for i in xrange(len(identifier)):
            if plant_names[key][0] == identifier[i]:
                values.append(content[i])
            if plant_names[key][1] == identifier[i]:
                values.append(content[i])
            if plant_names[key][2] == identifier[i]:
                values.append(content[i])

        if len(values) == 3:
            cer_frac = create_fraction_xml("PlantFraction", count, key, 
                                           values[0], values[1], values[2])    
            plant_xml.AddNestedElement(cer_frac)

def parse_fertilizer_fractions(root, identifier, content):
    """!Parse the fertilizer parameter
    """
    fert_ids = ["DPM_Humif_coeff_ref","RPM_Humif_coeff_ref","HUM_Humif_coeff_ref"]

    count = 0
    # Create an ordered list of prefixes that are used as keys
    keys = [str(i + 1) for i in xrange(24)]

    fert_names = {}
    for key in keys:
        fert_names[key] = [name + "_" + key for name in fert_ids]

    fert_xml = root.FindNestedElementWithName("FertilizerFractions")

    count = 0
    for key in keys:
        count += 1
        values = []
        for i in xrange(len(identifier)):
            names = fert_names[key]
            if names[0] == identifier[i]:
                values.append(content[i])
            if names[1] == identifier[i]:
                values.append(content[i])
            if names[2] == identifier[i]:
                values.append(content[i])

        if len(values) == 3:
            cer_frac = create_fraction_xml("FertilizerFraction", count, key, 
                                           values[0], values[1], values[2])    
            fert_xml.AddNestedElement(cer_frac)

def find_replace_parameter(root, p):
    """!Replace the value in a specific RothC XML parameter object
    """
    element = root.FindNestedElementWithName(p.element)
    subelement = element.FindNestedElementWithName(p.subelement)
    subelement.SetDoubleAttribute("max", p.value)
    subelement.SetDoubleAttribute("min", p.value)
    value = str(p.value)
    # Debug
    # print("Replace value: ", p.subelement, value)
    subelement.SetCharacterData(value, len(value))

def parse_file(filename, RothCParameterIndex):
    """!Parse the RothC calibration parameter file
       and create XML RothC Model files
    """
    input = open(filename, "r").readlines()
    identifier = input[0].split("|")
    dict_list = []
    count = 0
    for line in input[1:]:
        count += 1

        content = line.split("|")
 
        rp = vtkTAG2ERothCModelParameter()
        rp.GenerateXMLFromInternalScheme()
        root = vtkXMLDataElement()
        rp.GetXMLRepresentation(root)

        parse_plant_fractions(root, identifier, content)
        parse_fertilizer_fractions(root, identifier, content)
       
        for i in xrange(len(identifier)):
            if identifier[i] in RothCParameterIndex.keys():
                p = RothCParameterIndex[identifier[i]]
                p.value = float(content[i])
                find_replace_parameter(root, p)

        outfile = "RothCCalibration" + str(count) + ".xml"
        # Write the XML file
        root.PrintXML(outfile)

        # Just for testing and debugging
        #rp = vtkTAG2ERothCModelParameter()
        #rp.SetXMLRepresentation(root)
        #rp.GenerateInternalSchemeFromXML()
        #rp.GenerateXMLFromInternalScheme()
        #rp.SetFileName("check" + outfile)
        #rp.Write()

def main():

    # Identifier in the csv file
    RothCParameterIndex = {}
    RothCParameterIndex["temp_response_Fakt1"] = Parameter("a","a1", 0)
    RothCParameterIndex["temp_response_Fakt2"] = Parameter("a", "a2", 0)
    RothCParameterIndex["wfp_r_when_dry"] = Parameter("b", "b1", 0)
    RothCParameterIndex["wfp_r_obere_schwelle"] = Parameter("b", "b3", 0)
    RothCParameterIndex["mult_Co2_humbio"] = Parameter("x", "x1", 0)
    RothCParameterIndex["co2_humbio_f2"] = Parameter("x", "x3", 0)

    parse_file("RothC_Calibration.csv", RothCParameterIndex)

main()
