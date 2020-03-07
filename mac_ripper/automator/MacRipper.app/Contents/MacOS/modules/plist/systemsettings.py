from __future__ import print_function
import os
import argparse
import plistlib
import csv


class SystemSettings:
    # --------------------------------------------------------------------
    # main
    def __init__(self, evidence_root, output_path):
        print("[+]parse systemsettings for Mac OSX 13.x Ver.0.1")
        print("[+]You must mount image on your system before you run it.")
        print("[+]Or your system will process")
        print("[+]This tool will parse the follows.")
        print("[+]OS Version")
        #print("[+]Timezone")
        self.evidence_root = evidence_root
        self.output_path = output_path
        self.parse_plist = {}
        self.plist_path_version = 'System/Library/CoreServices/SystemVersion.plist'
        self.plist_path_timezone = ''
        self.text = "----------------------------------------------------------\n"

""""
        output.append("Timezone")
        output.append("/Library/Preferences/.GlobalPreferences.plist\n\n")
        output.append("Target file path on your machine(not true path):\n{}\n".format(SystemVersion_path))
        print("[+]now processing -> {}".format("File path on your machine(not true path): " + SystemVersion_path))
""""
        self.search()

    def parse_osversion(self, file_path):
        """parse user's finder plist.

        Args:
            user: user name
            file_path: user's plist path
        """

        print(f"[+] Processing to parse {file_path}")
        self.text += "[*] SystemSettings for Mac OSX Ver.190523"
        self.text += "[*] OS Version from SystemVersion plist."
        self.text += "[*] This attribute show the os version of evidence."
        self.text += "[*] This tool will parse the following."
        self.text += "[*] このツールは下記のファイルをパースし、調査に有用な情報を出力します"
        self.text += "/System/Library/CoreServices/SystemVersion.plist\n\n"
        self.text += f"[*]Target file path on your machine(not true path):\n{SystemVersion_path}\n"


        with open(file_path, 'rb') as file:
            osver_plist = plistlib.load(file)
            if osver_plist.get('ProductVersion') is None:
                self.text += "[-] ProductVersion are not found."
                print(self.text)
                return

            osver = osver_plist.get('ProductVersion')
            self.text += f"[+] os version: {osver}\n"

    def extract(self):
        if self.parse_plist.item('exists') is False:
            continue
        self.parse_osversion(self.evidence_root)
    
    def output_txt(self):
        with open(os.path.join(self.output_path, 'ststemsettings.txt'), 'w') as file:
            file.write(self.text)

    def search(self):
        """search users finder plist.

        Args:
            -
        """

        print("[+] Searching os version plist")
        #parse_path = (f"{self.evidence_root}{self.plist_path_version}")

        # root
        self.parse_plist['root'] = {
            'plist': os.path.join(self.evidence_root, self.plist_path_version),
            'exists': os.path.isfile(os.path.join(self.evidence_root, self.plist_path_version)
        }

        for key, val in self.parse_plist.items():
            if val.get('exists'):
                print(f"[+] Plist: {val.get('plist')}")






    # parse_systemVersion from /System/Library/CoreServices/SystemVersion.plist [+]arg = Evidence_root_path
    def parse_system_version(self):

        print("[+]parse systemsettings for Mac OSX 13.x Ver.0.1")
        print("[+]You must mount image on your system before you run it.")
        print("[+]Or your system will process")
        print("[+]This tool will parse the follows.")
        print("[+]OS Version")
        print("[+]Timezone")

        # 読み込むプロパティリストファイルのパス
        SystemVersion_path = ("{}System/Library/CoreServices/SystemVersion.plist".format(self.evidence_root))
        output_file = os.path.join(self.output_path, 'SystemSettings.txt')

        #read plist file
        with open(SystemVersion_path, 'rb') as SysVer:
                print("[+]start processing...")
                # make&open

                output = []
                output.append("[+]SystemSettings for Mac OSX Ver.190523")
                output.append("[+]This tool will parse the following.")
                output.append("[+]このツールは下記のファイルをパースし、調査に有用な情報を出力します")
                output.append("OS Version")
                output.append("System/Library/CoreServices/SystemVersion.plist\n\n")
                output.append("Timezone")
                output.append("/Library/Preferences/.GlobalPreferences.plist\n\n")
                output.append("Target file path on your machine(not true path):\n{}\n".format(SystemVersion_path))
                print("[+]now processing -> {}".format("File path on your machine(not true path): " + SystemVersion_path))

                SystemVersion = plistlib.load(SysVer)
                fieldnames = SystemVersion.keys()

                output.append("Program Path: " + "\n" + cnt["Program"] + "\n")

                f.write('\n'.join(fieldnames))
                row_str = [SystemVersion[fieldname] for fieldname in fieldnames]

                str_ = '\n'.join(output)
                with open("{}/".format(self.output_folder_path) + "Persistence_LaunchAgents.txt", 'wt') as f:
                    f.write(str_)


    def parse_timezone(self):
        # 読み込むプロパティリストファイルのパス
        timezoneversion_path = ("{}Library/Preferences/.GlobalPreferences.plist".format(self.evidence_root))
        output_file = os.path.join(self.output_path, 'SystemSettings.txt')

        # read plist file
        with open(timezoneversion_path, 'rb') as Tzone:
            print("[+]start processing...")
            # make&open csv file
            with open(output_file, 'w', newline='') as f:
                # read plist file
                Timezone = plistlib.load(Tzone)
                fieldnames = Timezone.keys()
                f.write(','.join(fieldnames) + '\n')
                # for row in SystemVersion:
                row_str = [Timezone[fieldname] for fieldname in fieldnames]
                f.write(','.join(row_str) + '\n')

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()

    # 標準入力以外の場合
    args_parser.add_argument("evidence_root_path", help="please input evidence root path:e.g. /Volumes/disk3s1/",
                             type=str)
    # 結果を受ける
    args = args_parser.parse_args()

    GetSystemInfo = SystemSettings(args.evidence_root_path)