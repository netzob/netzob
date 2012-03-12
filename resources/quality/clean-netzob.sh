#!/bin/sh

# Nettoyage des espaces en fin de ligne :
sed -i -e "s, *\$,,g" **/*.py

# Nettoyage des espaces devant deux points :
sed -i -e 's, :$,:,g' **/*.py

# Whitespaces after parenthesis (
sed -i -e 's,( ,(,g' **/*.py
sed -i -e 's,\[ ,\[,g' **/*.py

# Whitespaces before parenthesis )
sed -i -e 's, ),),g' **/*.py
sed -i -e 's, \],\],g' **/*.py

# Blank lines at the end of file
sed -i -e ":a" -e '/^\n*$/{$d;N;ba}'

# Deux espaces avant un inline comment
sed -i -re 's,([^ ]) #,\1  #,' **/*.py
