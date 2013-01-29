\name{prismaHclust}
\alias{prismaHclust}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
  Matrix Factorization Based on Hierarchical Clustering
}
\description{
  A matrix factorization $A = B C$ based on the results of hclust is constructed,
  which holds the mean feature values for each cluster in the matrix $B$
  and the indication of the cluster in the matrix $C$ for each data
  point (i.e. each data point is represented by its assigned cluster center).
}
\usage{
prismaHclust(prismaData, ncomp, method = "single")
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{prismaData}{
    prisma data for which a clustering should be calculated
}
  \item{ncomp}{
    the number of components that should be extracted.
}
  \item{method}{
    the method used for clustering.
}
}
\value{
\item{prismaHclust}{Matrix factorization object containing $B$ and $C$
  resulting from the hierarchical clustering of the data.}
}
\author{
Tammo Krueger <t.krueger@tu-berlin.de>
}

\seealso{
\code{\link{hclust}}
}
\examples{
data(asap)
\donttest{asapHclust = prismaHclust(asap)}
}
