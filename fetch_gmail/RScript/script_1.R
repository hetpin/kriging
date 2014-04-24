library(sp)
library(gstat)
d <- read.csv('C:/xampp/htdocs/firer/fetch_gmail/RScript/elev.csv')
e <- na.omit(d)
coordinates(e) <- ~ x+y
bubble(e, zcol='elev', fill=FALSE, do.sqrt=FALSE, maxsize=2)
x.range <- as.integer(range(e@coords[,1]))
y.range <- as.integer(range(e@coords[,2]))
grd <- expand.grid(x=seq(from=x.range[1], to=x.range[2], by=500), y=seq(from=y.range[1], to=y.range[2], by=500) )
coordinates(grd) <- ~ x+y
gridded(grd) <- TRUE
plot(grd, cex=0.5)
points(e, pch=1, col='red', cex=0.7)
title("Interpolation Grid and Sample Points")
fileConn<-file("C:/xampp/htdocs/firer/fetch_gmail/RScript/output.txt")
writeLines(c("Hello","World"), fileConn)
close(fileConn)