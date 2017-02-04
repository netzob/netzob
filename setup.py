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

sys.path.insert(0, 'src/')
from netzob import release

from resources.sdist.pybuild_command import pybuild_command
from resources.sdist.test_command import test_command
from resources.sdist.utils import find_data_files, opj, getPluginPaths

# +----------------------------------------------------------------------------
# | Definition of variables
# +----------------------------------------------------------------------------
# Path to the resources
staticResourcesPath = opj("resources", "static")
netzobStaticResourcesPath = opj(staticResourcesPath, "netzob")

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

# +----------------------------------------------------------------------------
# | Definition of the dependencies
# +----------------------------------------------------------------------------
dependencies = []
with open('requirements.txt', 'r') as fd_requirements:
    for dependency in fd_requirements:
        dependencies.append(dependency.strip())

extra_dependencies = {
    'docs': ['Sphinx>=1.1.3'],
    'network': ['pcapy>=0.10.8', 'impacket>=0.9.12'],
    'correlation': ['numpy>=1.9.2', 'minepy>=1.0.0']
}

dependency_links = []

# +----------------------------------------------------------------------------
# | Extensions in the build operations (create manpage, i18n, ...)
# +----------------------------------------------------------------------------
CMD_CLASS = {
    'build_py': pybuild_command,
    'test': test_command
}

# +----------------------------------------------------------------------------

root_data_files = find_data_files(opj("share", "netzob"), netzobStaticResourcesPath, 'logo.png', recursive=False)
app_data_files = find_data_files(opj("share", "applications"), netzobStaticResourcesPath, 'netzob.desktop', recursive=False)
icons_data_files = find_data_files(opj("share", "netzob", "icons"), opj(netzobStaticResourcesPath, "icons"), '*.png')
default_data_files = find_data_files(opj("share", "netzob", "defaults"), opj(netzobStaticResourcesPath, "defaults"), '*.default', recursive=False)

data_files = root_data_files + app_data_files + icons_data_files + default_data_files

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
    ext_modules=[moduleLibNeedleman, moduleLibScoreComputation, moduleLibInterface, moduleLibRelation],
    data_files=data_files,
    scripts=["netzob"],
    install_requires=dependencies,
    extras_require=extra_dependencies,
    dependency_links=dependency_links,
    version=release.version,
    license=release.licenseName,
    description=release.description,
    platforms=release.platforms,
    author=release.author,
    author_email=release.author_email,
    url=release.url,
    download_url=release.download_url,
    keywords=release.keywords,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: C",
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: French",
        "Topic :: Security",
        "Topic :: System :: Networking"
    ],
    long_description=README + '\n' + NEWS,
    cmdclass=CMD_CLASS,
)

