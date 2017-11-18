import json

from hh.settings.base import *

# file paths
API_DATA_DIR = "/Users/tural/PyProjects/clustered_cars/data/"
USER_CLUSTERS_JSON_PATH = os.path.join(API_DATA_DIR, "clustered/user.txt")
BOOKING_CSV_PATH = os.path.join(API_DATA_DIR, "cleaned/booking.csv")
ITEM_CSV_PATH = os.path.join(API_DATA_DIR, "cleaned/property.csv")

# property data
PROPERTY_DESCR_PATH = os.path.join(API_DATA_DIR, "property_descrs.json")
with open(PROPERTY_DESCR_PATH) as f:
    PROPERTY_DESCR = json.load(f)
