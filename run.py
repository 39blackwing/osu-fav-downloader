#!/usr/bin/python3.7

import getpass
import osu_fav_downloader


class Argument:
    def _get_sigin_in_info(self,
                           downloader: osu_fav_downloader.OsuFavDownloader):
        if downloader.check_cookie():
            delete = input("Cookie has existed, delete it? [Y/N]: ")
            return not (delete == "Y" or delete == 'y')
        else:
            print("Cookie does not exist, please sign in")
            return False

    def __init__(self, downloader: osu_fav_downloader.OsuFavDownloader):
        self.user_id = ""
        self.username = ""
        self.password = ""
        self.list_size = 0

        if (self._get_sigin_in_info(downloader) == False):
            self.username = input("Input your username: ")
            self.password = getpass.getpass("Input your password: ")
        self.user_id = input("Input the user id (* if current user): ")
        self.list_size = int(input("Input the size of list (default is 100): "))


def main():
    downloader = osu_fav_downloader.OsuFavDownloader()
    args = Argument(downloader)

    if (len(args.username) + len(args.password) != 0 and
            downloader.sign_in(args.username, args.password) == False):
        print ("Sign in failed.")
        return

    begin = 0
    end = args.list_size
    favourite_list = downloader.get_favourite_list(
        downloader.get_current_user_id(), begin, end)
    length = len(favourite_list)

    while length > 0:
        print(f"\n\n{'Num':^5}   {'Artist':^40}   {'Title':^40}")

        for i in range(0, length):
            print(f"{i:^5}", end="   ")
            print(f"{favourite_list[i]['artist']:^40}", end="   ")
            print(f"{favourite_list[i]['title']:^40}")

        print(f"\n{length} beatmaps have been found.")
        if (length < end - begin):
            print("The end of the list")

        to_exit = to_next = False
        while not to_next:
            choices = input('Input the Num to download, "exit" to exit or '
                            '"next" to get next list: ').split()
            for choice in choices:
                if choice.isnumeric() and int(choice) < length:
                    if not downloader.download(favourite_list[choice]):
                        print("Download failed.")
                elif choice == "exit":
                    to_exit = to_next = True
                elif choice == "next":
                    to_next = True
                elif choice == "*":
                    for info in favourite_list:
                        downloader.download(info)

        if to_exit:
            break
        begin = end
        end += args.list_size
        favourite_list = downloader.get_favourite_list(
            downloader.get_current_user_id(), begin, end)
        length = len(favourite_list)

    print("Done.\n")


if __name__ == "__main__":
    main()
