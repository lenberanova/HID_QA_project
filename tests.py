#!/usr/bin/env python3

import wrapper
import os
from logger import log
import hashlib


def readhashLog(library):
    hashedFilesLogLines = []
    print('')
    while True:
        returnCode, logLine = wrapper.hashReadNextLogLine(library)
        if int(returnCode) == 0:
            print('HashReadNextLogLine: {}.'.format(logLine))
            logLineParsed = logLine.split()
            hashedFilesLogLines.append(logLineParsed)
        else:
            break
    return hashedFilesLogLines

def waitforHashDirectory(library, opID:int):
    while True:
        returnCode, opRunning = wrapper.hashStatus(library, opID)
        if (int(returnCode) != 0) or (opRunning != True):
            break
    print('\nHashDirectory has finished.')
    return True, int(returnCode)


def logTestResults(testName, expRes, actRes, errMsg=None):
    log.error("{} - expected result: {}, actual result: {}, message: {}".format(
        testName,
        wrapper.ReturnCodes[expRes],
        wrapper.ReturnCodes[actRes] if isinstance(actRes, int) else actRes,
        errMsg if errMsg else ''
    ))


def test1_positiveTestCase():
    """positive test case - check the error code"""
    expectedReturnCode = 0
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, "./tested_dir")
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)
        if returnCode != expectedReturnCode:
            log.error("test1_positiveTestCase - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test1_positiveTestCase - {}".format(e))
        print(e)
        return False


def test2_checkCountOfHashedFiles():
    """check count of hashed files and count of files in tested directory, tested directiory must not be empty"""
    testedDirectory = "./tested_dir"
    files = []
    with os.scandir(testedDirectory) as entries:
        for entry in entries:
            if entry.is_file():
                files.append(entry.name)

    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, testedDirectory)
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)

        if files and not logLines:
            log.error("test2_checkCountOfHashedFiles - count of files in directory: {},files hashed: 0".format(len(files)))
            return False
        elif files and logLines and len(files) != len(logLines):
            log.error("test2_checkCountOfHashedFiles - count of files in directory: {},files hashed: {}".format(
                len(files), len(logLines)
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test4_checkCountOfHashedFiles - {}".format(e))
        print(e)
        return False


def test3_checkNamesOfHashedFiles():
    """check count of hashed files and count of files in tested directory and compare them,
    tested directiory must not be empty"""
    testedDirectory = "./tested_dir"
    files = []
    with os.scandir(testedDirectory) as entries:
        for entry in entries:
            if entry.is_file():
                files.append(entry)
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, testedDirectory)
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)

        actualHashedFiles = []
        for logLine in logLines:
            actualHashedFiles.append(logLine[1:])

        calculatedHashedFiles = []
        for file in files:
            with open(file, "rb") as input_file:
                content = input_file.read()
                encoded_content = hashlib.md5(content)
                calculatedmd5 = encoded_content.hexdigest()
                # if "b'" at the begining is a bug
                # calculatedHashedFiles.append([file.name, calculatedmd5])
                calculatedHashedFiles.append(["b'"+file.name, "b'"+calculatedmd5])

        # Comment:
        # 1) I add string "b'" (I expect, it is not a bug, that the data in rows contains "b'" at the beginning),
        # 2) file names contains / or /. (/rootfs-pkgs.txt)
        # 3) this files are not from tested directoty

        if sorted(calculatedmd5[0]) != sorted(actualHashedFiles[0]):
            log.error("test3_checkNamesOfHashedFiles - comparison of file names failed")
            return False
    except Exception as e:
        log.exception("test3_checkNamesOfHashedFiles - {}".format(e))
        print(e)
        return False


def test4_checkHashesOfHashedFiles():
    """check MD5 hashes of hashed files and compare them with calculated hashes"""
    testedDirectory = "./tested_dir"
    files = []
    with os.scandir(testedDirectory) as entries:
        for entry in entries:
            if entry.is_file():
                files.append(entry)
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, testedDirectory)
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)

        actualHashedFiles = []
        for logLine in logLines:
            actualHashedFiles.append(logLine[1:])

        calculatedHashedFiles = []
        for file in files:
            with open(file, "rb") as input_file:
                content = input_file.read()
                encoded_content = hashlib.md5(content)
                calculatedmd5 = encoded_content.hexdigest()
                # calculatedHashedFiles.append([file.name, calculatedmd5])
                calculatedHashedFiles.append(["b'"+file.name, "b'"+calculatedmd5])

        # Comment:
        # hash MD5 - usually 32 lowercase hexadecimal digits ('d48691948fc6267bf5bc3715382e5ba4'),
        # here I can see in debug mode this format: b'FFF094F5139CA6F3EE01BC94F4E3A3'
        # now the test can not pass, files are not from tested direcotry

        if sorted(calculatedmd5[0]) == sorted(actualHashedFiles[0]):
            if sorted(calculatedmd5[1]) != sorted(actualHashedFiles[1]):
                log.error("test4_checkHashesOfHashedFiles - comparison of hashes failed")
                return False
            else:
                return True
        else:
            log.error("test4_checkHashesOfHashedFiles - comparison of file names failed")
            return False
    except Exception as e:
        log.exception("test4_checkHashesOfHashedFiles - {}".format(e))
        print(e)
        return False


def test5_checkIDsOfHashedFiles():
    """check if IDs (identifier of the operation) in output are unique"""
    testedDirectory = "/home/lenka/PycharmProjects/pythonProject_HID/tested_dir"
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, testedDirectory)
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)

        actualHashedFilesIDs = []
        for logLine in logLines:
            actualHashedFilesIDs.append(logLine[0])

        for identifier in actualHashedFilesIDs:
            if actualHashedFilesIDs.count(identifier) != 1:
                log.error("test5_checkIDsOfHashedFiles - ID {} is not unique identifier".format(identifier))
                return False
            else:
                return True
    except Exception as e:
        log.exception("test5_checkIDsOfHashedFiles - {}".format(e))
        print(e)
        return False


# checking of error codes

def test6_hashInitTwice():
    """check the error code after second hashInit"""
    expectedReturnCode = 8
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode = wrapper.hashInit(lib)
        wrapper.hashTerminate(lib)
        if returnCode != expectedReturnCode:
            log.error("test6_hashInitTwice - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test6_hashInitTwice - {}".format(e))
        print(e)
        return False


def test7_fileInsteadOfDirectory():
    """testedDirectory is not a directory (is path to file)  - check the error code"""
    expectedReturnCode = 5
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib,  "./tested_dir/HID_QA_TestSpecification.pdf")
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)
        if returnCode != expectedReturnCode:
            log.error("test7_fileInsteadOfDirectory - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test7_fileInsteadOfDirectory - {}".format(e))
        print(e)
        return False


def test8_nonExistingDirectory():
    """testedDirectory does not exist - check the error code"""
    expectedReturnCode = 5
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, "./dir_none")
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)
        if returnCode != expectedReturnCode:
            log.error("test8_nonExistingDirectory - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode2]
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test8_nonExistingDirectory - {}".format(e))
        print(e)
        return False


# directory HASH_ERROR_ARGUMENT_NULL 6


def test9_missingHashInitBeforeHashDirectory():
    """check the error code after hashDirectory - not initialized before"""
    expectedReturnCode = 7
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        returnCode, ID = wrapper.hashDirectory(lib, "./tested_dir")

        if returnCode != expectedReturnCode:
            log.error("test9_missingHashInitBeforeHashDirectory - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test9_missingHashInitBeforeHashDirectory - {}".format(e))
        print(e)
        return False


def test10_missingHashInitBeforeTerminate():
    """check the error code after hashTerminete - missing hashInit before"""
    expectedReturnCode = 7
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        returnCode = wrapper.hashTerminate(lib)
        if returnCode != expectedReturnCode:
            log.error("test10_missingHashInitBeforeTerminate - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test10_missingHashInitBeforeTerminate - {}".format(e))
        print(e)
        return False

# status -

def test11_hashStopTwice():
    """check the error code after hashStop twice"""
    expectedReturnCode = 2 # here I am not sure, if this code is well
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, "./tested_dir")
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
                returnCode3 = wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)
        if returnCode3 != expectedReturnCode:
            log.error("test11_hashStopTwice - expected result for hashStop valid once more: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test11_hashStopTwice - {}".format(e))
        print(e)
        return False


def test12_hashStopInvalidID():
    """check the error code after hashStop with invalid ID"""
    expectedReturnCode = 5
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, "./tested_dir")
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                returnCode3 = wrapper.hashStop(lib, 2)
                returnCode4 = wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)
        if returnCode3 != expectedReturnCode:
            log.error("test12_hashStopInvalidID - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]
            ))
            return False
        if returnCode4 != 0:
            log.error("test12_hashStopInvalidID - expected result for second hashStop (valid): {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test12_hashStopInvalidID - {}".format(e))
        print(e)
        return False


def test13_hashStopAfterTerminate():
    """check the error code - hashStop after hashTerminate"""
    expectedReturnCode = 7
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, "./tested_dir")
        if returnCode == 0:
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)
        returnCode3 = wrapper.hashStop(lib, ID)
        if returnCode3 != expectedReturnCode:
            log.error("test13_hashStopAfterTerminate - expected result for hashStop after hashTerminate: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test13_hashStopAfterTerminate - {}".format(e))
        print(e)
        return False

def test14_hashTerminateTwice():
    """check the error code after hashTerminate twice"""
    expectedReturnCode = 7
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        wrapper.hashTerminate(lib)
        returnCode = wrapper.hashTerminate(lib)
        if returnCode != expectedReturnCode:
            log.error("test14_hashTerminateTwice - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]
            ))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test14_hashTerminateTwice - {}".format(e))
        print(e)
        return False


def main(test_suit):
    counter = 0
    for test in test_suit:
        try:
            result = test()
            if not result:
                counter += 1
            # else is here for better debugging
            # else:
            #     log.info("OK")
        except Exception as e:
            log.exception(e)

    log.info("{} tests failed".format(counter))


tests_to_run = [
    test1_positiveTestCase,
    test2_checkCountOfHashedFiles,
    test3_checkNamesOfHashedFiles,
    test4_checkHashesOfHashedFiles,
    test5_checkIDsOfHashedFiles,
    test6_hashInitTwice,
    test7_fileInsteadOfDirectory,
    test8_nonExistingDirectory,
    test9_missingHashInitBeforeHashDirectory,
    test10_missingHashInitBeforeTerminate,
    test11_hashStopTwice,
    test12_hashStopInvalidID,
    test13_hashStopAfterTerminate,
    test14_hashTerminateTwice
]

if __name__ == '__main__':
    main(tests_to_run)
