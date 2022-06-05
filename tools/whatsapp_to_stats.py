#!/usr/bin/env python3

from datetime import datetime, timedelta
import os
import sys

from modules.WhatsappToStats import WhatsappToStats

TODAY = datetime.now().strftime("%Y-%m-%d")
PATH_TO_WA_FILE = os.path.realpath(f"{os.path.dirname(__file__)}/storage/sources/whatsapp/export-{TODAY}.txt")

try:
    DATETIME_FROM = datetime.strptime(sys.argv[1], '%Y-%m-%d')
except:
    DATETIME_FROM = datetime.today() - timedelta(days=30)
    print(f"Warning: DATETIME_FROM defaulted to '{DATETIME_FROM}'")

whatsappToStats = WhatsappToStats(PATH_TO_WA_FILE, DATETIME_FROM)

whatsappToStats.show_data()
