# -*- coding: utf-8 -*-
import os
import argparse
from modules.spotlight.base_spotlight import BaseSpotlight, BaseBinarySpotlight
import logging


class BaseAppUsage:

    def find_cmd(self):
        path = os.path.join(self.evidence_root(), "Applications")
        return "find " + path + " -iname '*.app' -exec echo {} \;"


class AppUsage(BaseAppUsage, BaseSpotlight):

    def output_file_name(self):
        return "spotlight_app_usage_command.csv"

    def is_target(self, data):
        return data["FilePath"].endswith(".app")

    def attrs(self):
        return [
            "FilePath",
            "kMDItemUseCount",
            "kMDItemLastUsedDate",
            "kMDItemUsedDates"
        ]


class AppUsageBinary(BaseAppUsage, BaseBinarySpotlight):

    def output_file_name(self):
        return "spotlight_app_usage_binary.csv"

    def is_target(self, data):
        return \
            data["_kMDItemFileName"].endswith(".app") \
            # or data["kMDItemDisplayName"].endswith(".app") \
        # or data["_kMDItemDisplayNameWithExtensions"].endswith(".app")

    def attrs(self):
        # "Inode_Num" is required.
        return [
            "FilePath",
            "kMDItemDisplayName",
            "_kMDItemFileName",
            "kMDItemUseCount",
            "kMDItemLastUsedDate",
            "kMDItemUsedDates",
            "Inode_Num",
            "Parent_Inode_Num"
        ]


if __name__ == "__main__":
    LOG = logging.getLogger(__name__)
    LOG.setLevel(logging.INFO)

    print("[+]app_usage for Mac OSX 13.x Ver.20190926")
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-r", "--evidence_root_path",
                             help="please input evidence root path:e.g. /Volumes/disk3s1/",
                             type=str, default="/")
    args_parser.add_argument("-o", "--output", help="please input the output path.", type=str, default=os.getcwd())
    args_parser.add_argument("-t", "--timezone_difference", help="please input the timezone difference hour.", type=int,
                             default=0)
    args_parser.add_argument("-b", "--parse_spotlight_database", help="parse the raw spotlight database",
                             action="store_true")
    args = args_parser.parse_args()
    print("[+]start processing...")

    if args.parse_spotlight_database:
        AppUsageBinary(
            args.evidence_root_path,
            args.output,
            args.timezone_difference,
            LOG).parse()
    else:
        AppUsage(
            args.evidence_root_path,
            args.output,
            args.timezone_difference,
            LOG).parse()
