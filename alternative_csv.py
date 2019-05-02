import csv
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
