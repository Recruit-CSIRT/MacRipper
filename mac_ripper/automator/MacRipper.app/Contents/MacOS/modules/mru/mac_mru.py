# -*- coding: utf-8 -*-
import os
import argparse
import fnmatch
from modules.mru.bookmark import Bookmark
from modules.mru.alias import Alias
import modules.mru.ccl_bplist
import plistlib
import logging
import glob

class Formatter:
    def __init__(self):
        self._items = []
        self._splitter = "*" * 30

    def add_value(self, k, v):
        self._items.append({"key": k, "value": v})

    def set_splitter(self, splitter):
        self._splitter = splitter

    def format(self):
        res = []
        res.append(self._splitter)
        for item in self._items:
            res.append(item["key"] + " : " + item["value"])
        return "\n".join(res) + "\n"


class Mru:
    def __init__(self, evidence_root, out_path, logger):
        self.evidence_root = evidence_root
        self.out_path = os.path.join(out_path, "mru_parsed.txt")
        self.log = logger

        if os.path.exists(self.out_path):
            os.remove(self.out_path)
        os.makedirs(out_path, exist_ok=True)

    def isMatch(self, string, blobs, orMatch=False):
        if orMatch:
            for blob in blobs:
                if fnmatch.fnmatch(string, blob):
                    return True
            return False

        for blob in blobs:
            if not fnmatch.fnmatch(string, blob):
                return False
        return True

    def write(self, content):
        with open(self.out_path, 'a', encoding='utf_8_sig') as file:
            file.write(content)

    def load_bplist(self, path):
        try:
            with open(path, "rb") as plistfile:
                return modules.mru.ccl_bplist.load(plistfile)
        except Exception as e:
            return None

    def decode(self, plist):
        try:
            return modules.mru.ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
        except:
            return None

    def load_plist_objects(self, mru_file):
        plist = self.load_bplist(mru_file)
        if plist == None:
            return None

        objects = self.decode(plist)
        return objects

    def parseSFL(self, mru_file):
        plist_objects = self.load_plist_objects(mru_file)
        if plist_objects == None:
            return []
        bookmarks = []
        try:
            if plist_objects["root"]["NS.keys"][2] == "items":
                items = plist_objects["root"]["NS.objects"][2]["NS.objects"]
                for n, item in enumerate(items):
                    if "LSSharedFileList.RecentHosts" not in mru_file:
                        bookmarks.append(Bookmark(data=item["bookmark"]).parse())
        except Exception as e:
            pass
        return bookmarks

    def parseSFL2(self, mru_file):
        plist_objects = self.load_plist_objects(mru_file)

        print(mru_file, plist_objects)
        if plist_objects == None:
            return []
        bookmarks = []
        try:
            if plist_objects["root"]["NS.keys"][0] == "items":
                items = plist_objects["root"]["NS.objects"][0]["NS.objects"]
                for n, item in enumerate(items):
                    attribute_keys = plist_objects["root"]["NS.objects"][0]["NS.objects"][n]["NS.keys"]
                    attribute_values = plist_objects["root"]["NS.objects"][0]["NS.objects"][n]["NS.objects"]
                    attributes = dict(zip(attribute_keys, attribute_values))
                    if "LSSharedFileList.RecentHosts" not in mru_file:
                        bookmarks.append(Bookmark(data=attributes["Bookmark"]).parse())
        except Exception as e:
            pass
        return bookmarks

    def parseSFL2_FavoriteVolumes(self, mru_file):
        plist_objects = self.load_plist_objects(mru_file)
        if plist_objects == None:
            return []
        bookmarks = []
        try:
            if plist_objects["root"]["NS.keys"][0] == "items":
                items = plist_objects["root"]["NS.objects"][0]["NS.objects"]
                for n, item in enumerate(items):
                    attribute_keys = plist_objects["root"]["NS.objects"][0]["NS.objects"][n]["NS.keys"]
                    attribute_values = plist_objects["root"]["NS.objects"][0]["NS.objects"][n]["NS.objects"]
                    attributes = dict(zip(attribute_keys, attribute_values))
                    if "LSSharedFileList.RecentHosts" not in mru_file:
                        bookmarks.append(Bookmark(data=attributes["Bookmark"]).parse())
        except Exception as e:
            pass
        return bookmarks

    def parseLSSharedFileListPlist(self, mru_file):
        plist = self.load_bplist(mru_file)
        if plist == None:
            return []
        bookmarks = []
        try:
            for n, item in enumerate(plist["RecentDocuments"]["CustomListItems"]):
                bookmarks.append(Bookmark(data=item["Bookmark"]).parse())
        except Exception as e:
            pass
        return bookmarks

    def parseFinderPlist(self, mru_file):
        plist = self.load_bplist(mru_file)
        if plist == None:
            return [], []
        bookmarks = []
        aliases = []
        try:
            for n, item in enumerate(plist["FXRecentFolders"]):
                try:
                    bookmarks.append(Bookmark(data=item["file-bookmark"]).parse())
                except:
                    pass
                try:
                    pass
                    aliases.append(Alias(data=item["file-data"]["_CFURLAliasData"]).parse())
                except:
                    pass
        except:
            pass
        return bookmarks, aliases

    def parseSidebarlistsPlist(self, mru_file):
        plist = self.load_bplist(mru_file)
        if plist == None:
            return []
        aliases = []
        try:
            for n, item in enumerate(plist["systemitems"]['VolumesList']):
                try:
                    aliases.append(Alias(data=plist["systemitems"]['VolumesList'][n]['Alias']).parse())
                except Exception as e:
                    pass
        except:
            pass
        try:
            for n, item in enumerate(plist["favorites"]['VolumesList']):
                try:
                    pass
                    aliases.append(Alias(data=plist["systemitems"]['VolumesList'][n]['Alias']).parse())
                except:
                    pass
        except:
            pass
        return aliases

    def parseRecentItemsPlist(self, mru_file):
        plist = self.load_bplist(mru_file)
        if plist == None:
            return [], []
        bookmarks = []
        aliases = []
        try:
            for n, item in enumerate(plist["RecentApplications"]["CustomListItems"]):
                bookmarks.append(Bookmark(data=item["Bookmark"]).parse())
        except:
            pass
        try:
            for n, item in enumerate(plist["RecentDocuments"]["CustomListItems"]):
                bookmarks.append(Bookmark(data=item["Bookmark"]).parse())
        except:
            pass
        try:
            for n, item in enumerate(plist["RecentServers"]["CustomListItems"]):
                bookmarks.append(Bookmark(data=item["Bookmark"]).parse())
        except:
            pass
        try:
            for n, item in enumerate(plist["Applications"]["CustomListItems"]):
                aliases.append(Alias(data=item["Alias"]).parse())
        except:
            pass
        try:
            for n, item in enumerate(plist["Documents"]["CustomListItems"]):
                aliases.append(Alias(data=item["Alias"]).parse())
        except:
            pass
        try:
            for n, item in enumerate(plist["Servers"]["CustomListItems"]):
                aliases.append(Alias(data=item["Alias"]).parse())
        except:
            pass
        return bookmarks, aliases

    def parseMSOffice2016Plist(self, mru_file):
        bookmarks = []
        try:
            plistfile = plistlib.readPlist(mru_file)
            for n, item in enumerate(plistfile):
                try:
                    bookmarkdata = plistfile[item]["kBookmarkDataKey"]
                    for attr, blob in bookmarkdata.__dict__.items():
                        try:
                            bookmarks.append(Bookmark(data=blob).parse())
                        except:
                            pass
                except:
                    pass
        except:
            pass
        return bookmarks

    def parseMSOffice2011Plist(self, mru_file):
        plist = self.load_bplist(mru_file)
        if plist == None:
            return []
        aliases = []
        try:
            for n, item in enumerate(plist["14\File MRU\MSWD"]):
                aliases.append(Alias(data=item["File Alias"]).parse())
        except:
            pass
        try:
            for n, item in enumerate(plist["14\File MRU\XCEL"]):
                aliases.append(Alias(data=item["File Alias"]).parse())
        except:
            pass
        try:
            for n, item in enumerate(plist["14\File MRU\PPT3"]):
                aliases.append(Alias(data=item["File Alias"]).parse())
        except:
            pass
        return aliases

    def spotlightShortcuts(self, mru_file):
        data = {}
        try:
            plistfile = plistlib.readPlist(mru_file)
            for n, item in enumerate(plistfile):
                try:
                    data["display_name"] = plistfile[item]["DISPLAY_NAME"]
                except:
                    pass
                try:
                    data["lastUsed_timestamp"] = str(plistfile[item]["LAST_USED"])
                except:
                    pass
                try:
                    data["url"] = plistfile[item]["URL"]
                except:
                    pass
        except Exception as e:
            print(e)
            pass
        return data

    def build_header(self, mru_file):
        splitter = "=" * 90
        header = splitter + "\n"
        header += mru_file + "\n"
        header += splitter + "\n\n"
        return header

    def format_bookmarks(self, bookmarks):
        if bookmarks != None and isinstance(bookmarks, list) and len(bookmarks) > 0:
            formatters = []
            for bookmark in bookmarks:
                formatter = Formatter()
                formatter.add_value("creation_date", bookmark.targetCreationDate())
                formatter.add_value("file_path", "/" + "/".join(bookmark.targetPath()))
                formatter.add_value("creator", bookmark.creatorUsername())
                formatter.add_value("creator_UID", bookmark.creatorUID())
                # formatter.add_value("volumePath", bookmark.volumePath())
                # formatter.add_value("volumeName", bookmark.volumeName())
                # formatter.add_value("volumeFlag", bookmark.volumeFlag())
                # formatter.add_value("volumeIsRootFs", bookmark.volumeIsRootFs())
                # formatter.add_value("uuid,", bookmark.uuid())
                # formatter.add_value("volumeSize", bookmark.volumeSize())
                # formatter.add_value("volumeCreationDate", bookmark.volumeCreationDate())
                # formatter.add_value("volumeUrl", bookmark.volumeUrl())
                # formatter.add_value("volumeBookmark", bookmark.volumeBookmark())
                # formatter.add_value("volumeMountPoint", bookmark.volumeMountPoint())
                # formatter.add_value("securityExtention1", bookmark.securityExtention1())
                # formatter.add_value("securityExtention2", bookmark.securityExtention2())
                # formatter.add_value("targetCNIDPath", bookmark.targetCNIDPath())
                # formatter.add_value("containingFolderIndex", bookmark.containingFolderIndex())
                # formatter.add_value("targetFlags", bookmark.targetFlags())
                # formatter.add_value("targetFileName", bookmark.targetFileName())
                # formatter.add_value("unknown0x1003", bookmark.unknown0x1003())
                # formatter.add_value("unknown0x1054", bookmark.unknown0x1054())
                # formatter.add_value("unknown0x1055", bookmark.unknown0x1055())
                # formatter.add_value("unknown0x1056", bookmark.unknown0x1056())
                # formatter.add_value("unknown0x1101", bookmark.unknown0x1101())
                # formatter.add_value("unknown0x1102", bookmark.unknown0x1102())
                # formatter.add_value("tocPath", bookmark.tocPath())
                # formatter.add_value("unknown0x2070", bookmark.unknown0x2070())
                # formatter.add_value("fileReferenceFlag", bookmark.fileReferenceFlag())
                # formatter.add_value("creationOptions", bookmark.creationOptions())
                # formatter.add_value("urlLengthArray", bookmark.urlLengthArray())
                # formatter.add_value("localized", bookmark.localized())
                # formatter.add_value("unknown0xf022", bookmark.unknown0xf022())
                formatters.append(formatter)
            return formatters
        return []

    def format_aliases(self, aliases):
        if aliases != None and isinstance(aliases, list) and len(aliases) > 0:
            formatters = []
            for alias in aliases:
                formatter = Formatter()
                formatter.add_value("creation_date", alias.creation_date())
                formatter.add_value("file_path", "/" + alias.posix_path())
                formatter.add_value("creator_code", alias.creator_code())
                # formatter.add_value("name", alias.name())
                # formatter.add_value("fs_type", alias.fs_type())
                # formatter.add_value("disk_type", alias.disk_type())
                # formatter.add_value("attribute_flags", alias.attribute_flags())
                # formatter.add_value("fs_id", alias.fs_id())
                # formatter.add_value("appleshare_info", alias.appleshare_info())
                # formatter.add_value("driver_name", alias.driver_name())
                # formatter.add_value("disk_image_alias", alias.disk_image_alias())
                # formatter.add_value("dialup_info", alias.dialup_info())
                # formatter.add_value("network_mount_info", alias.network_mount_info())
                # formatter.add_value("kind", alias.kind())
                # formatter.add_value("filename", alias.filename())
                # formatter.add_value("folder_cnid", alias.folder_cnid())
                # formatter.add_value("cnid", alias.cnid())
                # formatter.add_value("creation_date", alias.creation_date())
                # formatter.add_value("type_code", alias.type_code())
                # formatter.add_value("levels_from", alias.levels_from())
                # formatter.add_value("levels_to", alias.levels_to())
                # formatter.add_value("folder_name", alias.folder_name())
                # formatter.add_value("cnid_path", alias.cnid_path())
                # formatter.add_value("carbon_path", alias.carbon_path())
                # formatter.add_value("posix_path", alias.posix_path())
                # formatter.add_value("user_home_prefix_len", alias.user_home_prefix_len())
                formatters.append(formatter)
            return formatters
        return []

    def format_dict_data(self, dict_data):
        if dict_data != None and isinstance(dict_data, dict) and len(dict_data) > 0:
            fmts = []
            fmt = Formatter()
            for k, v in dict_data.items():
                fmt.add_value(k, v)
            fmts.append(fmt)
            return fmts
        return []

    def format_bookmarks_alias(self, bookmarks, aliases):
        fmts = []
        if len(bookmarks) > 0:
            fmts.extend(self.format_bookmarks(bookmarks))
        if len(aliases) > 0:
            fmts.extend(self.format_aliases(aliases))
        return fmts

    def find_target_paths(self):
        targets = []
        glob_list = [
            "Users/*/Library/Preferences/*.LSSharedFileList.plist",
            "Users/*/Library/Preferences/com.apple.finder.plist",
            "Users/*/Library/Preferences/com.apple.recentitems.plist",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/*.sfl",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/RecentApplications.sfl",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/RecentDocuments.sfl",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/RecentServers.sfl",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/RecentHosts.sfl",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/*.sfl2",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.RecentApplications.sfl2",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.RecentDocuments.sfl2",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.RecentServers.sfl2",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.RecentHosts.sfl2",
            "Users/*/Library/Preferences/com.microsoft.office.plist",
            "Users/*/Library/Containers/com.microsoft.*/Data/Library/Preferences/com.microsoft.*.securebookmarks.plist",
            "Users/*/Library/Application Support/com.apple.spotlight.Shortcuts",
            "Users/*/Library/Preferences/com.apple.sidebarlists.plist",
            "Users/*/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.FavoriteVolumes.sfl2"
        ]
        for gl in glob_list:
            gl = os.path.join(self.evidence_root, gl)
            for g in glob.glob(gl):
                self.log.debug("target : " + g)
            targets.extend(glob.glob(gl))
        return targets

    def parse(self):
        self.log.debug("[+] Processing Mac MRU")
        for target_path in self.find_target_paths():
            f = os.path.basename(target_path)

            fmts = []
            if self.isMatch(f, ['*.sfl']) and not self.isMatch(f, ['*Favorite*.sfl', '*Project*.sfl',
                                                                   '*iCloudItems*.sfl'], orMatch=True):
                fmts = self.format_bookmarks(self.parseSFL(target_path))
            elif self.isMatch(f, ['*.sfl2']) and not self.isMatch(f, ['*Favorite*.sfl2', '*Project*.sfl2',
                                                                      '*iCloudItems*.sfl2'], orMatch=True):
                fmts = self.format_bookmarks(self.parseSFL2(target_path))
            elif self.isMatch(f, ['*FavoriteVolumes.sfl2']):
                fmts = self.format_bookmarks(self.parseSFL2_FavoriteVolumes(target_path))
            elif self.isMatch(f, ['*.LSSharedFileList.plist']):
                fmts = self.format_bookmarks(self.parseLSSharedFileListPlist(target_path))
            elif f == "com.apple.finder.plist":
                bookmarks, aliases = self.parseFinderPlist(target_path)
                fmts = self.format_bookmarks_alias(bookmarks, aliases)
            elif f == "com.apple.sidebarlists.plist":
                fmts = self.format_aliases(self.parseSidebarlistsPlist(target_path))
            elif f == "com.apple.recentitems.plist":
                bookmarks, aliases = self.parseRecentItemsPlist(target_path)
                fmts = self.format_bookmarks_alias(bookmarks, aliases)
            elif f.endswith(".securebookmarks.plist"):
                fmts = self.format_bookmarks(self.parseMSOffice2016Plist(target_path))
            elif f == "com.microsoft.office.plist":
                fmts = self.format_aliases(self.parseMSOffice2011Plist(target_path))
            elif f == "com.apple.spotlight.Shortcuts":
                fmts = self.format_dict_data(self.spotlightShortcuts(target_path))
            else:
                continue

            if len(fmts) > 0:
                self.log.debug("[+] now parsing " + str(target_path))
                self.write(self.build_header(target_path))
                for fmt in fmts:
                    self.write(fmt.format() + "\n")
        self.write("\n")

def usage():
    print("[+] parse plists relates to mru files (most rencently used file) .")
    print("[+] you need to specify root directory to start parsing,")
    print("[+] and output directory to write result.")


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-r', '--root',
                           help="please input the evidence root path."
                                "e.g. '/Volumes/disk3s1/' (mounted volume)",
                           type=str,
                           default='/Volumes/disk3s1/')
    argparser.add_argument('-o', '--output',
                           help="please input the output path. default is current directory",
                           type=str,
                           default=os.getcwd())
    argparser.add_argument('-q', '--quiet',
                           help="suppress verbose output.",
                           action='store_const',
                           const=True,
                           default=False)

    args = argparser.parse_args()

    if not args.quiet:
        usage()

    logger = logging.getLogger()
    Mru(args.root, args.output, logger).parse()
