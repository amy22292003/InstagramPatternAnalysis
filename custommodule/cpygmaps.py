import pygmaps
import random

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


    def drawpoint(self,f,lat,lon,color,title):
        title = title.replace("\'", "\\\'")
        title = title.replace("\"", "\\\"")
        output_html = \
            '[\'%s\',' % title +\
            '%f,' % lat +\
            '%f,' % lon +\
            '\'%s\'' % (self.coloricon.replace('XXXXXX',color)) +\
            ']'
        f.write(output_html)        

def output_clusters(point_all, cluster_membership, c, output_file):
    print("Outputing clusters' points on the map...")
    mymap = Googlemap(40.758899, -73.9873197, 13)
    rd = lambda: random.randint(0,255)
    color = ["#000000"] + ["#%02X%02X%02X" % (rd(), rd(), rd()) for i in range(0, c)]
    for i, a_point in enumerate(point_all):
        mymap.addpoint(a_point[0], a_point[1], color[cluster_membership[i]], a_point[2])
    mymap.draw(output_file) 