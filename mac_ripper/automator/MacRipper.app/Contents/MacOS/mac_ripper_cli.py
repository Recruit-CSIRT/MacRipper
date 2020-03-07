# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
from datetime import datetime
from modules.utils.bootstrap import LoggingConfig
import os
import logging
from logging import FileHandler
import traceback
import pytz
import sys
import inquirer

from modules.mru.mac_mru import Mru
from modules.plist.finder import Finder
from modules.plist.persistence import Persistence
from modules.spotlight.app_usage import AppUsage, AppUsageBinary
from modules.spotlight.downloaded import DownloadedFiles, DownloadedFilesBinary
from modules.spotlight.last_used import LastUsed, LastUsedBinary
from modules.spotlight.spotlight_all_files import SpotlightAllFiles, SpotlightAllFilesBinary
from modules.sqlite.gatekeeper import GateKeeper
from modules.unifiedlog.unified_log import UnifiedLogs


class BaseCli:
    def __init__(self, logger):
        self.log = logger
        self._name = ""

    def name(self):
        return self._name

    def try_run(self, module_name, parser):
        self.start_info(module_name)
        try:
            parser.parse()
        except Exception as e:
            self.log.error(str(traceback.format_exc()))
        self.end_info(module_name)

    def start_info(self, module_name):
        self.log.info("[+] start " + str(module_name) + " module ....")

    def end_info(self, module_name):
        self.log.info("[+] finish " + str(module_name) + " module")


class CliPlist(BaseCli):
    def __init__(self, log):
        super().__init__(log)
        self._name = "Plist"

    def parse(self, evidence_root_path, output_path, *args):
        self.try_run("Persistence", Persistence(evidence_root_path, output_path, self.log))
        self.try_run("Finder", Finder(evidence_root_path, output_path, self.log))


class CliSpotlight(BaseCli):
    def __init__(self, log, use_mac_cmd, use_all_module):
        super().__init__(log)
        self._use_mac_cmd = use_mac_cmd
        self._use_all_module = use_all_module
        self._name = "Spotlight"

    def parse(self, root, out, tz, *args):
        if self._use_mac_cmd:
            self._run(root, out, tz)
            if self._use_all_module:
                self._run_all_module(root, out, tz)
        else:
            self._run_binarily(root, out, tz)
            if self._use_all_module:
                self._run_all_module_binarily(root, out, tz)

    def _run(self, root, out, tz):
        self.try_run("Downloaded Files", DownloadedFiles(root, out, tz, self.log))
        self.try_run("App Usage", AppUsage(root, out, tz, self.log))
        self.try_run("Last Used", LastUsed(root, out, tz, self.log))

    def _run_binarily(self, root, out, tz):
        self.try_run("Downloaded Files Binary", DownloadedFilesBinary(root, out, tz, self.log))
        self.try_run("App Usage Binary", AppUsageBinary(root, out, tz, self.log))
        self.try_run("Last Used Binary", LastUsedBinary(root, out, tz, self.log))

    def _run_all_module(self, root, out, tz):
        self.try_run("Spotlight All Files", SpotlightAllFiles(root, out, tz, self.log))

    def _run_all_module_binarily(self, root, out, tz):
        self.try_run("Spotlight All Files Binary", SpotlightAllFilesBinary(root, out, tz, self.log))


class CliSqlite(BaseCli):
    def __init__(self, log):
        super().__init__(log)
        self._name = "Sqlite"

    def parse(self, evidence_root_path, output_path, *args):
        self.try_run("Gatekeeper", GateKeeper(evidence_root_path, output_path, self.log))


class CliMru(BaseCli):
    def __init__(self, log):
        super().__init__(log)
        self._name = "Mru"

    def parse(self, evidence_root_path, output_path, *args):
        self.try_run("Mru", Mru(evidence_root_path, output_path, self.log))


class CliUnifiedLogs(BaseCli):
    def __init__(self, log):
        super().__init__(log)
        self._name = "UnifiedLogs"

    def parse(self, evidence_root_path, output_path, tz, *args):
        self.start_info("Unified log")
        try:
            unified_logs = UnifiedLogs(evidence_root_path, output_path, self.log)
            unified_logs.parse("", "", "all", "csv", tz, "")
        except Exception as e:
            LOG.error(str(traceback.format_exc()))
        self.end_info("Unified log")


def banner(log):
    log.info("""                                
               ____ ___  ____ ______   _____(_)___  ____  ___  _____
              / __ `__ \/ __ `/ ___/  / ___/ / __ \/ __ \/ _ \/ ___/
             / / / / / / /_/ / /__   / /  / / /_/ / /_/ /  __/ /    
            /_/ /_/ /_/\__,_/\___/  /_/  /_/ .___/ .___/\___/_/     
                                           /_/   /_/              
                                                         ver. 0.1.0 """)


def is_arguments_valid(log, root, output, timezone):
    if type(root) is not str:
        log.error("[-] Evidence root path must be string")
        return False
    if len(root) == 0:
        log.error("[-] Evidence root path must not be empty")
        return False
    if not os.path.isdir(root):
        log.error("[-] Evidence root path must be directory: " + root)
        return False
    if type(output) is not str:
        log.error("[-] Output path path must be string")
        return False
    if len(output) == 0:
        log.error("[-] Output path must not be empty")
        return False
    if not os.path.isdir(output):
        log.error("[-] Output path must be directory: " + output)
        return False
    if timezone not in pytz.all_timezones:
        log.error("[-] Timezone is invalid: " + timezone)
        return False
    return True


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-r', '--root',
                             help="please input evidence root path:e.g. /Volumes/disk3s1/", type=str)
    args_parser.add_argument("-o", "--output",
                             help="please input the output path.", type=str, default=os.getcwd())
    args_parser.add_argument('-t', '--timezone',
                             help="please input timezone for unifid log and spotlight module. :default Asia/Tokyo",
                             type=str, default="Asia/Tokyo")
    args_parser.add_argument('-c', '--command',
                             help="spotlight module's option. parse store.db using Mac OS default command.",
                             action='store_true', default=False)
    args_parser.add_argument('-a', '--all_files',
                             help="spotlight module's option. parse all files.", action='store_true', default=False)
    args = args_parser.parse_args()
    root = args.root
    out_dir = args.output
    timezone = args.timezone
    use_command = args.command
    use_all_files = args.all_files

    out_file_name = ("mac_ripper_cli_{0:%Y_%m_%d_%H_%M_%S}.log".format(datetime.now()))
    out_file_path = os.path.join(out_dir, out_file_name)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    log = logging.getLogger(__name__)
    log.setLevel(LoggingConfig.level)
    file_handler = FileHandler(out_file_path, 'a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(LoggingConfig.formatter)
    log.addHandler(file_handler)

    banner(log)
    if not is_arguments_valid(log, root, out_dir, timezone):
        log.info("[+] Mac Ripper Cli finished.")
        sys.exit(1)
    log.info("[+] EVIDENCE ROOT PATH : " + root)
    log.info("[+] OUTPUT PATH : " + out_dir)
    log.info("[+] TIMEZONE : " + timezone)

    q = [
        inquirer.Checkbox('parsers',
                          message="実行モジュールを選択して下さい（右矢印キーで選択、左矢印キーで解除）",
                          choices=['Plist', 'Mru', 'Sqlite', 'Unified log', 'Spotlight'])
    ]
    selected_parser_names = inquirer.prompt(q)["parsers"]
    print(selected_parser_names)
    parsers = []
    for selected in selected_parser_names:
        if selected == "Plist":
            parsers.append(CliPlist(log))
        elif selected == "Mru":
            parsers.append(CliMru(log))
        elif selected == "Sqlite":
            parsers.append(CliSqlite(log))
        elif selected == "Unified log":
            parsers.append(CliUnifiedLogs(log))
        elif selected == "Spotlight":
            parsers.append(CliSpotlight(log, use_command, use_all_files))

    log.info("[+] Selected Parsers : " + ", ".join(list(map(lambda x: x.name(), parsers))))
    for p in parsers:
        try:
            p.parse(root, out_dir, timezone)
        except Exception as e:
            log.error(str(traceback.format_exc()))
    log.info("[+] Mac Ripper Cli finished.")

