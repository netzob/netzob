# public functions:
loadPrismaData = function(path, maxLines=-1, fastSally=TRUE, alpha=.05) {
  data = readPrismaInput(path, maxLines, fastSally)
  data = preprocessPrismaData(data, alpha)
  data$path = path
  class(data) = "prisma"
  return(data)
}

getDuplicateData = function(prismaData) {
  return(prismaData$data[, prismaData$remapper])
}

print.prisma = function(x, ...) {
	prismaData=x
  cat("PRISMA data", prismaData$path, "\n")
  cat("Unprocessed data: # features:", nrow(prismaData$unprocessed),
      "# entries:", ncol(prismaData$unprocessed), "\n")
  cat("Processed data: # features:", nrow(prismaData$data),
      "# entries:", ncol(prismaData$data), "\n")
}

plot.prisma = function(x, ...) {
	prismaData=x
  image(prismaData$data)
}

# private functions:
readFSally = function(path, maxLines=-1) {
  require(Matrix)
  f = file(path)
  cat("Reading data...\n")
  data = readLines(f)
  cat("Splitting ngrams...\n")
  ngrams = strsplit(data, " ", fixed=TRUE)
  total = length(data)
  allNgrams = ngrams[[total]]
  close(f)
  cat("Calc indices...\n")
  indices = match(unlist(ngrams[-total]), allNgrams)
  cat("Setup matrix...\n")
  N = total-1
  mat = sparseMatrix(indices, rep(1:N, sapply(ngrams[-total], length)),
    x=1,
    dims=c(length(allNgrams), N),
    dimnames=list(allNgrams, paste("line", 1:N, sep="")))
  if (maxLines > 0) {
    return(mat[, 1:maxLines])
  }
  else {
    return(mat)
  }
}

readSally = function(path, maxLines=-1) {
  require(Matrix)
  f = file(path)
  data = scan(f, what="char", sep=" ", quote="", quiet=TRUE, comment.char="", skip=1, nlines=maxLines)
  close(f)
  rawngrams = data[c(TRUE, FALSE)]
  origin = data[c(FALSE, TRUE)]
  processNgram = function(cv) {
    ret = cv[3]
    names(ret) = cv[2]
    return(ret)
  }
  ngrams = lapply(strsplit(rawngrams, ",", fixed=TRUE), function(obj) sapply(strsplit(obj, ":", fixed=TRUE), processNgram))
  allNgrams = unique(unlist(lapply(ngrams, function(ngram) names(ngram)), use.names=FALSE))
  indices = unlist(lapply(ngrams, function(ngram) match(names(ngram), allNgrams)), use.names=FALSE)
  # generate a matrix in ml-style: rows are the features, cols are the samples
  mat = sparseMatrix(indices, rep(1:length(ngrams), sapply(ngrams, length)), x= as.numeric(unlist(ngrams, use.names=FALSE)), dims=c(length(allNgrams), length(ngrams)), dimnames=list(allNgrams, origin))
  return(mat)
}

readHarry = function(path, maxLines=-1) {
  harry = read.table(path, sep="\t", quote="", comment.char="",
    as.is=TRUE, header=TRUE, nrows=maxLines)
  return(harry)
}

readRaw = function(path, maxLines=-1) {
  f = file(path)
  raw = readLines(f, n=maxLines)
  close(f)
  #rawsplit = strsplit(raw, " ", fixed=TRUE)
  return(raw)
}

readPrismaInput = function(path, maxLines=-1, fastSally=TRUE) {
  if (fastSally) {
    sally = readFSally(sprintf("%s.fsally", path), maxLines)
  }
  else {
    sally = readSally(sprintf("%s.sally", path), maxLines)
  }
  data = list(data=sally)
  hfile = sprintf("%s.harry", path)
  if (file.exists(hfile) && file.access(hfile, mode=4)) {
    data$annotation = readHarry(hfile, maxLines)
  }
  rfile = sprintf("%s.rawquoted", path)
  if (file.exists(rfile) && file.access(rfile, mode=4)) {
    data$raw = readRaw(rfile, maxLines)
  }
  return(data)
}

duplicateRemover = function(data) {
  if (inherits(data, "Matrix")) {
    classes = calcClassForSparseMatrix(data)
  }
  else {
    classes = sapply(1:ncol(data), function(colIndex) paste(which(data[, colIndex] == 1), collapse=" "))
  }
  classCount = table(classes)
  uniqueClasses = names(classCount)
  # just pick the first data point for each class:
  classIndex = sapply(uniqueClasses, function(cl) match(cl, classes))
  data = data[, classIndex]
  remapper = sapply(classes, function(cl) match(cl, uniqueClasses))
  return(list(data=data, remapper=remapper, count=classCount))
}

calcClassForSparseMatrix = function(data) {
  i = data@i
  dp = c(0, diff(data@p))
  csdp = cumsum(dp)
  oneClass = function(index) {
    from = csdp[index]+1
    to = csdp[index+1]
    if (from > to) {
      # zero entry
      return("")
    }
    else {
      return(paste(i[from:to], collapse=" "))
    }
  }
  sapply(1:ncol(data), oneClass)
}

preprocessPrismaData =function(data, alpha=.05) {
  data$unprocessed = data$data
  processed = filterDataByTestAndCor(data$data, alpha)
  duplicatesRemoved = duplicateRemover(processed$mat)
  data$data = duplicatesRemoved$data
  data$remapper = duplicatesRemoved$remapper
  data$duplicatecount = as.vector(duplicatesRemoved$count)

  data$group = processed$group
  data$occAlways = processed$always
  data$occNever = processed$never

  return(data)
}

count2freq = function(mat) {
  # use the samples x features view for simpler calculation
  mat = t(mat)
  return(t(mat / rowSums(mat)))
}

count2bin = function(mat) {
  require(Matrix)
  if (inherits(mat, "TsparseMatrix")) {
    ret = mat
  }
  else if (inherits(mat, "CsparseMatrix")) {
    ret = sparseMatrix(mat@i+1, p=mat@p, x=1, dims=mat@Dim, dimnames=mat@Dimnames)
  }
  else {
    ret = as.matrix(mat)
    ret[ret > 0] = 1
  }
  return(ret)
}

groupCorrelatedNgrams = function(data) {
  nfeats = nrow(data)
  ndocs = ncol(data)
  toCheck = 1:nfeats
  groups = rep(-1, nfeats)
  groupCount = 1
  # is it possible to calculate correlations on sparse matrices?
  #mat = as.matrix(data)
  mat = data
  while (length(toCheck) > 0) {
    cat("to check:", length(toCheck), "\n")
    if (length(toCheck) == 1) {
      curCor = 1
    }
    else {
      curCor = sparse.cor(mat[toCheck, ])
    }
    group = toCheck[curCor == 1]
    groups[group] = groupCount
    groupCount = groupCount + 1
    toCheck = toCheck[curCor != 1]
    #cat(data$str[group], "\n")
  }
  return(groups)
}

sparse.cor <- function(X){
  docsWithFeature = (X[1, ] != 0)
  onDocs = sum(docsWithFeature)
  offDocs = ncol(X) - onDocs
  ret = rep(0, nrow(X))
  ret[1] = 1
  if (onDocs >= 1) {
    onFeatureDocs = X[, docsWithFeature]
    offFeatureDocs = X[, !docsWithFeature]
    if (onDocs > 1) {
      # we have more than one document for this feature... 
      # so calculate the number of documents for this feature
      onFeatureDocs = rowSums(onFeatureDocs)
    }
    if (offDocs > 1) {
      offFeatureDocs = rowSums(offFeatureDocs)
    }
    # just set the correlation to one, if the number of
    # documents, in which the feature is turned of, is zero
    # and the number of documents, in which the feature is on, is the same
    ret[(offFeatureDocs == 0) & (onFeatureDocs == onDocs)] = 1
  }
  return(ret)
}

compressByGroup = function(data) {
  features = rownames(data)
  groups = groupCorrelatedNgrams(data)
  indByG = split(1:length(groups), groups)
  names(groups) = features
  newDimNames = sapply(indByG, function(g) paste(features[g], collapse=" "))
  # just keep the first feature of the group...
  # since the rest contains the same information (cor=1)
  data = data[sapply(indByG, function(g) g[1]), ]
  rownames(data) = newDimNames
  return(list(data=data, group=groups))
}

# data should be binary and unnormalized!
# hmmm... the "normal" testing weirdness of thinking-negative:
# never = ttestNgrams(data, 0, "greater")
# we would keep these...
# data$str[p.adjust(never, "bonf") < 0.05]
##   [1] "\nAcc" "\nHos" " */*"  " HTT"  " cgi"  " www"  "*/*\n" ".1\nH" ".com" 
##  [10] ".foo"  ".php"  "/1.1"  "/sea"  "1\nHo" "1.1\n" ": */"  ": ww"  "Acce" 
##  [19] "ET c"  "GET "  "HTTP"  "Host"  "P/1."  "T cg"  "TP/1"  "TTP/"  "ar.c" 
##  [28] "arch"  "bar."  "ccep"  "cept"  "cgi/"  "ch.p"  "com\n" "earc"  "ept:" 
##  [37] "foob"  "gi/s"  "h.ph"  "hp?s"  "i/se"  "m\nAc" "obar"  "om\nA" "ooba" 
##  [46] "ost:"  "p?s="  "php?"  "pt: "  "r.co"  "rch."  "sear"  "st: "  "t: *" 
##  [55] "t: w"  "w.fo"  "ww.f"  "www."  "&par"  "/adm"  "=ren"  "?act"  "acti" 
##  [64] "admi"  "ame&"  "ctio"  "dmin"  "e&pa"  "enam"  "gi/a"  "hp?a"  "i/ad" 
##  [73] "in.p"  "ion="  "me&p"  "min."  "n.ph"  "n=re"  "name"  "on=r"  "p?ac" 
##  [82] "par="  "rena"  "tion"  " sta"  ".htm"  "ET s"  "T st"  "atic"  "html" 
##  [91] "l HT"  "ml H"  "stat"  "tati"  "tic/"  "tml "  "=mov"  "move"  "n=mo" 
## [100] "on=m"  "ove&"  "ve&p"  "=sho"  "how&"  "n=sh"  "on=s"  "ow&p"  "show" 
## [109] "w&pa"  "=del"  "dele"  "elet"  "ete&"  "lete"  "n=de"  "on=d"  "te&p" 
## [118] "G HT" 
# always = ttestNgrams(data, 1, "less")
# ...and drop these...
# data$str[p.adjust(always, "bonf") > 0.05]
##  [1] "\nAcc" "\nHos" " */*"  " HTT"  " www"  "*/*\n" ".1\nH" ".com"  ".foo" 
## [10] "/1.1"  "1\nHo" "1.1\n" ": */"  ": ww"  "Acce"  "GET "  "HTTP"  "Host" 
## [19] "P/1."  "TP/1"  "TTP/"  "ar.c"  "bar."  "ccep"  "cept"  "com\n" "ept:" 
## [28] "foob"  "m\nAc" "obar"  "om\nA" "ooba"  "ost:"  "pt: "  "r.co"  "st: " 
## [37] "t: *"  "t: w"  "w.fo"  "ww.f"  "www."
# So finally just keep these:
# data$str[p.adjust(always, "bonf") < 0.05 & p.adjust(never, "bonf") < 0.05]
ttestNgrams = function(data, mu, alternative=c("greater", "less")) {
  require(Matrix)
  alternative <- match.arg(alternative)
  N = ncol(data)
  nfeats = nrow(data)
  muNgram = rowMeans(data) * N
  # some sources give 5, other 10 as a factor, of when the normal approx. works...
  # we just take the average here.
  mu = ifelse(mu == 0, 7.5/N, 1 - (7.5/N))
  theVar = sqrt(N * mu * (1 - mu))
  M = mu * N
  if (alternative == "greater") {
    pValues = sapply(muNgram, function(m) pnorm((m - M) / theVar, lower.tail = FALSE))
  }
  if (alternative == "less") {
    pValues = sapply(muNgram, function(m) pnorm((m - M) / theVar, lower.tail = TRUE))
  }
  return(pValues)
}

filterDataByTestAndCor = function(data, alpha=0.05) {
  data = count2bin(data)
  never = ttestNgrams(data, 0, "greater")
  always = ttestNgrams(data, 1, "less")

  alwaysP = p.adjust(always, "holm")
  neverP = p.adjust(never, "holm")
  if (is.null(alpha)) {
    keep = (alwaysP != 1)
  }
  else {
    keep = (alwaysP < alpha & neverP < alpha)
  }
  allStr = rownames(data)
  fdata = data[keep, ]
  dataAndGroup = compressByGroup(fdata)
  if (is.null(alpha)) {
    always = allStr[(alwaysP == 1)]
    never = c()
  }
  else {
    always = allStr[(alwaysP >= alpha)]
    never = allStr[(neverP >= alpha)]
  }
  return(list(mat=dataAndGroup$data, group=dataAndGroup$group, always=always, never=never))
}
