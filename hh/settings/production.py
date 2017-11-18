import json

from hh.settings.base import *

# file paths
API_DATA_DIR = "/www/clustered_cars/data/"
USER_CLUSTERS_JSON_PATH = os.path.join(API_DATA_DIR, "user.txt")
BOOKING_CSV_PATH = os.path.join(API_DATA_DIR, "booking.csv")
ITEM_CSV_PATH = os.path.join(API_DATA_DIR, "property.csv")

PROPERTY_DESCR_PATH = os.path.join(API_DATA_DIR, "property_descrs.json")
with open(PROPERTY_DESCR_PATH) as f:
    PROPERTY_DESCR = json.load(f)

ALLOWED_HOSTS = ['46.18.25.101']
DEBUG = False
