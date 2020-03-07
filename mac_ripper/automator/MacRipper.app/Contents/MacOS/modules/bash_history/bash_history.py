from __future__ import print_function
import sys
import argparse
import plistlib
import glob
import os


class Finder:

    def __init__(self, evidence_root, output_path):
        self.evidence_root = evidence_root
        self.output_path = output_path
        self.users_plist = {}
        self.bash_hist_path = '.bash_sessions/*'
        self.bash_sess_path = '.bash_sessions/*'
        self.text = "----------------------------------------------------------\n"
        self.text += "[*] Volume positions from finder plist.\n"
        self.text += "[*] This attribute show the .bash_history and .bash_sessions/*.\n"
        self.search()

    def parse_bash_history(self, user, file_path):
        """parse user's finder plist.

        Args:
            user: user name
            file_path: user's plist path
        """

        self.text += f"\n[*] User: {user}\n"
        print(f"[+] Processing to parse {user}'s {file_path}")
        with open(file_path, 'rb') as file:
            plist = plistlib.load(file)
            if plist.get('FXDesktopVolumePositions') is None:
                self.text += "[-] VolumePositions are not found."
                print(self.text)
                return

            for key, val in plist.get('FXDesktopVolumePositions').items():
                self.text += f"[+] Volume: {key}\n"

    def extract(self):
        for key, val in self.users_plist.items():
            if val.get('exists') is False:
                continue
            self.parse_volume_positions(key, val.get('plist'))

    def output_txt(self):
        with open(os.path.join(self.output_path, 'VolumePosition.txt'), 'w') as file:
            file.write(self.text)

    def search(self):
        """search users finder plist.

        Args:
            -
        """
        users_dir_path = os.path.join(self.evidence_root, "Users/")  # ディレクトリ一覧を取得したいディレクトリ

        print("[+] Searching user finder plist")
        for user_dir in os.listdir(users_dir_path):
            # パスに取り出したオブジェクトを足してフルパスに
            user_full_dir_path = os.path.join(users_dir_path, user_dir)

            if os.path.isdir(user_full_dir_path):
                self.users_plist[user_dir] = {
                    'plist': os.path.join(user_full_dir_path, self.plist_path),
                    'exists': os.path.isfile(os.path.join(user_full_dir_path, self.plist_path))
                }

        # root
        self.users_plist['root'] = {
            'plist': os.path.join(self.evidence_root, f"var/root/{self.plist_path}"),
            'exists': os.path.isfile(os.path.join(self.evidence_root, f"var/root/{self.plist_path}"))
        }

        for key, val in self.users_plist.items():
            if val.get('exists'):
                print(f"[+] User: {key}, Plist: {val.get('plist')}")


if __name__ == '__main__':

    # 準備
    args_parser = argparse.ArgumentParser()

    args_parser.add_argument('-r', '--root',
                             help="please input evidence root path:e.g. "
                                  "/Volumes/disk3s1/", type=str,
                             default="/Volumes/disk3s1/")
    args_parser.add_argument('-o', '--output',
                             help="please input output path:", type=str,
                             default=os.getcwd())
    # 結果を受ける
    args = args_parser.parse_args()

    fd = Finder(args.root, args.output)
    fd.extract()
    fd.output_txt()
