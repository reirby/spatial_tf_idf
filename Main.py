import pandas as pd
import math
import json

# Read file

surnames_with_coordinates = pd.read_csv("../project_data/ohio_geocoded/ohio_shortest.txt")
# Init  Level0

level0 = {
  "lat0": 38.05,
  "lon0": -84.83,
  "cell_size": 2.16,
  "heatmap": None
}

min_cell_size = 0.1
current_level_number = 0
# Define fillLevelHeatmap function


def fill_level_heatmap(current_level, name_list):
    global current_level_number
    print ('Calculating level ' + str(current_level_number))
    current_level_number += 1

    # init heatmap for current level
    current_level["heatmap"] = [[0, 1], [2, 3]]

    current_level["heatmap"][0][0] = {"lower_level": {}, "last_names": {}}
    current_level["heatmap"][0][1] = {"lower_level": {}, "last_names": {}}
    current_level["heatmap"][1][0] = {"lower_level": {}, "last_names": {}}
    current_level["heatmap"][1][1] = {"lower_level": {}, "last_names": {}}

    # loop through points and count surnames in each box
    for index, row in name_list.iterrows():
        point_lat = row["y"]
        point_lon = row["x"]
        if math.isnan(point_lat) or math.isnan(point_lon):
            continue

        #print('lat_ind = ('+ str(point_lat)+ ' - ' + str(current_level["lat0"])+ ' )/ '+ str(current_level["cell_size"]) )

        lat_ind = int(math.floor((point_lat - current_level["lat0"])/current_level["cell_size"]))
        lon_ind = int(math.floor((point_lon - current_level["lon0"])/current_level["cell_size"]))

        if lat_ind not in (0, 1) or lon_ind not in (0, 1):
            continue

        current_name = row['LAST_NAME']
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

                fill_level_heatmap(lower_level, name_list)

# Call fill_level_heatmap function


fill_level_heatmap(level0, surnames_with_coordinates)

# save level0 to json

print('Saving dictionary to json')
with open('../project_data/result.json', 'w') as fp:
    json.dump(level0, fp)
