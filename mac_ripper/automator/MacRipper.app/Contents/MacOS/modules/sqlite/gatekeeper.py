from __future__ import print_function
import argparse
import csv
import os
import sqlite3


class GateKeeper:

    def __init__(self, evidence_root, output_path, log):
        """Init function.

        Args:
            evidence_root: The evidence root directory path you mounted. e.g. /Volumes/disk3s1/.
            output_path: The output directory path.
        """
        self.log = log
        self.evidence_root = evidence_root
        self.output_file_name = os.path.join(output_path, 'gatekeeper.csv')
        self.users_db_list = {}
        self.logs = []
        self.db_path = 'Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2'


    def search(self):
        """search users gatekeeer sqlite db.

        Args:
            -
        """

        # QuarantineEventsV2の場所を探して、リストとして確保する

        # Usersディレクトリ以下のQuarantineEventsV2を探していく。rootとは別。
        users_dir_path = os.path.join(self.evidence_root, "Users/")

        self.log.debug("[+] Searching user directory and Gatakeeper db")
        for user_dir in os.listdir(users_dir_path):

            # パスに取り出したオブジェクトを足してフルパスに
            user_full_dir_path = os.path.join(users_dir_path, user_dir)

            if os.path.isdir(user_full_dir_path):
                self.users_db_list[user_dir] = {
                    'db': os.path.join(user_full_dir_path, self.db_path),
                    'exists': os.path.isfile(os.path.join(user_full_dir_path, self.db_path))
                }

        self.log.debug("=====")
        self.log.debug(self.evidence_root)
        self.log.debug(self.db_path)

        # rootのUsersディレクトリ以下のQuarantineEventsV2を探していく
        self.users_db_list['root'] = {
            'db': os.path.join(self.evidence_root, f"var/root/{self.db_path}"),
            'exists': os.path.isfile(os.path.join(self.evidence_root, f"var/root/{self.db_path}"))
        }

        for key, val in self.users_db_list.items():
            if val.get('exists'):
                self.log.debug(f"[+] User: {key}, DB: {val.get('db')}")

    def extract_gate_keeper_log(self, user="", db_path=""):
        """extract data from users gatekeeper sqlite3 db

        Args:
            user: username who have gatekeeper sqlite3 db.
            db_path: user's gatekeeper sqlite3 db path.
        """

        self.log.debug(f"[+] Processing to extract {db_path}")

        # Connect to SQLite DB
        connect = sqlite3.connect(db_path)
        c = connect.cursor()
        self.log.debug(f"###############{db_path}")

        # table が存在していない場合はスルーする。
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='LSQuarantineEvent'")
        cnt = c.fetchone()
        if cnt[0] == 0 or cnt[0] is None:
            return []

        # Query DB for Column Name and Date of IME Lexicon db
        # 生成物の１行目はカラム名にしたいのでここで取得して、保存先のリストに入れる。
        c.execute('pragma table_info(LSQuarantineEvent)')
        tuple_columns = c.fetchall()
        list_column_names = [column[1] for column in tuple_columns]

        # LSQuarantineTimeStampは、時間に変更する
        query_column = [name if name != "LSQuarantineTimeStamp" else f"datetime({name} + 978307200, 'unixepoch', 'localtime') as LSQuarantineTimeStamp" for name in list_column_names ]

        list_column_names.append('User')
        list_data = [list_column_names]

        # Extract DB contents & Convert from HEX to Japanese
        c.execute('select ' + ", ".join(query_column) + ' from LSQuarantineEvent')
        tuple_data = c.fetchall()
        for tuple_recode in tuple_data:
            list_recode = [val for index, val in enumerate(list(tuple_recode))]
            list_recode.append(user)
            list_data.append(list_recode)
        return list_data

    def parse(self):
        """extract all users gatekeeper sqlite3 db.

        Args:
            -
        """
        self.search()
        for key, val in self.users_db_list.items():
            if val.get('exists') is False:
                continue
            list_data = self.extract_gate_keeper_log(key, val.get('db'))
            if len(list_data) == 0:  # テーブルの中身に何もなかった場合
                continue

            if len(self.logs) == 0:  # まだカラム名がない場合
                self.logs.extend(list_data)
            else:
                self.logs.extend(list_data[1:])
        self.output_csv()

    def output_csv(self):
        """write data all users gatekeeper logs to csv

        Args:
            -
        """
        self.log.debug(f"[+] Writing GateKeeper logs to {self.output_file_name}")
        with open(self.output_file_name, 'w', encoding="utf_8_sig") as file:
            writer = csv.writer(file, delimiter=",", lineterminator='\n', doublequote=True, quoting=csv.QUOTE_ALL)
            writer.writerows(self.logs)


if __name__ == '__main__':

    # usage:
    #     python osx_ime_parser.py -f db_file
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-r', '--root',
                             help="please input the evidence root path",
                             type=str,
                             default='/')
    args_parser.add_argument('-o', '--output',
                             help="please input the output path.",
                             type=str,
                             default=os.getcwd())

    args = args_parser.parse_args()

    print("[+] Processing GateKeeper logs")
    gate_keeper = GateKeeper(args.root, args.output)
    gate_keeper.extract()
    gate_keeper.output_csv()
    print("[+] Finish parsing GateKeeper logs")
