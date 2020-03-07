# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import struct
import uuid
import datetime
import os
import sys
import pprint
import traceback
from modules.mru.utils import *
#from btypes import *

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

if sys.platform == 'darwin':
    import modules.mru.osx


BMK_DATA_TYPE_MASK = 0xffffff00
BMK_DATA_SUBTYPE_MASK = 0x000000ff

BMK_STRING = 0x0100
BMK_DATA = 0x0200
BMK_NUMBER = 0x0300
BMK_DATE = 0x0400
BMK_BOOLEAN = 0x0500
BMK_ARRAY = 0x0600
BMK_DICT = 0x0700
BMK_UUID = 0x0800
BMK_URL = 0x0900
BMK_NULL = 0x0a00

BMK_ST_ZERO = 0x0000
BMK_ST_ONE = 0x0001

BMK_BOOLEAN_ST_FALSE = 0x0000
BMK_BOOLEAN_ST_TRUE = 0x0001

kCFNumberSInt8Type = 1
kCFNumberSInt16Type = 2
kCFNumberSInt32Type = 3
kCFNumberSInt64Type = 4
kCFNumberFloat32Type = 5
kCFNumberFloat64Type = 6
kCFNumberCharType = 7
kCFNumberShortType = 8
kCFNumberIntType = 9
kCFNumberLongType = 10
kCFNumberLongLongType = 11
kCFNumberFloatType = 12
kCFNumberDoubleType = 13
kCFNumberCFIndexType = 14
kCFNumberNSIntegerType = 15
kCFNumberCGFloatType = 16

kCFURLResourceIsRegularFile = 0x00000001
kCFURLResourceIsDirectory = 0x00000002
kCFURLResourceIsSymbolicLink = 0x00000004
kCFURLResourceIsVolume = 0x00000008
kCFURLResourceIsPackage = 0x00000010
kCFURLResourceIsSystemImmutable = 0x00000020
kCFURLResourceIsUserImmutable = 0x00000040
kCFURLResourceIsHidden = 0x00000080
kCFURLResourceHasHiddenExtension = 0x00000100
kCFURLResourceIsApplication = 0x00000200
kCFURLResourceIsCompressed = 0x00000400
kCFURLResourceIsSystemCompressed = 0x00000400
kCFURLCanSetHiddenExtension = 0x00000800
kCFURLResourceIsReadable = 0x00001000
kCFURLResourceIsWriteable = 0x00002000
kCFURLResourceIsExecutable = 0x00004000
kCFURLIsAliasFile = 0x00008000
kCFURLIsMountTrigger = 0x00010000

kCFURLVolumeIsLocal = 0x1
kCFURLVolumeIsAutomount = 0x2
kCFURLVolumeDontBrowse = 0x4
kCFURLVolumeIsReadOnly = 0x8
kCFURLVolumeIsQuarantined = 0x10
kCFURLVolumeIsEjectable = 0x20
kCFURLVolumeIsRemovable = 0x40
kCFURLVolumeIsInternal = 0x80
kCFURLVolumeIsExternal = 0x100
kCFURLVolumeIsDiskImage = 0x200
kCFURLVolumeIsFileVault = 0x400
kCFURLVolumeIsLocaliDiskMirror = 0x800
kCFURLVolumeIsiPod = 0x1000
kCFURLVolumeIsiDisk = 0x2000
kCFURLVolumeIsCD = 0x4000
kCFURLVolumeIsDVD = 0x8000
kCFURLVolumeIsDeviceFileSystem = 0x10000
kCFURLVolumeSupportsPersistentIDs = 0x100000000
kCFURLVolumeSupportsSearchFS = 0x200000000
kCFURLVolumeSupportsExchange = 0x400000000

kCFURLVolumeSupportsSymbolicLinks = 0x1000000000
kCFURLVolumeSupportsDenyModes = 0x2000000000
kCFURLVolumeSupportsCopyFile = 0x4000000000
kCFURLVolumeSupportsReadDirAttr = 0x8000000000
kCFURLVolumeSupportsJournaling = 0x10000000000
kCFURLVolumeSupportsRename = 0x20000000000
kCFURLVolumeSupportsFastStatFS = 0x40000000000
kCFURLVolumeSupportsCaseSensitiveNames = 0x80000000000
kCFURLVolumeSupportsCasePreservedNames = 0x100000000000
kCFURLVolumeSupportsFLock = 0x200000000000
kCFURLVolumeHasNoRootDirectoryTimes = 0x400000000000
kCFURLVolumeSupportsExtendedSecurity = 0x800000000000
kCFURLVolumeSupports2TBFileSize = 0x1000000000000
kCFURLVolumeSupportsHardLinks = 0x2000000000000
kCFURLVolumeSupportsMandatoryByteRangeLocks = 0x4000000000000
kCFURLVolumeSupportsPathFromID = 0x8000000000000

kCFURLVolumeIsJournaling = 0x20000000000000
kCFURLVolumeSupportsSparseFiles = 0x40000000000000
kCFURLVolumeSupportsZeroRuns = 0x80000000000000
kCFURLVolumeSupportsVolumeSizes = 0x100000000000000
kCFURLVolumeSupportsRemoteEvents = 0x200000000000000
kCFURLVolumeSupportsHiddenFiles = 0x400000000000000
kCFURLVolumeSupportsDecmpFSCompression = 0x800000000000000
kCFURLVolumeHas64BitObjectIDs = 0x1000000000000000
kCFURLVolumePropertyFlagsAll = 0xffffffffffffffff

BMK_URL_ST_ABSOLUTE = 0x0001
BMK_URL_ST_RELATIVE = 0x0002

kBookmarkPath = 0x1004
kBookmarkCNIDPath = 0x1005
kBookmarkFileProperties = 0x1010

kBookmarkFileName = 0x1020
kBookmarkFileID = 0x1030
kBookmarkFileCreationDate = 0x1040

kBookmarkTOCPath = 0x2000
kBookmarkVolumePath = 0x2002
kBookmarkVolumeURL = 0x2005
kBookmarkVolumeName = 0x2010
kBookmarkVolumeUUID = 0x2011
kBookmarkVolumeSize = 0x2012
kBookmarkVolumeCreationDate = 0x2013
kBookmarkVolumeProperties = 0x2020

kBookmarkVolumeIsRoot = 0x2030
kBookmarkVolumeBookmark = 0x2040
kBookmarkVolumeMountPoint = 0x2050
kBookmarkContainingFolder = 0xc001
kBookmarkUserName = 0xc011
kBookmarkUID = 0xc012
kBookmarkWasFileReference = 0xd001
kBookmarkCreationOptions = 0xd010
kBookmarkURLLengths = 0xe003
kBookmarkSecurityExtension = 0xf080


class Data (object):
    def __init__(self, bytedata=None):
        self.bytes = bytes(bytedata)
    def __repr__(self):
        return 'Data(%r)' % self.bytes



def __repr__(self):
    result = ['Bookmark([']
    for tid,toc in self.tocs:
        result.append('(0x%x, {\n' % tid)
        for k,v in iteritems(toc):
            if isinstance(k, (str, unicode)):
                kf = repr(k)
            else:
                kf = '0x%04x' % k
            result.append('  %s: %r\n' % (kf, v))
        result.append('}),\n')
    result.append('])')
    return ''.join(result)



class URL (object):
    def __init__(self, base, rel=None):
        if rel is not None:
            self.base = base
            self.relative = rel
        else:
            self.base = None
            self.relative = base
    @property
    def absolute(self):
        if self.base is None:
            return self.relative
        else:
            base_abs = self.base.absolute
            return urljoin(self.base.absolute, self.relative)
    def __repr__(self):
        return 'URL(%r)' % self.absolute



class Bookmark(object):

    def __init__(self, data=None, debug=False):
        if isinstance(data, bytearray):
            data = bytes(data)
        if not isinstance(data, bytes):
            raise ValueError('You must pass bytes data.')
        self.data = data
        self.debug = debug


    def convertBytesToSpecificDataType(self, data, headerSize, offset):
        offset += headerSize
        if offset > len(data) - 8:
            raise ValueError('Offset out of range')

        entryDataSize, entryDataType = struct.unpack(b'<II', data[offset: (offset+8)])
        entryDataBytes = data[(offset+8): (offset+8+entryDataSize)]

        dataType = entryDataType & BMK_DATA_TYPE_MASK
        dataSubType = entryDataType & BMK_DATA_SUBTYPE_MASK


        if dataType == BMK_STRING:
            return entryDataBytes.decode('utf-8')

        elif dataType == BMK_DATA:
            return Data(entryDataBytes)

        elif dataType == BMK_NUMBER:
            if dataSubType == kCFNumberSInt8Type:
                return ord(entryDataBytes[0])
            elif dataSubType == kCFNumberSInt16Type:
                return struct.unpack(b'<h', entryDataBytes)[0]
            elif dataSubType == kCFNumberSInt32Type:
                return struct.unpack(b'<i', entryDataBytes)[0]
            elif dataSubType == kCFNumberSInt64Type:
                return struct.unpack(b'<q', entryDataBytes)[0]
            elif dataSubType == kCFNumberFloat32Type:
                return struct.unpack(b'<f', entryDataBytes)[0]
            elif dataSubType == kCFNumberFloat64Type:
                return struct.unpack(b'<d', entryDataBytes)[0]

        elif dataType == BMK_DATE:
            # Yes, dates really are stored as *BIG-endian* doubles; everything
            # else is little-endian
            secs = datetime.timedelta(seconds=struct.unpack(b'>d', entryDataBytes)[0])
            return secs + osx_epoch  

        elif dataType == BMK_BOOLEAN:
            if dataSubType == BMK_BOOLEAN_ST_TRUE:
                return True
            elif dataSubType == BMK_BOOLEAN_ST_FALSE:
                return False

        elif dataType == BMK_UUID:
            return uuid.UUID(bytes=entryDataBytes)

        elif dataType == BMK_URL:
            if dataSubType == BMK_URL_ST_ABSOLUTE:
                return URL(entryDataBytes.decode('utf-8'))

            elif dataSubType == BMK_URL_ST_RELATIVE:
                baseoffet, reloffset = struct.unpack(b'<II', entryDataBytes)
                base = self.convertBytesToSpecificDataType(data, headerSize, baseoffet)
                rel  = self.convertBytesToSpecificDataType(data, headerSize, reloffset)
                return URL(base, rel)

        elif dataType == BMK_ARRAY:
            result = []
            for i in range(offset+8, offset+8+entryDataSize, 4):
                nextOffset, = struct.unpack(b'<I', data[i: i+4])
                result.append(self.convertBytesToSpecificDataType(data, headerSize, nextOffset))
            return result

        elif dataType == BMK_DICT:
            result = {}
            for i in range(offset+8, offset+8+entryDataSize, 8):
                koffset, voffset = struct.unpack(b'<II', data[i: i+8])
                k = self.convertBytesToSpecificDataType(data, headerSize, koffset)
                v = self.convertBytesToSpecificDataType(data, headerSize, voffset)
                result[k] = v
            return result

        elif dataType == BMK_NULL:
            return None

        return "Unknown data type %08x" % dataType




    def parse_toc_entry_data(self, data, headerSize, offsetToTocEntryDataFromHeader):
        if self.debug:
            print("offsetToTocEntryDataFromHeader",offsetToTocEntryDataFromHeader)
        return self.convertBytesToSpecificDataType(data, headerSize, offsetToTocEntryDataFromHeader)




    def parse_toc(self, data, offsetToTocFromHeader, headerSize):
        offsetToToc = offsetToTocFromHeader + headerSize
        tocSize, = struct.unpack(b'<I', data[offsetToToc: offsetToToc + 4])
        toc = data[(offsetToToc+4): (offsetToToc+4) + tocSize]
        # parse Toc Entry.
        magic, identifier, offsetToNextToc, numOfTocEntry = struct.unpack(b'<IIII', toc[0:16])

        if self.debug:
            print("-offsetToTocFromHeader", offsetToToc)
            print("-len(data)",len(data))
            print("-tocsize",tocSize)
            print("-magic",magic)
            print("-identifier",identifier)
            print("-offsetToNextToc",offsetToNextToc)
            print("-numOfTocEntry",numOfTocEntry)

        tocData = {}
        for i in range(numOfTocEntry):
            offsetToTocEntry = offsetToToc + 20 + 12 * i
            key, offsetToTocEntryDataFromHeader, reserved = struct.unpack(b'<III', data[offsetToTocEntry: offsetToTocEntry + 12])

            if (key & 0xffffff00) == 0x1040:
                sys.exit(1)
            if key & 0x80000000:
                key = self.convertBytesToSpecificDataType(data, headerSize, key & 0x7fffffff)
            tocData[key] = self.parse_toc_entry_data(data, headerSize, offsetToTocEntryDataFromHeader)

            if self.debug:
                print("-offsetToTocEntry",offsetToTocEntry)
                print("-key",key)
                print("-offsetToTocEntryDataFromHeader", offsetToTocEntryDataFromHeader)
                print("-reserved", reserved)
                print("-offsetToTocEntryDataFromHeader",offsetToTocEntryDataFromHeader)
            
        return tocData, offsetToNextToc



    def do_parse(self):
        data = self.data
        magic,totalSize,unknown,headerSize, = struct.unpack(b'<4sIII', data[0:16])
        offsetToTocFromHeader, = struct.unpack(b'<I', data[headerSize: headerSize + 4])

        if self.debug:
            print("headerSize", headerSize)
            print("offsetToFirstTocFromHeader",offsetToTocFromHeader)

        offsetToNextTocFromHeader = offsetToTocFromHeader
        self.tocs = []
        while offsetToNextTocFromHeader != 0:
            tocData, offsetToNextTocFromHeader = self.parse_toc(data, offsetToNextTocFromHeader, headerSize)
            self.tocs.append(tocData)

            if self.debug:
                print("offsetToNextTocFromHeader",offsetToNextTocFromHeader)
                print("tocEntryData",tocData)


    def parse(self):
        try:
            self.do_parse()
            return self
        except Exception as e:
            raise e



    def searchFromToc(self, key, default=None):
        for toc in self.tocs:
            if key in toc:
                return toc[key]
        return default



    def volumeName(self):
        return str(self.searchFromToc(0x2010))
    def volumePath(self):
        return str(self.searchFromToc(0x2002))
    def volumeFlag(self):
        return str(self.searchFromToc(0x2020))
    def volumeIsRootFs(self):
        return str(self.searchFromToc(0x2030))
    def uuid(self):
        return str(self.searchFromToc(0x2011))
    def volumeSize(self):
        return str(self.searchFromToc(0x2012))
    def volumeCreationDate(self):
        return str(self.searchFromToc(0x2013))
    def volumeUrl(self):
        return str(self.searchFromToc(0x2005))
    def volumeBookmark(self):
        return str(self.searchFromToc(0x2040))
    def volumeMountPoint(self):
        return str(self.searchFromToc(0x2050))
    def securityExtention1(self):
        return str(self.searchFromToc(0xf080))
    def securityExtention2(self):
        return str(self.searchFromToc(0xf081))
    def targetPath(self):
        if self.searchFromToc(0x1004) == None:
            return []
        return list(self.searchFromToc(0x1004))
    def targetCNIDPath(self):
        return str(self.searchFromToc(0x1005))
    def containingFolderIndex(self):
        return str(self.searchFromToc(0xc001))
    def targetCreationDate(self):
        return str(self.searchFromToc(0x1040))
    def targetFlags(self):
        return str(self.searchFromToc(0x1010))
    def targetFileName(self):
        return str(self.searchFromToc(0x1020))
    def creatorUsername(self):
        return str(self.searchFromToc(0xc011))
    def creatorUID(self):
        return str(self.searchFromToc(0xc012))
    def unknown0x1003(self):
        return str(self.searchFromToc(0x1003))
    def unknown0x1054(self):
        return str(self.searchFromToc(0x1054))
    def unknown0x1055(self):
        return str(self.searchFromToc(0x1055))
    def unknown0x1056(self):
        return str(self.searchFromToc(0x1056))
    def unknown0x1101(self):
        return str(self.searchFromToc(0x1101))
    def unknown0x1102(self):
        return str(self.searchFromToc(0x1102))
    def tocPath(self):
        return str(self.searchFromToc(0x2000))
    def unknown0x2070(self):
        return str(self.searchFromToc(0x2070))
    def fileReferenceFlag(self):
        return str(self.searchFromToc(0xd001))
    def creationOptions(self):
        return str(self.searchFromToc(0xd010))
    def urlLengthArray(self):
        return str(self.searchFromToc(0xe003))
    def localized(self):
        return str(self.searchFromToc(0xf017))
    def unknown0xf022(self):
        return str(self.searchFromToc(0xf022))

