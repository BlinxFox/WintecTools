#################################################################################
##
## tktohtml.py - Convert gps tracklog from Wintec TK file into xml files and make
## them viewable with Google Maps and/or Microsoft Virtual Earth html file.
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
## - The file name of the created html file contains the date and time of the
##   first trackpoint in the TK file. The file name of the created xml files
##   contains the date and time of the first point of the track.
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
Convert gps tracklog from Wintec TK file into xml files and make them viewable with Google Maps and/or
Microsoft Virtual Earth html file.
"""

# pylint: disable-msg=C0302

import getopt
from glob import glob
import os
import sys

from winteclib import VERSION, DATETIME_FILENAME_TEMPLATE, TK1File, readTKFile, calculateVincentyDistance, \
                      createOutputFile, parseTimezone

# pylint: disable-msg=C0301

VE_HTML_TEMPLATE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
\t<head>
\t<title>TimeMachineX</title>
\t<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
\t<script src="http://dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=6"></script>
\t<script src="http://maps.google.com/maps?file=api&amp;v=2.x" type="text/javascript"></script>
\t<script type="text/javascript">
\t//<![CDATA[
\t\tvar map = null;
\t\tvar pinID = 0;
\t\tvar TrPint = 0;
\t\tvar nowShapeID = 0;
\t\tvar nowtotal=0;
\t\tvar FirstFlag = 1;
\t\tvar nowPushTrack=null;
\t\tvar nowTrack = [];
\t\tvar nowTime = [];
\t\tvar nowCurrentPoint=null;
\t\tvar gpsLogs = [];
\t\tvar nowid = null;
\t\tfunction GetMap(){
\t\t\tmap = new VEMap('myMap');
\t\t\tmap.LoadMap(new VELatLong(52.5190749,13.3401816), 12, 'r', false);
\t\t\tdocument.Myform.colorselect.value='#0000ff';
\t\t\tdocument.Myform.Widthselect.value='5';
\t\t\tChangeName("0");
\t\t\tChangeColor();
\t\t\tFirstFlag = 0;
\t\t}
\t\tfunction ShowPoly(){
\t\t\tif(nowTrack == null){window.alert('Select one track first.');}
\t\t\telse{
\t\t\t\tmap.DeleteAllPolylines();
\t\t\t\tvar strColor = document.Myform.colorselect.value;
\t\t\t\tvar R=parseInt(strColor.substr(1,2),16);
\t\t\t\tvar G=parseInt(strColor.substr(3,2),16);
\t\t\t\tvar B=parseInt(strColor.substr(5,2),16);
\t\t\t\tvar nowcolor = new VEColor(R,G,B,1);
\t\t\t\tvar nowwidth = document.Myform.Widthselect.value;
\t\t\t\tpoly = new VEPolyline(nowid,nowTrack);
\t\t\t\tpoly.SetWidth(nowwidth);
\t\t\t\tpoly.SetColor(nowcolor);
\t\t\t\tmap.AddPolyline(poly);
\t\t\t}  }
\t\tfunction ChangeColor(){
\t\t\tvar el=document.getElementById('colorselect');
\t\t\tel.style.backgroundColor=document.Myform.colorselect.value;
\t\t\tif(FirstFlag==0)
\t\t\t\tShowPoly();
\t\t\tdocument.getElementById('colorselect').blur();
document.getElementById('Widthselect').blur();
\t\t\twindow.focus();}
\t\tfunction ShowPush(){
\t\t\tif((nowPushTrack==null)||(nowPushTrack.length==0))
\t\t\t\t{window.alert("No Push LOG Points.");return;}
\t\t\tvar CCCounter=0;
\t\t\tvar cp=0;
\t\t\tfor(pinID=1; pinID < (nowtotal-1); pinID++){
\t\t\t\tcp=parseInt(nowPushTrack[CCCounter])-1;
\t\t\t\tif(pinID==cp){
\t\t\t\t\tmap.AddShape(createShape(pinID,"http://gps.wintec.tw/img/push_to_log.gif"));
\t\t\t\t\tCCCounter++;
\t\t\t\t\tif(CCCounter > nowPushTrack.length)
\t\t\t\t\t\treturn;}  }  }
\t\tfunction createShape(number,icon){
\t\t\tvar shape = new VEShape(VEShapeType.Pushpin, nowTrack[number]);
\t\t\tvar strDes="";
\t\t\tif(number==0)
\t\t\t\tstrDes="(Start)";
\t\t\telse if(number==(nowtotal-1))
\t\t\t\t{strDes="(End)";}
\t\t\tif(strDes==""){
\t\t\t\tvar cp=0;
\t\t\t\tfor(pinID=0; pinID < nowPushTrack.length; pinID++){
\t\t\t\t\tcp=parseInt(nowPushTrack[pinID])-1;
\t\t\t\t\tif(number==cp){
\t\t\t\t\t\tstrDes="(Push LOG)";
\t\t\t\t\t\tbreak;}  }  }
\t\t\t\t\t\tvar IconImg = "<img src=\\""+icon+"\\" width=\\"24\\" height=\\"24\\"/>";
\t\t\t\t\t\tshape.SetCustomIcon(IconImg);
\t\t\t\t\t\tshape.SetTitle('Point');
\t\t\t\t\t\tshape.SetDescription(strDes+'Point number #'+(number+1)+"     Lat & Long:     "+nowTrack[number]+"     Time: "+nowTime[number]);
\t\t\treturn shape;}
\t\tfunction GETStartPoint(){map.AddShape(createShape(0,"http://gps.wintec.tw/img/track_start.gif"));}
\t\tfunction GETEndPoint(){map.AddShape(createShape((nowtotal-1),"http://gps.wintec.tw/img/track_end.gif"));}
\t\tfunction GoToPoint(){
\t\t\tform1=document.Myform;
\t\t\tif(nowTrack == null){window.alert('Select one track first.');}
\t\t\telse{
\t\t\t\tvar tmpID;
\t\t\t\ttmpID = parseInt(form1.ToPoint.value);
\t\t\t\tif(tmpID >= 1){
\t\t\t\t\tif(tmpID <= nowtotal){nowShapeID=tmpID-1;}
\t\t\t\t\telse{
\t\t\t\t\t\tnowShapeID=nowtotal-1;
\t\t\t\t\t\tform1.ToPoint.value=nowtotal;}  }
\t\t\t\telse{
\t\t\t\t\tnowShapeID=0;
\t\t\t\t\tform1.ToPoint.value="1";}
\t\t\t\tShowShape();}  }
\t\tfunction ShowAllShapes(){
\t\t\tif(nowTrack == null){window.alert('Select one track first.');}
\t\t\telse{
\t\t\t\tvar percent=document.Myform.show_point_select.value;
\t\t\t\tif(percent==2){ShowPush();document.getElementById('show_point_select').blur();
window.focus();
return;}
\t\t\t\tif(percent==0){
\t\t\t\tnowShapeID = 0;
\t\t\t\tmap.DeleteAllShapes();
\t\t\t\tGETStartPoint();
\t\t\t\tGETEndPoint();
\t\t\t\tdocument.getElementById('show_point_select').blur();
window.focus();
return;}
\t\t\t\tvar showpoints=0;
\t\t\t\tvar showCounter=0;
\t\t\t\tvar ID2=0;
\t\t\t\tshowpoints=parseInt(nowtotal/percent);
\t\t\t\tif(showpoints==0){window.alert('Show Points interval too large. No points show up.');return;}
\t\t\t\tif(showpoints > 2000){
\t\t\t\t\tchoose=window.confirm('WayPoints too much, may led browser lag; "OK" Only show first 2000 points. "Cancel" Show all points.');
\t\t\t\t\tif(choose==true){showpoints=2000;}
\t\t\t\t}
\t\t\t\tnowShapeID = 0;
\t\t\t\tmap.DeleteAllShapes();
\t\t\t\tGETStartPoint();
\t\t\t\tGETEndPoint();
\t\t\t\tfor(ID2=1; ID2 < (nowtotal-1);ID2++){
\t\t\t\t\tif(ID2%%percent==0){
\t\t\t\t\t\tmap.AddShape(createShape(ID2,"http://gps.wintec.tw/img/track_point.gif"));
\t\t\t\t\t\tshowCounter++;}
\t\t\t\t\tif(showCounter>=showpoints){return;}  }
\t\t\t\tmap.SetMapView(nowTrack);
\t\t\tdocument.getElementById('show_point_select').blur();
window.focus();
\t\t\t}
\t\t}
\t\tfunction ShowShape(){
\t\t\tif(nowCurrentPoint!=null)
\t\t\tmap.DeleteShape(nowCurrentPoint);
\t\t\tif(nowShapeID==0){
\t\t\t\tmap.SetCenter(nowTrack[nowShapeID]);nowCurrentPoint=null;}
\t\t\telse if(nowShapeID==(nowtotal-1)){
\t\t\t\tmap.SetCenter(nowTrack[nowShapeID]);nowCurrentPoint=null;}
\t\t\telse
\t\t\t {
\t\t\t\tnowCurrentPoint=createShape(nowShapeID,"http://gps.wintec.tw/img/center.gif");
\t\t\t\tmap.AddShape(nowCurrentPoint);
\t\t\t\tmap.SetCenter(nowTrack[nowShapeID]);
\t\t\t}  }
\t\tfunction REF(){
\t\t\tGETStartPoint();
\t\t\tGETEndPoint();
\t\t\tmap.SetMapView(nowTrack);
window.status='Reloading new track; please wait!!.....60%%';
\t\t\tShowPoly();
\t\t}
\tvar GPSLog = function(lat, lng, vv) {
\t\t\t\tthis.latlng = new GLatLng(parseFloat(lat), parseFloat(lng));
\t\t\t\t\t\tvar arr = vv.split('<br>');
\t\t\t\t\t\tthis.date     = new Date(arr[0].substr(0, 10).replace(/-/g, '/') + ' ' + arr[0].substr(11, 8)); 
\t\t\t\t\t\tthis.speed    = parseInt(arr[1].replace(/Speed:/, ''));
\t\t\t\t\t\tthis.course = parseInt(arr[2].replace(/Course:/, ''));\t
\t\t\t\t\t\tGPSLog.prototype.ToString = function() {
\t\t\t\t\t\treturn '[' + this.point + '] ' + this.date + '(' + this.latlng.lat() + ', ' + this.latlng.lng() + ') ' + this.speed + 'Km/h '+ this.course + ' ';
\t\t\t\t\t\t};\t}    
\t\tfunction ChangeName(index){
\t\t\tvar\tcname="";
\t\t\tvar\tcpoint="";
\t\t\tvar\tctime="";
\t\t\tvar\tcdis="";
\t\t\tswitch(index){
%(tracklist)s\t\t\t\tdefault:nowTrack=null;cname="";cpoint="";ctime="";cdis="";nowTime=null;nowid =null;break;}
\t\t\tdocument.getElementById('CName').innerHTML=cname;
\t\t\tdocument.getElementById('CPoint').innerHTML=cpoint;
\t\t\tdocument.getElementById('CTime').innerHTML=ctime;
\t\t\tdocument.getElementById('CDis').innerHTML=cdis;
\t\t\tnowtotal=parseInt(cpoint);
\t\t\t\tdocument.Myform.show_point_select.value='0';
\t\t\tnowShapeID = 0;
\t\t\tmap.DeleteAllPolylines();
\t\t\tmap.DeleteAllShapes();
\t\t\twindow.status='Reloading new track; please wait!!.....20%%';
\t\t\tnowTrack = [];
\t\t\tnowTime = [];
\t\t\tgpsLogs = [];
\t\t\tGDownloadUrl(nowxml, function(data){
\t\t\t\tvar xml = GXml.parse(data);
\t\t\t\tvar params = xml.documentElement.getElementsByTagName("param");
\t\t\t\tfor (var i = 0; i < params.length; i++){
\t\t\t\t\tnowTrack.push(new VELatLong(parseFloat(params[i].getAttribute("lat")),parseFloat(params[i].getAttribute("lng"))));
\t\t\t\t\tnowTime.push(new String(params[i].getAttribute("vv")));
\t\t\t\t\tgpsLogs.push(new GPSLog(params[i].getAttribute("lat"), params[i].getAttribute("lng"), params[i].getAttribute("vv")));
\t\t\t\t\t}
\t\t\t\twindow.status='Reloading new track; please wait!!.....30%%';
\t\t\t\t\tREF(); });
\t\t\tdocument.Myform.ToPoint.value="1";
window.status='Reloading new track; please wait!!.....40%%';
\t\t\twindow.focus();
\t\t\twindow.status=''
\t\t}
%(pushTracks)s\t //]]>
\t</script>
\t<noscript><b>JavaScript must be enabled in order for you to use Virtual Earth.</b>
\t\tHowever, it seems JavaScript is either disabled or not supported by your browser.
\t\tTo view the map, enable JavaScript by changing your browser options, and then try again. </noscript>
\t<style type="text/css">
\t<!--
\t.grey {BACKGROUND: #ecedf4}
\t.block_a {BORDER-RIGHT: #9b9b9b 1px solid; BORDER-TOP: #9b9b9b 1px solid; BORDER-BOTTOM: #9b9b9b 1px solid; BORDER-LEFT: #9b9b9b 1px solid; PADDING: 1px 1px 1px 1px; MARGIN: 1px 1px 1px 1px; FLOAT: right; WIDTH: 99%%;}
\t.block_b {BORDER-RIGHT: #9b9b9b 1px solid; BORDER-TOP: #9b9b9b 1px solid; BORDER-LEFT: #9b9b9b 1px solid; BORDER-BOTTOM: #9b9b9b 1px solid; PADDING: 2px 1px 2px 1px; MARGIN: 1px 1px 2px 0.5em; FLOAT: right; WIDTH: 96%%;}
\t.block_d {BORDER-RIGHT: #9b9b9b 1px solid; BORDER-TOP: #9b9b9b 1px solid; BORDER-LEFT: #9b9b9b 1px solid; BORDER-BOTTOM: #9b9b9b 1px solid; PADDING: 2px 1px 2px  1px; MARGIN: 1px 1px 1px 1px; FLOAT: left; WIDTH: 100%%;}
\t.block_c {BORDER-BOTTOM: #9b9b9b 1px solid; MARGIN: 0.5em 0 1px 1px; FLOAT: left; WIDTH: 100%%;}
\tH6 {PADDING-RIGHT: 0.3em; MARGIN-TOP: 0px; PADDING-LEFT: 0.3em; FONT-SIZE: 1em; BACKGROUND: #9b9b9b; MARGIN-BOTTOM: 0.3em; PADDING-BOTTOM: 0.3em; COLOR: #fff; PADDING-TOP: 0.3em}
\t.selected {BACKGROUND-COLOR: #9b9b9b}
\tbody{ margin:0; padding:0;}
\t-->
\t</style>
\t<basefont size="3" color="#7d7d7d" />
\t</head>
\t<body onLoad="GetMap();">
\t<form name="Myform" method="post" action="">
\t<table width="99%%" border="0" cellspacing="0" cellpadding="0">
\t<tr><th scope="row">
\t\t<table class="block_c" rules="none" width="100%%" align="left" border="0" cellspacing="0" cellpadding="0">
\t\t<tr><th class="selected" width="14%%" align="center" scope="row"><font color="#FFFFFF">Virtual Earth</font></th>
\t\t<td width="86%%">&nbsp;</td></tr></table>
\t</th></tr>
\t<tr><th scope="row">
\t\t\t<table width="100%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<th valign="top" width="70%%" scope="row"><table  width="100%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<th class="block_d" scope="row"><div id='myMap' style="position:relative; width:98%%;"></div></th>
\t\t</table></th>
\t\t<td valign="top" align="center" width="30%%"><div class="block_b"><table  width="95%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<tr>
\t\t\t\t<th colspan="2" scope="row"><H6>Track Information</H6></th>
\t\t\t</tr>
\t\t\t<tr class="grey">
\t\t\t\t<th width="43%%" scope="row"><div align="left">Device Name </div></th>
\t\t\t\t<td width="57%%"><div align="left">TimeMachineX</div></td>
\t\t\t</tr>
\t\t\t<tr>
\t\t\t\t<th scope="row"><div align="left">Total track</div></th>
\t\t\t\t<td><div align="left">%(totaltracks)i</div></td>
\t\t\t</tr>
\t\t\t<tr class="grey">
\t\t\t\t<th scope="row"><div align="left">Total points</div></th>
\t\t\t\t<td><div align="left">%(totalpoints)i</div></td>
\t\t\t</tr>
\t\t\t<tr>
\t\t\t\t<th width="43%%" scope="row"><div align="left"><strong>Track</strong></div></th>
\t\t\t\t<td width="57%%"><div align="left" id="CName"></div></td>
\t\t\t</tr>
\t\t\t<tr class="grey">
\t\t\t\t<th scope="row"><div align="left"><strong>Track points</strong></div></th>
\t\t\t\t<td><div align="left" id="CPoint"></div></td>
\t\t\t</tr>
\t\t\t<tr>
\t\t\t\t<th scope="row"><div align="left"><strong>Track time</strong></div></th>
\t\t\t\t<td><div align="left"  id="CTime"></div></td>
\t\t\t</tr>
\t\t\t<tr class="grey">
\t\t\t\t<th scope="row"><div align="left"><strong>Track distance</strong></div></th>
\t\t\t\t<td><div align="left" id="CDis"></div></td>
\t\t\t</tr>
\t\t</table></div>
\t\t\t<script type="text/javascript">\t
\t\t\t\tvar m = document.getElementById("myMap");
\t\t\t\tvar facter=0.58;
\t\t\t\tif(screen.height<768)
\t\t\t\t\tfacter=0.87;
\t\t\t\tm.style.height = (Math.round((screen.height)*facter)+5) + "px";
\t\t\t</script>
%(selectedtrack)s\t\t\t<div class="block_b"><table width="95%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t\t<tr><th scope="row"><H6>Track Point Tour</H6></th></tr>
\t\t\t\t<tr><th class="grey" scope="row"><div align="left">
\t\t\t\t<input id="gotopoint" type="button" value="Go to" name="gotopoint" onclick="GoToPoint();" />
\t\t\t\t#<input type="text" size="6" name="ToPoint" value="1" />
\t\t\t\tpoint.</div></th></tr></table></div>
\t\t\t<div class="block_b"><table width="95%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<tr><th scope="row"><H6>Track Points Manager</H6></th></tr>
\t\t\t<tr><th class="grey" scope="row"><div align="left">
\t\t\tTo show one of points by every<select id="show_point_select" name="show_point_select" size="1" onchange="window.status='Marking track points; please wait!!';ShowAllShapes();window.status='';">
\t\t\t\t\t<option value="0">Hide all track</option>
\t\t\t\t\t<option value="2">Show Push LOG</option>
\t\t\t\t\t<option value="1">1</option>
\t\t\t\t\t<option value="3">3</option>
\t\t\t\t\t<option value="5">5</option>
\t\t\t\t\t<option value="7">7</option>
\t\t\t\t\t<option value="10">10</option>
\t\t\t\t\t<option value="30">30</option>
\t\t\t\t\t<option value="50">50</option>
\t\t\t\t\t<option value="70">70</option>
\t\t\t\t\t<option value="100">100</option>
\t\t\t\t\t<option value="300">300</option>
\t\t\t\t\t<option value="500">500</option>
\t\t\t\t\t<option value="700">700</option>
\t\t\t\t\t<option value="1000">1000</option>
\t\t\t\t\t<option value="3000">3000</option>
\t\t\t\t\t<option value="5000">5000</option>
\t\t\t\t</select>
\t\t\tpoints.</div></th></tr></table></div>
\t\t\t<div class="block_b"><table width="95%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<tr><th scope="row"><H6>Track Line Manager</H6></th></tr>
\t\t\t<tr><th class="grey" scope="row"><div align="left">
\t\t\tColor<select id="colorselect" name="colorselect" size="1" onChange="window.status='Re-drawing track line; please wait!!';ChangeColor();window.status=''" onfocus="window.status='Switch Track line color';return true;">
\t\t\t\t<option value="#000000">Black</option>
\t\t\t\t<option value="#ffffff">White</option>
\t\t\t\t<option value="#696969">Grey</option>
\t\t\t\t<option value="#999999">Light Grey</option>
\t\t\t\t<option value="#191970">Midnight blue</option>
\t\t\t\t<option value="#6a5acd">Slate Blue</option>
\t\t\t\t<option value="#0000cd">Medium Blue</option>
\t\t\t\t<option value="#0000ff">Blue</option>
\t\t\t\t<option value="#00bfff">Deep Sky blue</option>
\t\t\t\t<option value="#00ced1">Dark Turquoise</option>
\t\t\t\t<option value="#00ffff">Cyan</option>
\t\t\t\t<option value="#006400">Dark Green</option>
\t\t\t\t<option value="#2e8b57">Sea Green</option>
\t\t\t\t<option value="#00ff7f">Spring Green</option>
\t\t\t\t<option value="#7cfc00">Lawn Green</option>
\t\t\t\t<option value="#00ff00">Green</option>
\t\t\t\t<option value="#32cd32">Lime Green</option>
\t\t\t\t<option value="#ffff00">Yellow</option>
\t\t\t\t<option value="#ffd700">Gold</option>
\t\t\t\t<option value="#daa520">Goldenrod</option>
\t\t\t\t<option value="#b8860b">Dark Goldenrod</option>
\t\t\t\t<option value="#bc8f8f">Rosy Brown</option>
\t\t\t\t<option value="#cd5c5c">Indian Red</option>
\t\t\t\t<option value="#8b4513">Saddle Brown</option>
\t\t\t\t<option value="#b22222">Firebrick</option>
\t\t\t\t<option value="#a52a2a">Brown</option>
\t\t\t\t<option value="#fa8072">Salmon</option>
\t\t\t\t<option value="#ffa500">Orange</option>
\t\t\t\t<option value="#f08080">Light Coral</option>
\t\t\t\t<option value="#ff0000">Red</option>
\t\t\t\t<option value="#ff1493">Deep Pink</option>
\t\t\t\t<option value="#b03060">Maroon</option>
\t\t\t\t<option value="#d02090">Violet Red</option>
\t\t\t\t<option value="#ff00ff">Magenta</option>
\t\t\t\t<option value="#9932cc">Dark Orchid</option>
\t\t\t\t<option value="#8a2be2">Blue Violet</option>
\t\t\t\t<option value="#a020f0">Purple</option>
\t\t\t\t</select>
\t\t\tWidth
\t\t\t\t<select id="Widthselect" name="Widthselect" size="1" onChange="window.status='Re-drawing track line; please wait!!';ChangeColor();window.status=''" onfocus="window.status='Switch Track line width';return true;">
\t\t\t\t\t<option value="1">1</option>
\t\t\t\t\t<option value="2">2</option>
\t\t\t\t\t<option value="3">3</option>
\t\t\t\t\t<option value="4">4</option>
\t\t\t\t\t<option value="5">5</option>
\t\t\t\t\t<option value="6">6</option>
\t\t\t\t\t<option value="7">7</option>
\t\t\t\t\t<option value="8">8</option>
\t\t\t\t\t<option value="9">9</option>
\t\t\t\t\t<option value="10">10</option>
\t\t\t\t\t<option value="11">11</option>
\t\t\t\t\t<option value="12">12</option>
\t\t\t\t\t<option value="13">13</option>
\t\t\t\t\t<option value="14">14</option>
\t\t\t\t\t<option value="15">15</option>
\t\t\t\t</select></div></th></tr></table></div>
\t\t\t</td></tr></table>
\t</th></tr></table>
\t</form>
\t</body>
\t</html>
"""
""" The Virtual Earth html page template. """

GM_HTML_TEMPLATE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">
\t<head>
\t<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
\t<title>TimeMachineX</title>
\t<script src="http://maps.google.com/maps?file=api&amp;v=2.x" type="text/javascript"></script>
\t<script type="text/javascript">
\t//<![CDATA[
\tfunction SpeedBarControl() { }
\tSpeedBarControl.prototype = new GControl();
\tSpeedBarControl.prototype.initialize = function(map){ 
\t\tvar image = document.createElement('img');
\t\timage.src="http://gps.wintec.tw/img/SPEEDBAR.gif";  
\t\tmap.getContainer().appendChild(image);
\t\treturn image;}  
\t\tSpeedBarControl.prototype.getDefaultPosition = function() { 
\t\treturn new GControlPosition(G_ANCHOR_BOTTOM_LEFT, new GSize(-3, 50)); } 
\t\tvar map = null;
\t\tvar pinID = 0;
\t\tvar TrPint = 0;
\t\tvar nowShapeID = 0;
\t\tvar nowtotal=0;
\t\tvar FirstFlag = 1;
\t\tvar nowPushTrack=null;
\t\tvar nowTrack = [];
\t\tvar nowTime = [];
\t\tvar nowCurrentPoint=null;
\t\tvar gpsLogs = [];
\t\tvar Mapzoom=15;
\t\tvar nowCurrentPolyline=null;
\t\tvar nowBounds=null;
\t\tvar TrackDependOpt=null;
\t\tvar iconstart = new GIcon();
\t\ticonstart.image = "http://gps.wintec.tw/img/track_start.png";
\t\ticonstart.iconSize = new GSize(24, 24);
\t\ticonstart.iconAnchor = new GPoint(12, 12);
\t\ticonstart.infoWindowAnchor = new GPoint(12, 12);
\t\tvar iconend = new GIcon();
\t\ticonend.image = "http://gps.wintec.tw/img/track_end.png";
\t\ticonend.iconSize = new GSize(24, 24);
\t\ticonend.iconAnchor = new GPoint(12, 12);
\t\ticonend.infoWindowAnchor = new GPoint(12, 12);
\t\tvar iconpoints = new GIcon();
\t\ticonpoints.image = "http://gps.wintec.tw/img/track_point.png";
\t\ticonpoints.iconSize = new GSize(24, 24);
\t\ticonpoints.iconAnchor = new GPoint(12, 12);
\t\ticonpoints.infoWindowAnchor = new GPoint(12, 12);
\t\tvar iconcurrent = new GIcon();
\t\ticoncurrent.image = "http://gps.wintec.tw/img/center.png";
\t\ticoncurrent.iconSize = new GSize(20, 20);
\t\ticoncurrent.iconAnchor = new GPoint(10, 10);
\t\ticoncurrent.infoWindowAnchor = new GPoint(10, 10);
\t\tvar iconpush = new GIcon();
\t\ticonpush.image = "http://gps.wintec.tw/img/push_to_log.png";
\t\ticonpush.iconSize = new GSize(24, 24);
\t\ticonpush.iconAnchor = new GPoint(12, 12);
\t\ticonpush.infoWindowAnchor = new GPoint(12, 12);
\t\tfunction GetMap(){
\t\t\tif (GBrowserIsCompatible()){
\t\t\t\tmap = new GMap2(document.getElementById("myMap"));
\t\t\t\tmap.addControl(new GLargeMapControl());
\t\t\t\tmap.addControl(new GMapTypeControl());
\t\t\t\tmap.addControl(new GScaleControl());
\t\t\t\tmap.addControl(new SpeedBarControl);
\t\t\t\tmap.addMapType(G_PHYSICAL_MAP);
\t\t\t\tmap.setCenter(new GLatLng(52.5190749,13.3401816), 12);
\t\t\t\tdocument.Myform.colorselect.value='#0000ff';
\t\t\t\tdocument.Myform.Widthselect.value='5';
\t\t\t\tChangeColor();
\t\t\t\tChangeName("0");
\t\t\t\tFirstFlag = 0;
\t\t\t\tGEvent.addListener(map,"zoomend", function ZoomChange(oldLevel, newLevel){
\t\t\t\tMapzoom = newLevel; });
\t\t\t}
\t\t\telse { map = document.getElementById("mymap");
\t\t\t\tmap.innerHTML = ""; map.innerHTML = "Sorry, Your browser not support Google Maps"; }
\t\t}
\t\tfunction ShowPoly(){
\t\t\tif(nowTrack == null){window.alert('Select one track first.');}
\t\t\telse{
\t\t\t\tif(nowCurrentPolyline!=null)
\t\t\t\t\tmap.removeOverlay(nowCurrentPolyline);
\t\t\t\tvar nowcolor = document.Myform.colorselect.value;
\t\t\t\tvar nowwidth = document.Myform.Widthselect.value;
\t\t\t\tnowCurrentPolyline=new GPolyline(nowTrack,nowcolor,nowwidth,1);
\t\t\t\tmap.addOverlay(nowCurrentPolyline);
\t\t\t}  }
\t\tfunction ChangeColor(){
\t\t\tvar el=document.getElementById('colorselect');
\t\t\tel.style.backgroundColor=document.Myform.colorselect.value;
\t\t\tif(FirstFlag==0)
\t\t\t\tShowPoly();
\t\t\tdocument.getElementById('colorselect').blur();
document.getElementById('Widthselect').blur();
\t\t\twindow.focus();}
\t\tfunction ShowPush(){
\t\t\tif((nowPushTrack==null)||(nowPushTrack.length==0))
\t\t\t\t{window.alert("No Push LOG Points.");return;}
\t\t\tvar CCCounter=0;
\t\t\tvar cp=0;
\t\t\tfor(pinID=1; pinID < (nowtotal-1); pinID++){
\t\t\t\tcp=parseInt(nowPushTrack[CCCounter])-1;
\t\t\t\tif(pinID==cp){
\t\t\t\t\tmap.addOverlay(createMarker(pinID,iconpush));
\t\t\t\t\tCCCounter++;
\t\t\t\t\tif(CCCounter > nowPushTrack.length)
\t\t\t\t\t\treturn;}  }  }
\t\tfunction createMarker(number,icon){
\t\t\tvar marker = new GMarker(nowTrack[number],icon);
\t\t\tvar strDes="";
\t\t\tif(number==0)
\t\t\t\tstrDes="(Start)";
\t\t\telse if(number==(nowtotal-1))
\t\t\t\tstrDes="(End)";
\t\t\tif(strDes==""){
\t\t\t\tvar cp=0;
\t\t\t\tfor(pinID=0; pinID < nowPushTrack.length; pinID++){
\t\t\t\t\tcp=parseInt(nowPushTrack[pinID])-1;
\t\t\t\t\tif(number==cp){
\t\t\t\t\t\tstrDes="(Push LOG)";
\t\t\t\t\t\tbreak;}  }  }
\t\t\tGEvent.addListener(marker, "click", function(overlay, point) {
\t\t\tmarker.openInfoWindowHtml("<p align=\\"left\\">"+strDes+'Point number #'+(number+1)+"<br>Latitude: "+nowTrack[number].lat()+"<br>Longitude: "+nowTrack[number].lng()+"<br>Time: "+nowTime[number]+"<br></p>");
\t\t\tnowShapeID=number;
\t\t\tdocument.Myform.ToPoint.value=(nowShapeID+1); });
\t\t\treturn marker;}
\t\tfunction GETStartPoint(){map.addOverlay(createMarker(0,iconstart));}
\t\tfunction GETEndPoint(){map.addOverlay(createMarker((nowtotal-1),iconend));}
\t\tfunction GoToPoint(){
\t\t\tform1=document.Myform;
\t\t\tif(nowTrack == null){window.alert('Select one track first.');}
\t\t\telse{
\t\t\t\tvar tmpID;
\t\t\t\ttmpID = parseInt(form1.ToPoint.value);
\t\t\t\tif(tmpID >= 1){
\t\t\t\t\tif(tmpID <= nowtotal){nowShapeID=tmpID-1;}
\t\t\t\t\telse{
\t\t\t\t\t\tnowShapeID=nowtotal-1;
\t\t\t\t\t\tform1.ToPoint.value=nowtotal;}  }
\t\t\t\telse{
\t\t\t\t\tnowShapeID=0;
\t\t\t\t\tform1.ToPoint.value="1";}
\t\t\t\tShowShape();}  }
\t\tfunction ShowAllShapes(){
\t\t\tif(nowTrack == null){window.alert('Select one track first.');}
\t\t\telse{
\t\t\t\tvar percent=document.Myform.show_point_select.value;
\t\t\t\tif(percent==2){ShowPush();document.getElementById('show_point_select').blur();
window.focus();
return;}
\t\t\t\tif(percent==0){
\t\t\t\tnowShapeID = 0;
\t\t\t\tmap.clearOverlays();
\t\t\t\tShowPoly();
\t\t\t\tGETStartPoint();
\t\t\t\tGETEndPoint();
\t\t\t\tdocument.getElementById('show_point_select').blur();
window.focus();
return;}
\t\t\t\tvar showpoints=0;
\t\t\t\tvar showCounter=0;
\t\t\t\tvar ID2=0;
\t\t\t\tshowpoints=parseInt(nowtotal/percent);
\t\t\t\tif(showpoints==0){window.alert('Show Points interval too large. No points show up.');return;}
\t\t\t\tif(showpoints > 2000){
\t\t\t\t\tchoose=window.confirm('WayPoints too much, may led browser lag; "OK" Only show first 2000 points. "Cancel" Show all points.');
\t\t\t\t\tif(choose==true){showpoints=2000;}
\t\t\t\t}
\t\t\t\tnowShapeID = 0;
\t\t\t\tmap.clearOverlays();
\t\t\t\tShowPoly();
\t\t\t\tGETStartPoint();
\t\t\t\tGETEndPoint();
\t\t\t\tfor(ID2=1; ID2 < (nowtotal-1);ID2++){
\t\t\t\t\tif(ID2%%percent==0){
\t\t\t\t\t\tvar NowSPD = parseInt(gpsLogs[ID2].speed) ;
\t\t\t\t\t\tvar NowCUR = parseInt(gpsLogs[ID2].course) ;
\t\t\t\t\t\tvar SPDIndex=0;
\t\t\t\t\t\tvar CURIndex=0;
\t\t\t\t\t\tif(NowSPD<20)
\t\t\t\t\t\t        SPDIndex=0;
\t\t\t\t\t\telse if(NowSPD<40)
\t\t\t\t\t\t\tSPDIndex=1;
\t\t\t\t\t\telse if(NowSPD<60)
\t\t\t\t\t\t\tSPDIndex=2;
\t\t\t\t\t\telse if(NowSPD<80)
\t\t\t\t\t\t\tSPDIndex=3;
\t\t\t\t\t\telse if(NowSPD<100)
\t\t\t\t\t\t\tSPDIndex=4;
\t\t\t\t\t\telse if(NowSPD<120)
\t\t\t\t\t\t\tSPDIndex=5;
\t\t\t\t\t\telse if(NowSPD>=120)
\t\t\t\t\t\t\tSPDIndex=6;
\t\t\t\t\t\tif(NowCUR >= 360)
\t\t\t\t\t\t   NowCUR = NowCUR%%360;
\t\t\t\t\t\tif(SPDIndex<0) 
\t\t\t\t\t\t   SPDIndex=0; 
\t\t\t\t\t\tCURIndex=Math.round((NowCUR)/10);\t
\t\t\t\t\t\tvar SCPNG = "http://gps.wintec.tw/img/SC_"+SPDIndex+"_"+CURIndex+".png";\t
\t\t\t\t\t\tvar icontest = new GIcon();
\t\t\t\t\t\ticontest.image = SCPNG;
\t\t\t\t\t\ticontest.iconSize = new GSize(24, 24);
\t\t\t\t\t\ticontest.iconAnchor = new GPoint(12, 12);
\t\t\t\t\t\ticontest.infoWindowAnchor = new GPoint(12, 12);
\t\t\t\t\t\tmap.addOverlay(createMarker(ID2,icontest));
\t\t\t\t\t\tshowCounter++;}
\t\t\t\t\tif(showCounter>=showpoints){return;}  }
\t\t\tdocument.getElementById('show_point_select').blur();
window.focus();
\t\t\t}
\t\t}
\t\tfunction ShowShape(){
\t\t\tif(nowCurrentPoint!=null)
\t\t\t\tmap.removeOverlay(nowCurrentPoint);
\t\t\tif(nowShapeID==0){
\t\t\t\tmap.setCenter(nowTrack[nowShapeID]);nowCurrentPoint=null;}
\t\t\telse if(nowShapeID==(nowtotal-1)){
\t\t\t\tmap.setCenter(nowTrack[nowShapeID]);nowCurrentPoint=null;}
\t\t\telse
\t\t\t {
\t\t\t\tnowCurrentPoint=createMarker(nowShapeID,iconcurrent);
\t\t\t\tmap.addOverlay(nowCurrentPoint);
\t\t\t\tmap.setCenter(nowTrack[nowShapeID]);
\t\t\t}  }
\t\tfunction REF(){
\t\t\tGETStartPoint();
\t\t\tGETEndPoint();
\t\t\tShowAllShapes();
\t\t\tmap.setCenter(nowTrack[0], map.getBoundsZoomLevel(nowBounds));
window.status='Reloading new track; please wait!!.....60%%';
\t\t\tShowPoly();
\t\t}
\tvar GPSLog = function(lat, lng, vv) {
\t\t\t\tthis.latlng = new GLatLng(parseFloat(lat), parseFloat(lng));
\t\t\t\t\t\tvar arr = vv.split('<br>');
\t\t\t\t\t\tthis.date     = new Date(arr[0].substr(0, 10).replace(/-/g, '/') + ' ' + arr[0].substr(11, 8)); 
\t\t\t\t\t\tthis.speed    = parseInt(arr[1].replace(/Speed:/, ''));
\t\t\t\t\t\tthis.course = parseInt(arr[2].replace(/Course:/, ''));\t
\t\t\t\t\t\tGPSLog.prototype.ToString = function() {
\t\t\t\t\t\treturn '[' + this.point + '] ' + this.date + '(' + this.latlng.lat() + ', ' + this.latlng.lng() + ') ' + this.speed + 'Km/h '+ this.course + ' ';
\t\t\t\t\t\t};\t}    
\t\tfunction ChangeName(index){
\t\t\tvar\tcname="";
\t\t\tvar\tcpoint="";
\t\t\tvar\tctime="";
\t\t\tvar\tcdis="";
\t\t\tswitch(index){
%(tracklist)s\t\t\t\tdefault:nowTrack=null;cname="";cpoint="";ctime="";cdis="";nowTime=null;nowid =null;break;}
\t\t\tdocument.getElementById('CName').innerHTML=cname;
\t\t\tdocument.getElementById('CPoint').innerHTML=cpoint;
\t\t\tdocument.getElementById('CTime').innerHTML=ctime;
\t\t\tdocument.getElementById('CDis').innerHTML=cdis;
\t\t\tnowtotal=parseInt(cpoint);
\t\t\tif(nowtotal>100)
\t\t\t\t{
\t\t\t\t\t  var ShowIntervay=parseInt(nowtotal/100);
\t\t\t\tif(ShowIntervay==2)
\t\t\t\t      ShowIntervay=3;
\t\t\t\t\t  var ShowPntSel=document.getElementById('show_point_select');
\t\t\t\t if(TrackDependOpt!=null)
\t\t\t\t { 
\t\t\t\t    ShowPntSel.remove((ShowPntSel.length)-1); 
\t\t\t\t }
\t\t\t\t  TrackDependOpt = document.createElement("option");
\t\t\t\t  TrackDependOpt.value=new String(ShowIntervay) ;
\t\t\t\t  TrackDependOpt.text="Auto" ;
\t\t\t\t  ShowPntSel.options.add(TrackDependOpt);
\t\t\t\t  document.Myform.show_point_select.value=new String(ShowIntervay);
\t\t\t\t}
\t\t\telse
\t\t\t\tdocument.Myform.show_point_select.value="1";
\t\t\tnowShapeID = 0;
\t\t\tmap.clearOverlays();
\t\t\twindow.status='Reloading new track; please wait!!.....20%%';
\t\t\tnowTrack = [];
\t\t\tnowTime = [];
\t\t\tgpsLogs = [];
\t\t\tGDownloadUrl(nowxml, function(data){
\t\t\t\tvar xml = GXml.parse(data);
\t\t\t\tvar params = xml.documentElement.getElementsByTagName("param");
\t\t\t\tfor (var i = 0; i < params.length; i++){
\t\t\t\t\tnowTrack.push(new GLatLng(parseFloat(params[i].getAttribute("lat")),parseFloat(params[i].getAttribute("lng"))));
\t\t\t\t\tnowTime.push(new String(params[i].getAttribute("vv")));
\t\t\t\t\tgpsLogs.push(new GPSLog(params[i].getAttribute("lat"), params[i].getAttribute("lng"), params[i].getAttribute("vv")));
\t\t\t\t\t}
\t\t\t\twindow.status='Reloading new track; please wait!!.....30%%';
\t\t\t\t\tREF(); });
\t\t\tdocument.Myform.ToPoint.value="1";
window.status='Reloading new track; please wait!!.....40%%';
\t\t\twindow.focus();
\t\t\twindow.status=''
\t\t}
%(bounds)s%(pushTracks)s\t //]]>
\t</script>
\t<noscript><b>JavaScript must be enabled in order for you to use Google Maps.</b>

\t\tHowever, it seems JavaScript is either disabled or not supported by your browser.
\t\tTo view the map, enable JavaScript by changing your browser options, and then try again. </noscript>
\t<style type="text/css">
\t<!--
\t.grey {BACKGROUND: #ecedf4}
\t.block_a {BORDER-RIGHT: #9b9b9b 1px solid; BORDER-TOP: #9b9b9b 1px solid; BORDER-BOTTOM: #9b9b9b 1px solid; BORDER-LEFT: #9b9b9b 1px solid; PADDING: 1px 1px 1px 1px; MARGIN: 1px 1px 1px 1px; FLOAT: right; WIDTH: 99%%;}
\t.block_b {BORDER-RIGHT: #9b9b9b 1px solid; BORDER-TOP: #9b9b9b 1px solid; BORDER-LEFT: #9b9b9b 1px solid; BORDER-BOTTOM: #9b9b9b 1px solid; PADDING: 2px 1px 2px 1px; MARGIN: 1px 1px 2px 0.5em; FLOAT: right; WIDTH: 96%%;}
\t.block_d {BORDER-RIGHT: #9b9b9b 1px solid; BORDER-TOP: #9b9b9b 1px solid; BORDER-LEFT: #9b9b9b 1px solid; BORDER-BOTTOM: #9b9b9b 1px solid; PADDING: 2px 1px 2px  1px; MARGIN: 1px 1px 1px 1px; FLOAT: left; WIDTH: 100%%;}
\t.block_c {BORDER-BOTTOM: #9b9b9b 1px solid; MARGIN: 0.5em 0 1px 1px; FLOAT: left; WIDTH: 100%%;}
\tH6 {PADDING-RIGHT: 0.3em; MARGIN-TOP: 0px; PADDING-LEFT: 0.3em; FONT-SIZE: 1em; BACKGROUND: #9b9b9b; MARGIN-BOTTOM: 0.3em; PADDING-BOTTOM: 0.3em; COLOR: #fff; PADDING-TOP: 0.3em}
\t.selected {BACKGROUND-COLOR: #9b9b9b}
\tbody{ margin:0; padding:0;}
\t-->
\t</style>
\t<basefont size="3" color="#7d7d7d" />
\t</head>
\t<body onLoad="GetMap()" onunload="GUnload()">
\t<form name="Myform" method="post" action="">
\t<table width="99%%" border="0" cellspacing="0" cellpadding="0">
\t<tr><th scope="row">
\t\t<table class="block_c" rules="none" width="100%%" align="left" border="0" cellspacing="0" cellpadding="0">
\t\t<tr><th class="selected" width="14%%" align="center" scope="row"><font color="#FFFFFF">Google Maps</font></th>
\t\t<td width="86%%">&nbsp;</td></tr></table>
\t</th></tr>
\t<tr><th scope="row">
\t\t\t<table width="100%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<th valign="top" width="70%%" scope="row"><table  width="100%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<th class="block_d" scope="row"><div id='myMap' style="position:relative; width:98%%;"></div></th>
\t\t</table></th>
\t\t<td valign="top" align="center" width="30%%"><div class="block_b"><table  width="95%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<tr>
\t\t\t\t<th colspan="2" scope="row"><H6>Track Information</H6></th>
\t\t\t</tr>
\t\t\t<tr class="grey">
\t\t\t\t<th width="43%%" scope="row"><div align="left">Device Name </div></th>
\t\t\t\t<td width="57%%"><div align="left">TimeMachineX</div></td>
\t\t\t</tr>
\t\t\t<tr>
\t\t\t\t<th scope="row"><div align="left">Total track</div></th>
\t\t\t\t<td><div align="left">%(totaltracks)i</div></td>
\t\t\t</tr>
\t\t\t<tr class="grey">
\t\t\t\t<th scope="row"><div align="left">Total points</div></th>
\t\t\t\t<td><div align="left">%(totalpoints)i</div></td>
\t\t\t</tr>
\t\t\t<tr>
\t\t\t\t<th width="43%%" scope="row"><div align="left"><strong>Track</strong></div></th>
\t\t\t\t<td width="57%%"><div align="left" id="CName"></div></td>
\t\t\t</tr>
\t\t\t<tr class="grey">
\t\t\t\t<th scope="row"><div align="left"><strong>Track points</strong></div></th>
\t\t\t\t<td><div align="left" id="CPoint"></div></td>
\t\t\t</tr>
\t\t\t<tr>
\t\t\t\t<th scope="row"><div align="left"><strong>Track time</strong></div></th>
\t\t\t\t<td><div align="left"  id="CTime"></div></td>
\t\t\t</tr>
\t\t\t<tr class="grey">
\t\t\t\t<th scope="row"><div align="left"><strong>Track distance</strong></div></th>
\t\t\t\t<td><div align="left" id="CDis"></div></td>
\t\t\t</tr>
\t\t</table></div>
\t\t\t<script type="text/javascript">\t
\t\t\t\tvar m = document.getElementById("myMap");
\t\t\t\tvar facter=0.58;
\t\t\t\tif(screen.height<768)
\t\t\t\t\tfacter=0.87;
\t\t\t\tm.style.height = (Math.round((screen.height)*facter)+5) + "px";
\t\t\t</script>
%(selectedtrack)s\t\t\t<div class="block_b"><table width="95%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t\t<tr><th scope="row"><H6>Track Point Tour</H6></th></tr>
\t\t\t\t<tr><th class="grey" scope="row"><div align="left">
\t\t\t\t<input id="gotopoint" type="button" value="Go to" name="gotopoint" onclick="GoToPoint();" />
\t\t\t\t#<input type="text" size="6" name="ToPoint" value="1" />
\t\t\t\tpoint.</div></th></tr></table></div>
\t\t\t<div class="block_b"><table width="95%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<tr><th scope="row"><H6>Track Points Manager</H6></th></tr>
\t\t\t<tr><th class="grey" scope="row"><div align="left">
\t\t\tTo show one of points by every<select id="show_point_select" name="show_point_select" size="1" onchange="window.status='Marking track points; please wait!!';ShowAllShapes();window.status='';">
\t\t\t\t\t<option value="0">Hide all track</option>
\t\t\t\t\t<option value="2">Show Push LOG</option>
\t\t\t\t\t<option value="1">1</option>
\t\t\t\t\t<option value="3">3</option>
\t\t\t\t\t<option value="5">5</option>
\t\t\t\t\t<option value="7">7</option>
\t\t\t\t\t<option value="10">10</option>
\t\t\t\t\t<option value="30">30</option>
\t\t\t\t\t<option value="50">50</option>
\t\t\t\t\t<option value="70">70</option>
\t\t\t\t\t<option value="100">100</option>
\t\t\t\t\t<option value="300">300</option>
\t\t\t\t\t<option value="500">500</option>
\t\t\t\t\t<option value="700">700</option>
\t\t\t\t\t<option value="1000">1000</option>
\t\t\t\t\t<option value="3000">3000</option>
\t\t\t\t\t<option value="5000">5000</option>
\t\t\t\t</select>
\t\t\tpoints.</div></th></tr></table></div>
\t\t\t<div class="block_b"><table width="95%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<tr><th scope="row"><H6>Track Line Manager</H6></th></tr>
\t\t\t<tr><th class="grey" scope="row"><div align="left">
\t\t\tColor<select id="colorselect" name="colorselect" size="1" onChange="window.status='Re-drawing track line; please wait!!';ChangeColor();window.status=''" onfocus="window.status='Switch Track line color';return true;">
\t\t\t\t<option value="#000000">Black</option>
\t\t\t\t<option value="#ffffff">White</option>
\t\t\t\t<option value="#696969">Grey</option>
\t\t\t\t<option value="#999999">Light Grey</option>
\t\t\t\t<option value="#191970">Midnight blue</option>
\t\t\t\t<option value="#6a5acd">Slate Blue</option>
\t\t\t\t<option value="#0000cd">Medium Blue</option>
\t\t\t\t<option value="#0000ff">Blue</option>
\t\t\t\t<option value="#00bfff">Deep Sky blue</option>
\t\t\t\t<option value="#00ced1">Dark Turquoise</option>
\t\t\t\t<option value="#00ffff">Cyan</option>
\t\t\t\t<option value="#006400">Dark Green</option>
\t\t\t\t<option value="#2e8b57">Sea Green</option>
\t\t\t\t<option value="#00ff7f">Spring Green</option>
\t\t\t\t<option value="#7cfc00">Lawn Green</option>
\t\t\t\t<option value="#00ff00">Green</option>
\t\t\t\t<option value="#32cd32">Lime Green</option>
\t\t\t\t<option value="#ffff00">Yellow</option>
\t\t\t\t<option value="#ffd700">Gold</option>
\t\t\t\t<option value="#daa520">Goldenrod</option>
\t\t\t\t<option value="#b8860b">Dark Goldenrod</option>
\t\t\t\t<option value="#bc8f8f">Rosy Brown</option>
\t\t\t\t<option value="#cd5c5c">Indian Red</option>
\t\t\t\t<option value="#8b4513">Saddle Brown</option>
\t\t\t\t<option value="#b22222">Firebrick</option>
\t\t\t\t<option value="#a52a2a">Brown</option>
\t\t\t\t<option value="#fa8072">Salmon</option>
\t\t\t\t<option value="#ffa500">Orange</option>
\t\t\t\t<option value="#f08080">Light Coral</option>
\t\t\t\t<option value="#ff0000">Red</option>
\t\t\t\t<option value="#ff1493">Deep Pink</option>
\t\t\t\t<option value="#b03060">Maroon</option>
\t\t\t\t<option value="#d02090">Violet Red</option>
\t\t\t\t<option value="#ff00ff">Magenta</option>
\t\t\t\t<option value="#9932cc">Dark Orchid</option>
\t\t\t\t<option value="#8a2be2">Blue Violet</option>
\t\t\t\t<option value="#a020f0">Purple</option>
\t\t\t\t</select>
\t\t\tWidth
\t\t\t\t<select id="Widthselect" name="Widthselect" size="1" onChange="window.status='Re-drawing track line; please wait!!';ChangeColor();window.status=''" onfocus="window.status='Switch Track line width';return true;">
\t\t\t\t\t<option value="1">1</option>
\t\t\t\t\t<option value="2">2</option>
\t\t\t\t\t<option value="3">3</option>
\t\t\t\t\t<option value="4">4</option>
\t\t\t\t\t<option value="5">5</option>
\t\t\t\t\t<option value="6">6</option>
\t\t\t\t\t<option value="7">7</option>
\t\t\t\t\t<option value="8">8</option>
\t\t\t\t\t<option value="9">9</option>
\t\t\t\t\t<option value="10">10</option>
\t\t\t\t\t<option value="11">11</option>
\t\t\t\t\t<option value="12">12</option>
\t\t\t\t\t<option value="13">13</option>
\t\t\t\t\t<option value="14">14</option>
\t\t\t\t\t<option value="15">15</option>
\t\t\t\t</select></div></th></tr></table></div>
\t\t\t</td></tr></table>
\t</th></tr></table>
\t</form>
\t</body>
\t</html>
"""
""" The Google Maps html page template. """

SELECTED_TRACK_TEMPLATE = """\t\t\t<div class="block_b"><table width="95%%" border="0" cellspacing="0" cellpadding="0">
\t\t\t<tr><th scope="row"><H6>Selected Track</H6></th></tr>
\t\t\t<tr><th class="grey" scope="row"><div align="left">Selected Track
\t\t\t\t<select name="alltrack" size="1" onChange="window.status='Reloading new track; please wait!!';ChangeName(Myform.alltrack.value);window.status=''" onfocus="window.status='Switch Tracks';return true;">
%(trackselections)s\t\t\t\t</select></div></th></tr></table></div>
"""
""" Track selection template for TK1 files. """

VE_TRACKLIST_TEMPLATE = '\t\t\t\tcase "%(track)i":nowxml="%(filename)s";cname="%(datetime)s";cpoint="%(trackpoints)i";ctime="%(hours)ih:%(minutes)im:%(seconds)is";cdis="%(distance).2fkm";nowid =\'%(track)i\';nowPushTrack=PushTrack%(track)i;break;\n'
""" The Virtual Earth tracklist template. """

GM_TRACKLIST_TEMPLATE = '\t\t\t\tcase "%(track)i":nowxml="%(filename)s";cname="%(datetime)s";cpoint="%(trackpoints)i";ctime="%(hours)ih:%(minutes)im:%(seconds)is";cdis="%(distance).2fkm";nowBounds=Bounds%(track)i;nowPushTrack=PushTrack%(track)i;break;\n'
""" The Google Maps tracklist template. """

BOUNDS_TEMPLATE = '\t\tBounds%(track)i = new GLatLngBounds(new GLatLng(%(minlat).7f,%(minlon).7f), new GLatLng(%(maxlat).7f,%(maxlon).7f));\n'
""" The bounds template. """

TRACKSELECTIONS_TEMPLATE = '\t\t\t\t<option value="%(track)i">%(datetime)s</option>\n'
""" The track selections template. """

PUSHTRACK_TEMPLATE = """\t\tvar PushTrack%i=[\n%s\t\t];\n"""
""" The push track template. """

FIRST_PUSHTRACK_POINT = '\t\t%i\n'
""" The template for the first push trackpoint. """

PUSHTRACK_POINT = '\t\t,%i\n'
""" The template for the following push trackpoints. """

DATA_HEADER = '<params>\n'
""" The XML data header. """

FIRST_DATA_POINT = '\t\t<param lat="%(lat).7f" lng="%(lon).7f" vv="%(datetime)s&lt;br&gt;Speed: %(speed)i km/hr&lt;br&gt;Course: %(bearing)i deg.&lt;br&gt;%(logextension)s"/>\n'
""" The template for the first data point. """

DATA_POINT = '\t\t<param lat="%(lat).7f" lng="%(lon).7f" vv="%(datetime)s&lt;br&gt;Speed: %(speed).2f km/hr&lt;br&gt;Course: %(bearing)i deg&lt;br&gt;%(logextension)s"/>\n'
""" The template for the following data points. """

DATA_POINT_EXTENSION = 'Temperature: %s centigrade&lt;br&gt;Air Pressure: %s hPa &lt;br&gt;'
""" The template extension for WSG1000 log version 2.0. """

DATA_FOOTER = '</params>\n'
""" The XML data footer. """

# pylint: enable-msg=C0301

def createTracks(tkfiles, template):
    """
    Create track information.
    
    @param tkfiles: A list of TK files with track data.
    @param template: The html template.
    @return: A string with track information.
    """
    s = ""
    trackNumber = 0
    for tkfile in tkfiles:
        for track in tkfile.tracks():
            dateString = track.getFirstPoint().getDateTime().strftime(DATETIME_FILENAME_TEMPLATE)
            filename = "%s.xml" % dateString
            minutes, seconds = divmod(track.getTrackDuration(), 60)
            hours, minutes = divmod(minutes, 60)
            values = {"track": trackNumber,
                      "datetime": track.getFirstPoint().getDateTime(track.getTimezone()).strftime('%Y_%m_%d %H:%M:%S'),
                      "trackpoints": track.getTrackPointCount(), "hours": hours, "minutes": minutes, "seconds": seconds,
                      "distance": track.getTrackLength(), "filename": filename}
            s += template % values
            trackNumber += 1
    return s

def createTrackSelections(tkfiles):
    """
    Create track selection information.
    
    @param tkfile: A list of TK files with track data.
    @return: A string with track selection information.
    """
    s = ""
    trackNumber = 0
    for tkfile in tkfiles:
        for track in tkfile.tracks():
            values = {"track": trackNumber,
                      "datetime": track.getFirstPoint().getDateTime(track.getTimezone()).strftime('%Y_%m_%d %H:%M:%S')}
            s += TRACKSELECTIONS_TEMPLATE % values
            trackNumber += 1
    return s

def createBounds(tkfiles):
    """
    Create track bounds information.
    
    @param tkfiles: A list of TK files with track data.
    @return: A string with track bounds information.
    """
    s = ""
    trackNumber = 0
    for tkfile in tkfiles:
        for track in tkfile.tracks():
            maxLat = None
            maxLon = None
            minLat = None
            minLon = None
            for point in track.trackpoints():
                latitude = point.getLatitude()
                longitude = point.getLongitude()
                if maxLat is None or latitude > maxLat:
                    maxLat = latitude
                
                if maxLon is None or longitude > maxLon:
                    maxLon = longitude
                
                if minLat is None or latitude < minLat:
                    minLat = latitude
                
                if minLon is None or longitude < minLon:
                    minLon = longitude
                # FIXME: Time Machine X uses values higher than the maximum/lower than the minimum.
                #        I have no idea how these values are computed.
    
            values = {"track" : trackNumber, "minlat": minLat, "minlon": minLon, "maxlat": maxLat, "maxlon": maxLon}
            s += BOUNDS_TEMPLATE % values
            trackNumber += 1 
    return s

def createWaypoints(tkfiles):
    """
    Create waypoint information.
    
    @param tkfiles: A list of TK files with track data.
    @return: A string with waypoint informations
    """
    result = ""
    trackNumber = 0
    for tkfile in tkfiles:
        for track in tkfile.tracks():
            pointNumber = 0
            s = ""
            for point in track.trackpoints():
                pointNumber += 1
                if point.isLogPoint():
                    if s:
                        s += PUSHTRACK_POINT % pointNumber
                    else:
                        s = FIRST_PUSHTRACK_POINT % pointNumber
            result += PUSHTRACK_TEMPLATE % (trackNumber, s)
            trackNumber += 1
    return result

def writeTrack(track, outputFile, logversion):
    """
    Write track as xml file.
    
    @param track: The L{Track} to write.
    @param outputFile: The file handle.
    @param logversion: The logversion of the TK file.
    """
    previousPoint = None
    outputFile.write(DATA_HEADER)
    for point in track.trackpoints():
        speed = 0
        bearing = 0
        if previousPoint:
            distance, bearing = calculateVincentyDistance(previousPoint.getLatitude(), previousPoint.getLongitude(),
                                                          point.getLatitude(), point.getLongitude())
            timedelta = point.getDateTime() - previousPoint.getDateTime()
            time = timedelta.days * 24 * 60 * 60 + timedelta.seconds
            if time != 0:
                speed = distance / (time / float(60 * 60))
        if logversion == 2.0:
            extension = DATA_POINT_EXTENSION % (point.getTemperature(), point.getAirPressure())
        else:
            extension = ""
        pointDate = point.getDateTime(track.getTimezone()).strftime("%Y_%m_%d %H:%M:%SZ%z")
        pointDate = pointDate[:-2] + ":" + pointDate[-2:]
        values = {"lat": point.getLatitude(), "lon": point.getLongitude(), "datetime": pointDate, "speed": speed,
                  "bearing": bearing, "logextension": extension}
        if previousPoint:
            outputFile.write(DATA_POINT % values)
        else:
            outputFile.write(FIRST_DATA_POINT % values)
        previousPoint = point
    outputFile.write(DATA_FOOTER)

def writeHtmlFile(tkfiles, outputFile, values, template, trackTemplate):
    """
    Write html file.
    
    @param tkfiles: A list of TK files with track data.
    @param outputFile: The html file handle.
    @param values: A dictionary of strings.
    @param template: The html template.
    @param trackTemplate: The html track template.
    """
    # pylint: disable-msg=R0913
    values["tracklist"] = createTracks(tkfiles, trackTemplate)
    outputFile.write(template % values)

def createCommonValues(tkfiles):
    """
    Create dictionary with common values.
    
    @param tkfiles: A list of TK files with track data.
    @param timezone: The timezone as offset to UTC.
    @return: A dictionary of strings.
    """
    if len(tkfiles) > 1 or isinstance(tkfiles[0], TK1File):
        selectedtrack = SELECTED_TRACK_TEMPLATE % ({"trackselections": createTrackSelections(tkfiles)})
    else:
        selectedtrack = ""
    totaltracks = 0
    totalpoints = 0
    for tkfile in tkfiles:
        totaltracks += tkfile.getTrackCount()
        totalpoints += tkfile.getTrackpointCount()
    return {"totaltracks": totaltracks,
            "totalpoints": totalpoints,
            "pushTracks": createWaypoints(tkfiles), 
            "bounds": createBounds(tkfiles),
            "selectedtrack": selectedtrack}

def usage():
    """
    Print program usage.
    """
    executable = os.path.split(sys.argv[0])[1]
    print "%s Version %s (C) 2008 Steffen Siebert <siebert@steffensiebert.de>" % (executable, VERSION)
    print "Convert gps tracklogs from Wintec TK files into xml files and make them viewable"
    print "with Google Maps and/or Microsoft Virtual Earth html file.\n"
    print 'Usage: %s [-g] [-v] [-d directory] [-o filename] [-t +hh:mm|--autotz] <tk files>' % executable
    print "-g: Create Google Maps html file."
    print "-v: Create Microsoft Virtual Earth html file."
    print "-d: Use output directory."
    print "-o: Use output filename."
    print "-t: .tk1: Use timezone for local time (offset to UTC). .tk2/.tk3: Ignored."
    print "--autotz: .tk1: Determine timezone from first trackpoint. .tk2/.tk3: Ignored."

def main():
    """
    The main method.
    """
    #pylint: disable-msg=R0912, R0914, R0915
    createGoogleMaps = False
    createVirtualEarth = False
    outputDir = None
    filename = None
    timezone = None
    autotimezone = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "?hgvd:o:t:", "autotz")
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
        if o == "-g":
            createGoogleMaps = True
        if o == "-v":
            createVirtualEarth = True
        if o == "-d":
            outputDir = a
        if o == "-t":
            timezone = parseTimezone(a)
            if timezone == None:
                print "Timzone string doesn't match pattern +hh:mm!"
                sys.exit(4)
        if o == "-o":
            filename = a
        if o == "--autotz":
            autotimezone = True
    
    # if neither -g nor -v is specified, create both file types.
    if not createGoogleMaps and not createVirtualEarth:
        createGoogleMaps = createVirtualEarth = True

    if outputDir and not os.path.exists(outputDir):
        print "Output directory %s doesn't exist!" % outputDir
        sys.exit(3)

    tkfiles = []
    for arg in args:
        for tkFileName in glob(arg):
            tkfile = readTKFile(tkFileName)
            if isinstance(tkfile, TK1File):
                if timezone:
                    tkfile.setTimezone(timezone)
                tkfile.setAutotimezone(autotimezone)
            tkfiles.append(tkfile)

    tkfiles.sort(lambda x, y: cmp(x.getFirstTrackpoint().getDateTime(), y.getFirstTrackpoint().getDateTime()))
    
    if len(tkfiles) > 1:
        dateString = tkfiles[0].getFirstTrackpoint().getDateTimeString()
        dateString2 = tkfiles[-1].getFirstTrackpoint().getDateTimeString()
        filenameBase = '%s-%s#%03i' % (dateString, dateString2, len(tkfiles))
    else:
        if isinstance(tkfiles[0], TK1File):
            dateString = tkfiles[0].getFirstTrackpoint().getDateTimeString()
            dateString2 = tkfiles[0].getLastTrackpoint().getDateTimeString()
            filenameBase = '%s-%s#%03i' % (dateString, dateString2, tkfiles[0].getTrackCount())
        else:
            dateString = tkfiles[0].getFirstTrackpoint().getDateTimeString(DATETIME_FILENAME_TEMPLATE)
            filenameBase = '%s' % dateString

    for tkfile in tkfiles:
        for track in tkfile.tracks():
            dateString = track.getFirstPoint().getDateTime().strftime(DATETIME_FILENAME_TEMPLATE)
            outputFile = createOutputFile(outputDir, None, "%s.xml", dateString)
            if outputFile != None:
                writeTrack(track, outputFile, tkfile.getLogVersion())
                outputFile.close()

    values = createCommonValues(tkfiles)

    outputFile = createOutputFile(outputDir, filename, "%s_ve.html", filenameBase)
    writeHtmlFile(tkfiles, outputFile, values, VE_HTML_TEMPLATE, VE_TRACKLIST_TEMPLATE)
    outputFile.close()

    outputFile = createOutputFile(outputDir, filename, "%s_gm.html", filenameBase)
    writeHtmlFile(tkfiles, outputFile, values, GM_HTML_TEMPLATE, GM_TRACKLIST_TEMPLATE)
    outputFile.close()

if __name__ == "__main__":
    main()
