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

import os
from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeTemporalPython import *
from libvtkGRASSBridgeCommonPython import *

################################################################################
################################################################################
################################################################################

# This script converts the FIS format into the tag2e XML format

# Beschreibung des Reneschen Fuzzy Modells und der Eingabedateien
cropFactors = []
cropFactors.append("fert_N") # 1
cropFactors.append("pH") # 2
cropFactors.append("precip_yearly") # 3
cropFactors.append("temp_mean_yearly") # 4
cropFactors.append("sand") # 5
cropFactors.append("silt") # 6
cropFactors.append("clay") # 7
cropFactors.append("bulk_density") # 8
cropFactors.append("soil_c") # 9
cropFactors.append("total_N") # 10
cropFactors.append("precip_summer") # 11
cropFactors.append("precip_fall") # 12
cropFactors.append("temp_winter_last_year") # 13

grassFactors = []
grassFactors.append("fert_N") # 1
grassFactors.append("clay") # 2
grassFactors.append("sand") # 3
grassFactors.append("bulk_density") # 4
grassFactors.append("soil_c") # 5
grassFactors.append("total_N") # 6
grassFactors.append("pH") # 7
grassFactors.append("rain") # 8
grassFactors.append("rain") # 9
grassFactors.append("rain") # 10
grassFactors.append("rain") # 11
grassFactors.append("temp_winter") # 12
grassFactors.append("temp_spring") # 13
grassFactors.append("temp_summer") # 14
grassFactors.append("temp_fall") # 15
grassFactors.append("precip") # 16


# Konfigurationsdatei
# 1. Eintrag: Anzahl potentieller Faktoren + Konklusion (15 + 1)
# 2. Eintrag: Anzahl der verwendeten Modellfaktoren + Konklusion (3 + 1)
config = "config"

# Faktor Fuzzy-Set Layout
# Tabellenlayout:
# Pro Zeile ein Faktor
# Die letzte Zeile codiert die Conclusion fuer (concl_dual_27_10.fuz)
# Spalten:
# 1. Fuzzy Shape 
# 2. Anzahl der Fuzzy Sets
# 3. Minimaler Wert
# 4. Maximaler Wert
# 5. ?
# 6. ?
# 7. ?
# 8. ?
# 9. ?
#10. ?
fact_dual = "fakt_dual"

# Faktor Kodierung 
# Das layout dieser Datei haengt von fakt_dual ab
# Kodiert die Zeilen in fakt_dual, und beschreibt die Position der
# verwendeten Faktoren, Index startet bei 0 -> Erste Zeile in fakt_dual
facto = "facto"

# Fuzzysets
# Tabellenlayout:
# Spalten:
# 1. Id's der Faktoren, beginnend bei 1
#    Die erste Zeile eines Faktors ist das linke Fuzzy Set
#    Die Letzte Zeile eines Faktors das rechte Fuzzy Set
#    Fuzzy Sets dazwischen wandern mit zunehmender Zeilennummer nach rechts
# 2. Fuzzy Set Center in normierten Kooridnaten
# 3. Offset linke Seite normiert, oder 222222 fuer unendlich
# 4. Offset rechte Seite normiert, oder 222222 fuer unendlich
# Nur fuer Kalibrierung wichtig:
# 5. Fixiert die Position des Centers bei der Kalibrierung (0 nicht fixiert, 1 fixiert)
# 6. Expertenwissen, 0 -> nix, 1 - n Eingrenzungsparameter
fuzzy_sets = "fuzzy_multmat"


# Wichtungsfaktoren fuer Pflanzengruppen im Crop-Modell
# Kann bei Grassland ignoriert werden
# Je Zeile eine Pflanzengruppe, Reihenfolge ist fest
# 1. fallow / Brache
# 2. roots / Hackfruechte
# 3. cereals / Getreide
# 4. rap / Raps
# 5. vegtables / Gemuese
# 6. other
# 7. dummy
crop_weight = "cropspez_fakt"

# Wichtungsfaktoren fuer die Duengung
# Pro Zeile ein Duengungstyp
# 1. ?
# ...
#20. ?
fert_weight = "fertspez_fakt"

# Wichtungsfaktorswitch, schaltet die Pflanzengruppen dun Duengungswichtung ein
# Achtung Endung ".mda"
# 1. Zeile: Integer (0 = False oder 1 = True) fuer Pflanzengrupen 
# 2. Zeile: Integer (0 = False oder 1 = True) fuer Duengung
weight_switch = "fuzmodi"

# Responses
# Tabellenlayout:
# Pro Zeile eine Rule-Response, Reihenfolge ergibt sich aus der
# Faktorfolge und der Kombination der Fuzzy Sets -> kompatibel zu XML
# Spalten:
# 1. Normierte Response, min und max aus fakt_dual* letzte Zeile auslesen
# 2. ? Fixierung der Response (nur Kalibirierung)
# 3. Ganzzahlen, bestimmen welche Responses gleiche Werte haben,  (nur Kalibrierung)
# 4. Varianzen der Unsicherheit einer Response (normalverteilt)
response = "concl_dual"


################################################################################
################################################################################
################################################################################

# Return number of factors
def get_number_of_factors(id):
    global config
    file = open(config + id + ".fuz", "r")
    lines = file.readlines()
    file.close()

    n = int(lines[1])
    return n - 1

################################################################################
################################################################################
################################################################################

# Return factor ids
def get_factor_ids(id):
    global facto
    file = open(facto + id + ".fuz", "r")
    lines = file.readlines()
    file.close()
    
    ids = []
    for line in lines:
        ids.append(int(line))

    return ids

################################################################################
################################################################################
################################################################################

# Create fuzzy set
def create_fuzzy_set(id, num, numfs, min, max):

    global fuzzy_sets
    file = open(fuzzy_sets + id + ".fuz", "r")
    lines = file.readlines()
    file.close()
    
    fslist = []

    count = 1
    for line in lines:
        # For each line we create a fuzzy set
        fs = vtkXMLDataElement()
        fs.SetName("FuzzySet")
        fs.SetAttribute("type", "Triangular")
        fs.SetIntAttribute("priority", 0)
        fs.SetIntAttribute("const", 0)

        tri = vtkXMLDataElement()
        tri.SetName("Triangular")

        data = line.split("\t")
        fid = int(float(data[0]))
        center = float(data[1])
        left = float(data[2])
        right = float(data[3])

        if int(left) == 222222:
            left = 999999
        else:
            left = abs((max - min)*left)

        if int(right) == 222222:
            right = 999999
        else:
            right = abs((max - min)*right)

        center = min + (max - min)*center

        tri.SetDoubleAttribute("left",   left)
        tri.SetDoubleAttribute("center", center)
        tri.SetDoubleAttribute("right",  right)
        fs.AddNestedElement(tri)

        if fid == num:
            print "  Fuzzy Set %i center %g left %g right %g" % (fid, center, left, right)
            # Left
            if count == 1:
                fs.SetAttribute("position", "left")
            # Right
            elif count == numfs:
                fs.SetAttribute("position", "right")
            # Intermediate
            else:
                fs.SetAttribute("position", "intermediate")

            fslist.append(fs)
            count += 1

        
    return fslist    
 
################################################################################
################################################################################
################################################################################
      
# Create factors
def create_factors(id, type="crop"):
    fnum = get_number_of_factors(id)
    ids = get_factor_ids(id)
    print "Factors:", fnum
    print "Ids:", ids

    global fact_dual
    file = open(fact_dual + id + ".fuz", "r")
    lines = file.readlines()
    file.close()
    
    factlist = []

    for num in ids:
        line = lines[num]
        data = line.split("\t")
        shape = int(float(data[0]))
        numfs = int(float(data[1]))
        min = float(data[2])
        max = float(data[3])

        global cropFactors
        global grassFactors

        if type == "crop":
            factorName = cropFactors[num]
        else:
            factorName = grassFactors[num]
        fss = vtkXMLDataElement()

        print "Factor %s min %g max %g" % (factorName, min, max)

        fss.SetName("Factor")
        fss.SetIntAttribute("portId", 0)
        fss.SetAttribute("name", factorName)
        fss.SetDoubleAttribute("min", min)
        fss.SetDoubleAttribute("max",  max)

        if type == "crop":
            fsets = create_fuzzy_set(id, num, numfs, min, max)
        else:
            fsets = create_fuzzy_set(id, num + 1, numfs, min, max)
        for fs in fsets:
            fss.AddNestedElement(fs)

        factlist.append(fss)

    return factlist    

################################################################################
################################################################################
################################################################################

# Create the response XML object
def create_responses(id):

    global fact_dual
    global response

    print "FIS " + id

    file = open(fact_dual + id + ".fuz", "r")
    lines = file.readlines()
    file.close()

    data = lines[-1].split("\t")
 
    min = float(data[2])
    max = float(data[3])

    print "Resopne min", min, "max", max

    file = open(response + id + ".fuz", "r")
    lines = file.readlines()
    file.close()
 
    # Responses
    resp = vtkXMLDataElement()
    resp.SetName("Responses")
    resp.SetDoubleAttribute("min", min)
    resp.SetDoubleAttribute("max", max)

    count = 0
    for line in lines:
        data = line.split("\t")
        value = float(data[0])
        value = min + (max - min)*value
        print "Response number", count, "value:", value
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(value), 8)

        resp.AddNestedElement(rval)
        count  += 1

    return resp

################################################################################
################################################################################
################################################################################

def main(id, type):
    # Create the root XML elements
    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")
    resp = create_responses(id)
    factlist = create_factors(id, type)
    for fact in factlist:
        fuzzyRoot.AddNestedElement(fact)

    fuzzyRoot.AddNestedElement(resp)
    fuzzyRoot.SetAttribute("name", "Fuzzy_model" + id)
    fuzzyRoot.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
    fuzzyRoot.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    fuzzyRoot.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
    fuzzyRoot.PrintXML("Fuzzy_model" + id + ".xml")

################################################################################
################################################################################
################################################################################

if __name__ == "__main__":

    # Set these variables to identify the fuzzy text files
    type = "grass"
    num = 50
    identifier = "_27_"

    # Create the input ids
    for i in range(num):
        id = identifier + str(i + 1)
        print id
        # Convert the data into the tag2e XML format
        main(id, type)


