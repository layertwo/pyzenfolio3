import json
import mimetypes
import os
import urllib.request
import urllib.parse
import urllib.error
from hashlib import sha256
from random import randint
from datetime import datetime

import requests

from pyzenfolio.constants import (
    API_ENDPOINT,
    DEFAULT_OBJECTS,
)
from pyzenfolio3.exceptions import APIError, HTTPError, ZenfolioError
from pyzenfolio3.utils import convert_to_datetime
from pyzenfolio3.validate import assert_type, validate_object, validate_value


class PyZenfolio:
    def __init__(self, username, password):
        self.api_endpoint = API_ENDPOINT
        self.session = requests.Session()
        self.session.headers = {'Content-Type': 'application/json'}
        self.username = username
        self.authenticate(username, password)

    # ---------------------------------------------------------------#
    #                      Authentication                            #
    # ---------------------------------------------------------------#

    # TODO revist this
    def authenticate(self, username: str, password: str, force: bool=False) -> None:
        #if 'token' in self.auth and self.auth.token and not force:
        #    # TODO this could be wrong
        #    raise ConfigError('unable to retrieve authentication token!')

        _challenge = self.auth_challenge(username)
        salt = bytearray(_challenge.get('PasswordSalt', ''))
        challenge = bytearray(_challenge.get('Challenge', ''))

        password_hash = sha256(salt + password.encode('utf-8')).digest()
        proof_as_ints = list(sha256(challenge + password_hash).digest())

        token = self._make_request('Authenticate', [_challenge.get('Challenge', ''),
                                                    proof_as_ints])
        self.session.headers.update({'X-Zenfolio-Token': token})

    def auth_challenge(self, username: str) -> str:
        return self._make_request('GetChallenge', username)

    def authenticate_plain(self, username: str, password: str) -> str:
        return self._make_request('AuthenticatePlain', [username, password])

    def authenticate_visitor(self) -> str:
        return self._make_request('AuthenticateVisitor', [self.visitor_key])

    @property
    def visitor_key(self) -> str:
        return self._make_request('GetVisitorKey')

    # ---------------------------------------------------------------#
    #                        Get methods                             #
    # ---------------------------------------------------------------#

    def get_categories(self):
        return self._make_request('GetCategories')

    def get_download_original_key(self, photo_id: int, password):
        return self._make_request('GetDownloadOriginalKey', [photo_id, password])

    def get_popular_photos(self, offset: int=0, limit: int=1000):
        return self._make_request('GetPopularPhotos', [offset, limit])

    def get_popular_sets(self, set_type='Gallery', offset: int=0, limit: int=1000):
        validate_value(set_type, 'PhotoSetType', 'GetPopularSets')
        return self._make_request('GetPopularSets', [set_type, offset, limit])

    def get_recent_photos(self, offset: int=0, limit: int=1000):
        return self._make_request('GetRecentPhotos', [offset, limit])

    def get_recent_sets(self, set_type='Gallery', offset: int=0, limit: int=1000):
        validate_value(set_type, 'PhotoSetType', 'GetRecentSets')
        return self._make_request('GetRecentSets', [set_type, offset, limit])

    def get_video_playback(self, photo_id: int, mode='Http', width: int=1920, height: int=1080):
        validate_value(mode, 'VideoPlaybackMode', 'GetVideoPlaybackUrl')
        return self._make_request('GetVideoPlaybackUrl', [photo_id, mode, width, height])

    # ---------------------------------------------------------------#
    #                        Load methods                            #
    # ---------------------------------------------------------------#

    def load_access_realm(self, realm_id: int):
        return self._make_request('LoadAccessRealm', realm_id)

    def load_group(self, group_id: int, info_level: str='Full', recursive: bool=False):
        validate_value(info_level, 'InformationLevel', 'LoadGroup')
        return self._make_request('LoadGroup', [group_id, info_level, recursive])

    def load_group_hierarchy(self, username: str=None):
        if username is None:
            username = self.username
        return self._make_request('LoadGroupHierarchy', username)

    def load_message(self, mailbox_id: int, posted_since: datetime=None,
                    include_deleted: bool=False):
        return self._make_request('LoadMessages', [mailbox_id, posted_since, include_deleted])

    def load_shared_favorites_set(self):
        return self._make_request('LoadSharedFavoritesSets')

    def load_photo(self, photo_id: int, info_level: str='Full'):
        validate_value(info_level, 'InformationLevel', 'LoadPhoto')
        return self._make_request('LoadPhoto', [photo_id, info_level])

    def load_photo_set(self, set_id: int, info_level: str='Full', with_photos: bool=True):
        validate_value(info_level, 'InformationLevel', 'LoadPhotoSet')
        return self._make_request('LoadPhotoSet', [set_id, info_level, with_photos])

    def load_photo_sets_photos(self, set_id: int, start_index: int=0, limit: int=5000):
        return self._make_request('LoadPhotoSetPhotos', [set_id, start_index, limit])

    def load_private_profile(self):
        return self._make_request('LoadPrivateProfile')

    def load_public_profile(self, username: str=None):
        if username is None:
            username = self.username
        return self._make_request('LoadPublicProfile', username)

    # ---------------------------------------------------------------#
    #                       Create methods                           #
    # ---------------------------------------------------------------#

    def create_favorites_set(self, name, username, ids):
        return self._make_request('CreateFavoritesSet', [name, username, ids])

    def create_group(self, parent_id: int, group: dict=None):
        if group is None:
            group = {}
        updater = dict(DEFAULT_OBJECTS['GroupUpdater'])
        updater.update(group)
        validate_object(group, 'GroupUpdater', 'CreateGroup')
        return self._make_request('CreateGroup', [parent_id, updater])

    def create_photo_from_url(self, photoset_id: int, url, cookies=None):
        if isinstance(cookies, dict):
            cookies = ';'.join(['='.join([urllib.parse.quote_plus(i) for i in c])
                                for c in list(cookies.items())])
        return self._make_request('CreatePhotoFromUrl', [photoset_id, url, cookies])

    def create_photo_set(self, group_id: int, set_type='Gallery', photoset=None):
        validate_value(set_type, 'PhotoSetType', 'CreatePhotoSet')
        if photoset is None:
            photoset = {}
        updater = dict(DEFAULT_OBJECTS['PhotoSetUpdater'])
        updater.update(photoset)
        validate_object(updater, 'PhotoSetUpdater', 'CreatePhotoSet')
        return self._make_request('CreatePhotoSet', [group_id, set_type, updater])

    def create_video_from_url(self, photoset_id: int, url, cookies=None):
        if isinstance(cookies, dict):
            cookies = ';'.join(['='.join([urllib.parse.quote_plus(i) for i in c])
                                for c in list(cookies.items())])
        return self._make_request('CreateVideoFromUrl', [photoset_id, url, cookies])

    def upload_photo(self, photoset, path, filename=None):
        assert_type(photoset, 'PhotoSet', 'photoset', 'UploadPhoto')
        upload_url = photoset.UploadUrl

        # TODO should this be handled by the library
        # or bytes object read in from caller?
        with open(path, 'rb') as fid:
            data = fid.read()
            filename = filename or os.path.basename(path)

            headers = {'Content-Type': mimetypes.guess_type(filename)[0]}
            params = {'filename': filename }
            request = requests.post(upload_url,
                                    params=params,
                                    data=data,
                                    headers=headers)
            if request.status_code != 200:
                raise HTTPError(self.api_endpoint,
                                request.status_code,
                                request.headers,
                                request.content)
            # Should this be request.json()?
            return request.text

        raise APIError('Could not upload photo')

    def add_message(self, mail_id: int, message: str):
        validate_object(message, 'MessageUpdater', 'AddMessage')
        return self._make_request('AddMessage', [mail_id, message])

    # ---------------------------------------------------------------#
    #                         Set  methods                           #
    # ---------------------------------------------------------------#

    def set_group_title_photo(self, group_id: int, photo_id: int):
        return self._make_request('SetGroupTitlePhoto', [group_id, photo_id])

    def set_photo_set_featured_index(self, photoset_id: int, index):
        return self._make_request('SetPhotoSetFeaturedIndex', [photoset_id, index])

    def set_photo_set_title_photo(self, photoset_id: int, photo_id: int):
        return self._make_request('SetPhotoSetTitlePhoto', [photoset_id, photo_id])

    def set_random_photo_set_title_photo(self, photoset_id: int):
        return self._make_request('SetRandomPhotoSetTitlePhoto', [photoset_id])

    # ---------------------------------------------------------------#
    #                        Update methods                          #
    # ---------------------------------------------------------------#

    def update_group(self, group_id: int, group=None):
        if group is None:
            group = {}
        updater = dict(DEFAULT_OBJECTS['GroupUpdater'])
        updater.update(group)
        validate_object(updater, 'GroupUpdater', 'UpdateGroup')
        return self._make_request('UpdateGroup', [group_id, updater])

    def update_group_access(self, group_id: int, group_access=None):
        if group_access is None:
            group_access = {}
        updater = dict(DEFAULT_OBJECTS['AccessUpdater'])
        updater.update(group_access)
        validate_object(updater, 'AccessUpdater', 'UpdateGroupAccess')
        return self._make_request('UpdateGroupAccess', [group_id, updater])

    def update_photo(self, photo_id: int, photo=None):
        if photo is None:
            photo = {}
        updater = dict(DEFAULT_OBJECTS['PhotoUpdater'])
        updater.update(photo)
        validate_object(updater, 'PhotoUpdater', 'UpdatePhoto')
        return self._make_request('UpdatePhoto', [photo_id, updater])

    def update_photo_access(self, photo_id: int, photo_access=None):
        if photo_access is None:
            photo_access = {}
        updater = dict(DEFAULT_OBJECTS['AccessUpdater'])
        updater.update(photo_access)
        validate_object(updater, 'AccessUpdater', 'UpdatePhotoAccess')
        return self._make_request('UpdatePhotoAccess', [photo_id, updater])

    def update_photo_set(self, photoset_id: int, photoset=None):
        if photoset is None:
            photoset = {}
        updater = dict(DEFAULT_OBJECTS['PhotoSetUpdater'])
        updater.update(photoset)
        validate_object(updater, 'PhotoSetUpdater', 'UpdatePhotoSet')
        return self._make_request('UpdatePhotoSet', [photoset_id, updater])

    def update_photo_set_access(self, photoset_id: int, photoset_access=None):
        if photoset_access is None:
            photoset_access = {}
        updater = dict(DEFAULT_OBJECTS['AccessUpdater'])
        updater.update(photoset_access)
        validate_object(updater, 'AccessUpdater', 'UpdatePhotoSetAccess')
        return self._make_request('UpdatePhotoSetAccess', [photoset_id, updater])

    # ---------------------------------------------------------------#
    #                          Move methods                          #
    # ---------------------------------------------------------------#

    def move_group(self, group_id: int, dest_group_id: int, index):
        return self._make_request('MoveGroup', [group_id, dest_group_id, index])

    def move_photo(self, photoset_id: int, photo_id: int, dest_photoset_id: int, index):
        return self._make_request('MovePhoto', [photoset_id, photo_id, dest_photoset_id, index])

    def move_photos(self, photoset_id: int, dest_photoset_id: int, ids):
        return self._make_request('MovePhotos', [photoset_id, dest_photoset_id, ids])

    def move_photo_set(self, photoset_id: int, dest_group_id: int, index):
        return self._make_request('MovePhotoSet', [photoset_id, dest_group_id, index])

    # ---------------------------------------------------------------#
    #                            Search                              #
    # ---------------------------------------------------------------#

    def search_photo_by_category(self, search_id: int, sort, category, offset: int, limit: int):
        validate_value(sort, 'SortOrder', 'SearchPhotoByCategory')
        return self._make_request('SearchPhotoByCategory', [search_id, sort,
                                                            category, offset, limit])

    def search_photo_by_text(self, search_id: int, sort, query, offset: int, limit: int):
        validate_value(sort, 'SortOrder', 'SearchPhotoByText')
        return self._make_request('SearchPhotoByText', [search_id, sort, query, offset, limit])

    def search_set_by_category(self, search_id: int, photoset_type, sort,
                               category, offset: int, limit: int):
        validate_value(photoset_type, 'PhotoSetType', 'SearchSetByCategory')
        validate_value(sort, 'SortOrder', 'SearchSetByCategory')
        return self._make_request('SearchSetByCategory', [search_id, photoset_type,
                                                 sort, category, offset, limit])

    def search_set_by_text(self, search_id: int, photoset_type, sort,
                           query, offset: int, limit: int):
        validate_value(photoset_type, 'PhotoSetType', 'SearchSetByText')
        validate_value(sort, 'SortOrder', 'SearchSetByText')
        return self._make_request('SearchSetByText', [search_id, photoset_type, sort,
                                             query, offset, limit])

    # ---------------------------------------------------------------#
    #                        Delete methods                          #
    # ---------------------------------------------------------------#

    def delete_group(self, group_id: int):
        return self._make_request('DeleteGroup', group_id)

    def delete_message(self, mailbox_id: int, index):
        return self._make_request('DeleteMessage', [mailbox_id, index])

    def delete_photo(self, photo_id: int):
        return self._make_request('DeletePhoto', photo_id)

    def delete_photos(self, photo_ids):
        return self._make_request('DeletePhotos', photo_ids)

    def delete_photo_set(self, photoset_id: int):
        return self._make_request('DeletePhotoSet', photoset_id)

    # ---------------------------------------------------------------#
    #                         Miscellaneous                          #
    # ---------------------------------------------------------------#

    def collection_add_photo(self, coll_id: int, photo_id: int):
        return self._make_request('CollectionAddPhoto', [coll_id, photo_id])

    def collection_remove_photo(self, coll_id: int, photo_id: int):
        return self._make_request('CollectionRemovePhoto', [coll_id, photo_id])

    def keyring_add_key_plain(self, keyring, realm_id: int, password):
        return self._make_request('KeyringAddKeyPlain', [keyring, realm_id, password])

    def keyring_get_unlocked_realms(self, keyring):
        return self._make_request('KeyringGetUnlockedRealms', keyring)

    def reindex_photo_set(self, photoset_id: int, index, mapping):
        return self._make_request('ReindexPhotoSet', [photoset_id, index, mapping])

    def remove_group_title_photo(self, group_id: int):
        return self._make_request('RemoveGroupTitlePhoto', [group_id])

    def remove_photo_set_title_photo(self, photoset_id: int):
        return self._make_request('RemovePhotoSetTitlePhoto', [photoset_id])

    def reorder_group(self, group_id: int, order):
        validate_value(order, 'GroupShiftOrder', 'ReorderGroup')
        return self._make_request('ReorderGroup', [group_id, order])

    def reorder_photo_set(self, photoset_id: int, order):
        validate_value(order, 'ShiftOrder', 'ReorderPhotoSet')
        return self._make_request('ReorderPhotoSet', [photoset_id, order])

    def replace_photo(self, original_id: int, replacement_id):
        return self._make_request('ReplacePhoto', [original_id, replacement_id])

    def rotate_photo(self, photo_id: int, rotation):
        validate_value(rotation, 'PhotoRotation', 'RotatePhoto')
        return self._make_request('RotatePhoto', [photo_id, rotation])

    def share_favorites_set(self, favset_id: int, favset_name, name, email, message):
        return self._make_request('ShareFavoritesSet', [favset_id, favset_name,
                                                        name, email, message])

    def undelete_message(self, mailbox_id: int, message_index):
        return self._make_request('UndeleteMessage', [mailbox_id, message_index])

    # ---------------------------------------------------------------#
    #                           Internals                            #
    # ---------------------------------------------------------------#

    def _make_request(self, method: str, params=None):
        if params is None:
            params = []
        elif not isinstance(params, (list, tuple)):
            params = [params]

        data = {'method': method,
                'params': params,
                'id': randint(0, 2 ** 16 - 1)}

        try:
            request = self.session.post(self.api_endpoint,
                                        data=json.dumps(data))
        except Exception as pyzenfolio_api_error:
            raise APIError from pyzenfolio_api_error
        if request.status_code != 200:
            raise HTTPError(self.api_endpoint,
                            request.status_code,
                            request.headers,
                            request.content)

        resp = request.json()
        if resp.get('error', ''):
            code = None
            message = None
            if resp['error'].get('code', ''):
                code = resp['error']['code']
            if resp['error'].get('message', ''):
                message = resp['error']['code']
            raise ZenfolioError(code, message)

        if resp.get('id', 0) != data.get('id', 0):
            raise APIError('Response ID does match request ID')

        #return convert_to_datetime(resp.get('result', {}))
        return resp.get('result', {})
