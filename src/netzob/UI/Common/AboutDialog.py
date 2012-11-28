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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gi.repository import Gtk, GdkPixbuf
import gi
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
gi.require_version('Gtk', '3.0')
import os
from netzob import release
from gettext import gettext as _


#+----------------------------------------------
#| AboutDialog:
#|     Shows the about dialog of Netzob
#+----------------------------------------------
class AboutDialog(object):
    """Static class which includes the method
    to display the about dialog of Netzob."""

    @staticmethod
    def display(parent=None):
        about = Gtk.AboutDialog(parent=parent)
        about.set_program_name(release.appname)
        about.set_version(release.version)
        about.set_copyright(release.copyright)
        if release.versionName is not None:
            about.set_comments("--{0}--\n{1}".format(release.versionName, release.description))
        else:
            about.set_comments(release.description)
        about.set_license(_("Netzob is released under the terms of the {0} license.\n\n{1}").format(release.licenseName, release.license))
        about.set_website(release.url)
        about.set_translator_credits(release.translator_credits)
        about.set_authors(release.contributors)

        logoPath = os.path.join(ResourcesConfiguration.getStaticResources(), "logo.png")
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file_at_size(logoPath, 200, 200))
        about.run()
        about.destroy()
