#################################################################################
##
## overview.py - Create static html file with information about TK files.
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
Create static html file with information about TK files.

The file includes small static Google maps.
See http://code.google.com/apis/maps/documentation/staticmaps/ for more information.
"""

from binascii import crc32
import datetime
import os
import getopt
from pytz import utc
import sys
import time
from urllib import FancyURLopener

from winteclib import VERSION, DATETIME_FILENAME_TEMPLATE, readTKFile, TK2File, TK3File

GMAPS_API_KEY = "ABQIAAAAzr2EBOXUKnm_jVnk0OJI7xSsTL4WIgxhMZ0ZK_kHjwHeQuOD4xQJpBVbSrqNn69S6DOTv203MQ5ufA"
""" Google Maps API key. """

MAX_POINT_COUNT = 50
""" Maximum number of path points accepted by Google. """

IMAGE_WIDTH = 250
""" Width of the image. 512 is the maximum supported by Google Maps. """

IMAGE_HEIGHT = 150
""" Height of the image. 512 is the maximum supported by Google Maps. """

DATETIME_TEMPLATE = '%Y-%m-%d %H:%M:%SZ%z'
""" Date and time format template. """

INFO_TEMPLATE = """<ul>
  <li><b>Start:</b> %s\n
  <li><b>End:</b> %s\n
  <li><b>Track points:</b> %i\n
  <li><b>Push points:</b> %i\n
%s%s
</ul>
"""
""" Track information template. """

TK1TK2_TEMPLATE = """
  <li><b>Track length:</b> %.2fkm\n
  <li><b>Track duration:</b> %02ih %02im %02is
"""
""" Additional track information template for tk1 and tk2 files. """

TK2TK3_TEMPLATE = """
  <li><b>Timezone:</b> %s
  <li><b>Comment:</b> %s
"""
""" Additional track information template for tk2 and tk3 files. """

ERROR_GIF_CRC = -529913289
""" CRC32 of Google error image. """

ERROR_GIF_LEN = 3824
""" Length of Google error image. """

googleFailed = False # pylint: disable-msg=C0103
""" Will be set to True if google image download fails. """

def processTKFile(path, filename, timezone = utc, force = False):
    """
    Handle all tracks of given TK file.
    
    @param path: The directory of the tk file.
    @param filename: The file name of the tk file.
    @param timezone: The local timezone.
    @param force: If False don't download already existing files; True otherwise.
    """
    # pylint: disable-msg=R0914
    result = {}
    tkfile = readTKFile(os.path.join(path, filename))
    for track in tkfile.tracks():
        url = "http://maps.google.com/staticmap?size=%ix%i&key=%s&path=rgb:0x0000ff,weight:5" % (IMAGE_WIDTH,
                                                                                                 IMAGE_HEIGHT,
                                                                                                 GMAPS_API_KEY)
        trackpointcount = track.getTrackPointCount()
        if trackpointcount > MAX_POINT_COUNT:
            trackpoints = []
            for i in range(0, trackpointcount, trackpointcount / MAX_POINT_COUNT):
                trackpoints.append(track.getPoint(i))
            # The range clause might result in more than MAX_POINT_COUNT elements.
            # So we limit the length to MAX_POINT_COUNT - 1 and always append the last track point.
            trackpoints = trackpoints[:MAX_POINT_COUNT - 1]
            trackpoints.append(track.getLastPoint())
            assert len(trackpoints) <= MAX_POINT_COUNT
        else:
            trackpoints = track.trackpoints()
        for point in trackpoints:
            url += "|%.6f,%.6f" % (point.getLatitude(), point.getLongitude())
        url += "&markers=%.6f,%.6f,midgreens|%.6f,%.6f,midrede" % (track.getFirstPoint().getLatitude(),
                                                                   track.getFirstPoint().getLongitude(),
                                                                   track.getLastPoint().getLatitude(),
                                                                   track.getLastPoint().getLongitude())
        filename = "%s.gif" % (track.getFirstPoint().getDateTimeString(DATETIME_FILENAME_TEMPLATE))
        getImage(os.path.join(path, filename), url, force)
        if isinstance(tkfile, TK3File):
            tk1tk2info = ""
        else:
            minutes, seconds = divmod(track.getTrackDuration(), 60)
            hours, minutes = divmod(minutes, 60)
            tk1tk2info = TK1TK2_TEMPLATE % (track.getTrackLength(), hours, minutes, seconds)
        if isinstance(tkfile, TK2File):
            tz = tkfile.getTimezone()
            tzstring = datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo = tkfile.getTimezone()).strftime("%z")
            tk2tk3info = TK2TK3_TEMPLATE % (tzstring, tkfile.getComment())
        else:
            tz = timezone
            tk2tk3info = ""
        info = INFO_TEMPLATE % (track.getFirstPoint().getDateTimeString(DATETIME_TEMPLATE, tz),
                                track.getLastPoint().getDateTimeString(DATETIME_TEMPLATE, tz),
                                trackpointcount, track.getPushPointCount(), tk1tk2info, tk2tk3info)
        result[filename] = info
    return result

def getImage(filename, url, force = False):    
    """
    Get Google image.
    
    @param filename: The file name of the image.
    @param url: The Google image url.
    @param force: If False don't download already existing files; True otherwise.
    """
    global googleFailed
    if (os.path.exists(filename) and not force) or googleFailed:
        return
    print "Download image %s." % filename
    urlopener = FancyURLopener()
    con = urlopener.open(url)
    image = con.read()
    con.close()
    if ERROR_GIF_LEN == len(image) and ERROR_GIF_CRC == crc32(image):
        print "Google returned error image. We sleep 2 seconds and try again."
        time.sleep(2)
        con = urlopener.open(url)
        image = con.read()
        con.close()
        if ERROR_GIF_LEN == len(image) and ERROR_GIF_CRC == crc32(image):
            print "Google returned again error image. Please try again later."
            googleFailed = True
    f = open(filename, "wb")
    f.write(image)
    f.close()

def usage():
    """
    Print program usage.
    """
    executable = os.path.split(sys.argv[0])[1]
    print "%s Version %s (C) 2008 Steffen Siebert <siebert@steffensiebert.de>" % (executable, VERSION)
    print "Create static html file with information about TK files.\n"
    print 'Usage: %s [-d directory]' % executable
    print "-d: Process tk files in directory."

def main():
    """
    Main method.
    """
    path = "."
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "?hd:")
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    if len(args) != 0:
        usage()
        sys.exit(1)

    for o, a in opts:
        if o in ("-h", "-?"):
            usage()
            sys.exit()
        if o == "-d":
            path = a

    result = {}
    for filename in os.listdir(path):
        _, ext = os.path.splitext(filename)
        if ext.lower() in [".tk1", ".tk2", ".tk3"]:
            result[filename] = processTKFile(path, filename)
    f = open(os.path.join(path, "index.html"), "w")
    keys = result.keys()
    keys.sort()
    f.write("<html><body>\n")
    for key in keys:
        f.write('<h2>%s</h2><table>\n' % key)
        images = result[key].keys()
        images.sort()
        for image in images:
            f.write('<tr><td>%s</td><td><img src="%s" width="%i" height="%i"/></td></tr>\n' % (result[key][image],
                                                                                               image,
                                                                                               IMAGE_WIDTH,
                                                                                               IMAGE_HEIGHT))
        f.write("</table>")
    f.write("</body></html>\n")
    f.close()
    
if __name__ == '__main__':
    main()
