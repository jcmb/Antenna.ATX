#! /usr/bin/env python3

import fileinput
from pprint import pprint
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tempfile
import base64

# pprint=pprint.PrettyPrinter(stream=sys.stderr)

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

GPS = 0
GLONASS = 1
GALILEO = 2
COMPASS = 3
QZSS = 4
IRNSS = 5
SBAS = 6

SYSTEM_NAMES = [None] * (SBAS + 1)

SYSTEM_NAMES[GPS] = "GPS"
SYSTEM_NAMES[GLONASS] = "GLONASS"
SYSTEM_NAMES[GALILEO] = "GALILEO"
SYSTEM_NAMES[COMPASS] = "BeiDOU"
SYSTEM_NAMES[QZSS] = "QZSS"
SYSTEM_NAMES[IRNSS] = "IRNSS"
SYSTEM_NAMES[SBAS] = "SBAS"


L1 = 1
L2 = 2
L5 = 5

E1 = 1
E2 = 2
E5a = 5
E5b = 7
E5 = 8
E6 = 6

LEX = 6

N_Offset = 0
E_Offset = 1
U_Offset = 2


NO_AZ = -99

GPS_Generic_Cal_Antennas = "# Number of Calibrated Antennas:"
GPS_Generic_Cal_Antennas_Length = len(GPS_Generic_Cal_Antennas)

GPS_Cal_Antennas = "# Number of Calibrated Antennas GPS:"
GPS_Cal_Antennas_Length = len(GPS_Cal_Antennas)

GLO_Cal_Antennas = "# Number of Calibrated Antennas GLO:"
GLO_Cal_Antennas_Length = len(GLO_Cal_Antennas)


SV_Types = {
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
    "IRNSS-2GEO",
}


def safe_filename(filename):

    result = filename.replace("\\", "_")
    result = result.replace("/", "_")
    result = result.replace(":", "_")
    result = result.replace(" ", "_")
    return result


def plot_polar_contour(Title, values, azimuths, zeniths, range):
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
    fig, ax = plt.subplots(subplot_kw=dict(projection="polar"))
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


# def create_mean_plot (Antenna,Band,Elev_Correction_L1,Elev_Correction_L2):


def create_mean_plot(antennaName, System, Elev_Corrections, Elev_Names):
    Elev_Labels = []
    Elev_values = []

    Max_Correction = 0

    plt.figure(figsize=(8, 6), dpi=100)
    plt.ylabel("Bias (mm)")
    plt.xlabel("Elevation angle (degrees)")
    plt.suptitle(antennaName)
    plt.title("Antenna Phase Biases: " + SYSTEM_NAMES[System])
    # plt.grid()

    xplot_range = [0, 90]
    plt.xlim(xplot_range)

    if len(Elev_Corrections) == 0:
        returrn("")

    if len(Elev_Corrections[0]) == 0:
        returrn("")

    for Item in Elev_Corrections[0]:
        Elev_Labels.append(Item[0])

    Name_Index = 0

    for band in Elev_Corrections:
        Elev_values = []

        for Item in band:
            if abs(Item[1]) > Max_Correction:
                Max_Correction = abs(Item[1])
            Elev_values.insert(0, Item[1])

        #      print(Elev_Names[Name_Index])
        #      pprint(Elev_Labels)
        #      print("Values")
        #      pprint(Elev_values)
        plt.plot(Elev_Labels, Elev_values, label=Elev_Names[Name_Index])
        Name_Index += 1

    #   plot_range=[x_values[0],x_values[len(x_values)-1]]

    if Max_Correction <= 5.0:
        yplot_range = [-5, 5]
        plt.ylim(yplot_range)
    elif Max_Correction <= 10.0:
        yplot_range = [-10, 10]
        plt.ylim(yplot_range)
    elif Max_Correction <= 15.0:
        yplot_range = [-15, 15]
        plt.ylim(yplot_range)
    elif Max_Correction <= 20.0:
        yplot_range = [-20, 20]
        plt.ylim(yplot_range)

    #
    #   plt.plot(x_values,y_values)
    plt.legend()
    filename = safe_filename(antennaName) + "." + SYSTEM_NAMES[System] + ".MEAN.png"

    try:
        plt.savefig(filename, format="png")
    except:
        filename = "Error"

    plt.close("all")
    return filename


def create_az_plot(antennaName, bandName, Az_Elev_Correction):

#    pprint(antennaName)
#    pprint(bandName)
    Elev_Labels = []
    L1_values = []
    L2_values = []

    plt.figure(figsize=(8, 6), dpi=100)
    plt.ylabel("Bias (mm)")
    plt.xlabel("Elvation angle (degrees)")
    plt.suptitle(antennaName)
    plt.title("Antenna Phase Biases: " + bandName)
    # plt.grid()
    plot_range = [0, 90]
    plt.xlim(plot_range)

    for Item in Az_Elev_Correction[0]:
        Elev_Labels.append(Item[0])
    #      Elev_Labels.insert(0,Item[0])

    Max_Correction = 0
    for Az in sorted(Az_Elev_Correction):
        if Az != NO_AZ:
            for Item in Az_Elev_Correction[Az]:
                #          values.append(Item[1])
                if abs(Item[1]) > Max_Correction:
                    Max_Correction = abs(Item[1])

    yplot_range = [-50, 50]
    if Max_Correction <= 5.0:
        yplot_range = [-5, 5]
        plt.ylim(yplot_range)
    elif Max_Correction <= 10.0:
        yplot_range = [-10, 10]
        plt.ylim(yplot_range)
    elif Max_Correction <= 15.0:
        yplot_range = [-15, 15]
        plt.ylim(yplot_range)
    elif Max_Correction <= 20.0:
        yplot_range = [-20, 20]
        plt.ylim(yplot_range)

    for Az in sorted(Az_Elev_Correction):
        if Az != NO_AZ:
            values = []
            for Item in Az_Elev_Correction[Az]:
                #          values.append(Item[1])
                values.insert(0, Item[1])

            plt.plot(Elev_Labels, values, label=bandName + "-" + str(Az))
    filename = safe_filename(antennaName + "." + bandName + ".AZ.png")
    try:
        plt.savefig(filename, format="png")
    except:
        filename = "ERROR"

    plt.close()

    return filename


def create_az_delta_plot(antennaName, Band, Az_Elev_Correction):

    Elev_Labels = []
    L1_values = []
    L2_values = []

    plt.figure(figsize=(8, 6), dpi=100)
    plt.ylabel("Bias from mean (mm)")
    plt.xlabel("Elvation angle (degrees)")
    plt.suptitle(antennaName)
    plt.title("Delta Antenna Phase Biases: " + Band)
    # plt.grid()
    yplot_range = [-5, 5]
    plt.ylim(yplot_range)
    plot_range = [0, 90]
    plt.xlim(plot_range)

    for Item in Az_Elev_Correction[0]:
        Elev_Labels.append(Item[0])
    #      Elev_Labels.insert(0,Item[0])

    for Az in sorted(Az_Elev_Correction):
        if Az != NO_AZ:
            values = []
            #       pprint (Az_Elev_Correction[Az],stream=sys.stderr)
            for index, item in enumerate(Az_Elev_Correction[Az]):
                #          values.append(Item[1])
                values.insert(0, item[1] - Az_Elev_Correction[NO_AZ][index][1])

            plt.plot(Elev_Labels, values, label=Band + "-" + str(Az))
    filename = safe_filename(antennaName) + "." + Band + ".AZ-Difference.png"
    try:
        plt.savefig(filename, format="png")
    except:
        filename = "ERROR"

    plt.close()

    return filename


def create_plot_radial(antennaName, Band, Az_Elev_Correction):

    Az_Labels = []
    for Az in sorted(Az_Elev_Correction):
        if Az != NO_AZ:
            Az_Labels.append(Az)

    Elev_Labels = []
    for Item in Az_Elev_Correction[0]:
        Elev_Labels.append(Item[0])

    Max_Correction = 0
    Bias_values = []
    for Az in sorted(Az_Elev_Correction):
        if Az != NO_AZ:
            for Item in Az_Elev_Correction[Az]:
                Bias_values.append(Item[1])
                #          Bias_values.insert(0,Item[1])

                if abs(Item[1]) > Max_Correction:
                    Max_Correction = abs(Item[1])

    yplot_range = list(range(-30, 31, 1))

    if Max_Correction <= 5.0:
        yplot_range = list(range(-5, 6, 1))
    elif Max_Correction <= 10.0:
        yplot_range = list(range(-10, 11, 1))
    elif Max_Correction <= 15.0:
        yplot_range = list(range(-15, 16, 1))
    elif Max_Correction <= 20.0:
        yplot_range = list(range(-20, 21, 1))

    #   pprint(Bias_values)
    #   pprint(Az_Labels)
    #   pprint(Elev_Labels)
    #   pprint(yplot_range)

    plot_polar_contour(
        "Antenna Phase Biases: " + antennaName + " " + Band,
        Bias_values,
        Az_Labels,
        Elev_Labels,
        yplot_range,
    )

    filename = safe_filename(antennaName) + "." + Band + ".POLAR.png"
    try:
        plt.savefig(filename, format="png")
    except:
        filename = "ERROR"
    plt.close("all")

    return filename


def create_plot_delta_radial(antennaName, Band, Az_Elev_Correction):

    Az_Labels = []
    for Az in sorted(Az_Elev_Correction):
        if Az != NO_AZ:
            Az_Labels.append(Az)

    Elev_Labels = []
    for Item in Az_Elev_Correction[0]:
        Elev_Labels.append(Item[0])

    Bias_values = []
    for Az in sorted(Az_Elev_Correction):
        if Az != NO_AZ:
            for index, item in enumerate(Az_Elev_Correction[Az]):

                Bias_values.append(item[1] - Az_Elev_Correction[NO_AZ][index][1])

    yplot_range = list(range(-5, 6, 1))

    plot_polar_contour(
        "Delta Antenna Phase Biases: " + antennaName + " " + Band,
        Bias_values,
        Az_Labels,
        Elev_Labels,
        yplot_range,
    )

    filename = safe_filename(antennaName) + "." + Band + ".POLAR-Difference.png"
    try:
        plt.savefig(filename, format="png")
    except:
        filename = "ERROR"
    plt.close("all")

    return filename


def dump_NEE_Offsets(Az_html_file, offsets):
    #  pprint(offsets)
    #  Az_html_file.write('<div class="row">')
    #  Az_html_file.write('<div class="column">SV System')

    #  Az_html_file.write("<h2>SV System</h2><pre>")

    HTML_Unit.output_table_header(
        Az_html_file,
        "Antenna_Offsets",
        "Antenna Offsets",
        [
            "SV System",
            "Bands"
        ],
    )


    Az_html_file.write('<tr><td style="vertical-align:top;font-family: monospace;">')

    if GPS in offsets:
        Az_html_file.write("<h3>GPS</h3>")
        if L1 in offsets[GPS]:
            Az_html_file.write(
                "L1: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GPS][L1][N_Offset],
                    offsets[GPS][L1][E_Offset],
                    offsets[GPS][L1][U_Offset],
                )
            )

        if L2 in offsets[GPS]:
            Az_html_file.write(
                "L2: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GPS][L2][N_Offset],
                    offsets[GPS][L2][E_Offset],
                    offsets[GPS][L2][U_Offset],
                )
            )

        if L5 in offsets[GPS]:
            Az_html_file.write(
                "L5: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GPS][L5][N_Offset],
                    offsets[GPS][L5][E_Offset],
                    offsets[GPS][L5][U_Offset],
                )
            )

    if GLONASS in offsets:
        Az_html_file.write("<h3>GLONASS</h3>")
        if L1 in offsets[GLONASS]:
            Az_html_file.write(
                "L1: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GLONASS][L1][N_Offset],
                    offsets[GLONASS][L1][E_Offset],
                    offsets[GLONASS][L1][U_Offset],
                )
            )

        if L2 in offsets[GLONASS]:
            Az_html_file.write(
                "L2: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GLONASS][L2][N_Offset],
                    offsets[GLONASS][L2][E_Offset],
                    offsets[GLONASS][L2][U_Offset],
                )
            )

    if GALILEO in offsets:
        Az_html_file.write("<h3>GALILEO</h3>")
        if E1 in offsets[GALILEO]:
            Az_html_file.write(
                "E1:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E1][N_Offset],
                    offsets[GALILEO][E1][E_Offset],
                    offsets[GALILEO][E1][U_Offset],
                )
            )

        if E5a in offsets[GALILEO]:
            Az_html_file.write(
                "E5a: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E5a][N_Offset],
                    offsets[GALILEO][E5a][E_Offset],
                    offsets[GALILEO][E5a][U_Offset],
                )
            )

        if E5b in offsets[GALILEO]:
            Az_html_file.write(
                "E5b: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E5b][N_Offset],
                    offsets[GALILEO][E5b][E_Offset],
                    offsets[GALILEO][E5b][U_Offset],
                )
            )

        if E5 in offsets[GALILEO]:
            Az_html_file.write(
                "E5:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E5][N_Offset],
                    offsets[GALILEO][E5][E_Offset],
                    offsets[GALILEO][E5][U_Offset],
                )
            )

        if E6 in offsets[GALILEO]:
            Az_html_file.write(
                "E6:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E6][N_Offset],
                    offsets[GALILEO][E6][E_Offset],
                    offsets[GALILEO][E6][U_Offset],
                )
            )

    if COMPASS in offsets:
        Az_html_file.write("<h3>BeiDou</h3>")
        if E1 in offsets[COMPASS]:
            Az_html_file.write(
                "E1:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[COMPASS][E1][N_Offset],
                    offsets[COMPASS][E1][E_Offset],
                    offsets[COMPASS][E1][U_Offset],
                )
            )

        if E2 in offsets[COMPASS]:
            Az_html_file.write(
                "E2:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[COMPASS][E2][N_Offset],
                    offsets[COMPASS][E2][E_Offset],
                    offsets[COMPASS][E2][U_Offset],
                )
            )

        if E5b in offsets[COMPASS]:
            Az_html_file.write(
                "E5b: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[COMPASS][E5b][N_Offset],
                    offsets[COMPASS][E5b][E_Offset],
                    offsets[COMPASS][E5b][U_Offset],
                )
            )

        if E6 in offsets[COMPASS]:
            Az_html_file.write(
                "E6:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[COMPASS][E6][N_Offset],
                    offsets[COMPASS][E6][E_Offset],
                    offsets[COMPASS][E6][U_Offset],
                )
            )

    if QZSS in offsets:
        Az_html_file.write("<h3>QZSS</h3>")
        if L1 in offsets[QZSS]:
            Az_html_file.write(
                "L1:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[QZSS][L1][N_Offset],
                    offsets[QZSS][L1][E_Offset],
                    offsets[QZSS][L1][U_Offset],
                )
            )

        if L2 in offsets[QZSS]:
            Az_html_file.write(
                "L2:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[QZSS][L2][N_Offset],
                    offsets[QZSS][L2][E_Offset],
                    offsets[QZSS][L2][U_Offset],
                )
            )

        if L5 in offsets[QZSS]:
            Az_html_file.write(
                "L5:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[QZSS][L5][N_Offset],
                    offsets[QZSS][L5][E_Offset],
                    offsets[QZSS][L5][U_Offset],
                )
            )

        if LEX in offsets[QZSS]:
            Az_html_file.write(
                "LEX: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[QZSS][LEX][N_Offset],
                    offsets[QZSS][LEX][E_Offset],
                    offsets[QZSS][LEX][U_Offset],
                )
            )

    if IRNSS in offsets:
        Az_html_file.write("<h3>IRNSS</h3>")
        if L5 in offsets[IRNSS]:
            Az_html_file.write(
                "L5: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[IRNSS][L5][N_Offset],
                    offsets[IRNSS][L5][E_Offset],
                    offsets[IRNSS][L5][U_Offset],
                )
            )

    if SBAS in offsets:
        Az_html_file.write("<h3>SBAS</h3>")
        if L1 in offsets[SBAS]:
            Az_html_file.write(
                "L1: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[SBAS][L1][N_Offset],
                    offsets[SBAS][L1][E_Offset],
                    offsets[SBAS][L1][U_Offset],
                )
            )

        if L5 in offsets[SBAS]:
            Az_html_file.write(
                "L5: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[SBAS][L5][N_Offset],
                    offsets[SBAS][L5][E_Offset],
                    offsets[SBAS][L5][U_Offset],
                )
            )



    #  Az_html_file.write('</div><div class="column">Bands')
    Az_html_file.write('</td><td style="vertical-align:top;font-family: monospace;">')

    if (
        (GPS in offsets and L1 in offsets[GPS])
        or (GLONASS in offsets and L1 in offsets[GLONASS])
        or (QZSS in offsets and L1 in offsets[QZSS])
        or (SBAS in offsets and L1 in offsets[SBAS])
    ):

        Az_html_file.write("<h3>L1</h3>")
        if GPS in offsets and L1 in offsets[GPS]:
            Az_html_file.write(
                "GPS:     N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GPS][L1][N_Offset],
                    offsets[GPS][L1][E_Offset],
                    offsets[GPS][L1][U_Offset],
                )
            )
        if GLONASS in offsets and L1 in offsets[GLONASS]:
            Az_html_file.write(
                "GLONASS: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GLONASS][L1][N_Offset],
                    offsets[GLONASS][L1][E_Offset],
                    offsets[GLONASS][L1][U_Offset],
                )
            )
        if QZSS in offsets and L1 in offsets[QZSS]:
            Az_html_file.write(
                "QZSS:    N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[QZSS][L1][N_Offset],
                    offsets[QZSS][L1][E_Offset],
                    offsets[QZSS][L1][U_Offset],
                )
            )
        if SBAS in offsets and L1 in offsets[SBAS]:
            Az_html_file.write(
                "SBAS:    N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[SBAS][L1][N_Offset],
                    offsets[SBAS][L1][E_Offset],
                    offsets[SBAS][L1][U_Offset],
                )
            )

    if (
        GPS in offsets
        and L2 in offsets[GPS]
        or GLONASS in offsets
        and L2 in offsets[GLONASS]
        or QZSS in offsets
        and L2 in offsets[QZSS]
    ):

        Az_html_file.write("<h3>L2</h3>")
        if GPS in offsets and L2 in offsets[GPS]:
            Az_html_file.write(
                "GPS:     N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GPS][L2][N_Offset],
                    offsets[GPS][L2][E_Offset],
                    offsets[GPS][L2][U_Offset],
                )
            )
        if GLONASS in offsets and L2 in offsets[GLONASS]:
            Az_html_file.write(
                "GLONASS: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GLONASS][L2][N_Offset],
                    offsets[GLONASS][L2][E_Offset],
                    offsets[GLONASS][L2][U_Offset],
                )
            )
        if QZSS in offsets and L2 in offsets[QZSS]:
            Az_html_file.write(
                "QZSS:    N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[QZSS][L2][N_Offset],
                    offsets[QZSS][L2][E_Offset],
                    offsets[QZSS][L2][U_Offset],
                )
            )

    if (
        GPS in offsets
        and L5 in offsets[GPS]
        or QZSS in offsets
        and L5 in offsets[QZSS]
        or SBAS in offsets
        and L5 in offsets[SBAS]
        or IRNSS in offsets
        and L5 in offsets[IRNSS]
    ):

        Az_html_file.write("<h3>L5</h3>")
        if GPS in offsets and L5 in offsets[GPS]:
            Az_html_file.write(
                "GPS:     N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GPS][L5][N_Offset],
                    offsets[GPS][L5][E_Offset],
                    offsets[GPS][L5][U_Offset],
                )
            )
        if QZSS in offsets and L5 in offsets[QZSS]:
            Az_html_file.write(
                "QZSS:    N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[QZSS][L5][N_Offset],
                    offsets[QZSS][L5][E_Offset],
                    offsets[QZSS][L5][U_Offset],
                )
            )
        if SBAS in offsets and L5 in offsets[SBAS]:
            Az_html_file.write(
                "SBAS:    N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[SBAS][L5][N_Offset],
                    offsets[SBAS][L5][E_Offset],
                    offsets[SBAS][L5][U_Offset],
                )
            )
        if IRNSS in offsets and L5 in offsets[IRNSS]:
            Az_html_file.write(
                "IRNSS:   N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[IRNSS][L5][N_Offset],
                    offsets[IRNSS][L5][E_Offset],
                    offsets[IRNSS][L5][U_Offset],
                )
            )

    if (
        GALILEO in offsets
        and E1 in offsets[GALILEO]
        or COMPASS in offsets
        and E1 in offsets[COMPASS]
    ):

        Az_html_file.write("<h3>E1</h3>")
        if GALILEO in offsets and E1 in offsets[GALILEO]:
            Az_html_file.write(
                "GALILEO: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E1][N_Offset],
                    offsets[GALILEO][E1][E_Offset],
                    offsets[GALILEO][E1][U_Offset],
                )
            )
        if COMPASS in offsets and E1 in offsets[COMPASS]:
            Az_html_file.write(
                "BeiDou:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[COMPASS][E1][N_Offset],
                    offsets[COMPASS][E1][E_Offset],
                    offsets[COMPASS][E1][U_Offset],
                )
            )

    if COMPASS in offsets and E2 in offsets[COMPASS]:
        Az_html_file.write("<h3>E2</h3>")
        if COMPASS in offsets and E2 in offsets[COMPASS]:
            Az_html_file.write(
                "BeiDou:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[COMPASS][E2][N_Offset],
                    offsets[COMPASS][E2][E_Offset],
                    offsets[COMPASS][E2][U_Offset],
                )
            )

    if GALILEO in offsets and E5 in offsets[GALILEO]:
        Az_html_file.write("<h3>E5</h3>")
        if GALILEO in offsets and E5 in offsets[GALILEO]:
            Az_html_file.write(
                "GALILEO: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E5][N_Offset],
                    offsets[GALILEO][E5][E_Offset],
                    offsets[GALILEO][E5][U_Offset],
                )
            )

    if GALILEO in offsets and E5a in offsets[GALILEO]:
        Az_html_file.write("<h3>E5a</h3>")
        if GALILEO in offsets and E5a in offsets[GALILEO]:
            Az_html_file.write(
                "GALILEO: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E5a][N_Offset],
                    offsets[GALILEO][E5a][E_Offset],
                    offsets[GALILEO][E5a][U_Offset],
                )
            )

    if (
        GALILEO in offsets
        and E5b in offsets[GALILEO]
        or COMPASS in offsets
        and E5b in offsets[COMPASS]
    ):

        Az_html_file.write("<h3>E5b</h3>")
        if GALILEO in offsets and E5b in offsets[GALILEO]:
            Az_html_file.write(
                "GALILEO: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E5b][N_Offset],
                    offsets[GALILEO][E5b][E_Offset],
                    offsets[GALILEO][E5b][U_Offset],
                )
            )
        if COMPASS in offsets and E5b in offsets[COMPASS]:
            Az_html_file.write(
                "BeiDou:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[COMPASS][E5b][N_Offset],
                    offsets[COMPASS][E5b][E_Offset],
                    offsets[COMPASS][E5b][U_Offset],
                )
            )

    if (
        GALILEO in offsets
        and E6 in offsets[GALILEO]
        or COMPASS in offsets
        and E6 in offsets[COMPASS]
    ):

        Az_html_file.write("<h3>E6</h3>")
        if GALILEO in offsets and E6 in offsets[GALILEO]:
            Az_html_file.write(
                "GALILEO: N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[GALILEO][E6][N_Offset],
                    offsets[GALILEO][E6][E_Offset],
                    offsets[GALILEO][E6][U_Offset],
                )
            )
        if COMPASS in offsets and E6 in offsets[COMPASS]:
            Az_html_file.write(
                "BeiDou:  N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[COMPASS][E6][N_Offset],
                    offsets[COMPASS][E6][E_Offset],
                    offsets[COMPASS][E6][U_Offset],
                )
            )

    if QZSS in offsets and LEX in offsets[QZSS]:
        Az_html_file.write("<h3>LEX</h3>")
        if QZSS in offsets and LEX in offsets[QZSS]:
            Az_html_file.write(
                "QZSS:    N: {: .2f}  E: {: .2f}  U: {: .2f}<br>".format(
                    offsets[QZSS][LEX][N_Offset],
                    offsets[QZSS][LEX][E_Offset],
                    offsets[QZSS][LEX][U_Offset],
                )
            )

    Az_html_file.write("</td></tr>")

    HTML_Unit.output_table_footer(Az_html_file)

    Az_html_file.write("<br/><hr/></pre>")


#  Az_html_file.write('</div>')

def Az_Link(Antenna,Az_filename,System):
    SystemName=SYSTEM_NAMES[System]
    if System in Antenna.APC_Offsets:
        return (f'<a target="_blank" href="{Az_filename}#{SystemName}">Azimuth</a>')
    else:
        return ("")

def output_antenna_details(Antenna):
    if not Antenna.Type in SV_Types:
        #        print ("Type: {} Serial: {} Bands: {} Freqs: {} GPS Antennas: {} GLONASS Antennas: {}".format(Type,Serial,len(APC_Offsets[SV_System]),Num_Freqs,GPS_Antennas,GLO_Antennas))

        Az_html_file = None
        Az_filename = safe_filename(Antenna.Type) + ".html"
#        print(Az_filename)
        Az_html_file = open(Az_filename, "w")
#        pprint(Az_html_file)
        HTML_Unit.output_html_header(
            Az_html_file, "Antenna information for " + Antenna.Type
        )
        HTML_Unit.output_html_body(Az_html_file)
        Az_html_file.write("<h1>Antenna information for {}</h1>".format(Antenna.Type))
        Az_html_file.write("\n")
        dump_NEE_Offsets(Az_html_file, Antenna.NEE_Offsets)
        Az_html_file.write("\n")

        HTML_Unit.output_table_row(sys.stdout,
            [f'<a target="_blank" href="{Az_filename}">{Antenna.Type}</a>',
                len(Antenna.APC_Offsets[GPS]),
                Antenna.Num_Freqs,
                Antenna.GPS_Antennas,
                Az_Link(Antenna,Az_filename,GPS),
                Az_Link(Antenna,Az_filename,GLONASS),
                Az_Link(Antenna,Az_filename,GALILEO),
                Az_Link(Antenna,Az_filename,COMPASS),
                Az_Link(Antenna,Az_filename,QZSS),
                Az_Link(Antenna,Az_filename,SBAS),
                Az_Link(Antenna,Az_filename,IRNSS)
                ])


        Az_html_file.write('<h1>Means</h1>\n')


        if GPS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_means(Az_html_file,GPS, [L1, L2, L5], ["L1", "L2", "L5"])

        if GLONASS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_means(Az_html_file,GLONASS, [L1, L2], ["L1", "L2"])

        if GALILEO in Antenna.APC_Offsets:
            Antenna.plot_SV_System_means(Az_html_file,GALILEO, [E1, E5a, E5b, E5, E6], ["E1", "E5a","E5b", "E5", "E6"])

        if COMPASS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_means(Az_html_file,COMPASS, [E1, E2, E5b, E6], ["E1", "E2","E5b", "E6"])

        if QZSS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_means(Az_html_file,QZSS, [L1, L2, L5], ["L1", "L2", "L5"])

        if SBAS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_means(Az_html_file,SBAS, [L1, L5], ["L1", "L5"])

        if IRNSS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_means(Az_html_file,IRNSS, [L5], ["L5"])




        Az_html_file.write('<h1>Azimuths</h1>\n')


        if GPS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_Azimuth(Az_html_file, GPS, [L1, L2, L5], ["L1", "L2", "L5"])

        if GLONASS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_Azimuth(Az_html_file, GLONASS, [L1, L2], ["L1", "L2"])

        if GALILEO in Antenna.APC_Offsets:
            Antenna.plot_SV_System_Azimuth(Az_html_file,GALILEO, [E1, E5a, E5b, E5, E6], ["E1", "E5a","E5b", "E5", "E6"])

        if COMPASS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_Azimuth(Az_html_file,COMPASS, [E1, E2, E5b, E6], ["E1", "E2","E5b", "E6"])

        if QZSS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_Azimuth(Az_html_file,QZSS, [L1, L2, L5], ["L1", "L2", "L5"])

        if SBAS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_Azimuth(Az_html_file,SBAS, [L1, L5], ["L1", "L5"])

        if IRNSS in Antenna.APC_Offsets:
            Antenna.plot_SV_System_Azimuth(Az_html_file,IRNSS, [L5], ["L5"])



        # Really need to split this one up, it is super ugly

        #           HTML_Unit.output_table_row(sys.stdout,
        #               [Type,len(APC_Offsets[SV_System]),Num_Freqs,GPS_Antennas,GLO_Antennas,
        #                 GPS_Offsets_Txt,GPS_L1_Offsets_Txt,GPS_L2_Offsets_Txt,
        #                 GLO_Offsets_Txt,GLO_L1_Offsets_Txt,GLO_L2_Offsets_Txt])

        if Az_html_file != None:
            HTML_Unit.output_html_footer(Az_html_file, [])

            Az_html_file.close()
            Az_html_file = None


class GNSSAntenna:
    def __init__(self):
        self.NEE_Offsets = {}
        self.APC_Offsets = {}
        self.GPS_Antennas = None
        self.GLO_Antennas = None
        self.GAL_Antennas = None
        self.BDS_Antennas = None
        self.SBAS_Antennas = None
        self.QZSS_Antennas = None
        self.Type = None
        self.Serial = None
        self.DAZI = None
        self.ZEN1 = None
        self.ZEN2 = None
        self.DZEN = None
        self.Num_Freqs = None
        self.Sinex_Code = None
        self.SV_System = None
        self.Freq_Number = None
        self.North = None
        self.East = None
        self.Up = None

    def process_NEU(self, line):
        North = float(line[0:10])
        East = float(line[10:20])
        Up = float(line[20:30])
        if not self.SV_System in self.NEE_Offsets:
            self.NEE_Offsets[self.SV_System] = {}
            self.APC_Offsets[self.SV_System] = {}
        self.NEE_Offsets[self.SV_System][self.Freq_Number] = (North, East, Up)
        self.APC_Offsets[self.SV_System][self.Freq_Number] = {}

    def process_comment(self, line):
        #      print "COMMENT"
        if line.find(GPS_Cal_Antennas) == 0:
            #        print "GPS"
            self.GPS_Antennas = int(line[GPS_Cal_Antennas_Length:60], base=10)
        #        print GPS_Antennas
        elif line.find(GPS_Generic_Cal_Antennas) == 0:
            #        print "GPS Generic"
            self.GPS_Antennas = int(line[GPS_Generic_Cal_Antennas_Length:60], base=10)
        #        print GPS_Antennas
        elif line.find(GLO_Cal_Antennas) == 0:
            #        print "GLONASS"
            self.GLO_Antennas = int(line[GLO_Cal_Antennas_Length:60], base=10)
        #        print GLO_Antennas
        elif line.find("# Number of Individual GLO-Calibrations:") == 0:
            if self.GLO_Antennas == None:
                self.GLO_Antennas = self.GPS_Antennas
                # Handle the antennas with a generic antenna total comment and GLONASS

    #      print line

    def process_type_serial(self, line):
        self.Type = line[0:20].rstrip()
        self.Serial = line[20:60].rstrip()

    #        print Type,Serial

    def process_freq(self, line):
        SV_System_Char = line[3:4]
        if SV_System_Char == "G":
            self.SV_System = GPS
        elif SV_System_Char == "R":
            self.SV_System = GLONASS
        elif SV_System_Char == "E":
            self.SV_System = GALILEO
        elif SV_System_Char == "C":
            self.SV_System = COMPASS
        elif SV_System_Char == "J":
            self.SV_System = QZSS
        elif SV_System_Char == "S":
            self.SV_System = SBAS
        elif SV_System_Char == "I":
            self.SV_System = IRNSS
        else:
            raise Exception("Uknown SV_System_Char" + line)
        self.Freq_Number = int(line[4:6])

    def process_offsets(self, line):
        Az = line[0:8]
        if Az == "   NOAZI":
            Az = NO_AZ
        else:
            Az = float(Az)

        line = line[8:]

        zen = self.ZEN1

        Offsets = []

        while zen <= self.ZEN2:
            # Yes if someone really did models at 0.1 resolution we would break but since they are all 5 degrees at the moment we don't care.
            offset = float(line[0:8])
            line = line[8:]
            Offsets.append([zen, offset])
            zen += self.DZEN

        self.APC_Offsets[self.SV_System][self.Freq_Number][Az] = Offsets

    def plot_SV_System_means(self, Az_file, System, bands, bands_names):

        Offsets = []
        if System in self.APC_Offsets:
            band_number = 0
            bands_included = []
            for band in bands:
                if band in self.APC_Offsets[System]:
                    Offsets.append(self.APC_Offsets[System][band][NO_AZ])
                    bands_included.append(bands_names[band_number])
                    band_name=bands_names[band_number]
                    band_number += 1



            plot_name = create_mean_plot(self.Type, System, Offsets, bands_names)
            Az_file.write('<H3>{}</H3>\n'.format(SYSTEM_NAMES[System]))
            Az_file.write('<img src="{}" alt={}>\n'.format(plot_name, plot_name,self.Type))


    def plot_SV_System_Azimuth(self, Az_html_file, System, bands, bands_names):
        Offsets = []
#        print(f"Type: {System}")

        if System in self.APC_Offsets:
            band_number = 0
            systemName = SYSTEM_NAMES[System]
            bands_included = []
            Az_html_file.write('<p/>\n')
            Az_html_file.write('<p/>\n')
            HTML_Unit.output_table_header(
                Az_html_file,
                systemName,
                f'<h2>{systemName}</h2><br/>\n',
                [
                    "Bias",
                    "Delta"
                ],
            )



            for band in bands:
#                pprint(self.APC_Offsets)
#                pprint(self.APC_Offsets[0])
#                pprint(System)
#                pprint(self.APC_Offsets[System])

                if band in self.APC_Offsets[System]:
                    if len(self.APC_Offsets[System][band]) == 1:
                        continue



                    bands_included.append(bands_names[band_number])
                    band_name = bands_names[band_number]
                    band_number += 1

                    Az_html_file.write(f'<tr><td colspan="2" style="text-align: center;"><h3>{systemName}-{band_name}</h3></td></tr>\n')
                    Az_html_file.write('<tr>')

                    #          pprint(APC_Offsets[GPS][L1])
                    Az_html_file.write(
                        '<td><img src="{}" alt="{}"></td>'.format(
                            create_az_plot(
                                self.Type, f"{systemName}-{band_name}", self.APC_Offsets[System][band]
                            ),
                            f"{systemName}-{band_name}",
                        )
                    )

                    Az_html_file.write(
                        '<td><img src="{}" alt="{}"></td>'.format(
                            create_az_delta_plot(
                              self.Type,  f"{systemName}-{band_name}", self.APC_Offsets[System][band]
                            ),
                            f"{systemName}-{band_name}",
                        )
                    )

                    Az_html_file.write('</tr><tr>')

                    Az_html_file.write("\n")
                    Az_html_file.write(
                        '<td><img src="{}" alt="{}"></td>'.format(
                            create_plot_radial(
                                self.Type, f"{systemName}-{band_name}", self.APC_Offsets[System][band]
                            ),
                            f"Radial {systemName}-{band_name}",
                        )
                    )

                    Az_html_file.write(
                        '<td><img src="{}" alt="{}"></td>'.format(
                            create_plot_delta_radial(
                                self.Type, f"{systemName}-{band_name}", self.APC_Offsets[System][band]
                            ),
                            f"Radial {systemName}-{band_name}",
                        )
                    )
                    Az_html_file.write('</tr>\n')

            HTML_Unit.output_table_footer(Az_html_file)

#           plot_name=create_mean_plot (Type,"GPS",Offsets,["L1","L2","L5"])


def main():

    In_Antenna = False
    In_APC_Offsets = False
    Antenna = None
    DAZI = None

    HTML_Unit.output_html_header(sys.stdout, "Antenna information")
    HTML_Unit.output_html_body(sys.stdout)
    HTML_Unit.output_table_header(
        sys.stdout,
        "Antenna_Information",
        "Antenna Information",
        [
            "Type",
            "Bands",
            "Freqs",
            "#Antennas",
            "GPS",
            "GLO",
            "GAL",
            "BDS",
            "QZSS",
            "SBAS",
            "IRNSS"

        ],
    )
    #       HTML_Unit.output_table_row(sys.stdout,[defect,defects_Desc[defect],Versions_Str])

    for line in fileinput.input():
        line = line.rstrip()
        #    print line
        Record_Type = line[60:]
        #    print Record_Type,"*"
        if Record_Type == "START OF ANTENNA":
            #      print "Start"
            Antenna = GNSSAntenna()

            if In_Antenna:
                raise Exception("Got start of antenna while in antenna")
            else:
                In_Antenna = True
                DAZI = None

        if Record_Type == "END OF ANTENNA":
            if In_Antenna:
                In_Antenna = False
                output_antenna_details(Antenna)
            else:
                raise Exception("Got end of antenna while not in antenna")

        if Record_Type == "COMMENT":
            if In_Antenna:
                Antenna.process_comment(line)

        if Record_Type == "TYPE / SERIAL NO":
            if In_Antenna:
                Antenna.process_type_serial(line)
            else:
                raise Exception("Got end of antenna while not in antenna")

        if Record_Type == "DAZI":
            #      print line
            if In_Antenna:
                Antenna.DAZI = float(line[2:6])
            else:
                raise Exception("Got DAZI while not in antenna")

        if Record_Type == "ZEN1 / ZEN2 / DZEN":
            if In_Antenna:
                Antenna.ZEN1 = float(line[2:8])
                Antenna.ZEN2 = float(line[8:14])
                Antenna.DZEN = float(line[14:20])
            else:
                raise Exception("Got ZEN1 / ZEN2 / DZEN while not in antenna")

        if Record_Type == "# OF FREQUENCIES":
            if In_Antenna:
                Antenna.Num_Freqs = int(line[0:6])
            #        print Num_Freqs
            else:
                raise Exception("Got # OF FREQUENCIES while not in antenna")

        if Record_Type == "SINEX CODE":
            if In_Antenna:
                Antenna.Sinex_Code = line[0:10]
            #        print Sinex_Code
            else:
                raise Exception("Got SINEX CODE while not in antenna")

        if Record_Type == "START OF FREQUENCY":
            if In_Antenna:
                Antenna.process_freq(line)
            else:
                raise Exception("Got START OF FREQUENCY while not in antenna")

        if Record_Type == "END OF FREQUENCY":
            if In_Antenna:
                In_APC_Offsets = False
            else:
                raise Exception("Got END OF FREQUENCY while not in antenna")

        # Here we may be in a antenna model set. We have to do the checking after the end of freq and before the NEU which shows the start of freqs

        if In_APC_Offsets:
            Antenna.process_offsets(line)

        if Record_Type == "NORTH / EAST / UP":
            if In_Antenna:
                Antenna.process_NEU(line)
                In_APC_Offsets = True
            else:
                raise Exception("Got NORTH / EAST / UP while not in antenna")

    HTML_Unit.output_table_footer(sys.stdout)

    HTML_Unit.output_html_footer(sys.stdout, ["Antenna_Information"])


if __name__ == "__main__":
    main()
