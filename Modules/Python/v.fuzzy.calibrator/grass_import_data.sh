#!/bin/sh

# If you want square root scale for n2o execute the following R script
# SFSDataset = read.table(file="SFSDataset.csv", header=TRUE, sep=",")
# copySFS = SFSDataset
# copySFS$n2o = sqrt(SFSDataset$n2o)
# write.table(copySFS, file="SFSDataset_log.csv", row.names = FALSE, sep=",")

v.in.ascii --o input=SFSDataset.csv output=n2o_emission_param fs=, skip=1 x=2 y=1 columns='y double precision, x double precision,n2o double precision,clay double precision,silt double precision,sand double precision,bd double precision,soc double precision,noc double precision,ph double precision,croptype double precision,Pwin_before double precision,Pspr_before double precision,Psum_before double precision,Paut_before double precision,Pwin double precision,Pspr double precision,Psum double precision,Paut double precision,Twin_before double precision,Tspr_before double precision,Tsum_before double precision,Taut_before double precision,Twin double precision,Tspr double precision,Tsum double precision,Taut double precision,ferttype double precision,fertN double precision,
NO3  double precision, NH4 double precision'

v.in.ascii --o input=SFSDataset_log.csv output=n2o_emission_param_log fs=, skip=1 x=2 y=1 columns='y double precision, x double precision,n2o double precision,clay double precision,silt double precision,sand double precision,bd double precision,soc double precision,noc double precision,ph double precision,croptype double precision,Pwin_before double precision,Pspr_before double precision,Psum_before double precision,Paut_before double precision,Pwin double precision,Pspr double precision,Psum double precision,Paut double precision,Twin_before double precision,Tspr_before double precision,Tsum_before double precision,Taut_before double precision,Twin double precision,Tspr double precision,Tsum double precision,Taut double precision,ferttype double precision,fertN double precision,
NO3  double precision, NH4 double precision'

