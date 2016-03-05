import pygmaps

class googlemap(pygmaps.maps):
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
                '\t\tgoogle.maps.event.addListener(marker, \'click\', (function(marker, i) {\n' +\
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