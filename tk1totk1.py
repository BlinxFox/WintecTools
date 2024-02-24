#################################################################################
##
## tk1totk1.py - Read tk1 file, recalculate the footer data and create a tk1
## file with a generic name.
##
## Copyright (c) 2008 Steffen Siebert <siebert@steffensiebert.de>
##
#################################################################################
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
##
#################################################################################
## Requirements                                                                ##
#################################################################################
##
## Python 2.5 or later:
## <http://www.python.org>
##
#################################################################################
## Support                                                                     ##
#################################################################################
##
## The latest version of the wintec tools is always available from my homepage:
## <http://www.SteffenSiebert.de/soft/python/wintec_tools.html>
##
## If you have bug reports, patches or some questions, just send a mail to
## <wintec_tools@SteffenSiebert.de>
##
#################################################################################

"""
Read tk1 file, recalculate the footer data and create a tk1 file with a generic name.
"""

import getopt
import os
import sys

from winteclib import VERSION, TK1File, createOutputFile

def createTK1File(tk1Source):    
    """
    Create new L{TK1File} from existing L{TK1File} and recalculate footer values.
    The export timestring remains unchanged.
     
    @param tk1Source: The existing tk1 file.
    @return: The new tk1 file.
    """
    tk1Target = TK1File()
    tk1Target.init(tk1Source.getDeviceName(), tk1Source.getDeviceInfo(), tk1Source.getDeviceSerial(),
                   tk1Source.trackdata, tk1Source.getExportTimeString())
    return tk1Target

def usage():
    """
    Print program usage.
    """
    executable = os.path.split(sys.argv[0])[1]
    print "%s Version %s (C) 2008 Steffen Siebert <siebert@steffensiebert.de>" % (executable, VERSION)
    print "Read tk1 file, recalculate the footer data and create a tk1 file with a generic name.\n"
    print 'Usage: %s [-d directory] [-o filename] [--delete] <tk1 file>' % executable
    print "-d: Use output directory."
    print "-o: Use output filename."
    print "--delete: Delete source file after successful processing."

def main():
    """
    Main method.
    """
    deleteSource = False
    outputDir = None
    filename = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "?hd:o:", "delete")
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    if len(args) != 1:
        usage()
        sys.exit(1)

    for o, a in opts:
        if o in ("-h", "-?"):
            usage()
            sys.exit()
        if o == "-d":
            outputDir = a
        if o == "-o":
            filename = a
        if o == "--delete":
            deleteSource = True

    if filename and os.path.exists(os.path.join(outputDir if outputDir else ".", filename)):
        print "Output file %s already exists!" % filename
        sys.exit(4)

    tk1Source = TK1File()
    f = open(args[0], "rb")
    tk1Source.read(f)
    f.close()

    tk1Target = createTK1File(tk1Source)

    f = createOutputFile(outputDir, filename, "%s", tk1Target.createFilename(), flags = "wb")
    tk1Target.write(f)
    f.close()
    
    if deleteSource:
        os.remove(args[0])

if __name__ == "__main__":
    main()
