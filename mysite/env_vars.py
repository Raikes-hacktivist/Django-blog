
import os

DEBUG_VALUE = os.environ.get('DEBUG_VALUE')


SECRET_KEY = os.environ.get('SECRET_KEY')

RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY =os.environ.get('RECAPTCHA_PRIVATE_KEY')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')


EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

DATABASES = {
    'default': {
        
        'USER': ('DATABASE_USER'),
        'PASSWORD' : ('DATABASE_PASSWORD'),
       
    }
}