# -*- coding: utf-8 -*-
from __future__ import print_function

import subprocess
import shlex
import os
from abc import abstractmethod, ABC
from modules.spotlight.mac_command_util import MacCommandUtil
from modules.spotlight.myutil import strftime
from modules.spotlight.mdls_util import MdlsUtil
from modules.spotlight.spotlight_parser_utils import SpotlightParserOutputIterator, SpotlightUtil
from modules.spotlight.vendor.spotlight_parser import ProcessStoreDb
import csv
import traceback


class BaseSpotlight:

    def __init__(self, root='/', output_folder='./output', timezone="asia/tokyo", log=None):
        self._root = root
        self._output_folder = output_folder
        self.timezone = timezone
        self.NULL_VALUE = '(null)'
        self.log = log

    @abstractmethod
    def is_target(self, data):
        return False

    @abstractmethod
    def attrs(self):
        return []

    @abstractmethod
    def output_file_name(self):
        return "base_spotlight.csv"

    @abstractmethod
    def find_cmd(self):
        return ""

    def output_dir(self):
        return self._output_folder

    def evidence_root(self):
        return self._root.replace(" ", "\\ ")

    def find_target_file_paths(self):
        self.log.debug(self.find_cmd())
        cmd_res = subprocess.Popen(shlex.split(self.find_cmd()), stdout=subprocess.PIPE)
        file_paths = cmd_res.stdout.read().decode().splitlines()
        return file_paths

    def get_file_meta_info(self, attrs, file_path, encoding='utf8'):
        mdls_util = MdlsUtil(attrs, file_path, MacCommandUtil())
        return mdls_util.execute().as_dict()

    def add_optional_attribute(self, data, file_path):
        data["FilePath"] = file_path
        return data

    def create_output_dir(self):
        if not os.path.exists(self.output_dir()):
            os.makedirs(self.output_dir())

    def parse(self):
        self.create_output_dir()

        file = open(self.abs_output_file_path(), mode="w", encoding='utf_8_sig')
        writer = csv.writer(file)
        # write csv headers.
        writer.writerow(self.attrs())

        self._run(writer)
        file.close()

    def _run(self, writer):
        attrs = self.attrs()
        for file_path in self.find_target_file_paths():
            self.log.debug('[+]now processing ' + str(file_path))
            data = self.get_file_meta_info(attrs, file_path)
            data = self.add_optional_attribute(data, file_path)
            if self.is_target(data):
                writer.writerow(self.convert_to_array(data, attrs))

    def convert_to_array(self, data, attrs):
        res = []
        for attr in attrs:
            if data[attr] == self.NULL_VALUE:
                res.append(data[attr])
            elif type(data[attr]) is str:
                if self.is_date_type(attr):
                    try:
                        data[attr] = self.strftime(data[attr])
                    except Exception as e:
                        self.log.error("attr is : " + attr)
                        self.log.error(str(traceback.format_exc()))
                        data[attr] = "(error)"
                res.append(data[attr])
            elif type(data[attr]) is list:
                if self.is_date_type(attr):
                    try:
                        data[attr] = map(lambda t: self.strftime(t), data[attr])
                    except Exception as e:
                        self.log.error("attr is : " + attr)
                        self.log.error(str(traceback.format_exc()))
                        data[attr] = ["(error)"]
                res.append(",".join(data[attr]))
        return res

    def is_date_type(self, attr):
        return 'Date' in attr or 'date' in attr

    def strftime(self, date):
        input_format = "%Y-%m-%d %H:%M:%S %z"
        output_format = "%Y-%m-%d %H:%M:%S"
        return strftime(date, input_format, output_format, self.timezone)

    def abs_output_file_path(self):
        return os.path.join(self.output_dir(), self.output_file_name())


class BaseBinarySpotlight(BaseSpotlight, ABC):

    def _run(self, writer):
        self.parse_spotlight_binary()
        reader = open(self.spotlight_parser_output_path(), mode="rb")
        attrs = self.attrs()
        it = SpotlightParserOutputIterator(reader, attrs)
        while it.has_next():
            data = it.next()
            data = SpotlightUtil.format_attributes(attrs, data)
            file_path = self.convert_inode_to_file_path(data["Inode_Num"])
            self.log.debug('[+] now processing ' + str(file_path))
            data = self.add_optional_attribute(data, file_path)
            if not self.is_target(data):
                continue
            writer.writerow(self.convert_to_array(data, attrs))
        reader.close()
        self.clear_temporary_files()

    def clear_temporary_files(self):
        targets = [
            self.spotlight_parser_output_path(),
            os.path.join(self.output_dir(), 'spotlight-store_fullpaths.csv')
        ]
        for t in targets:
            if os.path.isfile(t):
                os.remove(t)

    def strftime(self, date):
        # remove HHHH:MM:SS.ssss pattern by split() function.
        date = date.split(".")[0]
        date += " +0000"
        input_format = "%Y-%m-%d %H:%M:%S %z"
        output_format = "%Y-%m-%d %H:%M:%S"
        return strftime(date, input_format, output_format, self.timezone)

    def add_optional_attribute(self, data, file_path):
        data["FilePath"] = file_path
        return data

    def spotlight_parser_output_path(self):
        return os.path.join(self.output_dir(), self.spotlight_parser_output_file_name_prefix() + "_data.txt")

    def spotlight_parser_output_file_name_prefix(self):
        return "spotlight-store"

    def spotlight_store_db_path(self):
        return SpotlightUtil.spotlight_store_db_path(self.log, self.evidence_root())

    def parse_spotlight_binary(self):
        abs_in_path = self.spotlight_store_db_path()
        abs_out_path = self.output_dir()
        prefix = self.spotlight_parser_output_file_name_prefix()
        ProcessStoreDb(abs_in_path, abs_out_path, prefix)

    def convert_inode_to_file_path(self, inode):
        if inode == self.NULL_VALUE:
            return self.NULL_VALUE
        input_file = os.path.join(self.output_dir(), 'spotlight-store_fullpaths.csv')
        return SpotlightUtil.get_file_path_by_inode(inode, input_file)
