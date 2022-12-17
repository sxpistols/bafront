# -*- encoding: utf-8 -*-
"""
License: Commercial
Copyright (c) 2019 - present AppSeed.us
"""

from flask_migrate import Migrate
from os import environ
from sys import exit

from config import config_dict
from app import create_app, db


DEBUG = False
get_config_mode = 'Debug' if DEBUG else 'Production'

# get_config_mode = environ.get('APPSEED_CONFIG_MODE', 'Debug')

try:
    config_mode = config_dict[get_config_mode.capitalize()]
    print(config_mode,flush=True)
except KeyError:
    exit('Error: Invalid APPSEED_CONFIG_MODE environment variable entry.')

app = create_app(config_mode) 
Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True)
