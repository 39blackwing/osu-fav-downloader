"""osu! favourite beatmaps downloader."""

import requests
import http
import json


class OsuFavDownloader:
    """osu! favourite beatmaps downloader class."""

    _COOKIE_FILENAME = "cookies.txt"

    def __init__(self):
        """Constructor."""
        self._session = requests.Session()
        self._session.headers = {
            "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }

    def __del__(self):
        """Destructor."""
        self._session.close()

    def check_cookie(self) -> bool:
        """Check the cookie files
        """

        try:
            with open(self._COOKIE_FILENAME) as _:
                return True

        except FileNotFoundError:
            return False

    def sign_in(self, username: str, password: str) -> bool:
        """Sign in to osu!

        Args:
            username: Your username of osu!
            password: Your password of osu!

        Returns:
            return True if sign in successfully, False if failed.
        """
        self._session.cookies = http.cookiejar.LWPCookieJar()
        response = self._session.post("https://osu.ppy.sh/session",
                                      data={
                                          "username": username,
                                          "password": password
                                      })

        if response.status_code / 100 > 2: return False

        self._session.cookies.save(filename=self._COOKIE_FILENAME,
                                   ignore_discard=True,
                                   ignore_expires=True)
        return True

    def get_current_user_id(self) -> str:
        """Get current osu! user ID.

        Returns:
            A string of user ID, or an empty string if failed.
        """
        self._session.cookies = http.cookiejar.LWPCookieJar()
        self._session.cookies.load(filename="cookies.txt")
        response = self._session.get("https://osu.ppy.sh/home")

        if response.status_code / 100 > 2: return ""

        # view-source:https://osu.ppy.sh/home Line 2990:
        # var currentUser = {"id":0,"username":" ...
        pos_l = response.text.rfind('currentUser = {"id":')
        pos_r = response.text.rfind('username":"')

        if pos_l < 0 or pos_r < 0: return ""
        return response.text[pos_l + 20:pos_r - 2]

    def get_favourite_list(self, user_id: str, begin=0, end=99999) -> list:
        """Get osu! favourite beatmaps by user ID.

        Returns:
            A list of favourite beatmaps.
        """
        favourite_list = []

        while begin < end:
            url = f"https://osu.ppy.sh/users/{user_id}/beatmapsets/favourite"
            url += f"?offset={begin}&limit={min(end - begin, 51)}"
            begin += min(end - begin, 51)
            response = self._session.get(url)

            if response.status_code / 100 > 2: return []

            data = json.loads(response.text)
            if data == []: break
            favourite_list += data

        return favourite_list

    def download(self, info: dir) -> bool:
        """Download osu! beatmaps.

        Args:
            info: The beatmap info from get_favourite_list()

        Returns:
            A list of favourite beatmaps.
        """
        # URL: "https://osu.ppy.sh/beatmapsets/10435/download"
        # File name: "10435 Masayoshi Minoshima ft. nomico - Bad Apple!!.osz"
        filename = f"{info['id']} {info['artist']} - {info['title']}.osz"

        if "downloaded" in info: return True

        print(f"Downloading: {filename}")
        response = self._session.get(
            f"https://osu.ppy.sh/beatmapsets/{info['id']}/download")

        if response.status_code / 100 > 2: return False

        with open(filename, "wb") as file:
            file.write(response.content)

        info["downloaded"] = True
        return True
