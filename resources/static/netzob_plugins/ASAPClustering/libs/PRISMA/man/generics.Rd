\name{plot.prisma}
\alias{plot.prisma}
\alias{print.prisma}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
  Generics For PRISMA Objects
}
\description{
  Print and plot generic for the PRISMA objects.
}
\usage{
\method{print}{prisma}(x, ...)
\method{plot}{prisma}(x, ...)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{x}{
    prisma data loaded via \code{\link{loadPrismaData}}
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
print(asap)
plot(asap)

}
