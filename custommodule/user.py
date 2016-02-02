#from sets import Set
from bs4 import BeautifulSoup
import requests
import re
import datetime

class AUser:
    def __init__(self):
        self.uid = ""
        self.uname = ""
        self.allpostcount = 0
        self.locationpostcount = 0
        self.filterpostcount = 0
        self.posts = []

    def set_post_num(allpostcount, locationpostcount):
        self.allpostcount = allpostcount
        self.locationpostcount = locationpostcount
