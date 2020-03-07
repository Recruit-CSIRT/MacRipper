# -*- coding: utf-8 -*-
import unittest
from modules.spotlight.mdls_util import *


class MockMacCommandUtil:
    def __init__(self, test_data):
        self.test_data = test_data

    def execute(self, command):
        return self.test_data


class TestMyUtil(unittest.TestCase):

    def test_mdls_parse(self):
        tests = [
            {
                "arg":
                    """
                        kMDItemAuthors                           = (null)
                        kMDItemContentCreationDate               = 2019-09-10 12:46:53 +0000
                        kMDItemContentModificationDate           = 2019-09-10 12:46:53 +0000
                        kMDItemDateAdded                         = 2019-09-10 12:46:53 +0000
                        kMDItemDisplayName                       = "20190719-001 (2).pdf"
                        kMDItemDownloadedDate                    = (null)
                        kMDItemFSContentChangeDate               = 2019-09-10 12:46:53 +0000
                        kMDItemFSCreationDate                    = 2019-09-10 12:46:53 +0000
                        kMDItemFSSize                            = 55065
                        kMDItemKind                              = "PDF書類"
                        kMDItemLastUsedDate                      = (null)
                        kMDItemOriginSenderDisplayName           = (null)
                        kMDItemOwnerUserID                       = (null)
                        kMDItemTitle                             = (null)
                        kMDItemUserSharedReceivedDate            = (null)
                        kMDItemUserSharedReceivedRecipientHandle = (null)
                        kMDItemUserSharedReceivedSender          = (null)
                        kMDItemUserSharedReceivedSenderHandle    = (null)
                        kMDItemUserSharedReceivedTransport       = (null)
                        kMDItemWhereFroms                        = (
                        "https://google.com/?q=hello",
                        "https://google.com/?q=world"
                        )
                        kMDItemUsedDates     = (
                            "2019-05-23 15:00:00 +0000",
                            "2019-05-28 15:00:00 +0000",
                            "2019-09-17 15:00:00 +0000"
                        )
                    """,
                "expected": {
                    "kMDItemAuthors": "(null)",
                    "kMDItemWhereFroms": ["https://google.com/?q=hello", "https://google.com/?q=world"],
                    "kMDItemUsedDates": ["2019-05-23 15:00:00 +0000", "2019-05-28 15:00:00 +0000", "2019-09-17 15:00:00 +0000"]
                }
            },
            {
                "arg": "/.HFS+ Private Directory Data: could not find /.HFS+ Private Directory Data.",
                "expected": {}
            }
        ]
        for test in tests:
            mock = MockMacCommandUtil(test["arg"])
            result = MdlsUtil([], "", mock).execute()
            d = result.as_dict()
            for k, v in test["expected"].items():
                self.assertEqual(d[k], v)


if __name__ == "__main__":
    unittest.main()
