import argparse
import os
import socket
from typing import List, Dict

import requests

from pyzenfolio3 import PyZenfolio


class ZenfolioDownloader(PyZenfolio):
    """Zenfolio Downloader."""

    def __init__(self, username: str, password: str, basepath: str, timeout: int) -> None:
        self.basepath = basepath
        self.timeout = timeout
        super().__init__(username=username, password=password)

    def get_photo_sets(self) -> List[Dict]:
        groups = self.load_group_hierarchy().get("Elements", [])
        return self.recurse_photo_sets(groups)

    def recurse_photo_sets(self, elements: List) -> List[Dict]:
        """Get PhotoSets from User.Elements
        Need to recurse as PhotoSets are nested.
        """
        photosets = []
        for e in elements:
            _type = e.get("$type", "")
            if _type == "PhotoSet":
                photosets.append(e)
            elif _type == "Group":
                sets = self.recurse_photo_sets(e.get("Elements", []))
                if sets:
                    photosets.extend(sets)

        return photosets

    def get_photo_set_details(self, _id=None) -> List[Dict]:
        """Get and add individual Photos to PhotoSet structure."""
        _break = False
        for s in self.get_photo_sets():
            if _break:
                break
            if s.get("Id", ""):
                if _id and _id != s["Id"]:
                    _break = True
                    continue
                print(f'getting details for photoset {s["Id"]}, {s["Title"]}')
                photo_details = self.load_photo_sets_photos(s["Id"])
                photo_set = s.copy()
                photo_set["photos"] = photo_details
                yield photo_set

    def download_photos(self) -> None:
        """Get download photos from individual PhotoSet."""
        for d in self.get_photo_set_details():
            directory = d["Title"].strip()
            for p in d.get("photos", []):
                if p.get("$type", "") == "Photo":
                    self.download_photo_from_url(directory, p["OriginalUrl"], p["FileName"])
                else:
                    print(f'unexpected type in PhotoSet, $type = {p["$type"]}')

    def download_photo_from_url(self, directory: str, url: str, filename: str) -> None:
        """Download photo from url"""
        path = os.path.join(self.basepath, directory, filename)
        basename = os.path.dirname(path)
        if not os.path.exists(basename):
            os.makedirs(basename)

        if not os.path.exists(path):
            print(f"downloading file {filename} / {directory} from {url}")
            try:
                r = self.session.get(url, timeout=self.timeout)
            except (socket.timeout, requests.exceptions.Timeout):
                print(f"unable to download file {filename} / {directory} from {url}, timeout {self.timeout}")

            if r.ok:
                print(f"saving file {filename} / {directory} to {path}")
                with open(path, "wb") as fp:
                    fp.write(r.content)
        else:
            print(f"{filename} / {directory} already exists at {path}")


def get_args() -> argparse.Namespace:
    """Get args."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", required=True, type=str, help="Zenfolio username")
    parser.add_argument("-p", "--password", required=True, type=str, help="Zenfolio password")
    parser.add_argument("-b", "--base-path", default="photos",
                        help="root directory to store downloaded photos")
    parser.add_argument("-t", "--timeout", type=int, default=30,
                        help="Download request timeout")
    return parser.parse_args()


def main():
    """Main."""
    args = get_args()

    z = ZenfolioDownloader(args.username, args.password, args.base_path, args.timeout)
    z.download_photos()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
