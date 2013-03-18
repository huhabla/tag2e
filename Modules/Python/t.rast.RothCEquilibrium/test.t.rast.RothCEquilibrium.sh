#!/bin/sh

# We need to set a specific region in the
# @preprocess step of this test. 
# The region setting should work for UTM and LL test locations
#g.region s=0 n=80 w=0 e=120 b=0 t=50 res=0.25 res3=10 -p3
g.region s=0 n=80 w=0 e=120 b=0 t=50 res=1 res3=10 -p3

temp=`g.tempfile pid=1 -d` 
prec=`g.tempfile pid=2 -d` 
radi=`g.tempfile pid=3 -d` 
soil=`g.tempfile pid=4 -d` 
resi=`g.tempfile pid=5 -d` 
feti=`g.tempfile pid=6 -d` 

# TEMPERATURE
MONTHS=120

count=0
while [ ${count} -lt ${MONTHS} ] ; do 
    name="temp_${count}"
    echo "${name}" >> "${temp}"
    r.mapcalc --o expr="${name} = rand(10,30)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=temperature_RothC \
    title="RothC mean temperature" descr="RothC mean temperature"
t.register --o -i type=rast input=temperature_RothC file="${temp}" \
    start=2000-01-01 increment="1 months"

# PRECIPITATION

count=0
while [ ${count} -lt ${MONTHS} ] ; do 
    name="prec_${count}"
    echo "${name}" >> "${prec}"
    r.mapcalc --o expr="${name} = rand(0,80)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=precipitation_RothC \
    title="RothC precipitation" descr="RothC precipitation"
t.register --o -i type=rast input=precipitation_RothC file="${prec}" \
    start=2000-01-01 increment="1 months"

# GLOBAL RADIATION

count=0
while [ ${count} -lt ${MONTHS} ] ; do 
    name="radi_${count}"
    echo "${name}" >> "${radi}"
    r.mapcalc --o expr="${name} = rand(10,600)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=radiation_RothC \
    title="RothC radiation" descr="RothC radiation"
t.register --o -i type=rast input=radiation_RothC file="${radi}" \
    start=2000-01-01 increment="1 months"

# SOIL COVER
count=0
while [ ${count} -lt ${MONTHS} ] ; do 
    name="soil_${count}"
    echo "${name}" >> "${soil}"
    r.mapcalc --o expr="${name} = rand(0,1)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=soilCover_RothC \
    title="RothC soil cover" descr="RothC soil cover"
t.register --o -i type=rast input=soilCover_RothC file="${soil}" \
    start=2000-01-01 increment="1 months"

# RESIDUALS
t.rast.mapcalc --o input=temperature_RothC output=residuals_RothC \
    base=residuals nprocs=4 method=equal \
    expr="if(start_month() == 8, rand(2, 4), null())" 
    
t.info residuals_RothC
  
# FERTILIZER
t.rast.mapcalc --o input=temperature_RothC output=fertilizer_RothC \
    base=fertilizer nprocs=4 method=equal \
    expr="if(start_month() == 4 || start_month() == 6, rand(1, 3), null())" \

t.info fertilizer_RothC

# Several needed maps
r.mapcalc --o expr="clay = rand(1,20)"
r.mapcalc --o expr="initialC = 25.0"
r.mapcalc --o expr="residuals = rand(0,15)/10.0"

exit

################################################################################
# Equilibrium run
################################################################################

t.rast.RothCEquilibrium --o temperature=temperature_RothC \
    precipitation=precipitation_RothC radiation=radiation_RothC \
    soilcover=soilCover_RothC claycontent=clay soc=initialC \
    residuals=residuals output=soc1 iterations=20 years=300 \
    dpm=dpm1 rpm=rpm1 hum=hum1 bio=bio1 iom=iom1 resout=res1 \
    ax=0 cx=15  convergence=conv1 squaredresiduals=sqres1

r.info -r soc1
r.info -r dpm1
r.info -r rpm1
r.info -r hum1
r.info -r bio1
r.info -r iom1
r.info -r res1

t.rast.RothCEquilibrium --o temperature=temperature_RothC \
    precipitation=precipitation_RothC radiation=radiation_RothC \
    soilcover=soilCover_RothC claycontent=clay soc=initialC \
    residuals=residuals output=soc2 iterations=20 years=300 \
    dpm=dpm2 rpm=rpm2 hum=hum2 bio=bio2 iom=iom2 resout=res2 \
    ax=0 cx=15  convergence=conv2 squaredresiduals=sqres2

r.info -r soc2
r.info -r dpm2
r.info -r rpm2
r.info -r hum2
r.info -r bio2
r.info -r iom2
r.info -r res2

t.rast.RothCEquilibrium --o temperature=temperature_RothC \
    precipitation=precipitation_RothC radiation=radiation_RothC \
    soilcover=soilCover_RothC claycontent=clay soc=initialC \
    residuals=residuals output=soc3 iterations=20 years=300 \
    dpm=dpm3 rpm=rpm3 hum=hum3 bio=bio3 iom=iom3 resout=res3 \
    ax=0 cx=15  convergence=conv3 squaredresiduals=sqres3

r.info -r soc3
r.info -r dpm3
r.info -r rpm3
r.info -r hum3
r.info -r bio3
r.info -r iom3
r.info -r res3

################################################################################
# Equilibrium run with time series
################################################################################

t.rast.RothCEquilibrium --o temperature=temperature_RothC \
    precipitation=precipitation_RothC radiation=radiation_RothC \
    soilcover=soilCover_RothC claycontent=clay soc=initialC \
    residuals=residuals output=soc4 iterations=8 years=300 \
    dpm=dpm4 rpm=rpm4 hum=hum4 bio=bio4 iom=iom4 resout=res4 \
    mtemperature=temperature_RothC \
    mprecipitation=precipitation_RothC mradiation=radiation_RothC \
    msoilcover=soilCover_RothC mresiduals=residuals_RothC \
    mfertilizer=fertilizer_RothC ax=0 cx=15 convergence=conv4 \
     squaredresiduals=sqres4

r.info -r soc4
r.info -r dpm4
r.info -r rpm4
r.info -r hum4
r.info -r bio4
r.info -r iom4
r.info -r res4
r.info -r sqres4

t.rast.RothCEquilibrium --o temperature=temperature_RothC \
    precipitation=precipitation_RothC radiation=radiation_RothC \
    soilcover=soilCover_RothC claycontent=clay soc=initialC \
    residuals=residuals output=soc5 iterations=8 years=300 \
    dpm=dpm5 rpm=rpm5 hum=hum5 bio=bio5 iom=iom5 resout=res5 \
    mtemperature=temperature_RothC \
    mprecipitation=precipitation_RothC mradiation=radiation_RothC \
    msoilcover=soilCover_RothC mresiduals=residuals_RothC \
    mfertilizer=fertilizer_RothC ax=0 cx=10 convergence=conv5 \
     squaredresiduals=sqres5

r.info -r soc5
r.info -r dpm5
r.info -r rpm5
r.info -r hum5
r.info -r bio5
r.info -r iom5
r.info -r res5
r.info -r sqres5

t.rast.RothCEquilibrium --o temperature=temperature_RothC \
    precipitation=precipitation_RothC radiation=radiation_RothC \
    soilcover=soilCover_RothC claycontent=clay soc=initialC \
    residuals=residuals output=soc6 iterations=8 years=300 \
    dpm=dpm6 rpm=rpm6 hum=hum6 bio=bio6 iom=iom6 resout=res6 \
    mtemperature=temperature_RothC \
    mprecipitation=precipitation_RothC mradiation=radiation_RothC \
    msoilcover=soilCover_RothC mresiduals=residuals_RothC \
    mfertilizer=fertilizer_RothC ax=0 cx=5 convergence=conv6 \
     squaredresiduals=sqres6

r.info -r soc6
r.info -r dpm6
r.info -r rpm6
r.info -r hum6
r.info -r bio6
r.info -r iom6
r.info -r res6
r.info -r sqres6

exit


# @postprocess
t.remove type=strds input=temperature_RothC,precipitation_RothC,radiation_RothC,soilCover_RothC,residuals_RothC,fertilizer_RothC
t.unregister type=rast file="${temp}"
for name in `cat "${temp}"` ; do
    g.remove rast=${name}
done
t.unregister type=rast file="${prec}"
for name in `cat "${prec}"` ; do
    g.remove rast=${name}
done
t.unregister type=rast file="${radi}"
for name in `cat "${radi}"` ; do
    g.remove rast=${name}
done
t.unregister type=rast file="${soil}"
for name in `cat "${soil}"` ; do
    g.remove rast=${name}
done
g.remove rast=soc,dpm,rpm,hum,bio,iom,res
