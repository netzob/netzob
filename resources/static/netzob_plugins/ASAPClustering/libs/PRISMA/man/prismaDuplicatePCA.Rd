\name{prismaDuplicatePCA}
\alias{prismaDuplicatePCA}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
  Matrix Factorization Based on Duplicate-Aware PCA
}
\description{
  Efficient implementation of a duplicate-aware principal component
  anaylsis (PCA).
}
\usage{
prismaDuplicatePCA(prismaData)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{prismaData}{
    prisma data for which a PCA should be calculated
}
}
\value{
  \item{prismaPCA}{Matrix factorization object $A = B C$, in which the
    factors are calculate by a duplicate-aware PCA}
}
\author{
Tammo Krueger <t.krueger@tu-berlin.de>
}
\examples{
data(asap)
\donttest{asapPCA = prismaDuplicatePCA(asap)}
}
