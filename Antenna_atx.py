#! /usr/bin/env python

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

GPS=0
GLONASS=1
GALILEO=2
COMPASS=3
QZSS=4
SBAS=5
IRNSS=6

L1=1
L2=2

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
  "GLONASS",
  "GLONASS-M",
  "GLONASS-K1",
  "GALILEO-1",
  "GALILEO-2",
  "GALILEO-0A",
  "GALILEO-0B",
  "BEIDOU-2G",
  "BEIDOU-2I",
  "BEIDOU-2M",
  "QZSS",
  "IRNSS-1IGSO",
  "IRNSS-1GEO"
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

    ax.set_rgrids([30,60],labels=["30","60"],angle=[0,0],fmt=None,visible=False)
    cax = plt.contourf(theta, r, values, 30, levels=range)
    cb = fig.colorbar(cax)
    cb.set_label("Bias (mm)")

    return cax
    
def create_mean_plot (Antenna,Band,Elev_Correction_L1,Elev_Correction_L2):
   Elev_Labels=[]
   L1_values=[]
   L2_values=[]
   
   Max_Correction=0
   for Item in Elev_Correction_L1:
#      print day, Days_Since[day]
      Elev_Labels.append(Item[0])
#      L1_values.append(Item[1])
      if abs(Item[1]) > Max_Correction:
         Max_Correction=abs(Item[1])
      L1_values.insert(0,Item[1])
      

   if Elev_Correction_L2 != None:
     for Item in Elev_Correction_L2:
#        L2_values.append(Item[1])
        L2_values.insert(0,Item[1])
        if abs(Item[1]) > Max_Correction:
           Max_Correction=abs(Item[1])
      
#   plot_range=[x_values[0],x_values[len(x_values)-1]]
      
   plt.figure(figsize=(8,6),dpi=100)
   plt.ylabel("Bias (mm)")
   plt.xlabel("Elevation angle (degrees)")
   plt.suptitle(Antenna)
   plt.title("Antenna Phase Biases: " + Band)
   #plt.grid()
   
   xplot_range=[0,90]
   plt.xlim(xplot_range)

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
   


   plt.plot(Elev_Labels,L1_values,label="L1" )


   if L2_values != []:
     plt.plot(Elev_Labels,L2_values,label="L2")   
#
#   plt.plot(x_values,y_values)
   plt.legend()
   filename=safe_filename(Antenna)+"." + Band+'.MEAN.png'

   try:
    plt.savefig(filename,format="png")
   except:
    filename="Error" 
   plt.close('all')
#   plt.show()
#   tmp_file=tempfile.SpooledTemporaryFile()
#   plt.savefig(tmp_file,format="png")
#   tmp_file.seek(0)
#   img_data=base64.b64encode(tmp_file.read(-1))
#   tmp_file.close('all')
#   plt.close('all')
#   return(img_data)
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

   yplot_range=range(-30,30,1)

   if Max_Correction <= 5.0:
      yplot_range=range(-5,5,1)
   elif Max_Correction <= 10.0:
      yplot_range=range(-10,10,1)
   elif Max_Correction <= 15.0:
      yplot_range=range(-15,15,1)
   elif Max_Correction <= 20.0:
      yplot_range=range(-20,20,1)
       
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

   yplot_range=range(-5,5,1)
       
   plot_polar_contour("Delta Antenna Phase Biases: " + Antenna+' ' + Band,Bias_values, Az_Labels, Elev_Labels,yplot_range)

   filename= safe_filename(Antenna)+"." + Band+'.POLAR-Difference.png'
   try:
    plt.savefig(filename,format="png")
   except:
     filename="ERROR"
   plt.close('all')

   return (filename)



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
#        print "Type: {} Serial: {} Bands: {} Freqs: {} GPS Antennas: {} GLONASS Antennas: {}".format(Type,Serial,len(APC_Offsets[SV_System]),Num_Freqs,GPS_Antennas,GLO_Antennas)
        
        GPS_Offsets=None
        GPS_L1_Offsets=None
        GPS_L2_Offsets=None
        GLO_Offsets=None
        GLO_L1_Offsets=None
        GLO_L2_Offsets=None
        
        if 0 in APC_Offsets:
          GPS_Offsets=len(APC_Offsets[0])
#          print "  GPS Offsets: {}".format(GPS_Offsets)
          if 1 in APC_Offsets[0]:
            GPS_L1_Offsets=len(APC_Offsets[GPS][L1])
#            print "    GPS L1 Offsets: {}".format(GPS_L1_Offsets)
          if 2 in APC_Offsets[0]:
            GPS_L2_Offsets=len(APC_Offsets[GPS][L2])
#            print "    GPS L2 Offsets: {}".format(GPS_L2_Offsets)


        if 1 in APC_Offsets:
          GLO_Offsets=len(APC_Offsets[1])
#          print "  GLO Offsets: {}".format(GLO_Offsets)
          if 1 in APC_Offsets[1]:
            GLO_L1_Offsets=len(APC_Offsets[GLONASS][L1])
#            print "    GLO L1 Offsets: {}".format(GLO_L1_Offsets)
          if 2 in APC_Offsets[1]:
            GLO_L2_Offsets=len(APC_Offsets[GLONASS][L2])
#            print "    GLO L2 Offsets: {}".format(GLO_L2_Offsets)


  #      print
  #      print "End"
#        pprint (APC_Offsets)
  #      print
  
        GPS_L1_Offsets_Txt=""

        Az_html_file = None

        if GPS_L1_Offsets!=None:
          if GPS_L2_Offsets:
              plot_name=create_mean_plot (Type,"GPS",APC_Offsets[GPS][L1][NO_AZ],APC_Offsets[GPS][L2][NO_AZ])
          else:
              plot_name=create_mean_plot (Type,"GPS",APC_Offsets[GPS][L1][NO_AZ],None)

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
          if GPS_L2_Offsets:
             Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GPS-Mean","GPS Mean"))
             Az_html_file.write('<img src="'+plot_name+'" alt="GPS Mean">')
             Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GPS-L1","GPS L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GPS-L1",APC_Offsets[GPS][L1]),Type+" GPS-L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GPS-L1",APC_Offsets[GPS][L1]),Type+" GPS-L1"))
             Az_html_file.write("\n")
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GPS-L1",APC_Offsets[GPS][L1]),"Radial " + Type+" GPS-L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GPS-L1",APC_Offsets[GPS][L1]),"Radial " + Type+" GPS-L1"))
             Az_html_file.write("\n")
             Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GPS-L2","GPS L2"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GPS-L2",APC_Offsets[GPS][L2]),Type+" GPS-L2"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GPS-L2",APC_Offsets[GPS][L2]),Type+" GPS-L2"))
             Az_html_file.write("\n")
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GPS-L2",APC_Offsets[GPS][L2]),"Radial " + Type+" GPS-L2"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GPS-L2",APC_Offsets[GPS][L2]),"Radial " + Type+" GPS-L2"))
             Az_html_file.write("\n")

          else:
             Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GPS-L1","GPS L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GPS-L1",APC_Offsets[GPS][L1]),Type+" GPS-L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GPS-L1",APC_Offsets[GPS][L1]),Type+" GPS-L1"))
             Az_html_file.write("\n")
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GPS-L1",APC_Offsets[GPS][L1]),"Radial " + Type+" GPS-L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GPS-L1",APC_Offsets[GPS][L1]),"Radial " + Type+" GPS-L1"))
             Az_html_file.write("\n")


          
        GPS_L2_Offsets_Txt=""
        if GPS_L2_Offsets==1: #this has a bug if there is Az dependent L1 and Mean L2
          GPS_L2_Offsets_Txt='<a target="_blank" href="'+plot_name+'">Mean</a>'
          try:
            create_single_plot (Type,"GPS-L2",APC_Offsets[GPS][L2][NO_AZ])
          except:
            pass
        elif GPS_L2_Offsets>1:
          GPS_L2_Offsets_Txt='<a target="_blank" href="'+Az_filename+'#GPS-L2">Azimuth</a>'


        if GLO_L1_Offsets!=None:
          if GLO_L2_Offsets:
            try:
              create_mean_plot (Type,"GLO",APC_Offsets[GLONASS][L1][NO_AZ],APC_Offsets[GLONASS][L2][NO_AZ])
            except:
              pass
          else:
            try:
              create_mean_plot (Type,"GLO",APC_Offsets[GLONASS][L1][NO_AZ],None)
            except:
              pass



        GLO_L1_Offsets_Txt=""
        if GLO_L1_Offsets==1:
          GLO_L1_Offsets_Txt="Mean"
          try:
            create_single_plot (Type,"GLO",APC_Offsets[GLONASS][L1][NO_AZ])
          except:
            pass
        elif GLO_L1_Offsets>1:
#          GLO_L1_Offsets_Txt="Azimuth"
          GLO_L1_Offsets_Txt='<a target="_blank" href="'+Az_filename+'#GLO-L1">Azimuth</a>'

          
        GLO_L2_Offsets_Txt=""
        if GLO_L2_Offsets==1:
          GLO_L2_Offsets_Txt="Mean"
          try:
            create_single_plot (Type,"GLO-L2",APC_Offsets[GLONASS][L2][NO_AZ])
          except:
            pass
        elif GLO_L2_Offsets>1:
#          GLO_L2_Offsets_Txt="Azimuth"
          GLO_L2_Offsets_Txt='<a target="_blank" href="'+Az_filename+'#GLO-L2">Azimuth</a>'
          
          if GLO_L2_Offsets:
             Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GLO-Mean","GLO Mean"))
             Az_html_file.write('<img src="'+plot_name+'" alt="GPS Mean">')
             Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GLO-L1","GLO L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GLO-L1",APC_Offsets[GLONASS][L1]),Type+" GLO-L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GLO-L1",APC_Offsets[GLONASS][L1]),Type+" GLO-L1"))
             Az_html_file.write("\n")
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GLO-L1",APC_Offsets[GLONASS][L1]),"Radial " + Type+" GLO-L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GLO-L1",APC_Offsets[GLONASS][L1]),"Radial " + Type+" GLO-L1"))
             Az_html_file.write("\n")
             Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GLO-L2","GLO L2"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GLO-L2",APC_Offsets[GLONASS][L2]),Type+" GLO-L2"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GLO-L2",APC_Offsets[GLONASS][L2]),Type+" GLO-L2"))
             Az_html_file.write("\n")
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_radial(Type,"GLO-L2",APC_Offsets[GLONASS][L2]),"Radial " + Type+" GLO-L2"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GLO-L2",APC_Offsets[GLONASS][L2]),"Radial " + Type+" GLO-L2"))
             Az_html_file.write("\n")

          else:
             Az_html_file.write('<h2><a name="{}">{}</h2>'.format("GLO-L1","GLO L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_plot (Type,"GLO-L1",APC_Offsets[GLONASS][L1]),Type+" GLO-L1"))
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_az_delta_plot (Type,"GLO-L1",APC_Offsets[GLONASS][L1]),Type+" GLO-L1"))
             Az_html_file.write("\n")
             Az_html_file.write('<br><img src="{}" alt="{}">'.format(create_plot_delta_radial(Type,"GLO-L1",APC_Offsets[GLONASS][L1]),"Radial " + Type+" GLO-L1"))
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


    