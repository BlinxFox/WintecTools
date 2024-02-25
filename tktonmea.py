#################################################################################
##
## tktonmea.py - Convert gps tracklogs from Wintec TK file into a single NMEA-0183 file.
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
## Program information:                                                        ##
#################################################################################
##
## - The file name of the created nmea file contains the date and time of the
##   first trackpoint in the TK file.
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
Convert gps tracklogs from Wintec TK file into a single NMEA-0183 file.
"""

import getopt
from glob import glob
import os
import sys

from winteclib import VERSION, DATETIME_FILENAME_TEMPLATE, readTKFile, calculateVincentyDistance, createOutputFile, \
    TK1File

# pylint: disable-msg=C0301

GPRMC_TEMPLATE = "$GPRMC,%(timeString)s,A,%(lat)02i%(latMinutes)02.6f,%(ns)s,%(lon)03i%(lonMinutes)02.6f,%(ew)s,%(speed)2.1f,%(bearing)i.0,%(dateString)s,,,,"
"""
RMC - Recommended Minimum Navigation Information::

                                                            12
        1         2 3       4 5        6 7   8   9    10  11|
        |         | |       | |        | |   |   |    |   | |
 $--RMC,hhmmss.ss,A,llll.ll,a,yyyyy.yy,a,x.x,x.x,xxxx,x.x,a*hh<CR><LF>

 Field Number: 
  1) UTC Time
  2) Status, V = Navigation receiver warning
  3) Latitude
  4) N or S
  5) Longitude
  6) E or W
  7) Speed over ground, knots
  8) Track made good, degrees true
  9) Date, ddmmyy
 10) Magnetic Variation, degrees
 11) E or W
 12) Checksum 
"""

GPGGA_TEMPLATE = "$GPGGA,%(timeString)s,%(lat)02i%(latMinutes)02.6f,%(ns)s,%(lon)03i%(lonMinutes)02.6f,%(ew)s,1,,,%(altitude)i,M,,M,,"
"""
GGA - Global Positioning System Fix Data, Time, Position and fix related data fora GPS receiver::

                                                      11
        1         2       3 4        5 6 7  8   9  10 |  12 13  14   15
        |         |       | |        | | |  |   |   | |   | |   |    |
 $--GGA,hhmmss.ss,llll.ll,a,yyyyy.yy,a,x,xx,x.x,x.x,M,x.x,M,x.x,xxxx*hh<CR><LF>

 Field Number: 
  1) Universal Time Coordinated (UTC)
  2) Latitude
  3) N or S (North or South)
  4) Longitude
  5) E or W (East or West)
  6) GPS Quality Indicator,
     0 - fix not available,
     1 - GPS fix,
     2 - Differential GPS fix
  7) Number of satellites in view, 00 - 12
  8) Horizontal Dilution of precision
  9) Antenna Altitude above/below mean-sea-level (geoid) 
 10) Units of antenna altitude, meters
 11) Geoidal separation, the difference between the WGS-84 earth
     ellipsoid and mean-sea-level (geoid), "-" means mean-sea-level
     below ellipsoid
 12) Units of geoidal separation, meters
 13) Age of differential GPS data, time in seconds since last SC104
     type 1 or 9 update, null field when DGPS is not used
 14) Differential reference station ID, 0000-1023
 15) Checksum 
"""

def nmeaChecksum(string):
    """
    Calculate checksum of NMEA protocol string.
    
    @param string: The protocol string to calculate checksum for.
    @return: The NMEA checksum.
    """
    checksum = 0
    for char in string[1:]:
        checksum = checksum ^ ord(char)
    return "*%02X" % checksum

def createNmeaFile(tkfiles, outputFile):
    """
    Create nmea file.
    
    @param tkfiles: A list of TK files with track data.
    @param outputFile: The nmea file handle.
    """
    for tkfile in tkfiles:
        for track in tkfile.tracks():
            previousPoint = None
            for trackpoint in track.trackpoints():
                values = {}
                dateTime = trackpoint.getDateTime()
                values["dateString"] = dateTime.strftime('%d%m%y')
                values["timeString"] = dateTime.strftime('%H%M%S')
                latitude = trackpoint.getLatitude()
                longitude = trackpoint.getLongitude()
                values["lat"] = int(latitude)
                values["lon"] = int(longitude)
                values["altitude"] = trackpoint.getAltitude()
                values["speed"] = 0
                values["bearing"] = 0
                if previousPoint:
                    distance, values["bearing"] = calculateVincentyDistance(previousPoint.getLatitude(),
                                                                            previousPoint.getLongitude(),
                                                                            latitude, longitude)
                    timedelta = dateTime - previousPoint.getDateTime()
                    time = timedelta.days * 24 * 60 * 60 + timedelta.seconds
                    if time != 0:
                        # Speed in knots. 1 knot = 1.852 kilometers per hour
                        values["speed"] = distance / (time / float(60*60)) / 1.852 
                values["latMinutes"] = (latitude - int(latitude)) * 60.0
                values["lonMinutes"] = (longitude - int(longitude)) * 60.0
                values["ns"] = "N" if latitude >= 0 else "S"
                values["ew"] = "E" if longitude >= 0 else "W"
                line = GPRMC_TEMPLATE % values
                outputFile.write(line + nmeaChecksum(line) + "\n")
                line = GPGGA_TEMPLATE % values
                outputFile.write(line + nmeaChecksum(line) + "\n")
                previousPoint = trackpoint

def usage():
    """
    Print program usage.
    """
    executable = os.path.split(sys.argv[0])[1]
    print("%s Version %s (C) 2008 Steffen Siebert <siebert@steffensiebert.de>" % (executable, VERSION))
    print("Convert gps tracklogs from Wintec TK files into a single NMEA-0183 file.\n")
    print("Usage: %s [-d outputdir] [-o filename] <tk files>" % executable)
    print("-d: Use output directory.")
    print("-o: Use output filename.")

def main():
    """
    The main method.
    """
    # pylint: disable-msg=R0912
    outputDir = None
    filename = None
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "?hd:o:")
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
        if o == "-d":
            outputDir = a
        if o == "-o":
            filename = a

    if outputDir and not os.path.exists(outputDir):
        print("Output directory %s doesn't exist!" % outputDir)
        sys.exit(3)

    tkfiles = []
    for arg in args:
        for tkFileName in glob(arg):
            tkfiles.append(readTKFile(tkFileName))

    tkfiles.sort(key=lambda x: x.getFirstTrackpoint().getDateTime())
    
    try:
        if len(tkfiles) > 1:
            dateString = tkfiles[0].getFirstTrackpoint().getDateTimeString()
            dateString2 = tkfiles[-1].getFirstTrackpoint().getDateTimeString()
            outputFile = createOutputFile(outputDir, filename, '%s-%s#%03i.nmea', (dateString, dateString2,
                                                                                  len(tkfiles)))
        else:
            if isinstance(tkfiles[0], TK1File):
                dateString = tkfiles[0].getFirstTrackpoint().getDateTimeString()
                dateString2 = tkfiles[0].getLastTrackpoint().getDateTimeString()
                outputFile = createOutputFile(outputDir, filename, '%s-%s#%03i.nmea', (dateString, dateString2,
                                                                                      tkfiles[0].getTrackCount()))
            else:
                dateString = tkfiles[0].getFirstTrackpoint().getDateTimeString(DATETIME_FILENAME_TEMPLATE)
                outputFile = createOutputFile(outputDir, filename, '%s.nmea', dateString)
        if outputFile == None:
            return
        createNmeaFile(tkfiles, outputFile)
    finally:
        if outputFile != None:
            outputFile.close()

if __name__ == "__main__":
    main()
