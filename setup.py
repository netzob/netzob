#!/usr/bin/env python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+----------------------------------------------------------------------------
#| Global Imports
#+----------------------------------------------------------------------------
import sys
import os
import uuid
import subprocess
sys.path.insert(0, 'src/')
from setuptools import setup, Extension, find_packages
from netzob import release
from resources.sdist.manpage_command import manpage_command
from resources.sdist.pybuild_command import pybuild_command
from resources.sdist.test_command import test_command
from resources.sdist.utils import find_data_files, opj

#+----------------------------------------------------------------------------
#| Definition of variables
#+----------------------------------------------------------------------------
# Path to the resources
staticResourcesPath = opj("resources", "static")
netzobStaticResourcesPath = opj(staticResourcesPath, "netzob")
pluginsStaticResourcesPath = opj(staticResourcesPath, "plugins")

#+----------------------------------------------------------------------------
#| Definition of the extensions
#+----------------------------------------------------------------------------
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

# Regex path
regexPath = opj(libPath, "libRegex")
pyRegexPath = opj(regexPath, "Py_lib")

# Tools path
toolsPath = opj(libPath, "tools")

# Generate the random binary identifier BID
macros = [('BID', '"{0}"'.format(str(uuid.uuid4())))]

# Module Needleman
moduleLibNeedleman = Extension('netzob._libNeedleman',
                               # extra_compile_args=["-fopenmp"],
                               # extra_link_args=["-fopenmp"],
                               sources=[opj(interfacePath, "Interface.c"),
                                        opj(pyInterfacePath, "libInterface.c"),
                                        opj(pyNeedlemanPath, "libNeedleman.c"),
                                        opj(needlemanPath, "Needleman.c"),
                                        opj(needlemanPath, "scoreComputation.c"),
                                        opj(argsFactoriesPath, "factory.c"),
                                        opj(regexPath, "regex.c"),
                                        opj(regexPath, "manipulate.c"),
                                        opj(toolsPath, "getBID.c")],
                               define_macros=macros,
                               include_dirs=includes)

# Module ScoreComputation
moduleLibScoreComputation = Extension('netzob._libScoreComputation',
                                      # extra_compile_args=["-fopenmp"],
                                      # extra_link_args=["-fopenmp"],
                                      sources=[opj(needlemanPath, "scoreComputation.c"),
                                               opj(pyNeedlemanPath, "libScoreComputation.c"),
                                               opj(needlemanPath, "Needleman.c"),
                                               opj(interfacePath, "Interface.c"),
                                               opj(pyInterfacePath, "libInterface.c"),
                                               opj(argsFactoriesPath, "factory.c"),
                                               opj(regexPath, "regex.c"),
                                               opj(regexPath, "manipulate.c"),
                                               opj(toolsPath, "getBID.c")],
                                      define_macros=macros,
                                      include_dirs=includes)

# Module Interface
moduleLibInterface = Extension('netzob._libInterface',
                               sources=[opj(interfacePath, "Interface.c"),
                                        opj(pyInterfacePath, "libInterface.c"),
                                        opj(toolsPath, "getBID.c")],
                               define_macros=macros,
                               include_dirs=includes)

# Module Regex
moduleLibRegex = Extension('netzob._libRegex',
                           sources=[opj(regexPath, "regex.c"),
                                    opj(pyRegexPath, "libRegex.c"),
                                    opj(regexPath, "manipulate.c"),
                                    opj(toolsPath, "getBID.c")],
                           define_macros=macros,
                           include_dirs=includes)


#+----------------------------------------------------------------------------
#| Definition of the dependencies
#+----------------------------------------------------------------------------
dependencies = [
    'babel',
    'bitarray',
    'lxml',
    'httplib2',
]

extra_dependencies = {
    'docs': ['Sphinx>=1.1.3']
}

dependency_links = []

#+----------------------------------------------------------------------------
#| Extensions in the build operations (create manpage, i18n, ...)
#+----------------------------------------------------------------------------
CMD_CLASS = {
    'build_py': pybuild_command,
    'build_manpage': manpage_command,
    'test': test_command
}

#+----------------------------------------------------------------------------
#| Activate Babel (i18n) if available
#+----------------------------------------------------------------------------
try:
    import babel
    from babel.messages import frontend as babel
    from distutils.command.build import build

    CMD_CLASS.update({'compile_catalog': babel.compile_catalog,
                      'extract_messages': babel.extract_messages,
                      'init_catalog': babel.init_catalog,
                      'update_catalog': babel.update_catalog})

    build.sub_commands.append(('compile_catalog', None))
except ImportError:
    print "Info: Babel support unavailable, translations not available"


root_data_files = find_data_files(opj("share", "netzob"), netzobStaticResourcesPath, 'logo.png', recursive=False)
app_data_files = find_data_files(opj("share", "applications"), netzobStaticResourcesPath, 'netzob.desktop', recursive=False)
icons_data_files = find_data_files(opj("share", "netzob", "icons"), opj(netzobStaticResourcesPath, "icons"), '*.png')
default_data_files = find_data_files(opj("share", "netzob", "defaults"), opj(netzobStaticResourcesPath, "defaults"), '*.default', recursive=False)
xsds_data_files = find_data_files(opj("share", "netzob", "xsds"), opj(netzobStaticResourcesPath, "xsds"), '*.xsd')
locale_data_files = find_data_files(opj("share", "locale"), opj(netzobStaticResourcesPath, "locales"), '*.mo')
ui_data_files = find_data_files(opj("share", "netzob", "ui"), opj(netzobStaticResourcesPath, "ui"), '*.glade', '*.ui')

data_files = root_data_files + app_data_files + icons_data_files + default_data_files + xsds_data_files + locale_data_files + ui_data_files

# Extract the long description from README.rst and NEWS.rst files
README = open('README.rst', 'rt').read()
NEWS = open('NEWS.rst', 'rt').read()

#+----------------------------------------------------------------------------
#| Definition of Netzob for setup
#+----------------------------------------------------------------------------
setup(
    name=release.name,
    packages=find_packages(where='src'),
    package_dir={
        "netzob": opj("src", "netzob"),
        "netzob_plugins": opj("src", "netzob_plugins"),
    },
    ext_modules=[moduleLibNeedleman, moduleLibScoreComputation, moduleLibInterface, moduleLibRegex],
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
    entry_points="""[babel.extractors]
        glade = resources.sdist.babel_extract:extract_glade
    """,
    # Files that should be scanned by Babel (if available)
    message_extractors={
        'src': [
            ('**.py', 'python', None)
        ],
        'resources': [
            ('**.glade', 'glade', None)
        ]
    },
)

if len(sys.argv) > 1:
    command = sys.argv[1]
else:
    command = None
if command in ["build", "develop", "install", "clean"]:
    root_dir = os.getcwd()
    main_plugin_dir = root_dir + os.sep + "src" + os.sep + "netzob_plugins" + os.sep
    plugin_categories = ["Capturers", "Importers", "Exporters"]
    for plugin_category in plugin_categories:
        plugin_dir = main_plugin_dir + plugin_category + os.sep
        plugin_list = os.listdir(plugin_dir)
        for plugin_name in plugin_list:
            if plugin_name != "__init__.py" and plugin_name != "__init__.pyc":
                plugin_fullpath = plugin_dir + plugin_name
                print ""
                print "------------------------------"
                print "Handling plugin: " + plugin_name
                print "Plugin path: " + plugin_fullpath
                os.chdir(plugin_fullpath)
                cmd = "{0} setup.py {1}".format(sys.executable, " ".join(sys.argv[1:]))
                print "Using following command: " + cmd
                os.system(cmd)
