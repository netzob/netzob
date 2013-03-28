\name{estimateDimension}
\alias{estimateDimension}
\title{
  Estimate Inner Dimension
}
\description{
  Matrix factorization methods compress the original data matrix \eqn{A \in
  R^{f,N}} with \eqn{f} features and \eqn{N} samples into two parts,
  namely \eqn{A = B C} with \eqn{B \in R^{f,k}, C\in R^{k,
    N}}. The function estimateDimension estimates \eqn{k} based on a noise
  model estimated from a scrambled version of the original data matrix.
}
\usage{
estimateDimension(prismaData, alpha = 0.05, nScrambleSamples = NULL)
}
\arguments{
  \item{prismaData}{
    A prismaData object loaded via loadPrismaData
}
  \item{alpha}{
    Error probability for confidence intervals
}
  \item{nScrambleSamples}{
    The number of scrambled samples that should be used to estimate the
    noise model. NULL means to use the complete data set.
}
}
\value{
  \item{estDim}{prismaDimension object that can be printed and plotted.}
}
\references{
R.~Schmidt. Multiple emitter location and signal parameter estimation.
\emph{IEEE Transactions on Antennas and Propagation}, 34(3):276 -- 280, 1986.
}
\author{
Tammo Krueger <t.krueger@tu-berlin.de>
}

%% ~Make other sections like Warning with \section{Warning }{....} ~

\examples{
data(asap)
\donttest{asapDim = estimateDimension(asap)}
\donttest{plot(asapDim)}
}
