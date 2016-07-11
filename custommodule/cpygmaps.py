import pygmaps
import random

"""parameters"""
MAP_LAT = 40.758899
MAP_LNG = -73.9873197

class Googlemap(pygmaps.maps):
    def addpoint(self, lat, lng, color = '#FF0000', title = None):
        self.points.append((lat,lng,color[1:],title))

    def drawpoints(self,f):
        if len(self.points[0]) == 4:
            f.write('\t\tvar locations = [')
            for i, point in enumerate(self.points):
                if i != 0:
                    f.write(',\n\t\t\t')
                self.drawpoint(f, point[0], point[1], point[2], point[3])
            f.write('\n\t\t];\n')
            output_html = '\t\tvar infowindow = new google.maps.InfoWindow();\n' +\
                '\t\tvar marker, i;\n' +\
                '\t\tfor (i = 0; i < locations.length; i++) {\n' +\
                '\t\tmarker = new google.maps.Marker({\n' +\
                '\t\tposition: new google.maps.LatLng(locations[i][1], locations[i][2]),\n' +\
                '\t\ticon: new google.maps.MarkerImage(locations[i][3]),\n' +\
                '\t\tmap: map\n' +\
                '\t\t});\n' +\
                '\t\tgoogle.maps.event.addListener(marker, \'mouseover\', (function(marker, i) {\n' +\
                '\t\treturn function() {\n' +\
                '\t\tinfowindow.setContent(locations[i][0]);\n' +\
                '\t\tinfowindow.open(map, marker);\n' +\
                '\t\t}\n' +\
                '\t\t})(marker, i));\n' +\
                '\t\t}\n'
            f.write(output_html)
        else:
            for point in self.points:
                self.drawpoint(f,point[0],point[1],point[2])

    def drawpoint(self,f,lat,lon,color,title = None):
        title = title.replace("\'", "\\\'")
        title = title.replace("\"", "\\\"")
        output_html = '[' +\
            '\'%s\',' % title +\
            '%f,' % lat +\
            '%f,' % lon +\
            '\'%s\'' % (self.coloricon.replace('XXXXXX',color)) +\
            ']'
        f.write(output_html)

    def drawPolyline(self,f,path,\
            clickable = False, \
            geodesic = True,\
            strokeColor = "#FF0000",\
            strokeOpacity = 1.0,\
            strokeWeight = 1
            ):
        f.write('var PolylineCoordinates = [\n')
        for coordinate in path:
            f.write('new google.maps.LatLng(%f, %f),\n' % (coordinate[0],coordinate[1]))
        f.write('];\n')
        f.write('\n')

        f.write('var Path = new google.maps.Polyline({\n')
        f.write('clickable: %s,\n' % (str(clickable).lower()))
        f.write('geodesic: %s,\n' % (str(geodesic).lower()))
        f.write('path: PolylineCoordinates,\n')
        f.write('strokeColor: "%s",\n' %(strokeColor))
        f.write('strokeOpacity: %f,\n' % (strokeOpacity))
        f.write('strokeWeight: %d\n' % (strokeWeight))
        f.write('});\n')
        f.write('\n')
        f.write('Path.setMap(map);\n')
        f.write('\n\n')

def _get_color(num):
    rd = lambda: random.randint(0,255)
    color = ["#%02X%02X%02X" % (rd(), rd(), rd()) for i in range(0, num)]
    return color

def output_clusters(point_all, cluster_membership, c, file_path):
    print("[cpygmaps] Outputing clusters' points on the map, file:", file_path)
    mymap = Googlemap(MAP_LAT, MAP_LNG, 13)
    color = _get_color(c)
    for i, a_point in enumerate(point_all):
        mymap.addpoint(a_point[0], a_point[1], color[cluster_membership[i]], a_point[2])
    mymap.draw(file_path) 

# a point content: lat, lng, content
def output_patterns(trajectories, cluster_membership, c, file_path):
    print("[cpygmaps] Outputing patterns, file:", file_path)
    mymap = Googlemap(MAP_LAT, MAP_LNG, 13)
    color = _get_color(c)
    for i, s in enumerate(trajectories):
        path = [(float(a_point[0]), float(a_point[1])) for a_point in s]
        for j, a_point in enumerate(s):
            mymap.addpoint(float(a_point[0]), float(a_point[1]), color[cluster_membership[i]], a_point[2])
        mymap.addpath(path, color[cluster_membership[i]])
    mymap.draw(file_path)
