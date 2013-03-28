# public methods
estimateDimension = function(prismaData, alpha=0.05, nScrambleSamples=NULL) {
  N = length(prismaData$remapper)
  pca = prismaDuplicatePCA(prismaData)
  remapper = prismaData$remapper
  if (!is.null(nScrambleSamples)) {
    remapper = sample(remapper, nScrambleSamples)
  }
  spca = scramblePCA(scrambleFeature(prismaData$data[, remapper]))
  nVal = min(c(length(pca$pca$sdev), length(spca$pca$sdev)))
  # Bonferroni correction:
  alpha = alpha / nVal

  calcConfidence = function(sdev) {
    v = sdev^2
    tau = sqrt(2/(N - 1))
    z = qnorm(1-alpha/2)
    d1 = sqrt(1 + tau * z)
    d2 = sqrt(1 - tau * z)
    conf = cbind(v, v / d1, v / d2)
    return(conf)
  }
  cNorm = calcConfidence(pca$pca$sdev[1:nVal])
  sNorm = calcConfidence(spca$pca$sdev[1:nVal])
  data = data.frame(rbind(cbind(1:nVal, cNorm), cbind(1:nVal, sNorm)), rep(c("norm", "scramble"), c(nVal, nVal)), row.names=as.character(1:(2*nVal)))
  colnames(data) = c("x", "var", "low", "up", "class")

  norm = data$low[data$class == "norm"]
  scramble = data$up[data$class == "scramble"]
  dim = 2 * (match(TRUE, norm <= scramble) - 1)

  ret = list(data=data, dim=dim, pca=pca)
  class(ret) = "prismaDimension"
  return(ret)
}

print.prismaDimension = function(x, ...) {
  cat("Estimated data dimension for positive matrix factorization via simulated noise level:", x$dim, "\n")
}

plot.prismaDimension = function(x, ...) {
	dimData=x
  require(ggplot2)
  data = dimData$data

  p = ggplot(data, aes(x=x, y=var, ymin=low, ymax=up, color=class))
  p + geom_errorbar(width=2) + geom_line() 
}

# private methods

scramblePCA = function(mat) {
  # old version without duplicate information!
  pca = prcomp(t(mat), scale=FALSE, retx=FALSE)
  B = pca$rotation
  #C = t(pca$x)
  ret = list(B=B, C=NULL, pca=pca)
  return(ret)
}

scrambleFeature = function(mat) {
  require(Matrix)
  N = ncol(mat)
  F = nrow(mat)
  if (inherits(mat, "Matrix")) {
    p = mat@p
    newI = rep(0, length(mat@i))
    # scramble the features of all data points
    for (ind in 1:N) {
      if (p[ind+1]-p[ind] > 0) {
        newI[(p[ind]+1):p[ind+1]] = sample(F, p[ind+1]-p[ind], replace=FALSE) - 1
      }
    }
    ret = sparseMatrix(i=newI, p=p, x=mat@x, dims=c(F, N), dimnames=dimnames(mat), index1=FALSE)
  }
  else {
    ret = mat
    # scramble the features of all data points
    for (ind in 1:N) {
      ret[, ind] = ret[sample.int(F), ind]
    }
  }
  return(ret)
}

