import logging
import os
import pprint
from config import LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=os.environ.get("LOGLEVEL", "INFO"))

logger = logging.getLogger('PR-Reminder')

# pretty printer
pp = pprint.PrettyPrinter(indent=2)
