# convert all country lat and lon from txt file to 5 d.p.

def clean():
    lat_file = 'COUNTRY_LAT.txt'
    lon_file = 'COUNTRY_LON.txt'
    lat = []
    lon = []
    with open(lat_file, 'r') as f:
        for line in f:
            lat.append(line.strip())

    with open(lat_file, 'w') as f:
        for i in lat:
            f.write("{:.5f}\n".format(float(i)))

    with open(lon_file, 'r') as f:
        for line in f:
            lon.append(line.strip())

    with open(lon_file, 'w') as f:
        for i in lon:
            f.write("{:.5f}\n".format(float(i)))

if __name__ == '__main__':
    clean()