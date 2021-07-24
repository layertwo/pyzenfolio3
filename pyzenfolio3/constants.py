API_VERSION = '1.8'
API_ENDPOINT_FORMAT = 'https://api.zenfolio.com/api/{}/zfapi.asmx'
API_ENDPOINT = API_ENDPOINT_FORMAT.format(API_VERSION)

PROFILE_RESOLUTIONS = {
    50: (120, 120),
    51: (80, 80),
}
PHOTO_RESOLUTIONS = {
    0: (80, 80),
    1: (60, 60),
    2: (400, 400),
    3: (580, 450),
    4: (800, 630),
    5: (1100, 850),
    6: (1550, 960),
    10: (120, 120),
    11: (120, 120),
}
VIDEO_RESOLUTIONS = {
    200: 1080,
    210: 720,
    215: 480,
    220: 360,
    250: None,
}

DEFAULT_OBJECTS = {
    'AccessUpdater': {
        'IsDerived': True,
    },
    'GroupUpdater': {
        'Title': '',
    },
    'PhotoSetUpdater': {
        'Title': '',
    },
    'PhotoUpdater': {
        'Title': '',
    },
    'MessageUpdater': {
        'PosterName': '',
        'PosterUrl': '',
        'PosterEmail': '',
        'Body': '',
        'IsPrivate': False,
    },
}
