#################################################################################
##
## tk1split.py - Split .tk1 file into .tk2 and/or .tk3 files.
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
Split .tk1 file into .tk2 and/or .tk3 files.
"""

import getopt
from glob import glob
import os.path
from pytz import utc
import sys

from winteclib import VERSION, readTKFile, parseTimezone, TK1File, TK2File, TK3File

def splitTK1(tk1File, comment = ""):
    """
    Split TK1 file and return array of L{TK2File} and array of L{TK3File} objects.

    @param tk1File: The L{TK1File} to split.
    @return: Tuple of two arrays.
    """
    tk2Files = []
    tk3Files = []

    for footerCount in range(tk1File.getTrackCount()):
        footerEntry = tk1File.getFooterEntry(footerCount)
        track = tk1File.getTrack(footerEntry)
        pushpointCount = track.getPushPointCount()
        length = int(footerEntry.getFooterTrackLength() * 1000)
        tk2File = TK2File()
        tk2File.init(tk1File.getDeviceName(), tk1File.getDeviceInfo(), tk1File.getDeviceSerial(), 
                     tk1File.getExportTimeString(), track.getTrackData(), footerEntry.getFooterTrackDuration(),
                     length, pushpointCount, comment, track.getTimezone())
        tk2Files.append(tk2File)

        if pushpointCount > 0:
            tk3File = TK3File()
            tk3File.init(tk1File.getDeviceName(), tk1File.getDeviceInfo(), tk1File.getExportTimeString(),
                         track.getTrackData(), comment, track.getTimezone())
            tk3Files.append(tk3File)
    return tk2Files, tk3Files

def writeFile(tkFile, directory = None):
    """
    Create TK file.
     
    @param tkFile: The tk object to write.
    """
    fileName = tkFile.createFilename()
    if directory:
        fileName = os.path.join(directory, fileName)
    print("Create %s" % fileName)
    f = open(fileName, 'wb')
    tkFile.write(f)
    f.close()

def usage():
    """
    Print program usage.
    """
    executable = os.path.split(sys.argv[0])[1]
    print("%s Version %s (C) 2008 Steffen Siebert <siebert@steffensiebert.de>" % (executable, VERSION))
    print("Split .tk1 files into .tk2 and/or .tk3 files.\n")
    print('Usage: %s [-2] [-3] [-d directory] [--d2 directory] [--d3 directory] [-c "user comment"]' % executable,)
    print("[-t +hh:mm|--autotz] <tk1 files>")
    print("-2: Create .tk2 files.")
    print("-3: Create .tk3 files.")
    print("-d: Use output directory for tk2 and tk3 files.")
    print("--d2: Use output directory for tk2 files.")
    print("--d3: Use output directory for tk3 files.")
    print("-c: User comment string to store in the .tk2/tk3 header.")
    print("-t: Use timezone for local time (offset to UTC).")
    print("--autotz: Determine timezone from first trackpoint.")

def main():
    """
    Main method.
    """
    # pylint: disable-msg=R0912,R0914,R0915
    
    createTk2 = False
    createTk3 = False
    tk2OutputDir = None
    tk3OutputDir = None
    timezone = utc
    autotimezone = False
    comment = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "?h23d:t:c:", ["autotz", "d2=", "d3="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    if len(args) == 0:
        usage()
        sys.exit(1)

    for o, a in opts:
        if o in ("-h", "-?"):
            usage()
            sys.exit()
        if o == "-2":
            createTk2 = True
        if o == "-3":
            createTk3 = True
        if o == "-d":
            tk2OutputDir = tk3OutputDir = a
        if o == "--d2":
            tk2OutputDir = a
        if o == "--d3":
            tk3OutputDir = a
        if o == "-t":
            timezone = parseTimezone(a)
            if timezone == None:
                print("Timzone string doesn't match pattern +hh:mm!")
                sys.exit(4)
        if o == "-c":
            comment = a
        if o == "--autotz":
            autotimezone = True
    
    # if neither -2 nor -3 is specified, create both file types.
    if not createTk2 and not createTk3:
        createTk2 = createTk3 = True

    if tk2OutputDir and not os.path.exists(tk2OutputDir):
        print("Output directory %s doesn't exist!" % tk2OutputDir)
        sys.exit(3)
    if tk3OutputDir and not os.path.exists(tk3OutputDir):
        print("Output directory %s doesn't exist!" % tk3OutputDir)
        sys.exit(3)

    filelist = []
    for arg in args:
        filelist += glob(arg)

    for tk1FileName in filelist:
        print("Reading %s" % tk1FileName)
        tk1File = readTKFile(tk1FileName)
        if tk1File == None:
            print("Can't read %s!" % tk1FileName)
        elif not isinstance(tk1File, TK1File):
            print("%s is not a .tk1 file!" % tk1FileName)
        else:
            print("Track count: %i" % tk1File.getTrackCount())
            tk1File.setAutotimezone(autotimezone)
            tk1File.setTimezone(timezone)
            tk2Files, tk3Files = splitTK1(tk1File, comment)
            if createTk2:
                for tkFile in tk2Files:
                    writeFile(tkFile, tk2OutputDir)
            if createTk3:
                for tkFile in tk3Files:
                    writeFile(tkFile, tk3OutputDir)

if __name__ == "__main__":
    main()
