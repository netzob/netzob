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

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
import uuid
import sys
import os
from abc import ABCMeta, abstractmethod, abstractproperty
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import pkg_resources

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.Extensions.NetzobExtension import NetzobExtension
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


#+---------------------------------------------------------------------------+
#| NetzobPlugin:
#|     Abstract class every Netzob's plugin must subclass to be registered
#+---------------------------------------------------------------------------+
class NetzobPlugin(object):
    __metaclass__ = ABCMeta
    PLUGIN_FLAG_REJECTED = "rejected"
    instances = {}

    # Every plugin is an extended singleton (cf Borg)
    def __new__(cls, *args, **kargs):
        if NetzobPlugin.instances.get(cls) is None:
            NetzobPlugin.instances[cls] = object.__new__(cls, *args, **kargs)
        return NetzobPlugin.instances[cls]

    def __init__(self, netzob):
        # Generate a unique ID
        self.id = uuid.uuid4()
        self.netzob = netzob

    def getNetzob(self):
        return self.netzob

    __plugin_name__ = abstractproperty()
    __plugin_version__ = abstractproperty()
    __plugin_description__ = abstractproperty()
    __plugin_author__ = abstractproperty()

    def getName(self):
        return self.__plugin_name__

    def getVersion(self):
        return self.__plugin_version__

    def getDescription(self):
        return self.__plugin_description__

    def getAuthor(self):
        return self.__plugin_author__

    @abstractmethod
    def getEntryPoints(self):
        raise NotImplementedError("The plugin class doesn't implement method 'getEntryPoints'")

    def getNetzobStaticResourcesPath(self):
        """Computes and returns the path to the static
        resources associated with netzob"""
        return ResourcesConfiguration.getStaticResources()

    def getPluginStaticResourcesPath(self):
        """Computes and returns the path to the static
        resources associated with the current plugin"""
        pluginsPath = ResourcesConfiguration.getPluginsStaticResources()
        pluginPath = os.path.join(pluginsPath, self.getName())
        if os.path.isdir(pluginPath):
            return pluginPath
        else:
            logging.warning("The computed path ({0}) is not a valid directory.".format(pluginPath))
            return None

    @classmethod
    def getLoadedInstance(cls):
        try:
            return NetzobPlugin.instances[cls]
        except Exception, e:
            logging.warning("Impossible to retrieve loaded instance of plugin ({0})".format(e))

    @staticmethod
    def getLoadedPlugins(pluginClass):
        plugins = []
        classesSeen = []
        subs = pluginClass.__subclasses__()
        classesSeen.extend(subs)
        for sub in subs:
            # Retrieve all the subclasses of current class
            subsubs = sub.__subclasses__()
            # We only consider a plugin if it was loaded
            if sub in NetzobPlugin.instances:
                try:
                    # We verify the plugin has not been rejected (by the PluginChecker)
                    if getattr(sub.getLoadedInstance(), NetzobPlugin.PLUGIN_FLAG_REJECTED) is False:
                        plugins.append(sub.getLoadedInstance())
                except Exception, e:
                    pass
            else:
                # We retrieve possible plugin childs
                for subsub in subsubs:
                    if not subsub in classesSeen:
                        subs.append(subsub)

        return plugins

    @staticmethod
    def getLoadedPluginsExtension(extensionClass):
        pluginExtensions = []
        logging.debug("Get plugin by extension")
        for plugin in NetzobPlugin.getLoadedPlugins(NetzobPlugin):
            try:
                if plugin.getEntryPoints() is not None:
                    for pluginExtensionClass in plugin.getEntryPoints():
                        logging.debug("Plugin {0} has entry point {1}".format(
                            plugin.__class__.__name__,
                            pluginExtensionClass.__class__.__name__))
                        if issubclass(pluginExtensionClass.__class__, extensionClass):
                            pluginExtensions.append(pluginExtensionClass)
                        else:
                            logging.debug("oups not {0}".format(pluginExtensionClass))
            except Exception, e:
                logging.debug("Error while loading an extension : {0}".format(e))

        return pluginExtensions

    @staticmethod
    def loadPlugins(netzob):
        from netzob.Common.Plugins.PluginChecker import PluginChecker
        logging.debug("Loading plugins:")
        for entrypoint in pkg_resources.iter_entry_points('netzob.plugins'):
            try:
                plugin_class = entrypoint.load()
                if not PluginChecker.isValidPlugin(plugin_class):
                    logging.warning("Plugin implemented in class {0} has been rejected by the plugin checker (invalid).".format(plugin_class))
                    NetzobPlugin.unloadPlugin(plugin_class)
                else:
                    # We instantiate the plugin
                    instanciatedPlugin = plugin_class(netzob)
                    # We add a flag on it
                    setattr(instanciatedPlugin, NetzobPlugin.PLUGIN_FLAG_REJECTED, False)
                    logging.debug("Plugin {0} (v.{1}) loaded.".format(instanciatedPlugin.getName(), instanciatedPlugin.getVersion()))
            except Exception, e:
                logging.exception("Impossible to load plugin declared in entrypoint {0} : {1}".format(entrypoint, e))
        logging.debug("Plugins are loaded.")

    @staticmethod
    def unloadPlugin(pluginClass):
        logging.debug("Unloading plugin {0}".format(pluginClass))
        setattr(pluginClass, NetzobPlugin.PLUGIN_FLAG_REJECTED, True)
