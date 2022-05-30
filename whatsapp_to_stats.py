#!/usr/bin/env python3

from datetime import datetime, timedelta
import os
import sys
from git import Repo

from modules.WhatsAppStats import WhatsAppStats

TODAY = datetime.now().strftime("%Y-%m-%d")
# TODAY = "2022-05-29"
PATH_TO_WA_FILE = os.path.realpath(f"{os.path.dirname(__file__)}/storage/sources/whatsapp/export-{TODAY}.txt")

try:
    DATETIME_FROM = datetime.strptime(sys.argv[1], '%Y-%m-%d')
except:
    DATETIME_FROM = datetime.today() - timedelta(days=30)
    print(f"Warning: DATETIME_FROM defaulted to '{DATETIME_FROM}'")

whatsAppStats = WhatsAppStats(PATH_TO_WA_FILE, DATETIME_FROM)

whatsAppStats.show_data()
