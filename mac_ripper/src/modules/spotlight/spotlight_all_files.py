# -*- coding: utf-8 -*-
import os
import argparse
from modules.spotlight.base_spotlight import BaseSpotlight, BaseBinarySpotlight
import logging


class BaseSpotlightAllFiles:

    def is_target(self, data):
        return True

    def find_cmd(self):
        return 'mdfind -onlyin ' + self.evidence_root() + ' -name "kMDItemDisplayName == *"'


class SpotlightAllFiles(BaseSpotlightAllFiles, BaseSpotlight):

    def output_file_name(self):
        return "spotlight_all_command.csv"

    def attrs(self):
        return [
            "FilePath",
            "kMDItemDisplayName",
            "_kMDItemFileName",
            "kMDItemTitle",
            "kMDItemKind",
            "kMDItemContentCreationDate",
            "kMDItemFSCreationDate",
            "kMDItemContentModificationDate",
            "kMDItemFSContentChangeDate",
            "kMDItemLastUsedDate",
            "kMDItemDateAdded",
            "kMDItemFSSize",
            "kMDItemOwnerUserID",
            "kMDItemAuthors",
            "kMDItemDownloadedDate",
            "kMDItemWhereFroms"
        ]


class SpotlightAllFilesBinary(BaseSpotlightAllFiles, BaseBinarySpotlight):

    def output_file_name(self):
        return "spotlight_all_binary.csv"

    def attrs(self):
        # "Inode_Num" is required.
        return [
            "FilePath",
            "kMDItemDisplayName",
            "_kMDItemFileName",
            "kMDItemTitle",
            "kMDItemKind",
            "kMDItemContentCreationDate",
            "kMDItemContentModificationDate",
            "kMDItemLastUsedDate",
            "kMDItemDateAdded",
            "kMDItemOwnerUserID",
            "kMDItemAuthors",
            "kMDItemDownloadedDate",
            "kMDItemWhereFroms",
            "Inode_Num",
            "Parent_Inode_Num"
        ]


if __name__ == "__main__":
    LOG = logging.getLogger(__name__)
    LOG.setLevel(logging.INFO)

    print("[+]spotlight_all_files for Mac OSX 13.x Ver.20190926")
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
        SpotlightAllFilesBinary(
            args.evidence_root_path,
            args.output,
            args.timezone_difference).parse()
    else:
        SpotlightAllFiles(
            args.evidence_root_path,
            args.output,
            args.timezone_difference).parse()
