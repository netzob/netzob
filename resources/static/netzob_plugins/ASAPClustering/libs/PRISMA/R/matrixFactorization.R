# public methods

prismaHclust = function(prismaData, ncomp, method="single") {
  mat = prismaData$data
  d = dist(t(mat), "binary")
  clust = hclust(d, method)
  labels = cutree(clust, k=ncomp)

  label2ind = split(1:length(labels), labels)
  B = sapply(label2ind, function(ind) apply(mat[, ind], 1, mean))
  one = function(where) {
    ret = rep(0, ncomp)
    ret[where] = 1
    return(ret)
  }
  C = sapply(labels, function(l) one(l))
  ret = list(B=B, C=C)
  rownames(ret$B) = rownames(mat)
  colnames(ret$B) = as.character(1:ncomp)
  colnames(ret$C) = colnames(mat)
  ret$type = "hclust"
  ret$remapper = prismaData$remapper
  class(ret) = "prismaMF"
  return(ret)
}

prismaDuplicatePCA = function(prismaData) {
  pca = sparsePCA(sparseCov(prismaData))
  ret = list(B=pca$loadings, C=pca$scores, pca=pca)
  ret$type = "DuplicatePCA"
  ret$remapper = prismaData$remapper
  class(ret) = "prismaMF"
  return(ret)
}

prismaNMF = function(prismaData, ncomp, time=60, pca.init=TRUE, doNorm=TRUE, oldResult=NULL) {
  mat = prismaData$data
  B = NULL
  if (!(is.null(oldResult))) {
    B = oldResult$B
    k = ncol(B)
  }
  else if (pca.init) {
    # genBase duplicates the input, therefore we just take half of the components
    if (class(ncomp) == "prismaDimension") {
      k = ncomp$dim %/% 2
      B = genBase(ncomp$pca$B[, 1:k])
    }
    else {
      pca = prismaDuplicatePCA(prismaData)
      k = ncomp %/% 2
      B = genBase(pca$B[, 1:k])
    }
    k = 2*k
  }
  weights = prismaData$duplicatecount
  ret = pmf(mat, k, calcTime=time, B=B, doNorm=doNorm, weights=weights)

  rownames(ret$B) = rownames(mat)

  ret$remapper = prismaData$remapper
  colnames(ret$C) = colnames(mat)
  class(ret) = "prismaMF"
  return(ret)
}

plot.prismaMF = function(x, nLines=NULL, baseIndex=NULL, sampleIndex=NULL, minValue=NULL, noRowClustering=FALSE, noColClustering=FALSE, type=c("base", "coordinates"), ...) {
	mf=x  
	type = match.arg(type)
  if (type == "base") {
    B = mf$B
    if (!is.null(minValue)) {
      B[B < minValue] = 0
    }
    plotMatrixFactor(B, nLines, baseIndex, noRowClustering, noColClustering)
  }
  else if (type == "coordinates") {
    C = mf$C
    if (!is.null(sampleIndex)) {
      C = C[, sampleIndex]
    }
    if (!is.null(minValue)) {
      C[C < minValue] = 0
    }
    plotMatrixFactor(t(C), nLines, baseIndex)
  }
  else {
    stop("Unknown plot type!")
  }
}

# private methods

sparseCov = function(prismaData) {
  N = length(prismaData$remapper)
  k = nrow(prismaData$data)
  x = rep(NA, k*k)
  # efficient mean calculation
  fmean = colSums(t(prismaData$data) * prismaData$duplicatecount) / N
  scount = sqrt(prismaData$duplicatecount)
  centeredData = t(prismaData$data - fmean)
  centered = centeredData * scount
  theCov = new("dsyMatrix", Dim = c(k, k), x=as.numeric(t(centered) %*% centered / (N - 1)))
  dimnames(theCov) = list(rownames(prismaData$data), rownames(prismaData$data))
  return(list(cov=theCov, centeredData=centeredData, center=fmean))
}

sparsePCA = function(sparsecov) {
  # here we emulate the princom method... some parts of it are "reused" here
  cl = match.call()
  cl[[1L]] = as.name("sparsePCA")
  cv = sparsecov$cov
  z = sparsecov$centeredData
  n.obs = nrow(z)
  cen = sparsecov$center
  edc = eigen(cv, symmetric = TRUE)
  ev = edc$values
  evec = edc$vectors
  if (any(neg <- ev < 0)) {
    # throw away negative eigenvalues
    pos = which(!neg)
    ev = ev[pos]
    evec = evec[, pos]
  }
  cn = paste0("Comp.", 1L:ncol(evec))
  names(ev) = cn
  dimnames(evec) = list(dimnames(cv)[[2L]], cn)
  sdev = sqrt(ev)
  scr = t(z %*% evec)
  edc = list(sdev = sdev, loadings=evec,
    center = cen, n.obs = n.obs, scores = scr, call = cl)
  class(edc) = "princomp"
  return(edc)
}

reconstructSparsePCA = function(spca) {
  rec = spca$loadings %*% spca$scores + spca$center
  return(rec)
}

plotMatrixFactor = function(B, n.lines=NULL, base.index=NULL, noRowClustering=FALSE, noColClustering=FALSE) {
  require(gplots)
  B = as.matrix(B)
  if (!is.null(base.index)) {
    B = B[, base.index]
  }
  if (!is.null(n.lines)) {
    B = calcLinesPerThreshold(B, n.lines)
  }
  if (noRowClustering) {
    row.clust = NULL
    dendrogram = "column"
  }
  else {
    row.clust = as.dendrogram(hclust(dist(B, method="euclidean"), method="complete"))
    dendrogram = "both"
  }
  if (noColClustering) {
    col.clust = NULL
    dendrogram = ifelse(dendrogram == "both", "row", "none")
  }
  else {
    col.clust = as.dendrogram(hclust(dist(t(B), method="binary"), method="complete"))
  }
  breaks = c(0, seq(min(B[B>0])-1e-9, max(B), length=15))
  heatmap.2(B, Rowv=row.clust, Colv=col.clust, dendrogram=dendrogram, trace="none", breaks=breaks, col=function(n) gray(c(1, seq(0.8, 0, length=n-1))))
}

genBase = function(B) {
  negB = -B
  negB[negB < 0] = 0
  mat = cbind(negB, B + negB)
  colnames(mat) = c(paste(colnames(B), "neg", sep="."), paste(colnames(B), "pos", sep="."))
  return(mat)
}

normBase = function(ret) {
  r = ncol(ret$B)
  nfeats = nrow(ret$B)
  # norm the basis
  norms = sqrt(apply(ret$B^2, 2, sum))
  # look for all-zero base
  allZero = (norms == 0)
  ret$B = ret$B[, !allZero]
  ret$C = ret$C[!allZero, ]
  r = r - sum(allZero)
  ret$B = ret$B / rep(norms[!allZero], rep(nfeats, r))
  ret$C = ret$C * norms[!allZero]
  return(ret)
}

calcDatacluster = function(ret) {
  labels = apply(ret$C, 2, which.max)
  return(labels)
}

calcLinesPerThreshold = function(B, n.lines) {
  allVals = unique(sort(B, decreasing=TRUE))
  allMax = apply(B, 1, max)
  lines = sapply(allVals, function(v) sum(allMax > v))
  min.value = allVals[which.min(lines <= n.lines)-1]
  B = B[apply(B, 1, function(r) any(r > min.value)), ]
  return(B)
}


RRbyCV = function(Y, D, fold=5, lambdas=10^(-4:2), weights=NULL) {
  # Y is the data assumed to be [# samples X # vars]
  N = nrow(Y)
  F = ncol(D)
  Nfold = floor(N / fold)
  res = matrix(0, length(lambdas), fold, dimnames=list(as.character(lambdas), NULL))
  for (l in lambdas) {
    for (f in 1:fold) {
      index = ((f-1)*Nfold + 1):(f * Nfold)
      Sub = D[-index, ]
      # estimate the coefficients on the subsample
      if (is.null(weights)) {
        Beta = solve(t(Sub) %*% Sub + diag(l, F)) %*% t(Sub) %*% Y[-index, ]
        res[as.character(l), f] = sqrt(sum((Y[index, ] - (D[index, ] %*% Beta))^2))
      }
      else {
        W = Diagonal(x=weights[-index])
        Beta = solve(t(Sub) %*% W %*% Sub + diag(l, F)) %*% t(Sub) %*% W %*% Y[-index, ]
        res[as.character(l), f] = sqrt(sum((Y[index, ] - (D[index, ] %*% Beta))^2))
      }
    }
  }
  return(lambdas[which.min(apply(res, 1, mean))])
}

pmf = function(A, r, calcTime, B=NULL, doNorm=TRUE, weights=NULL) {
  require(Matrix)
  # A should contain the samples in the cols!
  nsamples = ncol(A)
  nfeats = nrow(A)
  if (is.null(weights)) {
    W = Diagonal(nsamples)
    weights = rep(1, nsamples)
  }
  else {
    W = Diagonal(nsamples, weights)
  }
  # the new basis
  if (is.null(B)) {
    B = abs(matrix(rnorm(nfeats * r), nfeats, r))
  }
  olderror = Inf
  iter = 0
  startTime = proc.time()[3]
  while (TRUE) {
    lambda = RRbyCV(A, B, weights=NULL)
    S = t(B) %*% B + diag(lambda, r, r)

    # faster?
    C = solve(S, t(B) %*% A) 
    # C = solve(S) %*% (t(B) %*% A)
    # set all negative coordinates to 0
    C[C < 0] = 0

    lambda = RRbyCV(t(A), t(C), weights=weights)
    S = C %*% W %*% t(C) + diag(lambda, r, r)

    # faster?
    B = t(solve(S, C %*% W %*% t(A)))
    #B = (A %*% W %*% t(C)) %*% solve(S)
    B[B < 0] = 0
    if (doNorm) {
      # norm the basis
      norms = sqrt(apply(B^2, 2, sum))
      # look for all-zero base
      allZero = (norms == 0)
      B = B[, !allZero, drop=FALSE]
      C = C[!allZero, , drop=FALSE]
      r = r - sum(allZero)
      B = B / rep(norms[!allZero], rep(nfeats, r))
      C = C * norms[!allZero]
    }
    iter = iter + 1
    timeElapsed = proc.time()[3] - startTime
    if (iter %% 10 == 0) {
      error = .5 * sum(colSums((A - B %*% C)^2) * weights)
      cat("Error:", error, "\n")
      if (abs(olderror - error) < 1e-9) {
        break
      }
      olderror = error
    }
    if (timeElapsed >= calcTime) {
      break
    }
  }
  ret = list(B=B, C=C)
  return(ret)
}
