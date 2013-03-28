# public methods

#"/home/gbt/Divers/R_prisma/tmpmHDOipnetzob_sally.output"
executePrisma = function(fsallyPath) {
  source("resources/static/netzob_plugins/ASAPClustering/libs/PRISMA/R/prisma.R")
  source("resources/static/netzob_plugins/ASAPClustering/libs/PRISMA/R/dimensionEstimation.R")
  source("resources/static/netzob_plugins/ASAPClustering/libs/PRISMA/R/matrixFactorization.R")

  data = loadPrismaData(fsallyPath)
  dim = estimateDimension(data)
  nmf = prismaNMF(data, dim)
  result = t(as.matrix(nmf$C[, nmf$remapper]))
  return(result)
}
