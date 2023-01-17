# -*- encoding: utf-8 -*-
import os
from   flask_minify  import Minify
from   sys import exit

from app.config import config_dict
from app import create_app, db

# WARNING: Don't run with debug turned on in production!
# 获此荣誉，感到十分荣幸。感谢公司对我的认可与激励，同时感谢公司给与我充分的发展空间，以及具有挑战性的任务让我可以在短时间内丰富以及提高自身的技能，迅速的成长起来。
# 感谢同事们的帮助与支持，在我遇到瓶颈时始终有突破和前进的方向。
# 最后祝愿公司在新的一年更上一层楼，越来越好！也预祝同事们新的一年，好事连连！
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
# Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )

if __name__ == "__main__":
    app.run()
