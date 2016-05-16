#!/usr/bin/env python3
import datetime
import numpy
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append(PACKAGE_PARENT)

import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.tag as ctag

"""parameters"""


"""file path"""
USER_POSTS_FILE = "./data/LocationTags"

def main():
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")
    
    # getting data
    #locations = clocation.open_locations()
    #users = cuser.open_users_posts_afile(USER_POSTS_FILE)
    locations = ctag.open_location_tags(USER_POSTS_FILE)

    corpus = ctag.get_corpus([x.tags for x in locations.values()])
    vector, tag_name = cfuzzy.get_tag_vector(corpus)
    cfuzzy.fit_lda(vector, tag_name)


    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

if __name__ == '__main__':
    main()
