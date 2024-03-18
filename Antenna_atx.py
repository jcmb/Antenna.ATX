#! /usr/bin/env python3

import fileinput
from pprint import pprint
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tempfile
import base64

#pprint=pprint.PrettyPrinter(stream=sys.stderr)

from JCMBSoftPyLib import HTML_Unit

"""
Record indicating the start of a new     |3X,A1,I2,54X|
 |                    | frequency section. The satellite system  |            |
 |                    | flag ('G','R','E','C','J','S') has to be |            |
 |                    | specified together with the frequency    |            |
 |                    | number code that has to be consistent    |            |
 |                    | with the RINEX definition:               |            |
 |                    | GPS:     'G01' - L1                      |            |
 |                    |          'G02' - L2                      |            |
 |                    |          'G05' - L5                      |            |
 |                    | GLONASS: 'R01' - G1                      |            |
 |                    |          'R02' - G2                      |            |
 |                    | Galileo: 'E01' - E1                      |            |
 |                    |          'E05' - E5a                     |            |
 |                    |          'E07' - E5b                     |            |
 |                    |          'E08' - E5 (E5a+E5b)            |            |
 |                    |          'E06' - E6                      |            |
 |                    | Compass: 'C01' - E1                      |            |
 |                    |          'C02' - E2                      |            |
 |                    |          'C07' - E5b                     |            |
 |                    |          'C06' - E6                      |            |
 |                    | QZSS:    'J01' - L1                      |            |
 |                    |          'J02' - L2                      |            |
 |                    |          'J05' - L5                      |            |
 |                    |          'J06' - LEX                     |            |
 |                    | SBAS:    'S01' - L1                      |            |
 |                    |          'S05' - L5                      |            |
 """

GPS=0
GLONASS=1
GALILEO=2
COMPASS=3
QZSS=4
SBAS=5
IRNSS=6

L1=1
L2=2
L5=5

E1=1
E2=2
E5a=5
E5b=7
E5=8
E6=6

LEX=6

N_Offset=0
E_Offset=1
U_Offset=2


NO_AZ=-99

In_Antenna=False
In_APC_Offsets=False

GPS_Cal_Antennas="# Number of Calibrated Antennas GPS:"
GPS_Cal_Antennas_Length=len(GPS_Cal_Antennas)

GPS_Generic_Cal_Antennas="# Number of Calibrated Antennas:"
GPS_Generic_Cal_Antennas_Length=len(GPS_Generic_Cal_Antennas)

GLO_Cal_Antennas="# Number of Calibrated Antennas GLO:"
GLO_Cal_Antennas_Length=len(GLO_Cal_Antennas)

SV_Types={
  "BLOCK I",
  "BLOCK II",
  "BLOCK IIA",
  "BLOCK IIF",
  "BLOCK IIR",
  "BLOCK IIR-A",
  "BLOCK IIR-B",
  "BLOCK IIR-M",
  "BLOCK IIIA",
  "GLONASS",
  "GLONASS-M",
  "GLONASS-K1",
  "GLONASS-K2",
  "GALILEO-1",
  "GALILEO-2",
  "GALILEO-0A",
  "GALILEO-0B",
  "BEIDOU-2G",
  "BEIDOU-2I",
  "BEIDOU-2M",
  "BEIDOU-3I",
  "BEIDOU-3G-CAST",
  "BEIDOU-3M-CAST",
  "BEIDOU-3M-SECM",
  "BEIDOU-3SM-CAST",
  "BEIDOU-3SI-CAST",
  "BEIDOU-3SI-SECM",
  "QZSS",
  "QZSS-2A",
  "QZSS-2G",
  "QZSS-2I",
  "IRNSS-1IGSO",
  "IRNSS-1GEO",
  "IRNSS-2GEO"
  }

HTML_Unit.output_html_header(sys.stdout,"Antenna information")
HTML_Unit.output_html_body(sys.stdout)
HTML_Unit.output_table_header(sys.stdout,"Antenna_Information","Antenna Information",
  [ "Type",
    "Bands",
    "Freqs",
    "GPS Antennas",
    "GLO Antennas",
    "GPS Freqs",
    "GPS L1 Offsets",
    "GPS L2 Offsets",
    "GLO Freqs",
    "GLO L1 Offsets",
    "GLO L2 Offsets",
    ])
#       HTML_Unit.output_table_row(sys.stdout,[defect,defects_Desc[defect],Versions_Str])


def safe_filename(filename):

  result = filename.replace('\\',"_")
  result = result.replace('/',"_")
  result = result.replace(':',"_")
  result = result.replace(' ',"_")
  return (result)

def plot_polar_contour(Title,values, azimuths, zeniths,range):
    """Plot a polar contour plot, with 0 degrees at the North.

    Arguments:

     * `values` -- A list (or other iterable - eg. a NumPy array) of the values to plot on the
     contour plot (the `z` values)
     * `azimuths` -- A list of azimuths (in degrees)
     * `zeniths` -- A list of zeniths (that is, radii)

    The shapes of these lists are important, and are designed for a particular
    use case (but should be more generally useful). The values list should be `len(azimuths) * len(zeniths)`
    long with data for the first azimuth for all the zeniths, then the second azimuth for all the zeniths etc.

    This is designed to work nicely with data that is produced using a loop as follows:

    values = []
    for azimuth in azimuths:
      for zenith in zeniths:
        # Do something and get a result
        values.append(result)

    After that code the azimuths, zeniths and values lists will be ready to be passed into this function.

    """
#    sys.stderr.write(Title+"\n")
#    sys.stderr.write("Az {}: {}\n".format(len(azimuths),azimuths))
#    sys.stderr.write("Elev {}: {}\n".format(len(zeniths),zeniths))
#    sys.stderr.write("Values: {}\n".format(values))


    theta = np.radians(azimuths)
    zeniths = np.array(zeniths)

    values = np.array(values)
    values = values.reshape(len(azimuths), len(zeniths))

    r, theta = np.meshgrid(zeniths, np.radians(azimuths))
    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    ax.set_theta_zero_location("N")
    ax.set_theta_direction("clockwise")
    plt.title(Title)
#    plt.ylim(range)

# Todo
#    ax.set_rgrids([30,60],labels=["30","60"],angle=[0,0],fmt=None,visible=False)
#    ax.set_rgrids([30.0,60.0],angle=[45,135],fmt=None)
    cax = plt.contourf(theta, r, values, 30, levels=range)
    cb = fig.colorbar(cax)
    cb.set_label("Bias (mm)")

    return cax

#def create_mean_plot (Antenna,Band,Elev_Correction_L1,Elev_Correction_L2):

def create_mean_plot (Antenna,System,Elev_Corrections,Elev_Names):
   Elev_Labels=[]
   Elev_values=[]

   Max_Correction=0

   plt.figure(figsize=(8,6),dpi=100)
   plt.ylabel("Bias (mm)")
   plt.xlabel("Elevation angle (degrees)")
   plt.suptitle(Antenna)
   plt.title("Antenna Phase Biases: " + System)
   #plt.grid()

   xplot_range=[0,90]
   plt.xlim(xplot_range)

   if len(Elev_Corrections) == 0:
      returrn("")

   if len(Elev_Corrections[0]) == 0:
      returrn("")

   for Item in Elev_Corrections[0]:
      Elev_Labels.append(Item[0])


   Name_Index=0

   for band in Elev_Corrections:
      Elev_values=[]

      for Item in band:
         if abs(Item[1]) > Max_Correction:
            Max_Correction=abs(Item[1])
         Elev_values.insert(0,Item[1])

      print(Elev_Names[Name_Index])
      pprint(Elev_Labels)
      print("Values")
      pprint(Elev_values)
      plt.plot(Elev_Labels,Elev_values,label=Elev_Names[Name_Index])
      Name_Index+=1


#   plot_range=[x_values[0],x_values[len(x_values)-1]]

   if Max_Correction <= 5.0:
      yplot_range=[-5,5]
      plt.ylim(yplot_range)
   elif Max_Correction <= 10.0:
      yplot_range=[-10,10]
      plt.ylim(yplot_range)
   elif Max_Correction <= 15.0:
      yplot_range=[-15,15]
      plt.ylim(yplot_range)
   elif Max_Correction <= 20.0:
      yplot_range=[-20,20]
      plt.ylim(yplot_range)

#
#   plt.plot(x_values,y_values)
   plt.legend()
   filename=safe_filename(Antenna)+"." + System +'.MEAN.png'

   try:
    plt.savefig(filename,format="png")
   except:
    filename="Error"
   plt.close('all')
   return (filename)

def create_az_plot (Antenna,Band,Az_Elev_Correction):

   Elev_Labels=[]
   L1_values=[]
   L2_values=[]


   plt.figure(figsize=(8,6),dpi=100)
   plt.ylabel("Bias (mm)")
   plt.xlabel("Elvation angle (degrees)")
   plt.suptitle(Antenna)
   plt.title("Antenna Phase Biases: " + Band)
   #plt.grid()
   plot_range=[0,90]
   plt.xlim(plot_range)

   for Item in Az_Elev_Correction[0]:
      Elev_Labels.append(Item[0])
#      Elev_Labels.insert(0,Item[0])

   Max_Correction=0
   for Az in sorted(Az_Elev_Correction):
     if Az !=NO_AZ:
       for Item in Az_Elev_Correction[Az]:
#          values.append(Item[1])
          if abs(Item[1]) > Max_Correction:
             Max_Correction=abs(Item[1])
   yplot_range=[-50,50]
   if Max_Correction <= 5.0:
      yplot_range=[-5,5]
      plt.ylim(yplot_range)
   elif Max_Correction <= 10.0:
      yplot_range=[-10,10]
      plt.ylim(yplot_range)
   elif Max_Correction <= 15.0:
      yplot_range=[-15,15]
      plt.ylim(yplot_range)
   elif Max_Correction <= 20.0:
      yplot_range=[-20,20]
      plt.ylim(yplot_range)


   for Az in sorted(Az_Elev_Correction):
     if Az !=NO_AZ:
       values=[]
       for Item in Az_Elev_Correction[Az]:
#          values.append(Item[1])
          values.insert(0,Item[1])



       plt.plot(Elev_Labels,values,label=Band + "-" + str(Az))
   filename= safe_filename(Antenna)+"." + Band+'.AZ.png'
   try:
     plt.savefig(filename,format="png")
   except:
     filename="ERROR"

   plt.close()

   return(filename)

def create_az_delta_plot (Antenna,Band,Az_Elev_Correction):

   Elev_Labels=[]
   L1_values=[]
   L2_values=[]


   plt.figure(figsize=(8,6),dpi=100)
   plt.ylabel("Bias from mean (mm)")
   plt.xlabel("Elvation angle (degrees)")
   plt.suptitle(Antenna)
   plt.title("Delta Antenna Phase Biases: " + Band)
   #plt.grid()
   yplot_range=[-5,5]
   plt.ylim(yplot_range)
   plot_range=[0,90]
   plt.xlim(plot_range)

   for Item in Az_Elev_Correction[0]:
      Elev_Labels.append(Item[0])
#      Elev_Labels.insert(0,Item[0])


   for Az in sorted(Az_Elev_Correction):
     if Az !=NO_AZ:
       values=[]
#       pprint (Az_Elev_Correction[Az],stream=sys.stderr)
       for index, item in enumerate(Az_Elev_Correction[Az]):
#          values.append(Item[1])
          values.insert(0,item[1]-Az_Elev_Correction[NO_AZ][index][1])



       plt.plot(Elev_Labels,values,label=Band + "-" + str(Az))
   filename= safe_filename(Antenna)+"." + Band+'.AZ-Difference.png'
   try:
     plt.savefig(filename,format="png")
   except:
     filename="ERROR"

   plt.close()

   return(filename)



def create_plot_radial(Antenna,Band,Az_Elev_Correction):

   Az_Labels=[]
   for Az in sorted(Az_Elev_Correction):
    if Az !=NO_AZ:
      Az_Labels.append(Az)

   Elev_Labels=[]
   for Item in Az_Elev_Correction[0]:
      Elev_Labels.append(Item[0])


   Max_Correction=0
   Bias_values=[]
   for Az in sorted(Az_Elev_Correction):
     if Az !=NO_AZ :
       for Item in Az_Elev_Correction[Az]:
          Bias_values.append(Item[1])
#          Bias_values.insert(0,Item[1])

          if abs(Item[1]) > Max_Correction:
             Max_Correction=abs(Item[1])

   yplot_range=list(range(-30,31,1))

   if Max_Correction <= 5.0:
      yplot_range=list(range(-5,6,1))
   elif Max_Correction <= 10.0:
      yplot_range=list(range(-10,11,1))
   elif Max_Correction <= 15.0:
      yplot_range=list(range(-15,16,1))
   elif Max_Correction <= 20.0:
      yplot_range=list(range(-20,21,1))

#   pprint(Bias_values)
#   pprint(Az_Labels)
#   pprint(Elev_Labels)
#   pprint(yplot_range)

   plot_polar_contour("Antenna Phase Biases: " + Antenna+' ' + Band,Bias_values, Az_Labels, Elev_Labels,yplot_range)

   filename= safe_filename(Antenna)+"." + Band+'.POLAR.png'
   try:
    plt.savefig(filename,format="png")
   except:
     filename="ERROR"
   plt.close('all')

   return (filename)


def create_plot_delta_radial(Antenna,Band,Az_Elev_Correction):

   Az_Labels=[]
   for Az in sorted(Az_Elev_Correction):
    if Az !=NO_AZ:
      Az_Labels.append(Az)

   Elev_Labels=[]
   for Item in Az_Elev_Correction[0]:
      Elev_Labels.append(Item[0])

   Bias_values=[]
   for Az in sorted(Az_Elev_Correction):
     if Az !=NO_AZ :
       for index, item in enumerate(Az_Elev_Correction[Az]):

          Bias_values.append(item[1]-Az_Elev_Correction[NO_AZ][index][1])

   yplot_range=list(range(-5,6,1))

   plot_polar_contour("Delta Antenna Phase Biases: " + Antenna+' ' + Band,Bias_values, Az_Labels, Elev_Labels,yplot_range)

   filename= safe_filename(Antenna)+"." + Band+'.POLAR-Difference.png'
   try:
    plt.savefig(filename,format="png")
   except:
     filename="ERROR"
   plt.close('all')

   return (filename)

def dump_NEE_Offsets(output_file,offsets):
  pprint(offsets)
  if GPS in offsets:
    Az_html_file.write("<h3>GPS</h3>")
    if L1 in offsets[GPS]:
      Az_html_file.write("L1: N: {}  E: {} U: {}<br>".format(offsets[GPS][L1][N_Offset],offsets[GPS][L1][E_Offset],offsets[GPS][L1][U_Offset]))

    if L2 in offsets[GPS]:
      Az_html_file.write("L2: N: {}  E: {} U: {}<br>".format(offsets[GPS][L2][N_Offset],offsets[GPS][L2][E_Offset],offsets[GPS][L2][U_Offset]))

    if L5 in offsets[GPS]:
      Az_html_file.write("L5: N: {}  E: {} U: {}<br>".format(offsets[GPS][L5][N_Offset],offsets[GPS][L5][E_Offset],offsets[GPS][L5][U_Offset]))

  if GLONASS in offsets:
    Az_html_file.write("<h3>GLONASS</h3>")
    if L1 in offsets[GLONASS]:
      Az_html_file.write("L1: N: {}  E: {} U: {}<br>".format(offsets[GLONASS][L1][N_Offset],offsets[GLONASS][L1][E_Offset],offsets[GLONASS][L1][U_Offset]))

    if L2 in offsets[GLONASS]:
      Az_html_file.write("L2: N: {}  E: {} U: {}<br>".format(offsets[GLONASS][L2][N_Offset],offsets[GLONASS][L2][E_Offset],offsets[GLONASS][L2][U_Offset]))


  if GALILEO in offsets:
    Az_html_file.write("<h3>GALILEO</h3>")
    if E1 in offsets[GALILEO]:
      Az_html_file.write("E1: N: {}  E: {} U: {}<br>".format(offsets[GALILEO][E1][N_Offset],offsets[GALILEO][E1][E_Offset],offsets[GALILEO][E1][U_Offset]))

    if E5a in offsets[GALILEO]:
      Az_html_file.write("E5a: N: {}  E: {} U: {}<br>".format(offsets[GALILEO][E5a][N_Offset],offsets[GALILEO][E5a][E_Offset],offsets[GALILEO][E5a][U_Offset]))

    if E5b in offsets[GALILEO]:
      Az_html_file.write("E5b: N: {}  E: {} U: {}<br>".format(offsets[GALILEO][E5b][N_Offset],offsets[GALILEO][E5b][E_Offset],offsets[GALILEO][E5b][U_Offset]))

    if E5 in offsets[GALILEO]:
      Az_html_file.write("E5: N: {}  E: {} U: {}<br>".format(offsets[GALILEO][E5][N_Offset],offsets[GALILEO][E5][E_Offset],offsets[GALILEO][E5][U_Offset]))

    if E6 in offsets[GALILEO]:
      Az_html_file.write("E6: N: {}  E: {} U: {}<br>".format(offsets[GALILEO][E6][N_Offset],offsets[GALILEO][E6][E_Offset],offsets[GALILEO][E6][U_Offset]))


  if COMPASS in offsets:
    Az_html_file.write("<h3>BeiDou</h3>")
    if E1 in offsets[COMPASS]:
      Az_html_file.write("E1: N: {}  E: {} U: {}<br>".format(offsets[COMPASS][E1][N_Offset],offsets[COMPASS][E1][E_Offset],offsets[COMPASS][E1][U_Offset]))

    if E2 in offsets[COMPASS]:
      Az_html_file.write("E2: N: {}  E: {} U: {}<br>".format(offsets[COMPASS][E2][N_Offset],offsets[COMPASS][E2][E_Offset],offsets[COMPASS][E2][U_Offset]))

    if E5b in offsets[COMPASS]:
      Az_html_file.write("E5b: N: {}  E: {} U: {}<br>".format(offsets[COMPASS][E5b][N_Offset],offsets[COMPASS][E5b][E_Offset],offsets[COMPASS][E5b][U_Offset]))

    if E6 in offsets[COMPASS]:
      Az_html_file.write("E6: N: {}  E: {} U: {}<br>".format(offsets[COMPASS][E6][N_Offset],offsets[COMPASS][E6][E_Offset],offsets[COMPASS][E6][U_Offset]))

  if QZSS in offsets:
    Az_html_file.write("<h3>QZSS</h3>")
    if L1 in offsets[QZSS]:
      Az_html_file.write("L1: N: {}  E: {} U: {}<br>".format(offsets[QZSS][L1][N_Offset],offsets[QZSS][L1][E_Offset],offsets[QZSS][L1][U_Offset]))

    if L2 in offsets[QZSS]:
      Az_html_file.write("L2: N: {}  E: {} U: {}<br>".format(offsets[QZSS][L2][N_Offset],offsets[QZSS][L2][E_Offset],offsets[QZSS][L2][U_Offset]))

    if L5 in offsets[QZSS]:
      Az_html_file.write("L5: N: {}  E: {} U: {}<br>".format(offsets[QZSS][L5][N_Offset],offsets[QZSS][L5][E_Offset],offsets[QZSS][L5][U_Offset]))

    if LEX in offsets[QZSS]:
      Az_html_file.write("LEX: N: {}  E: {} U: {}<br>".format(offsets[QZSS][LEX][N_Offset],offsets[QZSS][LEX][E_Offset],offsets[QZSS][LEX][U_Offset]))

  if SBAS in offsets:
    Az_html_file.write("<h3>SBAS</h3>")
    if L1 in offsets[SBAS]:
      Az_html_file.write("L1: N: {}  E: {} U: {}<br>".format(offsets[SBAS][L1][N_Offset],offsets[SBAS][L1][E_Offset],offsets[SBAS][L1][U_Offset]))

    if L5 in offsets[SBAS]:
      Az_html_file.write("L5: N: {}  E: {} U: {}<br>".format(offsets[SBAS][L5][N_Offset],offsets[SBAS][L5][E_Offset],offsets[SBAS][L5][U_Offset]))

  if IRNSS in offsets:
    Az_html_file.write("<h3>IRNSS</h3>")
    if L5 in offsets[IRNSS]:
      Az_html_file.write("L5: N: {}  E: {} U: {}<br>".format(offsets[IRNSS][L5][N_Offset],offsets[IRNSS][L5][E_Offset],offsets[IRNSS][L5][U_Offset]))






for line in fileinput.input():
    line = line.rstrip()
#    print line
    Record_Type=line [60:]
#    print Record_Type,"*"
    if Record_Type=="START OF ANTENNA":
#      print "Start"
      NEE_Offsets={}
      APC_Offsets={}
      GPS_Antennas=None
      GLO_Antennas=None

      if In_Antenna :
        raise Exception("Got start of antenna while in antenna")
      else:
        In_Antenna=True
        DAZI=None

    if Record_Type=="END OF ANTENNA":
      if not Type in SV_Types:
#        print ("Type: {} Serial: {} Bands: {} Freqs: {} GPS Antennas: {} GLONASS Antennas: {}".format(Type,Serial,len(APC_Offsets[SV_System]),Num_Freqs,GPS_Antennas,GLO_Antennas))

        GPS_Offsets=None
        GPS_L1_Offsets=None
        GPS_L2_Offsets=None
        GPS_L5_Offsets=None
        GLO_Offsets=None
        GLO_L1_Offsets=None
        GLO_L2_Offsets=None
#        print(NEE_Offsets)


#Really need to split this one up, it is super ugly

        GPS_L1_Offsets_Txt=""
        GPS_L2_Offsets_Txt=""

        Az_html_file = None

        if GPS in APC_Offsets:
          GPS_Offsets=len(APC_Offsets[GPS])
#          print "  GPS Offsets: {}".format(GPS_Offsets)
          if L1 in APC_Offsets[GPS]:
            GPS_L1_Offsets=len(APC_Offsets[GPS][L1])
#            print "    GPS L1 Offsets: {}".format(GPS_L1_Offsets)
          if L2 in APC_Offsets[GPS]:
            GPS_L2_Offsets=len(APC_Offsets[GPS][L2])
#            print "    GPS L2 Offsets: {}".format(GPS_L2_Offsets)
          if L5 in APC_Offsets[GPS]:
            GPS_L5_Offsets=len(APC_Offsets[GPS][L2])
#            print "    GPS L2 Offsets: {}".format(GPS_L2_Offsets)

        if GPS in APC_Offsets:
          Offsets=[APC_Offsets[GPS][L1][NO_AZ]]

          if L2 in APC_Offsets[GPS]:
            Offsets.append(APC_Offsets[GPS][L2][NO_AZ])

          if L5 in APC_Offsets[GPS]:
            Offsets.append(APC_Offsets[GPS][L5][NO_AZ])

          plot_name=create_mean_plot (Type,"GPS",Offsets,["L1","L2","L5"])


          if GPS_L1_Offsets==1:
            GPS_L1_Offsets_Txt='<a target="_blank" href="'+plot_name+'">Mean</a>'
          elif GPS_L1_Offsets>1:
            Az_filename = safe_filename(Type)+".html"
            GPS_L1_Offsets_Txt=""
            GPS_L1_Offsets_Txt='<a target="_blank" href="'+Az_filename+'#GPS-L1">Azimuth</a>'
            Az_html_file = open(Az_filename, 'w')
            HTML_Unit.output_html_header(Az_html_file,"Antenna information for " + Type)
            HTML_Unit.output_html_body(Az_html_file)

            Az_html_file.write('<h1>Antenna information for {}</h1>'.format(Type))
            Az_html_file.write("\n")
            dump_NEE_Offsets(Az_html_file,NEE_Offsets)
            Az_html_file.write("\n")
  #          pprint(APC_Offsets[GPS][L1])
            Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GPS-Mean","GPS Mean"))
            Az_html_file.write('<img src="'+plot_name+'" alt="GPS Mean">')
            Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GPS-L1","GPS L1"))
            Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GPS-L1",APC_Offsets[GPS][L1]),Type+" GPS-L1"))
            Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GPS-L1",APC_Offsets[GPS][L1]),Type+" GPS-L1"))
            Az_html_file.write("\n")
            Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GPS-L1",APC_Offsets[GPS][L1]),"Radial " + Type+" GPS-L1"))
            Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GPS-L1",APC_Offsets[GPS][L1]),"Radial " + Type+" GPS-L1"))
            Az_html_file.write("\n")

            if GPS_L2_Offsets:
               if GPS_L2_Offsets==1: #this has a bug if there is Az dependent L1 and Mean L2
                  GPS_L2_Offsets_Txt='<a target="_blank" href="'+plot_name+'">Mean</a>'
                  try:
                    create_single_plot (Type,"GPS-L2",APC_Offsets[GPS][L2][NO_AZ])
                  except:
                    pass
               else:
                  GPS_L2_Offsets_Txt='<a target="_blank" href="'+Az_filename+'#GPS-L2">Azimuth</a>'

               Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GPS-L2","GPS L2"))
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GPS-L2",APC_Offsets[GPS][L2]),Type+" GPS-L2"))
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GPS-L2",APC_Offsets[GPS][L2]),Type+" GPS-L2"))
               Az_html_file.write("\n")
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GPS-L2",APC_Offsets[GPS][L2]),"Radial " + Type+" GPS-L2"))
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GPS-L2",APC_Offsets[GPS][L2]),"Radial " + Type+" GPS-L2"))
               Az_html_file.write("\n")



            if GPS_L5_Offsets:
               Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GPS-L5","GPS L5"))
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GPS-L5",APC_Offsets[GPS][L5]),Type+" GPS-L5"))
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GPS-L5",APC_Offsets[GPS][L5]),Type+" GPS-L5"))
               Az_html_file.write("\n")
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GPS-L5",APC_Offsets[GPS][L5]),"Radial " + Type+" GPS-L5"))
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GPS-L5",APC_Offsets[GPS][L5]),"Radial " + Type+" GPS-L5"))
               Az_html_file.write("\n")



        if GLONASS in APC_Offsets:
          GLO_Offsets=len(APC_Offsets[GLONASS])
#          print "  GLO Offsets: {}".format(GLO_Offsets)
          if L1 in APC_Offsets[GLONASS]:
            GLO_L1_Offsets=len(APC_Offsets[GLONASS][L1])
#            print "    GLO L1 Offsets: {}".format(GLO_L1_Offsets)
          if L2 in APC_Offsets[GLONASS]:
            GLO_L2_Offsets=len(APC_Offsets[GLONASS][L2])
#            print "    GLO L2 Offsets: {}".format(GLO_L2_Offsets)



        GLO_L1_Offsets_Txt=""
        GLO_L2_Offsets_Txt=""

        if GLO_L1_Offsets!=None:
          if GLO_L2_Offsets:
            try:
              plot_name=create_mean_plot (Type,"GLO",APC_Offsets[GLONASS][L1][NO_AZ],APC_Offsets[GLONASS][L2][NO_AZ])
            except:
              pass
          else:
            try:
              plot_name=create_mean_plot (Type,"GLO",APC_Offsets[GLONASS][L1][NO_AZ],None)
            except:
              pass

        if GLONASS in APC_Offsets:
          Offsets=[APC_Offsets[GLONASS][L1][NO_AZ]]

          if L2 in APC_Offsets[GLONASS]:
            Offsets.append(APC_Offsets[GLONASS][L2][NO_AZ])


          plot_name=create_mean_plot (Type,"GLONASS",Offsets,["L1","L2"])


          if GLO_L1_Offsets==1:
            GLO_L1_Offsets_Txt="Mean"
            try:
              create_single_plot (Type,"GLO",APC_Offsets[GLONASS][L1][NO_AZ])
            except:
              pass
          elif GLO_L1_Offsets>1:
  #          GLO_L1_Offsets_Txt="Azimuth"
            GLO_L1_Offsets_Txt='<a target="_blank" href="'+Az_filename+'#GLO-L1">Azimuth</a>'

        if GLO_L2_Offsets!=None:

          if GLO_L2_Offsets==1:
            GLO_L2_Offsets_Txt="Mean"
            try:
              create_single_plot (Type,"GLO-L2",APC_Offsets[GLONASS][L2][NO_AZ])
            except:
              pass
          elif GLO_L2_Offsets>1:
  #          GLO_L2_Offsets_Txt="Azimuth"
            GLO_L2_Offsets_Txt='<a target="_blank" href="'+Az_filename+'#GLO-L2">Azimuth</a>'

            Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GLO-Mean","GLO Mean"))
            Az_html_file.write('<img src="'+plot_name+'" alt="GLO Mean">')


            Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GLO-L1","GLO L1"))
            Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GLO-L1",APC_Offsets[GLONASS][L1]),Type+" GLO-L1"))
            Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GLO-L1",APC_Offsets[GLONASS][L1]),Type+" GLO-L1"))
            Az_html_file.write("\n")
            Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GLO-L1",APC_Offsets[GLONASS][L1]),"Radial " + Type+" GLO-L1"))
            Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GLO-L1",APC_Offsets[GLONASS][L1]),"Radial " + Type+" GLO-L1"))
            Az_html_file.write("\n")


            if GLO_L2_Offsets:
               Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GLO-L2","GLO L2"))
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GLO-L2",APC_Offsets[GLONASS][L2]),Type+" GLO-L2"))
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GLO-L2",APC_Offsets[GLONASS][L2]),Type+" GLO-L2"))
               Az_html_file.write("\n")
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GLO-L2",APC_Offsets[GLONASS][L2]),"Radial " + Type+" GLO-L2"))
               Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GLO-L2",APC_Offsets[GLONASS][L2]),"Radial " + Type+" GLO-L2"))
               Az_html_file.write("\n")



        if GPS_Offsets == None:
          GPS_Offsets_Txt=""
        else:
          GPS_Offsets_Txt=str(GPS_Offsets)

        if GLO_Offsets == None:
          GLO_Offsets_Txt=""
        else:
          GLO_Offsets_Txt=str(GLO_Offsets)

        if GPS_Antennas==None:
          GPS_Antennas="N/A"
        if GLO_Antennas==None:
          GLO_Antennas="N/A"

        HTML_Unit.output_table_row(sys.stdout,
            [Type,len(APC_Offsets[SV_System]),Num_Freqs,GPS_Antennas,GLO_Antennas,
              GPS_Offsets_Txt,GPS_L1_Offsets_Txt,GPS_L2_Offsets_Txt,
              GLO_Offsets_Txt,GLO_L1_Offsets_Txt,GLO_L2_Offsets_Txt])

        if Az_html_file != None:
          HTML_Unit.output_html_footer(Az_html_file,[])

          Az_html_file.close()
          Az_html_file=None

      if In_Antenna :
        In_Antenna=False
      else:
        raise Exception("Got end of antenna while not in antenna")

    if Record_Type=="COMMENT":
#      print "COMMENT"
      if line.find(GPS_Cal_Antennas)==0 :
#        print "GPS"
        GPS_Antennas=int(line[GPS_Cal_Antennas_Length:60],base=10)
#        print GPS_Antennas
      elif line.find(GPS_Generic_Cal_Antennas)==0 :
#        print "GPS Generic"
        GPS_Antennas=int(line[GPS_Generic_Cal_Antennas_Length:60],base=10)
#        print GPS_Antennas
      elif line.find(GLO_Cal_Antennas)==0:
#        print "GLONASS"
        GLO_Antennas=int(line[GLO_Cal_Antennas_Length:60],base=10)
#        print GLO_Antennas
      elif line.find("# Number of Individual GLO-Calibrations:")==0:
        if GLO_Antennas==None:
          GLO_Antennas=GPS_Antennas
          #Handle the antennas with a generic antenna total comment and GLONASS
#      print line
    if Record_Type=="TYPE / SERIAL NO":
      if In_Antenna :
        Type=line[0:20].rstrip()
        Serial=line[20:60].rstrip()
#        print Type,Serial
      else:
        raise Exception("Got end of antenna while not in antenna")

    if Record_Type=="DAZI":
#      print line
      if In_Antenna :
        DAZI=float(line[2:6])
      else:
        raise Exception("Got DAZI while not in antenna")


    if Record_Type=="ZEN1 / ZEN2 / DZEN":
      if In_Antenna :
        ZEN1=float(line[2:8])
        ZEN2=float(line[8:14])
        DZEN=float(line[14:20])
      else:
        raise Exception("Got ZEN1 / ZEN2 / DZEN while not in antenna")

    if Record_Type=="# OF FREQUENCIES":
      if In_Antenna :
        Num_Freqs=int(line[0:6])
#        print Num_Freqs
      else:
        raise Exception("Got # OF FREQUENCIES while not in antenna")

    if Record_Type=="SINEX CODE":
      if In_Antenna :
        Sinex_Code=line[0:10]
#        print Sinex_Code
      else:
        raise Exception("Got SINEX CODE while not in antenna")

    if Record_Type=="START OF FREQUENCY":
      if In_Antenna :
        SV_System_Char=line[3:4]
        if SV_System_Char=="G":
          SV_System=GPS
        elif SV_System_Char=="R":
          SV_System=GLONASS
        elif SV_System_Char=="E":
          SV_System=GALILEO
        elif SV_System_Char=="C":
          SV_System=COMPASS
        elif SV_System_Char=="J":
          SV_System=QZSS
        elif SV_System_Char=="S":
          SV_System=SBAS
        elif SV_System_Char=="I":
          SV_System=IRNSS
        else:
          raise Exception("Uknown SV_System_Char" + line)
        Freq_Number=int(line[4:6])
      else:
        raise Exception("Got START OF FREQUENCY while not in antenna")

    if Record_Type=="END OF FREQUENCY":
      if In_Antenna :
        In_APC_Offsets=False
      else:
        raise Exception("Got END OF FREQUENCY while not in antenna")

# Here we may be in a antenna model set. We have to do the checking after the end of freq and before the NEU which shows the start of freqs

    if In_APC_Offsets:
      Az=line[0:8]
      if Az== "   NOAZI":
        Az=NO_AZ
      else:
        Az=float(Az)

      line=line[8:]

      zen=ZEN1

      Offsets=[]

      while zen<=ZEN2:
#Yes if someone really did models at 0.1 resolution we would break but since they are all 5 degrees at the moment we don't care.
        offset=float(line[0:8])
        line=line[8:]
        Offsets.append([zen,offset])
        zen+=DZEN

      APC_Offsets[SV_System][Freq_Number][Az]=Offsets




    if Record_Type=="NORTH / EAST / UP":
      if In_Antenna :
        North=float(line[0:10])
        East=float(line[10:20])
        Up=float(line[20:30])
        if not SV_System in NEE_Offsets:
          NEE_Offsets[SV_System]={}
          APC_Offsets[SV_System]={}
        NEE_Offsets[SV_System][Freq_Number]=(North,East,Up)
        APC_Offsets[SV_System][Freq_Number]={}
        In_APC_Offsets=True
      else:
        raise Exception("Got NORTH / EAST / UP while not in antenna")




HTML_Unit.output_table_footer(sys.stdout)

HTML_Unit.output_html_footer(sys.stdout,["Antenna_Information"])
