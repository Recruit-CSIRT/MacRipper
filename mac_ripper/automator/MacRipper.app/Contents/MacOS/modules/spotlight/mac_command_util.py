# -*- coding: utf-8 -*-
import shlex
import subprocess


class MacCommandUtil:

    def __init__(self, encoding='utf8'):
        self.encoding = encoding

    def execute(self, cmd):
        res = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        return res.stdout.read().decode(self.encoding)

