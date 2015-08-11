# encoding: utf-8
from .settings import *

ADMINS.extend([
    ('Octavi Font', 'tavifont@gmail.com'),
])

ALLOWED_HOSTS.extend([
    "horarispompeu.com",
    "wwww.horarispompeu.com",
])

#########################
# Current year and term #
#########################
# Use a valid AcademicYear.name
ACADEMIC_YEAR = "2013 - 2014"
# Use either 1, 2 or 3
TERM = "3"
# This will appear in HP header and HP ics calendars
TERM_STRING = '1r Trimestre, 2014-15'


############################
# EMail SMTP Server config #
############################
EMAIL_USE_TLS = True | False
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.hostname.com'
EMAIL_HOST_USER = 'user@hostname.com'
EMAIL_HOST_PASSWORD = 'secretPassword'
DEFAULT_FROM_EMAIL = 'user@hostname.com'
SERVER_EMAIL = 'user@hostname.com'

##########################################
# PhantomJS (GCal automatic subscription #
##########################################
PHANTOMJS_BIN = "/path/to/bin/phantomjs"

##############
# S3 Backups #
##############
S3_BACKUP = True
AWS_ACCESS_KEY = 'some string'
AWS_SECRET_KEY = 'some string'
S3_BUCKET = 'somebucket'

######################################
# Supervisord and Nginx config paths #
######################################
SUPERVISORD_CONFIG = '/etc/supervisor/conf.d/someconf.conf'
NGINX_CONFIG = '/etc/nginx/sites-enabled/someconf'
