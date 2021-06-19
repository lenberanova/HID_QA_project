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
        if (int(returnCode) == 0):
            print('HashReadNextLogLine: {}.'.format(logLine))
            logLineParsed = logLine.split()
            hashedFilesLogLines.append(logLineParsed)
        else:
            break
    return hashedFilesLogLines


def waitforHashDirectory(library, opID:int):
    while True:
        returnCode, opRunning = wrapper.hashStatus(library, opID)
        if ((int(returnCode) != 0) or (opRunning != True)):
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


def test1_positiveTC():
    """positive test case - check the error code"""
    expectedReturnCode = 0
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, "./tested_dir")
        if (returnCode == 0):
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if (ret):
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)
        if returnCode != expectedReturnCode:
            log.error("test1_positiveTC - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test1_positiveTC - {}".format(e))
        print(e)
        return False


def test2_invalidDirectory():
    """testedDirectory is not a directory (is path to file)  - check the error code"""
    expectedReturnCode = 5
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib,  "./tested_dir/HID_QA_TestSpecification.pdf")
        if (returnCode == 0):
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if (ret):
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)
        if returnCode != expectedReturnCode:
            log.error("test2_invalidDirectory - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode]))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test2_invalidDirectory - {}".format(e))
        print(e)
        return False


def test3_nonExistingDirectory():
    """testedDirectory does not exist - check the error code"""
    expectedReturnCode = 5
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, "./dir_none")
        if (returnCode == 0):
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if (ret):
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)
        if returnCode != expectedReturnCode:
            log.error("test3_nonExistingDirectory - expected result: {}, actual result: {}".format(
                wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCode2]))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test3_nonExistingDirectory - {}".format(e))
        print(e)
        return False


def test4_checkCountOfHashedFiles():
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
        if (returnCode == 0):
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if (ret):
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)

        if files and not logLines:
            log.error("test4_checkCountOfHashedFiles - count of files in directory: {},files hashed: 0".format(len(files)))
            return False
        elif files and logLines and len(files) != len(logLines):
            log.error("test4_checkCountOfHashedFiles - count of files in directory: {},files hashed: {}".format(len(files), len(logLines)))
            return False
        else:
            return True
    except Exception as e:
        log.exception("test4_checkCountOfHashedFiles - {}".format(e))
        print(e)
        return False


def test5_checkNamesOfHashedFiles():
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
        if (returnCode == 0):
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if (ret):
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
            log.error("test5_checkNamesOfHashedFiles - comparism of file names failed")
            return False
    except Exception as e:
        log.exception("test5_checkNamesOfHashedFiles - {}".format(e))
        print(e)
        return False

def test6_checkHashesOfHashedFiles():
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
        if (returnCode == 0):
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if (ret):
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
                log.error("test6_checkHashesOfHashedFiles - comparism of hashes failed")
                return False
            else:
                return True
        else:
            log.error("test6_checkHashesOfHashedFiles - comparism of file names failed")
            return False
    except Exception as e:
        log.exception("test6_checkHashesOfHashedFiles - {}".format(e))
        print(e)
        return False


def test7_checkIDsOfHashedFiles():
    """check if IDs (identifier of the operation) in output are unique"""
    testedDirectory = "/home/lenka/PycharmProjects/pythonProject_HID/tested_dir"
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        wrapper.hashInit(lib)
        returnCode, ID = wrapper.hashDirectory(lib, testedDirectory)
        if (returnCode == 0):
            ret, returnCode2 = waitforHashDirectory(lib, ID)
            if (ret):
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)
        wrapper.hashTerminate(lib)

        actualHashedFilesIDs = []
        for logLine in logLines:
            actualHashedFilesIDs.append(logLine[0])

        for identifier in actualHashedFilesIDs:
            if actualHashedFilesIDs.count(identifier) != 1:
                log.error("test7_checkIDsOfHashedFiles - ID {} is not unique identifier".format(identifier))
                return False
            else:
                return True
    except Exception as e:
        log.exception("test7_checkIDsOfHashedFiles - {}".format(e))
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
    test1_positiveTC,
    test2_invalidDirectory,
    test3_nonExistingDirectory,
    test4_checkCountOfHashedFiles,
    test5_checkNamesOfHashedFiles,
    test6_checkHashesOfHashedFiles,
    test7_checkIDsOfHashedFiles
]

if __name__ == '__main__':
    main(tests_to_run)
