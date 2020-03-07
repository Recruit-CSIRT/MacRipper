# -*- coding: utf-8 -*-
import os
import pathlib

class SpotlightParserOutputIterator:

    def __init__(self, reader, attrs):
        self.reader = reader
        self.data = {}
        self.attrs = attrs
        self.have_read = []
        self.sep_of_item = "------------------------------------------------------------"
        self.sep_of_key_and_value_of_an_item = " -->"
        # DirtyHack. First one line is item separator. We just skip it.
        self.reader.readline()

    def has_next(self):
        self.have_read = []
        # For this case:
        # <sep_of_items>
        # <key> --> <value-start
        # ~
        # ~
        # value-end>
        # <key> --> <value>
        is_reading_value = False
        reading_data = ""
        while True:

            line = self.reader.readline()
            if len(line) == 0:
                if is_reading_value:
                    self.have_read.append(reading_data)
                    return True
                return False

            line = line.strip().decode('utf-8')
            if self.sep_of_item in line:
                if is_reading_value:
                    self.have_read.append(reading_data)
                break

            elif self.sep_of_key_and_value_of_an_item in line:
                if is_reading_value:
                    self.have_read.append(reading_data)
                    reading_data = ""

                is_reading_value = True
                reading_data += line

            else:
                if is_reading_value:
                    reading_data += line
                pass

        return True

    def _parse_data_which_have_read(self):
        for line in self.have_read:
            (k, v) = line.split(self.sep_of_key_and_value_of_an_item)
            k = k.rstrip()
            v = v.lstrip()
            self.data[k] = v
        self.have_read = []

    def next(self):
        self._parse_data_which_have_read()
        data = self.data
        self.data = {}
        return data


class SpotlightUtil:

    # mapping of inode to file path.
    _inode_mapping = None

    @staticmethod
    def format_attributes(attrs, data):
        for key in data.keys():
            if 'Date' in key or 'date' in key:
                if ", " in data[key]:
                    data[key] = data[key].split(", ")
        for attr in attrs:
            if attr not in data.keys():
                data[attr] = "(null)"
        return data

    @staticmethod
    def spotlight_store_db_path(log, root):
        base_dirs = []
        candidates = [
            ".Spotlight-V100/Store-V2",
            "System/Volumes/Data/.Spotlight-V100/Store-V2"
        ]
        for cand in candidates:
            path = os.path.join(root, cand)
            path = path.replace("\\ ", " ")
            log.debug("path : " + path)
            if os.path.isdir(path):
                log.debug("path is dir : " + path)
                for d in os.listdir(path):
                    path2 = os.path.join(path, d)
                    log.debug("candidate : " + path2)
                    if os.path.isdir(path2):
                        log.debug("candidate is dir : " + path2)
                        base_dirs.append(path2)

        for d in base_dirs:
            log.debug("finding store.db in : " + str(d))
            for v in ["store.db", ".store.db"]:
                file_path = os.path.join(str(d), v)
                if os.path.isfile(file_path):
                    log.debug("store.db found at : " + str(file_path))
                    return file_path
        raise Exception("spotlight store.db is not exists.")

    @staticmethod
    def _load_inode_and_file_path_mapping(input_path):
        kv = {}
        with open(input_path, mode="rb") as reader:
            # ignore the header, first one line.
            reader.readline()

            for byte_line in reader:
                line = byte_line.decode('utf-8')
                words = line.split('\t', 1)
                if len(words) > 1:
                    inode, file_path = words
                    file_path = file_path.rstrip()
                    kv[inode] = file_path
        return kv

    @staticmethod
    def get_file_path_by_inode(inode, input_file_path):
        if not SpotlightUtil._inode_mapping:
            kv = SpotlightUtil._load_inode_and_file_path_mapping(input_file_path)
            SpotlightUtil._inode_mapping = kv
        if type(inode) is int:
            inode = str(inode)
        if inode in SpotlightUtil._inode_mapping.keys():
            return SpotlightUtil._inode_mapping[inode]
        return "unknown (file path not found)"
