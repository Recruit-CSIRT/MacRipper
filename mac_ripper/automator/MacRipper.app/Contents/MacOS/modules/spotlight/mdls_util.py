# -*- coding: utf-8 -*-


class MdlsUtil:

    def __init__(self, attrs, target_file_path, mac_command_util):
        self._target_file_path = target_file_path
        self._attrs = attrs
        self._result = ""
        self._mac_cmd_util = mac_command_util

    def escape(self, string):
        return string.replace('"', '\\"')

    def execute(self):
        path = self.escape(self._target_file_path)
        cmd = "mdls" + " -name " + " -name ".join(self._attrs) + ' "' + path + '"'
        self._result = self._mac_cmd_util.execute(cmd)
        return self

    def as_text(self):
        return self._result

    def as_dict(self):
        lines = self._result.split("\n")
        kvmap = {}
        in_parentheses = False
        tmpk = ""
        tmpv = ""
        for line in lines:
            if len(line.strip()) <= 0:
                continue

            if not in_parentheses and line.find("=") < 0:
                continue

            if in_parentheses:
                k = line
            else:
                kv = line.split("=")
                k = kv[0]

            if in_parentheses:
                k = k.strip().replace("\t", "").replace('"', "")
            else:
                k = k.strip().replace(" ", "").replace("\t", "").replace('"', "")

            if in_parentheses:
                if k == ")":
                    kvmap[tmpk] = tmpv
                    in_parentheses = False
                    tmpk = ""
                    tmpv = []
                else:
                    if len(k) > 0 and k[len(k) - 1] == ",":
                        k = k[: len(k) - 1]
                    tmpv.append(k)
                continue
            v = kv[1]
            v = v.strip().replace('"', "")
            if v == "(":
                in_parentheses = True
                tmpk = k
                tmpv = []
                continue
            kvmap[k] = v
        return kvmap