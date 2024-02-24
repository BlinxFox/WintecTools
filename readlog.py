#################################################################################
##
## readlog.py - Read gps tracklogs from Wintec WBT-201 or WSG-1000 and write
##              them into a .tk1 file.
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
## Required Python libraries:
## uspp-1.0 from http://ibarona.googlepages.com/uspp
## For usage with windows:
## pywin32 from http://sourceforge.net/projects/pywin32/ (required by uspp)
##
#################################################################################
## Support                                                                     ##
#################################################################################
##
## The latest version of readlog is always available from my homepage:
## <http://www.SteffenSiebert.de/soft/python/wintec_tools.html>
##
## If you have bug reports, patches or some questions, just send a mail to
## <wintec_tools@SteffenSiebert.de>
##
#################################################################################

"""
Read gps tracklogs from Wintec WBT-201 or WSG-1000 and write them into a .tk1 file.
"""

import getopt
import os
import sys
import time
import uspp

from winteclib import VERSION, Trackpoint, TK1File, createOutputFile

BLOCKSIZE = 4096
BAUDRATE = 57600
READ_TIMEOUT = 3000 # 3 seconds

def isChecksumCorrect(buf, checksum):
    """
    Validates buffer checksum.
    
    @param buf: The buffer to check.
    @param checksum: The expected checksum.
    @return True if checksum matches; False otherwise.
    """
    cs = 0
    for char in buf:
        cs = cs ^ ord(char)
    return cs == int(checksum, 16)

def getLogString(tty, debug):
    """
    Read line from tty and return value after last comma.
    
    @param tty: the tty device to read from.
    @param debug: If True print line read from tty.
    @return value after the last comma in read line.
    """
    line = tty.readline()
    if debug:
        print line
    return line.split(",")[-1].strip()

def getLogValue(tty, debug):
    """
    Read line from tty and return value after last comma as int.
    
    @param tty: the tty device to read from.
    @param debug: If True print line read from tty.
    @return int value after the last comma in read line.
    """
    return int(getLogString(tty, debug))

def toHex(s):
    """
    Convert string to hex values.
    
    @param s: string to convert.
    @return: string with hex values.
    """
    lst = []
    for ch in s:
        lst.append("0x%02X" % ord(ch))
    return reduce(lambda x, y: x + " " + y, lst)

def readLog(tty, password, debug):
    """
    Read log from gps device.
    
    @param tty: The serial device handle for the gps device.
    @param password: The password of the gps device or None if no password set.
    @param debug: True if debug information should be printed; False otherwise.
    """
    # pylint: disable-msg=R0912,R0914,R0915

    # Make sure that bypass mode is enabled.
    tty.write("@AL,02,01\n")
    tty.readline()

    print "Enter command mode"
    # Try to switch WBT-201 into command mode.
    if password:
        tty.write("@AL,1%s\n" % password)
    else:
        tty.write("@AL\n")

    # Try to switch WSG-1000 into command mode.
    tty.write("@AL,2,3\n")
    tty.write("@AL,2,3\n")

    # All supported devices should be now in command mode.
    ready = 0
    retrycount = 50
    tk1 = None
    while 1:
        try:
            line = tty.readline()
        except uspp.SerialPortException:
            if password == None:
                print "Device seem to be password protected!"
                print "Please provide the correct password using option -p"
                return None
            else:
                print "Device seem not to be password protected!"
                print "Please don't use option -p"
                return None
        if debug:
            print line
            print toHex(line)
        if "@AL,LoginOK" in line:
            ready = 1
            break
        if "@AL,PassworError" in line:
            if password:
                print "Wrong Password"
            else:
                print "Device is password protected!"
                print "Please provide the correct password using option -p"
            return None
        retrycount = retrycount - 1
        if retrycount <= 0:
            break

    if ready == 1:
        # Skip all remaining output.
        time.sleep(1)
        while tty.inWaiting() > 0:
            tty.readline()

        # Read information from device.
        tty.write("@AL,07,01\n")
        devicename = getLogString(tty, debug)
        tty.write("@AL,07,02\n")
        deviceinfo = getLogString(tty, debug)
        tty.write("@AL,07,03\n")
        deviceserial = getLogString(tty, debug)
        tty.write("@AL,05,01\n")
        logstart = getLogValue(tty, debug)
        tty.write("@AL,05,02\n")
        logend = getLogValue(tty, debug)
        tty.write("@AL,05,09\n")
        logareastart = getLogValue(tty, debug)
        tty.write("@AL,05,10\n")
        logareaend = getLogValue(tty, debug)

        print "Logarea: %s-%s (%08x-%08x)" % (logareastart, logareaend, logareastart, logareaend)
        print "Log: %s-%s (%08x-%08x)" % (logstart, logend, logstart, logend)

        if logstart == logend:
            print "No logdata available for export"
            return None

        logcapacy = (logareaend - logareastart) / Trackpoint.TRACKPOINTLEN
        lastsection = 0
        if logcapacy < BLOCKSIZE:
            readcount = logcapacy
            lastsection = 1
        elif logstart < logend and logstart + BLOCKSIZE >= logend:
            readcount = logend - logstart
            lastsection = 1
        else:
            readcount = BLOCKSIZE
        readstart = int(logstart)
        tracklog = ''
        retryCount = 5

        while True:
            assert readcount > 0
            print "Read buffer at %s (%s Bytes)" % (readstart, readcount)
            tty.write("@AL,05,03,%i\n" % readstart)
            try:
                buf = tty.read(readcount)
            except uspp.SerialPortException:
                print "Buffer read timeout, retrying"
                continue
            line = tty.readline()
            if debug:
                print line
            _, _, checksum, blockstart = line.split(",")
            blockstart = int(blockstart.strip())
            if debug:
                print "Expected block checksum: " + checksum
            if not (readstart == blockstart and isChecksumCorrect(buf, checksum)):
                retryCount = retryCount - 1
                if retryCount <= 0:
                    break
                else:
                    print "Buffer read error, retrying"
                    tty.flush()
                    continue
            else:
                tracklog = tracklog + buf
                retryCount = 5
            tty.flush()
            if lastsection == 1 or len(buf) == 0:
                break
            readstart = readstart + len(buf)
            if readstart >= logareaend:
                readstart = logareastart
            if (readstart < logend) and (readstart + BLOCKSIZE >= logend):
                readcount = logend - readstart
                lastsection = 1

        # Create TK1File from data
        tk1 = TK1File()
        tk1.init(devicename, deviceinfo, deviceserial, tracklog)
    else:
        print "Can't switch into command mode!"
    return tk1

def usage():
    """
    Print program usage.
    """
    executable = os.path.split(sys.argv[0])[1]
    print "%s Version %s (C) 2008 Steffen Siebert <siebert@steffensiebert.de>" % (executable, VERSION)
    print "Read gps tracklogs from Wintec WBT-201 or WSG-1000 and write them into a .tk1 file.\n"
    print "Usage: %s [-v] [-p password] [-d outputdir] [-o filename] [--delete] <serial port>" % executable
    print "-v: Print debug info."
    print "-p: Wintec WBT-201 password (4 digits)."
    print "-d: Use output directory."
    print "-o: Use output filename."
    print "--delete: Delete log from device after successful read."

def main():
    """
    Main method.
    """
    # pylint: disable-msg=R0912
    
    deleteLog = False
    debug = False
    password = None
    outputDir = None
    filename = None
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "?hvp:d:o:", "delete")
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    if len(args) != 1:
        usage()
        sys.exit(1)

    for o, a in opts:
        if o == "-v":
            debug = True
        if o in ("-h", "-?"):
            usage()
            sys.exit()
        if o == "-p":
            password = a
        if o == "-d":
            outputDir = a
        if o == "-o":
            filename = a
        if o == "--delete":
            deleteLog = True

    if outputDir and not os.path.exists(outputDir):
        print "Output directory %s doesn't exist!" % outputDir
        sys.exit(3)

    if filename and os.path.exists(os.path.join(outputDir if outputDir else ".", filename)):
        print "Output file %s already exists!" % filename
        sys.exit(4)

    tty = None
    try:
        tty = uspp.SerialPort(args[0], READ_TIMEOUT, BAUDRATE)
        tk1 = readLog(tty, password, debug)
        if tk1:
            f = createOutputFile(outputDir, filename, "%s", tk1.createFilename(), flags = "wb")
            tk1.write(f)
            f.close()
            if deleteLog:
                tty.write("@AL,05,06\n")
    finally:
        if tty != None:
            print "Exit command mode"
            tty.write("@AL,02,01\n")
            del tty

if __name__ == "__main__":
    main()
