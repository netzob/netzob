\name{plot.prismaDimension}
\alias{plot.prismaDimension}
\alias{print.prismaDimension}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
  Generics For PRISMA Objects
}
\description{
  Print and plot generic for the PRISMA dimension objects.
}
\usage{
\method{print}{prismaDimension}(x, ...)
\method{plot}{prismaDimension}(x, ...)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{x}{
    prisma dimension object generated via \code{\link{estimateDimension}}
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
\donttest{print(asapDim)}
\donttest{plot(asapDim)}
}
