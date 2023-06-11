import csv
import math
import json
from datetime import datetime
from __future__ import print_function

# Read file
with open('../project_data/ohio_geocoded/ohio_shortest.txt') as name_file:
    names = csv.reader(name_file, delimiter=',')
    names_list = []
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
# init list of  for each level
cell_lists = {}

# init list of IDF for unique names for each level
idf_list = {}

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


def fill_level_heatmap(current_level, names_list, lat_list, lon_list):
    global function_call
    a = datetime.now()
    print ('Calculating function_call: ' + str(function_call) + ' started at ' + str(a))
    function_call += 1

    # init heatmap for current level
    current_level["heatmap"] = [[0, 1], [2, 3]]

    current_level["heatmap"][0][0] = {"lower_level": {}, "last_names": {}}
    current_level["heatmap"][0][1] = {"lower_level": {}, "last_names": {}}
    current_level["heatmap"][1][0] = {"lower_level": {}, "last_names": {}}
    current_level["heatmap"][1][1] = {"lower_level": {}, "last_names": {}}

    # loop through points and count surnames in each box
    for i in range(len(names_list)):
        #print ('Calculating point index: ' + str(datetime.now()))
        point_lat = lat_list[i]
        point_lon = lon_list[i]
        if math.isnan(point_lat) or math.isnan(point_lon):
            continue

        #print('lat_ind = ('+ str(point_lat)+ ' - ' + str(current_level["lat0"])+ ' )/ '+ str(current_level["cell_size"]) )

        lat_ind = int(math.floor((point_lat - current_level["lat0"])/current_level["cell_size"]))
        lon_ind = int(math.floor((point_lon - current_level["lon0"])/current_level["cell_size"]))
        #print ('Check if point is in the box: '  + str(datetime.now()))
        if lat_ind not in (0, 1) or lon_ind not in (0, 1):
            continue

        current_name = names_list[i]
        current_name_list = current_level["heatmap"][lat_ind][lon_ind]["last_names"]
       # print ('Putting the name in the dict: '  + str(datetime.now()))
        if current_name not in current_name_list:
            current_name_list[current_name] = 1
        else:
            current_name_list[current_name] += 1

    # fill lower levels
    #print ('Starting init next level: '  + str(datetime.now()))
    if current_level["cell_size"] > min_cell_size:
        for i in range(0,2,1):
            for j in range(0,2,1):
                lower_level = current_level["heatmap"][i][j]["lower_level"]
                lower_lat0 = current_level["lat0"] + i * current_level["cell_size"]
                lower_lon0 = current_level["lon0"] + j * current_level["cell_size"]
                lower_cell_size = current_level["cell_size"]/2
                lower_level.update([("lat0", lower_lat0), ("lon0", lower_lon0), ("cell_size", lower_cell_size), ("heatmap", None)])
                #print ('Calling main function for the next level: '  + str(datetime.now()))
                fill_level_heatmap(lower_level, names_list,lat_list,lon_list)


# create "table of content" for cells on each level
def get_cell_lists_for_each_level(current_level):
    current_cell_size = round(current_level["cell_size"], 2)

    for i in (0, 1):
        for j in (0, 1):
            current_cell_address = current_level["heatmap"][i][j]["last_names"]
            lower_level = current_level["heatmap"][i][j]["lower_level"]
            if current_cell_size not in cell_lists:
                cell_lists[current_cell_size] = []
                cell_lists[current_cell_size].append(current_cell_address)
            else:
                cell_lists[current_cell_size].append(current_cell_address)

            if lower_level:
                get_cell_lists_for_each_level(lower_level)


# calculate IDF for a total list of unique names for each level
def calculate_idf(names_list):
    unique_name_list = list(set(names_list))
    # take a name from the list
    for fname in unique_name_list:
        #print ("calculating IDF for : " + fname + " stared " + str(datetime.now()))
        # calculate idf for each level for this name
        for i in list(cell_lists.keys()):
            # count number of documents on the level
            #print("level " + str(i))
            doc_count = len(cell_lists[i])
            doc_with_name_count = 0
            empty_doc_count = 0
            # count documents on current level, that contain current name
            for j in range(doc_count):
                if fname in cell_lists[i][j]:
                    doc_with_name_count += 1
                if len(cell_lists[i][j]) < 1:
                    empty_doc_count += 1
            non_empty_doc_count = doc_count - empty_doc_count
            # calculate IDF
           # print("doc count is " + str(doc_count) + " doc with name is " + str(doc_with_name_count))
            idf = math.log10(non_empty_doc_count/float(doc_with_name_count))
            # put IDF into idf_list
            if fname not in idf_list:
                idf_list[fname] = {}
                idf_list[fname][i] = idf
            else:
                idf_list[fname][i] = idf


# calculate  TF/IDF for each cell at each level
def calculate_tfidf(cell_lists):
    for i in list(cell_lists.keys()):  # for each level
        print ("Processing level " + str(i))
        for j in range(len(cell_lists[i])):  # for each cell on the level
            print('processing cell #{}'.format(j), end='\r')
            current_namelist = cell_lists[i][j]
            # for n in list(current_namelist.keys()):
            #                  if type(current_namelist[n]) is int:
            #                      current_namelist[n] = {"count": current_namelist[n], "tf-idf": None}
            name_count_sum = sum(d['count'] for d in current_namelist.values() if d)
            if name_count_sum == 0:
                continue
            for fname in current_namelist:
                # print("Name: " +str(fname) + " Level: " +str(i)+ " Doc# " +str(j)+ " curr Name count "
                #       +str(current_namelist[fname]["count"])+ " Name count sum " + str(name_count_sum)+
                #       " Curr name/lvl IDF" + str(idf_list[fname][i]))
                if idf_list[fname][i] == 0:
                    current_namelist[fname]["tf-idf"] = 0
                else:
                    current_namelist[fname]["tf-idf"] = \
                        (float(current_namelist[fname]["count"]) / name_count_sum)/idf_list[fname][i]

# get highest last name with highest TFIDF
def get_best_name(current_namelist):
    if len(current_namelist) < 1:
        return ['empty','empty','empty']
    max_tfidf = max(d['tf-idf'] for d in current_namelist.values() if d)
    for key, value in current_namelist.items():
        if value['tf-idf'] == max_tfidf:
            return [key, value['tf-idf'], value['count']]

    return "something is not ok"

# get counts for last name
def get_count_for_name(current_namelist,fname):
    if len(current_namelist) < 1:
        return ['empty','empty']
    if fname not in current_namelist:
        return ['empty', 'empty']
    return [fname, current_namelist[fname]["count"]]


# get rid of all empty names

# def global_tf(current_level):
#     for i in (0, 1):
#         for j in (0, 1):
#             current_name_count_list = current_level["heatmap"][i][j]["last_names"]
#             current_cell_tf(current_name_count_list)
#
#             lower_level = current_level["heatmap"][i][j]["lower_level"]
#             if lower_level:
#                 global_tf(lower_level)


# Call fill_level_heatmap function
fill_level_heatmap(level0, names_list,lat_list,lon_list)

# create "table of content" for cells on each level
get_cell_lists_for_each_level(level0)

# calculate IDF for a total list of unique names for each level
calculate_idf(names_list)

# calculate  TF/IDF for each cell at each level
calculate_tfidf(cell_lists)

# save level0 to json
print('Saving dictionary to json')
with open('../project_data/ohio_result_final_tfidf.json', 'w') as fp:
    json.dump(level0, fp)


##Export results for visualization

# level 0 high tfidf

for i in (0, 1):
    for j in (0, 1):
        #print (str(i) + str(j))
        print(str(i) + str(j)+' '+str(get_best_name(level0["heatmap"][i][j]["last_names"])[0]) + " tf-idf: " + str(
            get_best_name(level0["heatmap"][i][j]["last_names"])[1]) + " count: " + str(get_best_name(level0["heatmap"][i][j]["last_names"])[2]))

# level 1 high tfidf

for i in (0, 1):
    for j in (0, 1):
        for m in (0, 1):
            for n in (0, 1):
                #print (str(i) + str(j)+'-'+str(m) + str(n))
                curr_address = level0["heatmap"][i][j]['lower_level']["heatmap"][m][n]["last_names"]
                print(str(i) + str(j)+'-'+str(m) + str(n)+ ' ' +str(get_best_name(curr_address)[0]) + " tf-idf: " +
                       str(get_best_name(curr_address)[1]) + " count: " + str(get_best_name(curr_address)[2]))

# level 1 picked name
print('code,name,count')
for i in (0, 1):
    for j in (0, 1):
        for m in (0, 1):
            for n in (0, 1):
                #print (str(i) + str(j)+'-'+str(m) + str(n))
                curr_address = level0["heatmap"][i][j]['lower_level']["heatmap"][m][n]["last_names"]
                ans = get_count_for_name(curr_address, "ALI")
                print(str(i) + str(j)+'-'+str(m) + str(n)+ ',' +str(ans[0]) + "," + str(ans[1]))


# level 2 high tfidf

for i in (0, 1):
    for j in (0, 1):
        for m in (0, 1):
            for n in (0, 1):
                for k in (0, 1):
                    for p in (0, 1):
                        #print (str(i) + str(j)+'-'+str(m) + str(n)+'-'+str(k) + str(p))
                        curr_address = level0["heatmap"][i][j]['lower_level']["heatmap"][m][n]['lower_level']["heatmap"][k][p]["last_names"]
                        print(str(i) + str(j)+'-'+str(m) + str(n)+'-'+str(k) + str(p)+ ' ' +str(get_best_name(curr_address)[0]) + " tf-idf: " +
                            str(get_best_name(curr_address)[1]) + " count: " + str(get_best_name(curr_address)[2]))

# level 2 picked name
print('code,name,count')
for i in (0, 1):
    for j in (0, 1):
        for m in (0, 1):
            for n in (0, 1):
                for k in (0, 1):
                    for p in (0, 1):
                        curr_address = level0["heatmap"][i][j]['lower_level']["heatmap"][m][n]['lower_level']["heatmap"][k][p]["last_names"]
                        ans = get_count_for_name(curr_address, "WHITE")
                        print(str(i) + str(j)+'-'+str(m) + str(n)+'-'+str(k) + str(p)+ ',' + str(ans[0]) + "," + str(ans[1]))


# level 3 high tfidf
print('code,name,tfidf,count')
for i in (0, 1):
    for j in (0, 1):
        for m in (0, 1):
            for n in (0, 1):
                for k in (0, 1):
                    for p in (0, 1):
                        for q in (0, 1):
                            for w in (0, 1):
                                curr_address = level0["heatmap"][i][j]['lower_level']["heatmap"][m][n]['lower_level']["heatmap"][k][p]['lower_level']["heatmap"][q][w]["last_names"]

                                # print(str(c1) + '-' + str(c2) + '-' + str(c3) + '-' + str(c4) + ',' + str(get_best_name(curr_address)[0]) + "," +
                                #       str(get_best_name(curr_address)[1]) + "," + str(get_best_name(curr_address)[2]))

                                print(str(i) + str(j)+'-'+str(m) + str(n)+'-'+str(k) + str(p)+'-'+str(q) + str(w)+ ',' +str(get_best_name(curr_address)[0]) + "," +
                                      str(get_best_name(curr_address)[1]) + "," + str(get_best_name(curr_address)[2]))

# level 3 picked name
print('code,name,count')
for i in (0, 1):
    for j in (0, 1):
        for m in (0, 1):
            for n in (0, 1):
                for k in (0, 1):
                    for p in (0, 1):
                        for q in (0, 1):
                            for w in (0, 1):
                                curr_address = level0["heatmap"][i][j]['lower_level']["heatmap"][m][n]['lower_level']["heatmap"][k][p]['lower_level']["heatmap"][q][w]["last_names"]
                                ans = get_count_for_name(curr_address, "SMITH")
                                print(str(i) + str(j) + '-' + str(m) + str(n) + '-' + str(k) + str(p) + '-' + str(q) + str(w)+',' + str(
                                    ans[0]) + "," + str(ans[1]))

                                # print(str(i) + str(j)+'-'+str(m) + str(n)+'-'+str(k) + str(p)+'-'+str(q) + str(w)+ ',' +str(get_best_name(curr_address)[0]) + "," +
                                #       str(get_best_name(curr_address)[1]) + "," + str(get_best_name(curr_address)[2]))


# level 4 high tfidf
print('code,name,tfidf,count')
for i in (0, 1):
    for j in (0, 1):
        for m in (0, 1):
            for n in (0, 1):
                for k in (0, 1):
                    for p in (0, 1):
                        for q in (0, 1):
                            for w in (0, 1):
                                for e in (0, 1):
                                    for r in (0, 1):
                                        curr_address = level0["heatmap"][i][j]['lower_level']["heatmap"][m][n]['lower_level']["heatmap"][k][p]['lower_level']["heatmap"][q][w]['lower_level']["heatmap"][e][r]["last_names"]


                                        # print(str(c1) +'-'+ str(c2)+'-'+str(c3) +'-'+ str(c4)+'-'+str(c5) + ',' +str(get_best_name(curr_address)[0]) + "," +
                                        #     str(get_best_name(curr_address)[1]) + "," + str(get_best_name(curr_address)[2]))

                                        print(str(i) + str(j)+'-'+str(m) + str(n)+'-'+str(k) + str(p)+'-'+str(q) + str(w)+'-'+str(e) + str(r)+ ',' +str(get_best_name(curr_address)[0]) + "," +
                                            str(get_best_name(curr_address)[1]) + "," + str(get_best_name(curr_address)[2]))

# level 5 high tfidf
for i in (0, 1):
    for j in (0, 1):
        for m in (0, 1):
            for n in (0, 1):
                for k in (0, 1):
                    for p in (0, 1):
                        for q in (0, 1):
                            for w in (0, 1):
                                for e in (0, 1):
                                    for r in (0, 1):
                                        for t in (0, 1):
                                            for y in (0, 1):
                                                curr_address = level0["heatmap"][i][j]['lower_level']["heatmap"][m][n]['lower_level']["heatmap"][k][p]['lower_level']["heatmap"][q][w]['lower_level']["heatmap"][e][r]['lower_level']["heatmap"][t][y]["last_names"]

                                                print(str(i) + str(j)+'-'+str(m) + str(n)+'-'+str(k) + str(p)+'-'+str(q) + str(w)+'-'+str(e) + str(r)+'-'+str(t) + str(y)+ ' ' +str(get_best_name(curr_address)[0]) + " tf-idf: " +
                                                    str(get_best_name(curr_address)[1]) + " count: " + str(get_best_name(curr_address)[2]))
