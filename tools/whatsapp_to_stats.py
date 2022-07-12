#!/usr/bin/env python3

import argparse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from modules.helpers import *
from modules.WhatsappToStats import WhatsappToStats

TODAY = datetime.now().strftime('%Y-%m-%d')

parser = argparse.ArgumentParser(description='Get WhatsApp group stats from export')
parser.add_argument(
    '--filepath',
    help='Relative path top the export', 
    default=f"{get_path_to_storage()}/sources/whatsapp/export-{TODAY}.txt"
)
parser.add_argument(
    'period',
    help='The period to filter the data', 
    choices=['1m', '3m', '1yr', '3yr'],
    default='1m'
)
args = parser.parse_args()

if args.period == '1m':
    dateFrom = datetime.now() - relativedelta(days=30)
elif args.period == '3m':
    dateFrom = datetime.now() - relativedelta(months=3)
elif args.period == '1yr':
    dateFrom = datetime.now() - relativedelta(years=1)
elif args.period == '3yr':
    dateFrom = datetime.now() - relativedelta(years=3)
else:
    print(f"Error: Unexpected args.period of {args.period}")

dateFromString = dateFrom.__format__("%Y-%m-%d %H:%M:%S")
print(f"Generating stats since {args.filepath} ({dateFromString})")
print(f" --filepath={args.filepath}")
print(f" --period={args.period}")
exit(0)
