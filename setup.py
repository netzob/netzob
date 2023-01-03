#!/usr/bin/env python
# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011_2014 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +----------------------------------------------------------------------------
# | Global Imports
# +----------------------------------------------------------------------------
import sys
import os
import uuid

from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

sys.path.insert(0, 'src/')
from netzob import release

try:
    # Handle case where Netzob is not already installed
    from resources.sdist.test_command import test_command
except Exception:
    def dummy():
        pass
    test_command = dummy

def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

# +----------------------------------------------------------------------------
# | Compute the compilation arguments given the current compilation profile
# +----------------------------------------------------------------------------
# compileProfile = "[no-verify] devel|release"
#
# Note :
# if defined, the environment variable "NETZOB_COMPILE_PROFILE" sets
# the compileProfile
#
# Available compilation profile
#   - devel     : no optimization, include debugging symbols and stop on compilation warnings
#   - release   : activate optimization and symbols are stripped (default mode)
# Static analysis
#   - no-verify : deactivate the source code static analysis while compiling
#
# TODO : an unoptimized profile with options like -mno-mmx, -mno-sse,
#        -mno-sse2, -mno-3dnow, -fno-dwarf2-cfi-asm
#

compileProfile = "release"

NETZOB_COMPILE_PROFILE_ENV = "NETZOB_COMPILE_PROFILE"
# extract requested mode from the environment variable
if NETZOB_COMPILE_PROFILE_ENV in os.environ.keys():
    compileProfile = os.environ[NETZOB_COMPILE_PROFILE_ENV]

# Default compile arguments
extraCompileArgs = ["-std=c99"]
if "no-verify" not in compileProfile:
    extraCompileArgs.extend([
        "-Wall",                # gcc says: "Enable most warning messages"
        "-Wextra",              # gcc says: "Print extra (possibly unwanted) warnings"
        "-Wunused",             # gcc says: "Enable all -Wunused- warnings"
        "-Wsign-compare",       # gcc says: "Warn about signed-unsigned comparisons"
        "-Wstrict-prototypes",  # gcc says: "Warn about unprototyped function declarations"
        "-Wuninitialized",      # gcc says: "Warn about uninitialized automatic variables"
        "-Wshadow",             # gcc says: "Warn when one local variable shadows another"
        "-Wpointer-arith"])     # gcc says: "Warn about function pointer arithmetic"

if "devel" in compileProfile:
    extraCompileArgs.extend([
        "-O0",                  # gcc says: "Optimization level 0"
        "-Werror",              # gcc says: "Error out the compiler on warnings"
        "-pedantic-errors",     # gcc says: "Issue errors "needed for strict compliance to the standard"
        "-g"])                  # gcc says: "Generate debug information in default format"

elif "release" in compileProfile:
    extraCompileArgs.extend([
        "-O2"])                 # gcc says: "Optimization level 2"

# +----------------------------------------------------------------------------
# | Definition of the extensions
# +----------------------------------------------------------------------------
# Includes path
libPath = "lib"
includesPath = opj(libPath, "includes")
pyIncludesPath = opj(includesPath, "Py_lib")
includes = [includesPath, pyIncludesPath]

# Interface path
interfacePath = opj(libPath, "interface")
pyInterfacePath = opj(interfacePath, "Py_lib")

# Needleman path
needlemanPath = opj(libPath, "libNeedleman")
pyNeedlemanPath = opj(needlemanPath, "Py_lib")

# ArgsFactories path
argsFactoriesPath = opj(libPath, "argsFactories")

# Relation path
relPath = os.path.join(libPath, "libRelation")
pyRelPath = os.path.join(relPath, "Py_lib")
relImplPath = os.path.join(relPath, "algorithms")

# Tools path
toolsPath = opj(libPath, "tools")

# Generate the random binary identifier BID
macros = [('BID', '"{0}"'.format(str(uuid.uuid4())))]

# Module Needleman
moduleLibNeedleman = Extension('netzob._libNeedleman',
                               extra_compile_args=extraCompileArgs,
                               sources=[opj(interfacePath, "Interface.c"),
                                        opj(pyInterfacePath, "libInterface.c"),
                                        opj(pyNeedlemanPath, "libNeedleman.c"),
                                        opj(needlemanPath, "Needleman.c"),
                                        opj(needlemanPath, "scoreComputation.c"),
                                        opj(argsFactoriesPath, "factory.c"),
                                        opj(toolsPath, "getBID.c")],
                               define_macros=macros,
                               include_dirs=includes)

# Module ScoreComputation
moduleLibScoreComputation = Extension('netzob._libScoreComputation',
                                      extra_compile_args=extraCompileArgs,
                                      sources=[opj(needlemanPath, "scoreComputation.c"),
                                               opj(pyNeedlemanPath, "libScoreComputation.c"),
                                               opj(needlemanPath, "Needleman.c"),
                                               opj(interfacePath, "Interface.c"),
                                               opj(pyInterfacePath, "libInterface.c"),
                                               opj(argsFactoriesPath, "factory.c"),
                                               opj(toolsPath, "getBID.c")],
                                      define_macros=macros,
                                      include_dirs=includes)

# Module Interface
moduleLibInterface = Extension('netzob._libInterface',
                               extra_compile_args=extraCompileArgs,
                               sources=[opj(interfacePath, "Interface.c"),
                                        opj(pyInterfacePath, "libInterface.c"),
                                        opj(toolsPath, "getBID.c")],
                               define_macros=macros,
                               include_dirs=includes)

# Module Relation
moduleLibRelation = Extension('netzob._libRelation',
                              extra_compile_args=extraCompileArgs,
                              sources=[os.path.join(relPath, "relation.c"),
                                       os.path.join(pyRelPath, "libRelation.c")],
                              define_macros=macros,
                              include_dirs=includes,
                              libraries=["dl"])

# Cython extensions
cythonModules = cythonize(["src/netzob/Fuzzing/Generators/xorshift.pyx"],
                          compiler_directives={'language_level': "3"})


# +----------------------------------------------------------------------------
# | Definition of the dependencies
# +----------------------------------------------------------------------------
def get_dependencies():
    return """
    getmac==0.8.3
    bintrees==2.2.0
    bitarray==0.8.1
    colorama==0.4.6
    minepy==1.2.6
    pylstar==0.1.2
    impacket==0.10.0
    netaddr==0.8.0
    pcapy-ng==1.0.9
    pythoncrc==1.21
    numpy==1.24.1
    sphinx==4.5.0
    sphinx_book_theme==0.3.3
    """.split()

    # Temporary deactivate randomstate==1.13.1, which has dependency constraint with numpy==1.14.3

extra_dependencies = {
    # 'docs': ['Sphinx==5.3.0'],
}

dependency_links = []

# +----------------------------------------------------------------------------
# | Extensions in the build operations (create manpage, i18n, ...)
# +----------------------------------------------------------------------------
CMD_CLASS = {
    'test': test_command
}

# +----------------------------------------------------------------------------

# Extract the long description from README.rst and NEWS.rst files
README = open('README.rst', 'rt').read()
NEWS = open('NEWS.rst', 'rt').read()

# +----------------------------------------------------------------------------
# | Definition of Netzob for setup
# +----------------------------------------------------------------------------
setup(
    name=release.name,
    packages=find_packages(where='src'),
    package_dir={
        "": "src",
    },
    ext_modules=[moduleLibNeedleman, moduleLibScoreComputation,
                 moduleLibInterface, moduleLibRelation] + cythonModules,
    #data_files=data_files,
    scripts=["netzob"],
    install_requires=get_dependencies(),
    extras_require=extra_dependencies,
    dependency_links=dependency_links,
    version=release.version,
    license=release.licenseName,
    description=release.description,
    platforms=release.platforms,
    author=release.author,
    url=release.url,
    download_url=release.download_url,
    keywords=release.keywords,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: C",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Security",
        "Topic :: System :: Networking"
    ],
    long_description=README + '\n' + NEWS,
    cmdclass=CMD_CLASS,
)

