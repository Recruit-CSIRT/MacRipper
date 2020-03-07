# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division

import struct
import datetime
import io
import re
import os
import os.path
import stat
import sys
from modules.mru.utils import *

if sys.platform == 'darwin':
    import modules.mru.osx

try:
    long
except NameError:
    long = int



ALIAS_KIND_FILE = 0
ALIAS_KIND_FOLDER = 1

ALIAS_HFS_VOLUME_SIGNATURE = b'H+'

ALIAS_FIXED_DISK = 0
ALIAS_NETWORK_DISK = 1
ALIAS_400KB_FLOPPY_DISK = 2
ALIAS_800KB_FLOPPY_DISK = 3
ALIAS_1_44MB_FLOPPY_DISK = 4
ALIAS_EJECTABLE_DISK = 5

ALIAS_NO_CNID = 0xffffffff

def encode_utf8(s):
    if isinstance(s, bytes):
        return s
    return s.encode('utf-8')

def decode_utf8(s):
    if isinstance(s, bytes):
        return s.decode('utf-8')
    return s

class AppleShareInfo (object):
    def __init__(self, zone=None, server=None, user=None):
        #: The AppleShare zone
        self.zone = zone
        #: The AFP server
        self.server = server
        #: The username
        self.user = user

    def __repr__(self):
        return 'AppleShareInfo(%r,%r,%r)' % (self.zone, self.server, self.user)

class VolumeInfo (object):
    def __init__(self, name, creation_date, fs_type, disk_type,
                 attribute_flags, fs_id, appleshare_info=None,
                 driver_name=None, posix_path=None, disk_image_alias=None,
                 dialup_info=None, network_mount_info=None):
        #: The name of the volume on which the target resides
        self.name = name

        #: The creation date of the target's volume
        self.creation_date = creation_date

        #: The filesystem type (a two character code, e.g. ``b'H+'`` for HFS+)
        self.fs_type = fs_type

        #: The type of disk; should be one of
        #:
        #:   * ALIAS_FIXED_DISK
        #:   * ALIAS_NETWORK_DISK
        #:   * ALIAS_400KB_FLOPPY_DISK
        #:   * ALIAS_800KB_FLOPPY_DISK
        #:   * ALIAS_1_44MB_FLOPPY_DISK
        #:   * ALIAS_EJECTABLE_DISK
        self.disk_type = disk_type

        #: Filesystem attribute flags (from HFS volume header)
        self.attribute_flags = attribute_flags

        #: Filesystem identifier
        self.fs_id = fs_id

        #: AppleShare information (for automatic remounting of network shares)
        #: *(optional)*
        self.appleshare_info = appleshare_info

        #: Driver name (*probably* contains a disk driver name on older Macs)
        #: *(optional)*
        self.driver_name = driver_name

        #: POSIX path of the mount point of the target's volume
        #: *(optional)*
        self.posix_path = posix_path

        #: :class:`Alias` object pointing at the disk image on which the
        #: target's volume resides *(optional)*
        self.disk_image_alias = disk_image_alias

        #: Dialup information (for automatic establishment of dialup connections)
        self.dialup_info = dialup_info

        #: Network mount information (for automatic remounting)
        self.network_mount_info = network_mount_info

    def __repr__(self):
        args = ['name', 'creation_date', 'fs_type', 'disk_type',
                'attribute_flags', 'fs_id']
        values = []
        for a in args:
            v = getattr(self, a)
            values.append(repr(v))

        kwargs = ['appleshare_info', 'driver_name', 'posix_path',
                  'disk_image_alias', 'dialup_info', 'network_mount_info']
        for a in kwargs:
            v = getattr(self, a)
            if v is not None:
                values.append('%s=%r' % (a, v))
        return 'VolumeInfo(%s)' % ','.join(values)

class TargetInfo (object):
    def __init__(self, kind, filename, folder_cnid, cnid, creation_date,
                 creator_code, type_code, levels_from=-1, levels_to=-1,
                 folder_name=None, cnid_path=None, carbon_path=None,
                 posix_path=None, user_home_prefix_len=None):
        #: Either ALIAS_KIND_FILE or ALIAS_KIND_FOLDER
        self.kind = kind

        #: The filename of the target
        self.filename = filename

        #: The CNID (Catalog Node ID) of the target's containing folder;
        #: CNIDs are similar to but different than traditional UNIX inode
        #: numbers
        self.folder_cnid = folder_cnid

        #: The CNID (Catalog Node ID) of the target
        self.cnid = cnid

        #: The target's *creation* date.
        self.creation_date = creation_date

        #: The target's Mac creator code (a four-character binary string)
        self.creator_code = creator_code

        #: The target's Mac type code (a four-character binary string)
        self.type_code = type_code

        #: The depth of the alias? Always seems to be -1 on OS X.
        self.levels_from = levels_from

        #: The depth of the target? Always seems to be -1 on OS X.
        self.levels_to = levels_to

        #: The (POSIX) name of the target's containing folder. *(optional)*
        self.folder_name = folder_name

        #: The path from the volume root as a sequence of CNIDs. *(optional)*
        self.cnid_path = cnid_path

        #: The Carbon path of the target *(optional)*
        self.carbon_path = carbon_path

        #: The POSIX path of the target relative to the volume root.  Note
        #: that this may or may not have a leading '/' character, but it is
        #: always relative to the containing volume. *(optional)*
        self.posix_path = posix_path

        #: If the path points into a user's home folder, the number of folders
        #: deep that we go before we get to that home folder. *(optional)*
        self.user_home_prefix_len = user_home_prefix_len

    def __repr__(self):
        args = ['kind', 'filename', 'folder_cnid', 'cnid', 'creation_date',
                'creator_code', 'type_code']
        values = []
        for a in args:
            v = getattr(self, a)
            values.append(repr(v))

        if self.levels_from != -1:
            values.append('levels_from=%r' % self.levels_from)
        if self.levels_to != -1:
            values.append('levels_to=%r' % self.levels_to)

        kwargs = ['folder_name', 'cnid_path', 'carbon_path',
                  'posix_path', 'user_home_prefix_len']
        for a in kwargs:
            v = getattr(self, a)
            values.append('%s=%r' % (a, v))

        return 'TargetInfo(%s)' % ','.join(values)

TAG_CARBON_FOLDER_NAME = 0
TAG_CNID_PATH = 1
TAG_CARBON_PATH = 2
TAG_APPLESHARE_ZONE = 3
TAG_APPLESHARE_SERVER_NAME = 4
TAG_APPLESHARE_USERNAME = 5
TAG_DRIVER_NAME = 6
TAG_NETWORK_MOUNT_INFO = 9
TAG_DIALUP_INFO = 10
TAG_UNICODE_FILENAME = 14
TAG_UNICODE_VOLUME_NAME = 15
TAG_HIGH_RES_VOLUME_CREATION_DATE = 16
TAG_HIGH_RES_CREATION_DATE = 17
TAG_POSIX_PATH = 18
TAG_POSIX_PATH_TO_MOUNTPOINT = 19
TAG_RECURSIVE_ALIAS_OF_DISK_IMAGE = 20
TAG_USER_HOME_LENGTH_PREFIX = 21

class Alias (object):
    def __init__(self,
                data=None,
                debug=False,
                appinfo=b'\0\0\0\0',
                version=2,
                volume=None,
                target=None,
                extra=[]):

        if isinstance(data, bytearray):
            data = bytes(data)
        if not isinstance(data, bytes):
            raise ValueError('You must pass bytes data.')
        self.data = data
        self.appinfo = appinfo
        self.version = version
        self.volume = volume
        self.target = target
        self.extra = list(extra)


    def decode(self, bytedata):
        for i in ["utf-8", "shift-jis"]:
            try:
                d = bytedata.decode(i)
                return d
            except:
                continue
        return bytedata


    def do_parse(self, b):
        appinfo, recsize, version = struct.unpack(b'>4shh', b.read(8))

        if recsize < 150:
            raise ValueError('Incorrect alias length')

        if version != 2:
            raise ValueError('Unsupported alias version %u' % version)

        kind, volname, voldate, fstype, disktype, \
        folder_cnid, filename, cnid, crdate, creator_code, type_code, \
        levels_from, levels_to, volattrs, volfsid, reserved = \
              struct.unpack(b'>h28pI2shI64pII4s4shhI2s10s', b.read(142))

        voldate = mac_epoch + datetime.timedelta(seconds=voldate)
        crdate = mac_epoch + datetime.timedelta(seconds=crdate)

        self.appinfo = appinfo

        self.volume = VolumeInfo (volname.decode().replace('/',':'),
                                   voldate, fstype, disktype,
                                   volattrs, volfsid)

        self.target = TargetInfo (kind, self.decode(filename).replace('/',':'),
                                   folder_cnid, cnid,
                                   crdate, creator_code, type_code)
        self.target.levels_from = levels_from
        self.target.levels_to = levels_to

        tag = struct.unpack(b'>h', b.read(2))[0]

        while tag != -1:
            length = struct.unpack(b'>h', b.read(2))[0]
            value = b.read(length)
            if length & 1:
                b.read(1)

            if tag == TAG_CARBON_FOLDER_NAME:
                self.target.folder_name = value.decode().replace('/',':')
            elif tag == TAG_CNID_PATH:
                self.target.cnid_path = struct.unpack('>%uI' % (length // 4),
                                                           value)
            elif tag == TAG_CARBON_PATH:
                self.target.carbon_path = value
            elif tag == TAG_APPLESHARE_ZONE:
                if self.volume.appleshare_info is None:
                    self.volume.appleshare_info = AppleShareInfo()
                self.volume.appleshare_info.zone = value
            elif tag == TAG_APPLESHARE_SERVER_NAME:
                if self.volume.appleshare_info is None:
                    self.volume.appleshare_info = AppleShareInfo()
                self.volume.appleshare_info.server = value
            elif tag == TAG_APPLESHARE_USERNAME:
                if self.volume.appleshare_info is None:
                    self.volume.appleshare_info = AppleShareInfo()
                self.volume.appleshare_info.user = value
            elif tag == TAG_DRIVER_NAME:
                self.volume.driver_name = value
            elif tag == TAG_NETWORK_MOUNT_INFO:
                self.volume.network_mount_info = value
            elif tag == TAG_DIALUP_INFO:
                self.volume.dialup_info = value
            elif tag == TAG_UNICODE_FILENAME:
                self.target.filename = value[2:].decode('utf-16be')
            elif tag == TAG_UNICODE_VOLUME_NAME:
                self.volume.name = value[2:].decode('utf-16be')
            elif tag == TAG_HIGH_RES_VOLUME_CREATION_DATE:
                seconds = struct.unpack(b'>Q', value)[0] / 65536.0
                self.volume.creation_date \
                    = mac_epoch + datetime.timedelta(seconds=seconds)
            elif tag == TAG_HIGH_RES_CREATION_DATE:
                seconds = struct.unpack(b'>Q', value)[0] / 65536.0
                self.target.creation_date \
                    = mac_epoch + datetime.timedelta(seconds=seconds)
            elif tag == TAG_POSIX_PATH:
                self.target.posix_path = value.decode()
            elif tag == TAG_POSIX_PATH_TO_MOUNTPOINT:
                self.volume.posix_path = value.decode()
            elif tag == TAG_RECURSIVE_ALIAS_OF_DISK_IMAGE:
                self.volume.disk_image_alias = Alias.from_bytes(value)
            elif tag == TAG_USER_HOME_LENGTH_PREFIX:
                self.target.user_home_prefix_len = struct.unpack(b'>h', value)[0]
            else:
                self.extra.append((tag, value))

            tag = struct.unpack(b'>h', b.read(2))[0]

    def parse(self):
        try:
            with io.BytesIO(self.data) as b:
                self.do_parse(b)
            return self
        except Exception as e:
            raise e

    def name(self):
        return str(self.volume.name)
    def creation_date(self):
        return str(self.volume.creation_date)
    def fs_type(self):
        return str(self.volume.fs_type)
    def disk_type(self):
        return str(self.volume.disk_type)
    def attribute_flags(self):
        return str(self.volume.attribute_flags)
    def fs_id(self):
        return str(self.volume.fs_id)
    def appleshare_info(self):
        return str(self.volume.appleshare_info)
    def driver_name(self):
        return str(self.volume.driver_name)
    def posix_path(self):
        return str(self.volume.posix_path)
    def disk_image_alias(self):
        return str(self.volume.disk_image_alias)
    def dialup_info(self):
        return str(self.volume.dialup_info)
    def network_mount_info(self):
        return str(self.volume.network_mount_info)

    def kind(self):
        return str(self.target.kind)
    def filename(self):
        return str(self.target.filename)
    def folder_cnid(self):
        return str(self.target.folder_cnid)
    def cnid(self):
        return str(self.target.cnid)
    def creation_date(self):
        return str(self.target.creation_date)
    def creator_code(self):
        return str(self.target.creator_code)
    def type_code(self):
        return str(self.target.type_code)
    def levels_from(self):
        return str(self.target.levels_from)
    def levels_to(self):
        return str(self.target.levels_to)
    def folder_name(self):
        return str(self.target.folder_name)
    def cnid_path(self):
        return str(self.target.cnid_path)
    def carbon_path(self):
        return str(self.target.carbon_path)
    def posix_path(self):
        return str(self.target.posix_path)
    def user_home_prefix_len(self):
        return str(self.target.user_home_prefix_len)

    def __str__(self):
        return '<Alias target=%s>' % self.target.filename

    def __repr__(self):
        values = []
        if self.appinfo != b'\0\0\0\0':
            values.append('appinfo=%r' % self.appinfo)
        if self.version != 2:
            values.append('version=%r' % self.version)
        if self.volume is not None:
            values.append('volume=%r' % self.volume)
        if self.target is not None:
            values.append('target=%r' % self.target)
        if self.extra:
            values.append('extra=%r' % self.extra)
        return 'Alias(%s)' % ','.join(values)