from __future__ import print_function
import subprocess
import os
import json
import csv
import argparse


class UnifiedLogs:

    presets = {
        'usb': {  # USBの接続履歴を出力(内臓SDカードリーダのログは省く)
            'txt': "[+] Process to parse USB connected history without builtin SD card reader's log",
            'pre': "eventMessage contains 'USBMSC' and not eventMessage contains '000000000820 0x5ac 0x8406 0x820'",
            'suf': "_usb_filtered"
        },
        'ns': {  # Network Shareの接続履歴を出力
            'txt': "[+] Process to parse Network Share connected history",
            'pre': "eventMessage contains 'smb' or eventMessage contains 'afp' or eventMessage contains 'cifs' or eventMessage contains 'nfs' or eventMessage contains 'ftp'",
            'suf': "_networkshare_filtered"
        },
        'volume': {  # Volumeの接続履歴を出力
            'txt': "[+] Process to parse Volume connected history",
            'pre': "eventMessage contains '/Volumes/'",
            'suf': "_volume_filtered"
        },
        'hfs': {  # HFSの接続履歴を出力
            'txt': "[+] Process to parse Volume connected history",
            'pre': "eventMessage contains 'hfs' and eventMessage contains 'mounted'",
            'suf': "_hfs_filtered"
        },
        'all': {  # すべてのプリセットの結果を出力
            'txt': "[+] Process to parse all presets",
            'pre': "",
            'suf': ""
        },
    }

    def __init__(self, evidence_root, output_path, log):
        """Init function.

        Args:
            evidence_root: The evidence root directory path you mounted. e.g. /Volumes/disk3s1/.
            output_path: The output directory path.
        """
        self.log = log
        self.evidence_root = evidence_root
        self.output_path = output_path

        # カレントでリレクトリにコピー用のディレクトリを作成
        self.logarchive_path = os.path.join(self.output_path, "collected_unified_logs.logarchive")
        os.makedirs(self.logarchive_path, exist_ok=True)

    def copy_unified_logs(self):
        """Copy Unified Logs from evidence_root to output_path.

        """

        self.log.debug("[+] Start to copy Unified Logs")

        # uuidtextのパスの調査
        uuidtext_path = os.path.join(self.evidence_root, "var/db/uuidtext")
        self.log.debug(f"[+] Now copying Unified Logs from {uuidtext_path}")
        if not os.path.exists(uuidtext_path):
            self.log.warning(f"[-] Error: Directory {uuidtext_path} is not exists.")
            return

        # uuidtext logをコピー
        try:
            proc = subprocess.run(['cp', '-Rp', uuidtext_path + "/", self.logarchive_path])
        except subprocess.SubprocessError as err:
            self.log.warning(f"[-] Error: copy failed: Error: {err}")

        if proc.returncode is not 0:
            self.log.warning(f"[-] Error: copy failed: Error: {proc}")

        # diagnosticsのパスの調査
        diagnostics_path = os.path.join(self.evidence_root, "var/db/diagnostics")
        self.log.debug(f"[+] Now copying Unified Logs from {diagnostics_path}")
        if not os.path.exists(diagnostics_path):
            self.log.warning(f"[-] Error: Directory {diagnostics_path} is not exists.")
            return

        # diagnostics logをコピー
        try:
            proc = subprocess.run(['cp', '-Rp', diagnostics_path + "/", self.logarchive_path])
        except subprocess.SubprocessError as err:
            self.log.warning(f"[-] Error: copy failed: Error: {err}")

        if proc.returncode is not 0:
            self.log.warning(f"[-] Error: copy failed: Error: {proc}")

        self.log.debug(f"[+] Unified Logs copy is completed")

        self.create_info_plist()

    def create_info_plist(self):
        if os.path.exists(os.path.join(self.logarchive_path, "Info.plist")):
            return

        xml = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>OSArchiveVersion</key>
        <integer>4</integer>
    </dict>
</plist>
        """

        with open(os.path.join(self.logarchive_path, "Info.plist"), "w") as fplist:
            fplist.write(xml)

    def output_unifiled_log(self, predicate="", start="", end="", tz="", output_format="csv", file_name_suffix=""):
        """Parse Unified Logs and output.

        Args:
            predicate: The filter condition of Unified Logs. e.g. "eventMessage contains 'hfs'"
            start: The filter condition of the start datetime. e.g. "2019-01-01 10:00:00" or "2019-01-01"
            end: The filter condition of the end datetime. e.g. "2019-01-01 10:00:00" or "2019-01-01"
            tz: timezone.
            output_format: The output format. csv or json
            file_name_suffix: Strings appended to the end of name.
        """

        self.log.debug("[+] Start to parse Unified Logs")

        # logコマンドを使って内容を表示
        command = ['log', 'show', '--archive', self.logarchive_path, '--style', 'json', '--force', '--info', '--debug']
        file_name = os.path.join(self.output_path, "unified_log")

        if len(start) > 0:
            command.extend(['--start', start])
            file_name += f"_s{start.replace(' ', '_').replace(':', '')}"

        if len(end) > 0:
            command.extend(['--end', end])
            file_name += f"_e{end.replace(' ', '_').replace(':', '')}"

        if len(tz) > 0:
            command.extend(['--timezone', tz])

        # filter条件を取得
        if len(predicate) > 0:
            command.extend(['--predicate', predicate])
            if len(file_name_suffix) > 0:
                file_name += file_name_suffix
            else:
                file_name += "_pre"

        # 1回 logコマンドで触らないといけないと、log showができない
        dummy_commnad = ['log', 'show', '--archive', self.logarchive_path, '--force', '--start', '2099-12-31']
        proc = subprocess.run(dummy_commnad, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 本当のコマンド
        self.log.debug(f"[+] Now processing to parse Unified Logs...")
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            outs, errs = proc.communicate()
        except subprocess.SubprocessError as err:
            proc.kill()
            self.log.warning(f"[-] {err}")
            outs, errs = proc.communicate()

        text = outs.decode("utf8")
        # サイズが小さい場合は失敗している。
        if len(text) < 10:
            self.log.warning(f"[-] No results")
            return

        text_json = ""
        try:
            text_json = json.loads(text)
        except Exception as err:
            self.log.warning(f"[-] Filed to load as json format. {err}")
            return

        # 出力形式 json or csv
        if len(output_format) > 0:
            output_format = output_format.lower()
            if output_format not in ['json', 'csv']:  # dafault json
                output_format = 'csv'
            file_name += f".{output_format}"

        self.log.debug(f"[+] Now outputting parsed Unified Logs.")

        with open(file_name, 'w') as write_file:
            if output_format == 'json':
                json.dump(text_json, write_file, ensure_ascii=False, indent=2)

            elif output_format == 'csv':

                # fieldの定義
                field_name = ["timestamp", "traceID", "eventMessage", "eventType", "source", "formatString", "activityIdentifier", "subsystem", "category", "threadID", "senderImageUUID", "backtrace", "processImagePath", "senderImagePath", "machTimestamp", "messageType", "processImageUUID", "processID", "senderProgramCounter", "parentActivityIdentifier", "timezoneName", "creatorActivityID", "bootUUID"]

                # dialect(formatの指定方法)
                csv.register_dialect('unified_dialect', doublequote=True, quoting=csv.QUOTE_ALL)
                # DictWriter
                csv_writer = csv.DictWriter(write_file, fieldnames=field_name, dialect='unified_dialect')
                # CSVへの書き込み
                csv_writer.writeheader()
                for block in text_json:
                    try:
                        csv_writer.writerow(block)
                    except Exception as err:
                        self.log.error(f"[-] Error: Failed to write csv file. Error: {err}")

        self.log.debug(f"[+] Output Unified Logs is completed.")
        self.log.debug(f"[+] Filename is '{file_name}'.")

    def choose_preset(self, preset="", start="", end="", tz="", output_format="csv"):
        """Set preset outputs.

        Args:
            preset: The preset condition of Unified Logs.
            start: The filter condition of the start datetime. e.g. "2019-01-01 10:00:00" or "2019-01-01"
            end: The filter condition of the end datetime. e.g. "2019-01-01 10:00:00" or "2019-01-01"
            tz: timezone.
            output_format: The output format. csv or json
        """

        if preset == 'all':     # allの場合、再帰的にこの関数を呼び出す。
            key_list = [k for k in self.presets.keys() if k != 'all']
            for k in key_list:
                self.choose_preset(preset=k, start=start, end=end, tz=tz, output_format=output_format)
        elif preset in self.presets.keys():
            self.log.debug(self.presets.get(preset).get('txt'))
            self.output_unifiled_log(predicate=self.presets.get(preset).get('pre'), start=start, end=end, tz=tz,
                                     output_format=output_format,
                                     file_name_suffix=self.presets.get(preset).get('suf'))

    def parse(self, start, end, predicate, output_format, timezone, name):

        # ファイルコピー
        self.copy_unified_logs()

        # プリセットによっての処理
        if predicate in self.presets.keys():
            self.choose_preset(preset=predicate, start=start, end=end, tz=timezone, output_format=output_format)

        else:
            # ユーザの条件によって出力
            self.log.debug("[+] Process to parse Unified Logs along user input.")
            self.output_unifiled_log(predicate=predicate, start=start, end=end, tz=timezone,
                                             output_format=output_format, file_name_suffix=name)


if __name__ == '__main__':
    # usage:
    #   python unified_log.py -r /Volumes/disk3s1/ -s "2018-05-01 10:00:00" -e "2018-05-02 10:00:00" -p "eventMessage contains 'hfs'" -f csv -t asia/tokyo
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-r', '--root',
                             help="please input the evidence root path."
                                  "e.g. '/Volumes/disk3s1/' (mounted volume)",
                             type=str,
                             default='/')
    args_parser.add_argument('-s', '--start',
                             help="please input the start datetime you want to filter."
                                  "e.g. '2018-05-14 10:00:00', '2018-05-14'",
                             type=str,
                             default='')
    args_parser.add_argument('-e', '--end',
                             help="please input the end datetime you want to filter."
                                  "e.g. '2018-05-14 10:00:00', '2018-05-14'",
                             type=str,
                             default='')
    args_parser.add_argument('-p', '--predicate',
                             help="please input the flexible filter like \"eventMessage contains 'USBMSC'\". "
                                  "Also you can use a preset using the keyword: 'usb', 'ns'(network share), 'volume', 'hfs', 'all'",
                             type=str,
                             default='')
    args_parser.add_argument('-f', '--output_format',
                             help="please input the output format.\n csv or json",
                             type=str,
                             default='csv')
    args_parser.add_argument('-t', '--timezone',
                             help="please input the time zone. default is asia/tokyo",
                             type=str,
                             default='asia/tokyo')
    args_parser.add_argument('-o', '--output',
                             help="please input the output path. default is current directory",
                             type=str,
                             default=os.getcwd())
    args_parser.add_argument('-n', '--name',
                             help="please input the file name of the suffix.",
                             type=str,
                             default="")
    args = args_parser.parse_args()

    from logging import basicConfig, getLogger, DEBUG
    basicConfig(level=DEBUG)
    logger = getLogger(__name__)
    logger.debug('hello')

    # インスタンス作成
    #print(args)
    unified_logs = UnifiedLogs(args.root, args.output, logger)
    unified_logs.parse(args.start, args.end, args.predicate, args.output_format, args.timezone, args.name)



