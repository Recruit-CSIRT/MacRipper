# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import plistlib
import os
from pathlib import Path


class AgentPersistence:
    def __init__(self, log):
        self.log = log

    def parse(self, evidence_root, output_folder_name):
        user_dirs = []
        file_paths = []
        output = []

        sys_la_dir = os.path.join(evidence_root, "System/Library/LaunchAgents/")
        sys_la_path = Path(sys_la_dir)
        lib_la_dir = os.path.join(evidence_root, "Library/LaunchAgents/")
        lib_la_path = Path(lib_la_dir)
        sys_la_files = list(sys_la_path.glob("*"))
        lib_la_files = list(lib_la_path.glob("*"))
        file_paths.extend(sys_la_files)
        file_paths.extend(lib_la_files)

        user_dir_path = os.path.join(evidence_root, "Users/")
        for d in os.listdir(user_dir_path):
            if os.path.isdir(user_dir_path + d):  # パスに取り出したオブジェクトを足してフルパスに
                user_dirs.append(d)

        for user_dir in user_dirs:
            users_la_dir = os.path.join(evidence_root, f"Users/{user_dir}/Library/LaunchAgents/")
            users_la_path = Path(users_la_dir)
            user_la_files = list(users_la_path.glob("*"))
            file_paths.extend(user_la_files)

        output.append("[+]persistence for MacOS Ver.0.1")
        output.append("[+]LaunchAgents\n")
        output.append("[+]This tool will parse the following.")
        output.append("[+]このツールは下記のファイルをパースし、自動実行登録されているプログラムのラベル名とパスを出力します")
        output.append("/System/Library/LaunchAgents/*")
        output.append("/Library/LaunchAgents/*")
        output.append("/Users/$User/Library/LaunchAgents/*\n\n")

        self.log.debug("\n[+]LaunchAgents")
        self.log.debug("[+]start processing...")
        for file_path in file_paths:
            with open(str(file_path), 'rb') as file:
                output.append("----------------------------------------------------------")
                output.append("File path on your machine(not true path):\n{}\n".format(file_path))
                self.log.debug("[+]now processing -> {}".format("File path on your machine(not true path): " + str(file_path)))
                cnt = plistlib.load(file)
                if "Label" in cnt:
                    output.append("Program Label: " + "\n" + cnt["Label"] + "\n")
                else:
                    output.append("Program Path: \n" + "Error: Program cannot find the label of program.\n")
                    self.log.warning("[-] Program cannot found the label of persistence program.")
                    self.log.warning("[-] File path on your machine(not true path):\n{}".format(file_path))
                if "Program" in cnt:
                    output.append("Program Path: " + "\n" + cnt["Program"]+ "\n")
                elif "ProgramArguments" in cnt:
                    output.append("Program Path: " + "\n" + cnt["ProgramArguments"][0] + "\n")
                else:
                    output.append("Program Path: \n" + "Error: Program cannot find the path of program.\n")
                    self.log.warning("[-] Program cannot found the path of Persistence program.")
                    self.log.warning("[-] File path on your machine(not true path):\n{}".format(file_path))

        str_ = u'\n'.join(output)
        out_file_path = "{}/".format(output_folder_name) + "Persistence_LaunchAgents.txt"
        with open(out_file_path, 'wt', encoding='utf_8_sig') as f:
            f.write(str_)


class DaemonPersistentce:

    def __init__(self, log):
        self.log = log

    def parse(self, evidence_root, output_folder_name):
        userdirs = []
        file_paths = []
        output = []

        sys_ld_dir = os.path.join(evidence_root, "System/Library/LaunchDaemons/")
        sys_ld_path = Path(sys_ld_dir)
        lib_ld_dir = os.path.join(evidence_root, "Library/LaunchDaemons/")
        lib_ld_path = Path(lib_ld_dir)
        sys_ld_files = list(sys_ld_path.glob("*"))
        lib_ld_files = list(lib_ld_path.glob("*"))
        file_paths.extend(sys_ld_files)
        file_paths.extend(lib_ld_files)
        userdir_dir = os.path.join(evidence_root, "Users/")
        userdir_path = Path(userdir_dir)

        for d in os.listdir(userdir_path):
            if os.path.isdir(str(userdir_path) + d):  # パスに取り出したオブジェクトを足してフルパスに
                userdirs.append(d)

        for userdir in userdirs:
            users_ld_path = Path("/Users/{}/Library/LaunchDaemons/".format(userdir))
            user_ld_files = list(users_ld_path.glob("*"))
            file_paths.extend(user_ld_files)

        output.append("[+]persistence for MacOS Ver.0.1")
        output.append("[+]LaunchDaemons\n")
        output.append("[+]This tool will parse the following.")
        output.append("[+]このツールは下記のファイルをパースし、自動実行登録されているプログラムのラベル名とパスを出力します")
        output.append("/System/Library/LaunchDaemons/*")
        output.append("/Library/LaunchDaemons/*\n\n")

        self.log.debug("\n[+]LaunchDaemons")
        self.log.debug("[+]start processing...")
        for file_path in file_paths:
            with open(str(file_path), 'rb') as file:
                output.append("----------------------------------------------------------")
                output.append("File path on your machine(not true path):\n{}\n".format(file_path))
                self.log.debug("[+]now processing -> {}".format("File path on your machine(not true path): " + str(file_path)))
                cnt = plistlib.load(file)
                if "Label" in cnt:
                    output.append("Program Label: \n" + cnt["Label"] + "\n")
                else:
                    output.append("Program Path: \n" + "Error: Program cannot find the label of program.\n")
                    self.log.warning("[-] Program cannot found the label of persistence program.")
                    self.log.warning("[-] File path on your machine(not true path):\n{}".format(file_path))
                if "Program" in cnt:
                    output.append("Program Path: \n" + cnt["Program"]+ "\n")
                elif "ProgramArguments" in cnt:
                    output.append("Program Path: \n" + cnt["ProgramArguments"][0] + "\n")
                else:
                    output.append("Program Path: \n" + "Error: Program cannot find the path of program.\n")
                    self.log.warning("[-] Program cannot find the path of program.")
                    self.log.warning("[-] File path on your machine(not true path):\n{}".format(file_path))

        str_ = u'\n'.join(output)
        self.log.debug(str_)
        out_file_path = "{}/".format(output_folder_name) + "Persistence_LaunchDaemons.txt"
        with open(out_file_path, 'wt', encoding='utf_8_sig') as f:
            f.write(str_)


class Persistence:

    def __init__(self, evidence_root="", output_path="", log=None):
        self.evidence_root = evidence_root
        self.output_path = output_path
        self.log = log
        self.persistences = []
        self.persistences.append(AgentPersistence(self.log))
        self.persistences.append(DaemonPersistentce(self.log))

    def parse(self):
        for persistence in self.persistences:
            persistence.parse(self.evidence_root, self.output_path)


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

    persistence = Persistence(args.root, args.output)
    persistence.parse()

#TODO:デフォルトを省く
