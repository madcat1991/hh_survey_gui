from hh.settings.base import *

# file paths
API_DATA_DIR = "/www/clustered_cars/data/"
USER_CLUSTERS_JSON_PATH = os.path.join(API_DATA_DIR, "user.txt")
BOOKING_CSV_PATH = os.path.join(API_DATA_DIR, "booking.csv")
ITEM_CSV_PATH = os.path.join(API_DATA_DIR, "property.csv")

ALLOWED_HOSTS = ['46.18.25.101']
DEBUG = False
