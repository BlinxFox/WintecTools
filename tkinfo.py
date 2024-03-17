#################################################################################
##
## tkinfo.py - Display TK file information and set the user comment string for .tk2/.tk3 files.
##
## Copyright (c) 2008 Steffen Siebert <siebert@steffensiebert.de>
##
## Ported to Python 3 by BlinxFox
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
## Python 3.10 or later:
## <http://www.python.org>
##
#################################################################################
## Support                                                                     ##
#################################################################################
##
## The latest version of the wintec tools is available on Github
## <https://github.com/BlinxFox/WintecTools>
##
## If you have bug reports, patches or some questions, please create an 
## issue on Github:
## <https://github.com/BlinxFox/WintecTools>
##
#################################################################################

"""
Display TK file information and set the user comment string for .tk2/.tk3 files.
"""

import getopt
from glob import glob
import os
import sys

from winteclib import VERSION, readTKFile, TK1File, parseTimezone, determineTimezone

def usage():
    """
    Print program usage.
    """
    executable = os.path.split(sys.argv[0])[1]
    print("%s Version %s (C) 2008 Steffen Siebert <siebert@steffensiebert.de>" % (executable, VERSION))
    print("Display TK file information and optionally set user comment string and/or timezone for .tk2/.tk3 files.\n")
    print('Usage: %s [-c "user comment"] [-t +hh:mm|--autotz] <tk files>' % executable)
    print("-c: User comment string to store in the .tk2/tk3 header.")
    print("-t: .tk2/.tk3: Set timezone for local time (offset to UTC). .tk1: Ignored.")
    print("--autotz: .tk2/.tk3: Determine timezone from first trackpoint. .tk1: Ignored.")

def main():
    """
    Main method.
    """
    # pylint: disable-msg=R0912
    comment = None
    timezone = None
    autotimezone = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "?hc:t:", "autotz")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    if len(args) != 1:
        usage()
        sys.exit(1)
    
    for o, a in opts:
        if o in ("-h", "-?"):
            usage()
            sys.exit()
        
        if o == "-c":
            comment = a
        if o == "-t":
            timezone = parseTimezone(a)
            if timezone == None:
                print("Timzone string doesn't match pattern +hh:mm!")
                sys.exit(4)
        if o == "--autotz":
            autotimezone = True
    
    for arg in args:
        for tkFileName in glob(arg):
            tkfile = readTKFile(tkFileName)
            modified = False
            if not isinstance(tkfile, TK1File):
                if comment != None:
                    tkfile.setComment(comment)
                    modified = True
                if timezone != None:
                    tkfile.setTimezone(timezone)
                    modified = True
                if autotimezone == True:
                    tkfile.setTimezone(determineTimezone(tkfile.getFirstTrackpoint()))
                    modified = True
            if modified:
                f = open(tkFileName, "wb")
                tkfile.write(f)
                f.close()
            print("Filename: %s" % tkFileName)
            print("Canonical filename: %s" % tkfile.createFilename())
            print(tkfile)

if __name__ == "__main__":
    main()
