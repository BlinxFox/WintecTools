==============
Wintec Tools
==============

The Wintec tools for the `Wintec WBT-201 <http://www.wintec.com.tw/en/product_detail.php?pro_id=65>`_
(G-Rays II) GPS mouse and the `Wintec WSG-1000 <http://www.wintec.com.tw/en/product_detail.php?pro_id=78>`_
(G-Trender) GPS receiver are a replacement for the main tasks of the Windows Time Machine X application, which is
delivered with the devices.

If you can't run windows applications or prefer commandline tools over GUI applications, the Wintec Tools will be
useful for you.

If you need more information about the format of the Wintec files, I maintain some documentation on the
`Wintec 201 Fileformat <doc/wintec_201_fileformat.html>`_ page.

The Wintec Tools are GPL licensed open source (freeware) written in `Python <http://www.python.org>`_.

Included tools
--------------


* **readlog.py**
  Read gps tracklogs from Wintec WBT-201 or WSG-1000 and write them into a .tk1 file.
* **tk1split.py**
  Split .tk1 files into .tk2 and/or .tk3 files.
* **tk1totk1.py**
  Read tk1 file, recalculate the footer data and create a tk1 file with a generic name.
* **tkinfo.py**
  Display TK file information and optionally set user comment string and/or timezone for .tk2/.tk3 files.
* **tktogpx.py**
  Convert gps tracklogs from Wintec TK files into a single GPS eXchange file.
* **tktonmea.py**
  Convert gps tracklogs from Wintec TK files into a single NMEA-0183 file.


=========================
Download and installation
=========================

To get the tools running clone the repository and install the dependencies

::

    git clone https://github.com/BlinxFox/WintecTools.git

    cd WintecTools
    pip install -r requirements.txt


=====
Usage
=====

Note: The -o option to specify the output filename is optional and should be used for special needs only. Without this
option the tools create and use generic filenames based on the date and time of first point of the containted track.

readlog.py
----------

::

    Read gps tracklogs from Wintec WBT-201 or WSG-1000 and write them into a .tk1 file.

    Usage: readlog.py [-v] [-p password] [-d outputdir] [-o filename] [--delete] <serial port>;
    -v: Print debug info.
    -p: Wintec WBT-201 password (4 digits).
    -d: Use output directory.
    -o: Use output filename.
    --delete: Delete log from device after successful read.


tk1split.py
-----------

::

    Split .tk1 files into .tk2 and/or .tk3 files.

    Usage: tk1split.py [-2] [-3] [-d directory] [--d2 directory] [--d3 directory] [-c "user comment"] [-t +hh:mm|--autotz] <tk1 files>
    -2: Create .tk2 files.
    -3: Create .tk3 files.
    -d: Use output directory for tk2 and tk3 files.
    --d2: Use output directory for tk2 files.
    --d3: Use output directory for tk3 files.
    -c: User comment string to store in the .tk2/tk3 header.
    -t: Use timezone for local time (offset to UTC).
    --autotz: Determine timezone from first trackpoint.

tk1totk1.py
-----------

::

    Read tk1 file, recalculate the footer data and create a tk1 file with a generic name.

    Usage: tk1totk1.py [-d directory] [-o filename] [--delete] <tk1 file>
    -d: Use output directory.
    -o: Use output filename.
    --delete: Delete source file after successful processing.


tkinfo.py
---------

::

    Display TK file information and optionally set user comment string and/or timezone for .tk2/.tk3 files.

    Usage: tkinfo.py [-c "user comment"] [-t +hh:mm|--autotz] <tk files>
    -c: User comment string to store in the .tk2/tk3 header.
    -t: .tk2/.tk3: Set timezone for local time (offset to UTC). .tk1: Ignored.
    --autotz: .tk2/.tk3: Determine timezone from first trackpoint. .tk1: Ignored.


tktogpx.py
----------

::

    Convert gps tracklogs from Wintec TK files into a single GPS eXchange file.

    Usage: tktogpx.py [-d outputdir] [-o filename] [-t +hh:mm|--autotz] <tk files>
    -d: Use output directory.
    -o: Use output filename.
    -t: .tk1     : Use timezone for local time (offset to UTC).
        .tk2/.tk3: Use timezone stored in tk-file.
    --autotz: .tk1     : Determine timezone from first trackpoint.
            .tk2/.tk3: Use timezone stored in tk-file.

**Note**: The time in .gpx files is defined as UTC. If you use the -t or --autotz
option, the time is converted to the timezone, but still marked as UTC.
The used timezone is added to the <desc> tag.


tktonmea.py
-----------

::

    Convert gps tracklogs from Wintec TK files into a single NMEA-0183 file.

    Usage: tktonmea.py [-d outputdir] [-o filename] <tk files>
    -d: Use output directory.
    -o: Use output filename.


============
Known Issues
============

* The Time Machine X 2.7.0 doesn't set the log version to 2.0 for WGS-1000 logs containing temperature and air pressure
  values. Use tk1totk1 to create a fixed TK1 file or use readlog instead of TMX to read the log from GPS device.

* Computed values like track length, speed, direction might differ from the values in files created by
  Time Machine X 2.7.0. For most values the difference should be rather small, but the direction is more than 10 degrees
  off, because Time Machine X 2.7.0 computes wrong values. This issue is fixed in Time Machine X 2.7.1.

* Generally the values computed by Wintec tools should be more accurate than the values of Time Machine X, as they use
  the very precise Vincenty formula with the WGS-84 ellipsoidal earth model.


=========
Changelog
=========

Version 3.0
-----------

* Create fork on Github
* Port to Python 3
* Removing non-functional tools
  * overview.py
  * tktohtml.py

Version 2.1
-----------

* readlog: The WGS-1000 sometimes returns the wrong block. Retry if the returned data block is not the requested one.
* readlog: Wrapped logbuffer handling was broken.
* readlog: The WSG-1000 doesn't pad the checksum with a trailing zero.
* tktogpx: Recognize options -t and --autotz.

Version 2.0
-----------

* Local timezone can be automatically determined by location and date/time of first trackpoint.
* Windows executables available (running without separate Python installation).
* Wintec WSG-1000 support added to readlog.
* Support log format 2.0 of WSG-1000 (temperature and air pressure).
* .tk2 and .tk3 support added including user comments.
* NMEA output format added.
* Google Maps output added.
* GPX/NMEA/Google Maps/Virtual Earth format is Time Machine X 2.7.1 compatible.
* Support for 64-bit operating systems.

Version 1.0
-----------

* Initial release


=====
Links
=====

* `Wintec WBT-201 support download page: <http://www.wintec.com.tw/en/support_detail.php?cate_id=11&support_id=65>`_
* `Wintec WSG-1000 support download page: <http://www.wintec.com.tw/en/support_detail.php?cate_id=11&support_id=70>`_
* `Time Machine X/Wintec Firmware beta releases: <http://lai0330.googlepages.com/>`_
* `German Wintec distributor support download page: <http://www.wintec-gps.de/support.php>`_
* `GPSBabel version with Wintec support: <http://www.hexten.net/wiki/index.php/WBT-201>`_
* `WintecTool: <http://www.mobihand.com/product.asp?id=12327">`_ is a PalmOS Application to download tracklogs and change settings with PalmOS powered devices
* Several tools are available for geotagging photos with tracklog data; 
  I recommend `HappyCamel: <http://happycamel.sourceforge.net/>`_, which is also 
  freeware written in Python and contains unique features like
  `reverse geocoding: <http://www.geonames.org/export/reverse-geocoding.html>`_
