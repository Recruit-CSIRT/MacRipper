from __future__ import print_function
import sys
import argparse
from mac_ripper.modules.plist import *


class plist_ripper:
    # --------------------------------------------------------------------
    # main
    def __init__(self,evidence_root):

        print("[+]parse_SystemVersion for Mac OSX 13.x Ver.0.1")
        print("[+]You must mount image on your system before you run it.")
        self.plist_parser_plungins(evidence_root)
        print("[+]finish")

    # parse_SystemVersion from /System/Library/CoreServices/SystemVersion.plist [+]arg = Evidence_root_path
    def plist_parser_plungins(self, evidence_root):
        systeminfo_plist_parser.SystemInfo.parse_systemVersion(self, evidence_root)


if __name__ == '__main__':
    # get args
    def get_args(self):
        # 準備
        args_parser = argparse.ArgumentParser()

        # 標準入力以外の場合
        if sys.stdin.isatty():
            args_parser.add_argument("evidence_root_path", help="please input evidence root path:e.g. /Volumes/disk3s1/", type=str)
        # 結果を受ける
        args = args_parser.parse_args()

        return (args.evidence_root_path)

    evidence_root = get_args()
    plist_ripper = plist_ripper(evidence_root)

