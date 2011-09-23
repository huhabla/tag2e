# We store the stdout output in a file
sink(file="current_R_summary.txt")

# Rad data
sfs = read.table("current_result.txt", header=TRUE, sep="|")

################################################################################
# Compute linear regression model
sfslm = lm(sfs$n2o ~ 0 + sfs$result)
sfslmsum = summary(sfslm)
sfslmsum
paste("AKAIKE: " , AIC(sfslm))

# Plot to the first page
pdf("current_R_noscale_nointerc_result.pdf")
par(mfrow = c(3, 2))

axlim = c(min(sfs$n2o), max(sfs$n2o))
plot(sfs$n2o ~ sfs$result, xlim=axlim, ylim=axlim, asp="1", 
     main="current result", sub = paste("R squared: ", round(100 * sfslmsum$r.squared)/100, "   AKAIKE: " , round(AIC(sfslm))), 
     xlab="Model result", ylab="n2o Emission")
abline(sfslm, col="red")
abline(0,1, col="grey60", lty="dashed")

plot(sfslm)
dev.set(dev.next())

################################################################################
# Compute linear regression model with sqrt scaled data
sfslmsqrt = lm(sqrt(sfs$n2o) ~ 0 + sqrt(sfs$result))
sfslmsumsqrt = summary(sfslmsqrt)
sfslmsumsqrt
paste("AKAIKE: " , AIC(sfslmsqrt))


# Plot to the second page
pdf("current_R_sqrtscale_nointerc_result.pdf")
par(mfrow = c(3, 2))

axlimsqrt = c(min(sqrt(sfs$n2o)), max(sqrt(sfs$n2o)))
plot(sqrt(sfs$n2o) ~ sqrt(sfs$result), xlim=axlimsqrt, ylim=axlimsqrt, asp="1", 
     main="current result sqrt scaled", sub = paste("R squared: ", round(100 * sfslmsumsqrt$r.squared)/100, "   AKAIKE: " , round(AIC(sfslmsqrt))), 
     xlab="Model result", ylab="n2o Emission")
abline(sfslmsqrt, col="red")
abline(0,1, col="grey60", lty="dashed")

plot(sfslmsqrt)
dev.set(dev.next())

################################################################################
# Compute linear regression model
sfslm = lm(sfs$n2o ~ sfs$result)
sfslmsum = summary(sfslm)
sfslmsum
paste("AKAIKE: " , AIC(sfslm))

# Plot to the first page
pdf("current_R_noscale_result.pdf")
par(mfrow = c(3, 2))

axlim = c(min(sfs$n2o), max(sfs$n2o))
plot(sfs$n2o ~ sfs$result, xlim=axlim, ylim=axlim, asp="1", 
     main="current result", sub = paste("R squared: ", round(100 * sfslmsum$r.squared)/100, "   AKAIKE: " , round(AIC(sfslm))), 
     xlab="Model result", ylab="n2o Emission")
abline(sfslm, col="red")
abline(0,1, col="grey60", lty="dashed")

plot(sfslm)
dev.set(dev.next())

################################################################################
# Compute linear regression model with sqrt scaled data
sfslmsqrt = lm(sqrt(sfs$n2o) ~ sqrt(sfs$result))
sfslmsumsqrt = summary(sfslmsqrt)
sfslmsumsqrt
paste("AKAIKE: " , AIC(sfslmsqrt))

# Plot to the second page
pdf("current_R_sqrtscale_result.pdf")
par(mfrow = c(3, 2))

axlimsqrt = c(min(sqrt(sfs$n2o)), max(sqrt(sfs$n2o)))
plot(sqrt(sfs$n2o) ~ sqrt(sfs$result), xlim=axlimsqrt, ylim=axlimsqrt, asp="1", 
     main="current result sqrt scaled", sub = paste("R squared: ", round(100 * sfslmsumsqrt$r.squared)/100, "   AKAIKE: " , round(AIC(sfslmsqrt))), 
     xlab="Model result", ylab="n2o Emission")
abline(sfslmsqrt, col="red")
abline(0,1, col="grey60", lty="dashed")

plot(sfslmsqrt)
dev.set(dev.next())


###END