# PyZenfolio

Lightweight Zenfolio API Python wrapper.

Using this wrapper is pretty straight-forward and does not require to use any special data-structures.

### Example
```
from pyzenfolio3 import PyZenfolio

api = PyZenfolio(username='foo', 'password'='bar')

# lookup user
user = api.load_public_profile()

# create photoset
photoset = api.CreatePhotoSet(
    user.RootGroup.Id,
    attr={
        'Title': 'foo'
    }
)
photoset_url = photoset.page_url

# upload image
api.upload_photo(photoset, 'bar.jpg')

# get image download URL
image = api.load_photo_set_photos(photoset.Id)
url = image.original_url
```
