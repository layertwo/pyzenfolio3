from pyzenfolio3.exceptions import APIError


VALID_ENUM = {
    'AccessMask': [
        'None',
        'HideDateCreated',
        'HideDateModified',
        'HideDateTaken',
        'HideMetaData',
        'HideUserStats',
        'HideVisits',
        'NoCollections',
        'NoPrivateSearch',
        'NoPublicSearch',
        'NoRecentList',
        'ProtectExif',
        'ProtectXXLarge',
        'ProtectExtraLarge',
        'ProtectLarge',
        'ProtectMedium',
        'ProtectOriginals',
        'ProtectGuestbook',
        'NoPublicGuestbookPosts',
        'NoPrivateGuestbookPosts',
        'NoAnonymousGuestbookPosts',
        'ProtectComments',
        'NoPublicComments',
        'NoPrivateComments',
        'NoAnonymousComments',
        'PasswordProtectOriginals',
        'UnprotectCover',
        'ProtectAll',
    ],
    'AccessType': [
        'Private',
        'Public',
        'UserList',
        'Password',
    ],
    'InformationLevel': [
        'Level1',
        'Level2',
        'Full',
    ],
    'GroupShiftOrder': [
        'CreatedAsc',
        'CreatedDesc',
        'ModifiedAsc',
        'ModifiedDesc',
        'TitleAsc',
        'TitleDesc',
        'GroupsTop',
        'GroupsBottom',
    ],
    'PhotoSetType': [
        'Gallery',
        'Collection',
    ],
    'PhotoRotation': [
        'None',
        'Rotate90',
        'Rotate180',
        'Rotate270',
        'Flip',
        'Rotate90Flip',
        'Rotate180Flip',
        'Rotate270Flip',
    ],
    'ShiftOrder': [
        'CreatedAsc',
        'CreatedDesc',
        'TakenAsc',
        'TakenDesc',
        'TitleAsc',
        'TitleDesc',
        'SizeAsc',
        'SizeDesc',
        'FileNameAsc',
        'FileNameDesc',
    ],
    'SortOrder': [
        'Date',
        'Popularity',
        'Rank',
    ],
    'VideoPlaybackMode': [
        'Flash',
        'iOS',
        'Http',
    ],
}
VALID_OBJECTS = {
    'AccessUpdater': {
        'AccessMask': 'AccessMask',
        'AccessType': 'AccessType',
        'Viewers': None,
        'Password': None,
        'IsDerived': None,
        'PasswordHint': None,
    },
    'GroupUpdater': {
        'Title': None,
        'Caption': None,
        'CustomReference': None,
    },
    'PhotoSetUpdater': {
        'Title': None,
        'Caption': None,
        'Keywords': None,
        'Categories': None,
        'CustomReference': None,
    },
    'PhotoUpdater': {
        'Title': None,
        'Caption': None,
        'Keywords': None,
        'Categories': None,
        'Copyright': None,
        'Filename': None,
    },
    'MessageUpdater': {
        'PosterName': None,
        'PosterUrl': None,
        'PosterEmail': None,
        'Body': None,
        'IsPrivate': None,
    },
}


def assert_type(value, expected_type, param, method):
    if value['$type'] != expected_type:
        raise APIError(f"Got `{value['$type']}` instead of `{expected_type}` value for `{param}` for `{method}` method.")


def validate_value(value, data_struct, method):
    if value not in VALID_ENUM[data_struct]:
        raise APIError(f"`{value}` is an invalid value for `{data_struct}` enumeration for `{method}` method.")


def validate_object(value, data_struct, method):
    if not isinstance(value, dict):
        raise APIError(f"`{data_struct}` must be a dict for `{method}` method.'")

    for k, v in value.items():
        if k not in VALID_OBJECTS[data_struct]:
            raise APIError(f"`{value}` is an invalid key for `{data_struct}` object for `{method}` method.")
        enum = VALID_OBJECTS[data_struct][k]
        if enum is not None:
            validate_value(v, enum, method)
