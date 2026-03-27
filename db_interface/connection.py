"""
====================================================================================
File                :   connection.py
Description         :   Default connection config
Author              :   Murugesan G
Date Created        :   Feb 7th 2023
Last Modified BY    :   Murugesan G
Date Modified       :   Feb 9th 2023
====================================================================================
"""
API_KEY = "0099e5b8efdbbda46075f897bf6dea4e"
API_SECRET = "dc3221294f6178b74ea315e93d7088ba"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'star_runway',
        'USER': 'root',
        'PASSWORD': 'Sathiya@13',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
