import csv
import math
import json
from datetime import datetime

# Read file
with open ('d:/Andrei/Ohio/ohio_shortest.txt') as name_file:
    names = csv.reader(name_file, delimiter=',')
    names_list =[]
    lat_list = []
    lon_list = []
    next(names)
    for row in names:
        if row[3] and row[2]:
            name = row[0]
            lat = float(row[3])
            lon = float(row[2])

            names_list.append(name)
            lat_list.append(lat)
            lon_list.append(lon)
            
# Init  Level0

level0 = {
  "lat0": 38.05,
  "lon0": -84.83,
  "cell_size": 2.16,
  "heatmap": None
}

min_cell_size = 0.1
function_call = 0
# Define fillLevelHeatmap function


def fill_level_heatmap(current_level, names_list,lat_list,lon_list):
    global function_call
    a = datetime.now()
    print ('Calculating function_call: ' + str(function_call)+ ' started at '+ str(a) )
    function_call += 1

    # init heatmap for current level
    current_level["heatmap"] = [[0, 1], [2, 3]]

    current_level["heatmap"][0][0] = {"lower_level": {}, "last_names": {}}
    current_level["heatmap"][0][1] = {"lower_level": {}, "last_names": {}}
    current_level["heatmap"][1][0] = {"lower_level": {}, "last_names": {}}
    current_level["heatmap"][1][1] = {"lower_level": {}, "last_names": {}}

    # loop through points and count surnames in each box
    for i in range(len(names_list)):
        point_lat = lat_list[i]
        point_lon = lon_list[i]
        if math.isnan(point_lat) or math.isnan(point_lon):
            continue

        #print('lat_ind = ('+ str(point_lat)+ ' - ' + str(current_level["lat0"])+ ' )/ '+ str(current_level["cell_size"]) )

        lat_ind = int(math.floor((point_lat - current_level["lat0"])/current_level["cell_size"]))
        lon_ind = int(math.floor((point_lon - current_level["lon0"])/current_level["cell_size"]))

        if lat_ind not in (0, 1) or lon_ind not in (0, 1):
            continue

        current_name = names_list[i]
        current_name_list = current_level["heatmap"][lat_ind][lon_ind]["last_names"]

        if current_name not in current_name_list:
            current_name_list[current_name] = 1
        else:
            current_name_list[current_name] += 1

    # fill lower levels
    if current_level["cell_size"] > min_cell_size:
        for i in range(0,2,1):
            for j in range(0,2,1):
                lower_level = current_level["heatmap"][i][j]["lower_level"]
                lower_lat0 = current_level["lat0"] + i * current_level["cell_size"]
                lower_lon0 = current_level["lon0"] + j * current_level["cell_size"]
                lower_cell_size = current_level["cell_size"]/2
                lower_level.update([("lat0", lower_lat0), ("lon0", lower_lon0), ("cell_size", lower_cell_size), ("heatmap", None)])

                fill_level_heatmap(lower_level, names_list,lat_list,lon_list)

# Call fill_level_heatmap function


fill_level_heatmap(level0, names_list,lat_list,lon_list)

# save level0 to json

print('Saving dictionary to json')
with open('C:/Users/a_k257/OneDrive - Texas State University/ohio_result', 'w') as fp:
    json.dump(level0, fp)
