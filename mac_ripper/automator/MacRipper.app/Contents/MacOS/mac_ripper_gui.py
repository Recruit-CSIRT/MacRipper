# -*- coding: utf-8 -*-
import tkinter
from tkinter import ttk
import threading
import queue
from mac_ripper_cli import *
from gui.components import *
from modules.utils.bootstrap import LoggingConfig
from logging import FileHandler
import traceback
import sys
import pytz
from datetime import datetime


LOG = logging.getLogger(__name__)


class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class LogPanel:
    def __init__(self, parent, x, y):
        self._parent = parent
        self._x = x
        self._y = y
        self._tk_text = None
        self._lines = 0
        self._max_lines = 500
        self._capacity = 200

        self._queue = None
        self._queue_handler = None
        self.setup_logging()

    def setup_logging(self):
        self.setup_queue_handler()

    def setup_queue_handler(self):
        self._queue = queue.Queue()
        self._queue_handler = QueueHandler(self._queue)
        self._queue_handler.setLevel(logging.INFO)
        self._queue_handler.setFormatter(LoggingConfig.formatter)
        LOG.addHandler(self._queue_handler)

    def start(self):
        t = threading.Thread(target=self.polling_log_queue)
        t.setDaemon(True)
        t.start()

    def polling_log_queue(self):
        while True:
            try:
                record = self._queue.get(block=True)
            except queue.Empty:
                break
            else:
                self.display_log(record)

    def display_log(self, msg):
        formatted = self._queue_handler.format(msg)
        self._tk_text.insert(tk.END, formatted + "\n")
        self._tk_text.yview(tk.END)

    def build(self):
        self._tk_text = tk.Text(self._parent, height=15, width=83)
        self._tk_text.place(x=self._x, y=self._y)
        self.start()
        return self


class ParserSelectorOption:
    def __init__(self):
        self._checkbox = None

    def add_checkbox(self, checkbox):
        self._checkbox = checkbox


class ParserSelector:
    def __init__(self):
        self._checkbox = None
        self._children = []
        self._parsers = []
        self._options = []

    def children(self):
        return self._children

    def add_checkbox(self, checkbox):
        self._checkbox = checkbox

    def add_parser(self, parser):
        self._parsers.append(parser)

    def get_parsers(self):
        res = []
        for parser in self._parsers:
            res.append(parser(LOG))
        return res

    def add_child(self, child):
        """ add child parser selector."""
        self._children.append(child)

    def find_activated(self):
        """ return nested child checkbox if activated. This also contains myself. """
        res = []
        if self.is_active():
            candidates = [self]
            res.append(self)
            while len(candidates) > 0:
                candidate = candidates.pop()
                for child in candidate.children():
                    candidates.append(child)
                    res.append(child)
        else:
            for child in self.children():
                for activated in child.find_activated():
                    res.append(activated)
        return res

    def is_active(self):
        if not self._checkbox:
            return False
        return self._checkbox.get()


class SpotlightSelector(ParserSelector):
    def __init__(self):
        super().__init__()
        self._all_checkbox = None
        self._binary_checkbox = None
        self._all_checkbox = ButtonWithCheckbox(parent=None, x=370, y=145, text="(Spotlight option) all files").build()
        self._mac_cmd_checkbox = ButtonWithCheckbox(parent=None, x=370, y=165, text="(Spotlight option) command").build()

    def _use_all(self):
        if not self._all_checkbox:
            return False
        return self._all_checkbox.get()

    def _use_mac_command(self):
        if not self._mac_cmd_checkbox:
            return False
        return self._mac_cmd_checkbox.get()

    def get_parsers(self):
        res = []
        for parser in self._parsers:
            res.append(parser(LOG))
        res.append(CliSpotlight(LOG, self._use_mac_command(), self._use_all()))
        return res


class ModuleSelectorPanel:
    def __init__(self):
        self._button_action_mapping = []
        self._parse_all_btn = None
        self._parser_selector_panel = None
        self._parser_selector = ParserSelector()

    def build(self):
        self.build_module_selection_panel()
        return self

    def find_selected_parsers(self):
        res = []
        for selector in self._parser_selector.find_activated():
            for p in selector.get_parsers():
                res.append(p)
        return res

    def build_module_selection_panel(self):
        all_selector = ParserSelector()
        checkbox = ButtonWithCheckbox(parent=None, x=310, y=25, text="Use all modules").build()
        checkbox.set(True)
        all_selector.add_checkbox(checkbox)

        mapping = [
            {"parent": None, "x": 340, "y": 45,  "text": "Use plist module", "parser": CliPlist},
            {"parent": None, "x": 340, "y": 65,  "text": "Use MRU module", "parser": CliMru},
            {"parent": None, "x": 340, "y": 85, "text": "Use sqlite module", "parser": CliSqlite},
            {"parent": None, "x": 340, "y": 105, "text": "Use unified log module", "parser": CliUnifiedLogs}
        ]
        for m in mapping:
            s = ParserSelector()
            s.add_checkbox(ButtonWithCheckbox(m["parent"], m["x"], m["y"], m["text"]).build())
            s.add_parser(m["parser"])
            all_selector.add_child(s)
        self._parser_selector.add_child(all_selector)

        spotlight = SpotlightSelector()
        spotlight.add_checkbox(ButtonWithCheckbox(None, 340, 125, "Use spotlight module").build())
        all_selector.add_child(spotlight)


class TimezonePanel:
    def __init__(self, parent):
        self._parent = parent
        self._var = None

    def build(self):
        label = tk.Label(text="Timezone(unifiedlog, spotlight)", bg="#E8E8E8")
        label.place(x=10, y=120)
        self._var = tk.StringVar(self._parent)
        option_menu = ttk.OptionMenu(self._parent, self._var, *pytz.all_timezones)
        self._var.set("Asia/Tokyo")
        option_menu.config(width=20)
        option_menu.place(x=10, y=145)
        return self

    def timezone(self):
        return self._var.get()


class MacRipperGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self._name = "Mac Ripper Gui"
        self._evidence_root = "/"
        self._output_path = ""
        self._timezone = ""
        self._module_selector = ModuleSelectorPanel()
        self._evidence_root_selector = None
        self._output_path_selector = None
        self._log_panel = None
        self._file_handler = None
        self._timezone_panel = None

    def run(self):
        self.build()
        self.mainloop()

    def build(self):
        top = self.build_application_top_frame()
        tk.Menu(top)
        self.build_evidence_root_path_panel(top)
        self.build_output_path_panel(top)
        self.build_unified_log_timezone_panel(top)
        self.build_module_option_panel(top)
        self.build_log_display_panel(top)
        ttk.Button(self, text='Rip it', width=5, command=self.rip).place(x=220, y=450)
        ttk.Button(self, text='Quit', width=5, command=self.exit).place(x=320, y=450)
        return self

    def build_log_display_panel(self, parent):
        self._log_panel = LogPanel(parent, 10, 205)
        self._log_panel.build()

    def build_application_top_frame(self):
        frame = self
        frame.geometry()
        frame.title(self._name)
        frame['height'] = 500
        frame['width'] = 610
        frame['bg'] = '#E8E8E8'
        return frame

    def build_evidence_root_path_panel(self, parent):
        self._evidence_root_selector = DirectorySelector(
            parent, 10, 0, "Evidence root path", self._evidence_root).build()

    def build_output_path_panel(self, parent):
        self._output_path_selector = DirectorySelector(parent, 10, 60, "Output path", self._output_path).build()

    def build_module_option_panel(self, parent):
        self._module_selector = ModuleSelectorPanel().build()

    def build_unified_log_timezone_panel(self, parent):
        self._timezone_panel = TimezonePanel(parent).build()

    def evidence_root_path(self):
        return self._evidence_root_selector.get_value()

    def output_path(self):
        return self._output_path_selector.get_value()

    def find_selected_parsers(self):
        return self._module_selector.find_selected_parsers()

    def timezone(self):
        return self._timezone_panel.timezone()

    def setup_file_handler(self):
        if not self._file_handler:
            file_name = ("/mac_ripper_gui_{0:%Y%m%d%H%M%S}.log".format(datetime.now()))
            self._file_handler = FileHandler(self.output_path() + file_name, 'a')
            self._file_handler.setLevel(logging.DEBUG)
            self._file_handler.setFormatter(LoggingConfig.formatter)
            LOG.addHandler(self._file_handler)

    def rip(self):
        def work():
            banner(LOG)
            if not is_arguments_valid(LOG, self.evidence_root_path(), self.output_path(), self.timezone()):
                LOG.info("[+] Mac Ripper Gui finished.")
                return
            parsers = self.find_selected_parsers()
            LOG.info("[+] EVIDENCE ROOT PATH : " + self.evidence_root_path())
            LOG.info("[+] OUTPUT PATH : " + self.output_path())
            LOG.info("[+] TIMEZONE : " + self.timezone())
            LOG.info("[+] Selected Parsers : " + ", ".join(list(map(lambda x: x.name(), parsers))))
            tz = self.timezone()
            for parser in parsers:
                try:
                    parser.parse(self.evidence_root_path(), self.output_path(), tz)
                except Exception as e:
                    LOG.error(str(traceback.format_exc()))
            LOG.info("[+] Mac Ripper Gui finished.")
        self.setup_file_handler()
        t = threading.Thread(target=work)
        t.setDaemon(True)
        t.start()

    def exit(self):
        self.destroy()
        sys.exit(0)


def is_arguments_valid(log, root, output, timezone):
    if len(root) == 0:
        log.error("[-] Evidence root path must not be empty")
        return False
    if not os.path.isdir(root):
        log.error("[-] Evidence root path must be directory: " + root)
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
    MacRipperGui().run()
