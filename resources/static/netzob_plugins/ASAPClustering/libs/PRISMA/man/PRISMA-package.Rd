\name{PRISMA-package}
\alias{PRISMA-package}
\alias{PRISMA}
\docType{package}
\title{
PRISMA - Protocol Inspection and State Machine Analysis
}
\description{
The PRISMA package is capable of loading and processing
huge text corpora processed with the sally toolbox
(\url{http://www.mlsec.org/sally/}). sally acts as a ver fast preprocessor which
splits the text files into tokens or n-grams. These output files can
then be read with the PRISMA package which applies testing-based
token selection and has some duplicat-aware, highly tuned Non-Negative
Matrix Factorzation and Principal component Analysis implementation
which allows the processing of very big data sets even on desktop machines.
}
\details{
\tabular{ll}{
Package: \tab PRISMA\cr
Type: \tab Package\cr
Version: \tab 0.1\cr
Date: \tab 2012-10-02\cr
License: \tab GPL (>=2.0)\cr
}
}
\author{Tammo Krueger, Nicole Kraemer

Maintainer: Tammo Krueger <t.krueger@tu-berlin.de>
}
\references{
Krueger, T., Gascon, H., Kraemer, N., Rieck, K. (2012)
Learning Stateful Models for Network Honeypots
\emph{5th ACM Workshop on Artificial Intelligence and Security (AISEC 2012)}, accepted

Krueger, T., Kraemer, N., Rieck, K. (2011)
ASAP: Automatic Semantics-Aware Analysis of Network Payloads
\emph{Privacy and Security Issues in Data Mining and Machine Learning - International ECML/PKDD Workshop. Lecture Notes in Computer Science 6549}, Springer. 50 - 63
}
\keyword{ package }
\examples{
data(asap)
plot(asap)
\donttest{asapDim = estimateDimension(asap)}
\donttest{plot(asapDim)}
\donttest{asapNMF = prismaNMF(asap, asapDim, time=120)}
\donttest{plot(asapNMF, minValue=.2)}
}
