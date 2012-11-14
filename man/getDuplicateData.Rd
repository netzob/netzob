\name{getDuplicateData}
\alias{getDuplicateData}
\title{
  Restores Data with Duplicates
}
\description{
  The loadPrismaData function triggers a feature selection and
  combination methods which subsequently filters out duplicate values to
  save memory space. The getDuplicateData returns the data matrix with
  all duplicate entries.
}
\usage{
getDuplicateData(prismaData)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{prismaData}{
    prisma data loaded via loadPrismaData
}
}
\value{
  \item{dataWithDuplicates}{Data matrix containing explicit copies of all duplicates.}
}
\author{
Tammo Krueger <t.krueger@tu-berlin.de>
}

\examples{
data(asap)
dataWithDuplicates = getDuplicateData(asap)
}
