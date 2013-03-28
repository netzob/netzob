\name{plot.prismaMF}
\alias{plot.prismaMF}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
  Generics For PRISMA Objects
}
\description{
  Print and plot generic for the PRISMA matrix factorization objects.
}
\usage{
\method{plot}{prismaMF}(x, nLines = NULL, baseIndex = NULL, sampleIndex = NULL,
minValue = NULL, noRowClustering = FALSE, noColClustering = FALSE, type
= c("base", "coordinates"), ...)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
 
  \item{x}{
    Prisma matrix factorization object
}
  \item{nLines}{
    Number of lines that should be plotted
}
  \item{baseIndex}{
    Which bases should be plotted
}
  \item{sampleIndex}{
    Which samples should be plotted
}
  \item{minValue}{
    Cut-off value, i.e., every value smaller than \code{minValue} won't be shown
}
  \item{noRowClustering}{
    Don't cluster the rows
}
  \item{noColClustering}{
    Don't cluster the columns
}
  \item{type}{
    Show the base (\code{type = "base"}, i.e. the \eqn{B} matrix) or
    show the coordinate (\code{type = "coordinates"}, i.e. the \eqn{C} matrix).
}
  \item{...}{
    Not used
}
}
\author{
Tammo Krueger <t.krueger@tu-berlin.de>
}
\seealso{
\code{\link{estimateDimension}}, \code{\link{prismaHclust}}, \code{\link{prismaDuplicatePCA}}, \code{\link{prismaNMF}}
}
\examples{
data(asap)
\donttest{asapDim = estimateDimension(asap)}
\donttest{asapNMF = prismaNMF(asap, asapDim, time=120)}
\donttest{plot(asapNMF, minValue=.2)}
}
