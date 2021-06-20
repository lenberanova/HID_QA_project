#!/usr/bin/env python3

import wrapper
import os
from logger import log
import hashlib
import inspect

inputLib = "libhash.so"
inputDirectory = "./tested_dir"


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
        if int(returnCode) != 0 or not opRunning:
            break
    print('\nHashDirectory has finished.')
    return True, int(returnCode)


# tests

def test1_positiveTestCase():
    """positive test case - check the error code"""
    expectedReturnCode = 0
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        lib = wrapper.loadHashLibrary(inputLib)
        returnCodeI = wrapper.hashInit(lib)
        if returnCodeI != expectedReturnCode:
            log.error("{} - expected result hashInit: {}, actual result: {}".format(
                testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeI]
            ))
        returnCodeD, ID = wrapper.hashDirectory(lib, inputDirectory)
        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                returnCodeS = wrapper.hashStop(lib, ID)
                if returnCodeS != expectedReturnCode:
                    log.error("{} - expected result hashStop: {}, actual result: {}".format(
                        testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeS]
                    ))
            if returnCodeW != expectedReturnCode:
                log.error("{} - expected result waitforHashDirectory: {}, actual result: {}".format(
                    testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeW]
                ))
            else:
                testPassed = True
        else:
            log.error("{} - expected result hashDirectory: {}, actual result: {}".format(
                testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeD]
            ))

        returnCodeT = wrapper.hashTerminate(lib)
        if returnCodeT != expectedReturnCode:
            log.error("{} - expected result hashTerminate: {}, actual result: {}".format(
                testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeT]
            ))
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test2_checkCountOfHashedFiles():
    """check count of hashed files and count of files in tested directory, tested directory must not be empty"""
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        files = []
        with os.scandir(inputDirectory) as entries:
            for entry in entries:
                if entry.is_file():
                    files.append(entry.name)

        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeD, ID = wrapper.hashDirectory(lib, inputDirectory)

        logLines = None
        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)

        if files and not logLines:
            log.error("{} - count of files in directory: {},files hashed: 0".format(testName, len(files)))
        elif files and logLines and len(files) != len(logLines):
            log.error("{} - count of files in directory: {},files hashed: {}".format(testName, len(files), len(logLines)))
        else:
            testPassed = True
        wrapper.hashTerminate(lib)
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test3_checkNamesOfHashedFiles():
    """check count of hashed files and count of files in tested directory and compare them,
    tested directiory must not be empty"""
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        files = []
        with os.scandir(inputDirectory) as entries:
            for entry in entries:
                if entry.is_file():
                    files.append(entry)
        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeD, ID = wrapper.hashDirectory(lib, inputDirectory)

        logLines = []
        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)

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
                    calculatedHashedFiles.append(["b'" + file.name, "b'" + calculatedmd5])

            # Comment:
            # 1) I add string "b'" (I expect, it is not a bug, that the data in rows contains "b'" at the beginning),
            # 2) file names contains / or /. (/rootfs-pkgs.txt)
            # 3) this files are not from tested directoty

            if sorted(calculatedmd5[0]) != sorted(actualHashedFiles[0]):
                log.error("{} - comparison of file names failed".format(testName))
            else:
                testPassed = True

        wrapper.hashTerminate(lib)
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test4_checkHashesOfHashedFiles():
    """check MD5 hashes of hashed files and compare them with calculated hashes"""
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        files = []
        with os.scandir(inputDirectory) as entries:
            for entry in entries:
                if entry.is_file():
                    files.append(entry)

        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeD, ID = wrapper.hashDirectory(lib, inputDirectory)
        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)

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
                        calculatedHashedFiles.append(["b'" + file.name, "b'" + calculatedmd5])

                # Comment:
                # hash MD5 - usually 32 lowercase hexadecimal digits ('d48691948fc6267bf5bc3715382e5ba4'),
                # here I can see in debug mode this format: b'FFF094F5139CA6F3EE01BC94F4E3A3'
                # now the test can not pass, files are not from tested direcotry

                if sorted(calculatedmd5[0]) == sorted(actualHashedFiles[0]):
                    if sorted(calculatedmd5[1]) != sorted(actualHashedFiles[1]):
                        log.error("{} - comparison of hashes failed".format(testName))
                    else:
                        testPassed = True
                else:
                    log.error("{} - comparison of file names failed".format(testName))
            wrapper.hashTerminate(lib)
            return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test5_checkIDsOfHashedFiles():
    """check if IDs (identifier of the operation) in output are unique"""
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeD, ID = wrapper.hashDirectory(lib, inputDirectory)

        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                logLines = readhashLog(lib)
                wrapper.hashStop(lib, ID)

                actualHashedFilesIDs = []
                for logLine in logLines:
                    actualHashedFilesIDs.append(logLine[0])

                for identifier in actualHashedFilesIDs:
                    if actualHashedFilesIDs.count(identifier) != 1:
                        log.error("{} - ID {} is not unique identifier".format(testName, identifier))
                        break
                    else:
                        testPassed = True
        wrapper.hashTerminate(lib)
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


# checking of error codes

def test6_hashInitTwice():
    """check the error code after second hashInit"""
    expectedReturnCode = 8
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeI = wrapper.hashInit(lib)

        if returnCodeI != expectedReturnCode:
            log.error("{} - expected result hashInit: {}, actual result: {}".format(
                testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeI]
            ))
        else:
            testPassed = True
        wrapper.hashTerminate(lib)
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test7_fileInsteadOfDirectory():
    """testedDirectory is not a directory (is path to file)  - check the error code"""
    expectedReturnCode = 5
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeD, ID = wrapper.hashDirectory(lib,  "./tested_dir/HID_QA_TestSpecification.pdf")
        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                wrapper.hashStop(lib, ID)

        if returnCodeD != expectedReturnCode:
            log.error("{} - expected result hashDirectory: {}, actual result: {}".format(
                testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeD]
            ))
        else:
            testPassed = True

        wrapper.hashTerminate(lib)
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test8_nonExistingDirectory():
    """testedDirectory does not exist - check the error code"""
    expectedReturnCode = 5
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeD, ID = wrapper.hashDirectory(lib, "./dir_none")
        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                wrapper.hashStop(lib, ID)

                if returnCodeD != expectedReturnCode:
                    log.error("{} - expected result hashDirectory: {}, actual result: {}".format(
                    testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeD]
                    ))
                else:
                    testPassed = True
        wrapper.hashTerminate(lib)
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test9_missingHashInitBeforeHashDirectory():
    """check the error code after hashDirectory - not initialized before"""
    expectedReturnCode = 7
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        lib = wrapper.loadHashLibrary(inputLib)
        returnCodeD, ID = wrapper.hashDirectory(lib, inputDirectory)

        if returnCodeD != expectedReturnCode:
            log.error("{} - expected result hashDirectory: {}, actual result: {}".format(
                testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeD]
            ))
            return False
        return True
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test10_missingHashInitBeforeTerminate():
    """check the error code after hashTerminete - missing hashInit before"""
    expectedReturnCode = 7
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        lib = wrapper.loadHashLibrary("libhash.so")
        returnCodeT = wrapper.hashTerminate(lib)
        if returnCodeT != expectedReturnCode:
            log.error("{} - expected result hashTerminate: {}, actual result: {}".format(
                testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeT]
            ))
            return False
        return True
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test11_hashStopTwice():
    """check the error code after hashStop twice"""
    expectedReturnCode = 5
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeD, ID = wrapper.hashDirectory(lib, inputDirectory)

        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
                returnCodeS = wrapper.hashStop(lib, ID)

                if returnCodeS != expectedReturnCode:
                    log.error("{} - expected result for second hashStop (valid): {}, actual result: {}".format(
                        testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeS]
                    ))
                else:
                    testPassed = True
        wrapper.hashTerminate(lib)
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test12_hashStopInvalidID():
    """check the error code after hashStop with invalid ID"""
    expectedReturnCode = 5
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeD, ID = wrapper.hashDirectory(lib, inputDirectory)
        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                returnCodeS = wrapper.hashStop(lib, 2)
                returnCodeS2 = wrapper.hashStop(lib, ID)

                if returnCodeS != expectedReturnCode:
                    log.error("{} - expected result hashStop (invalid): {}, actual result: {}".format(
                        testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeS]
                    ))
                if returnCodeS2 != 0:
                    log.error("{} - expected result for second hashStop (valid): {}, actual result: {}".format(
                        testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeS2]
                    ))
                if returnCodeS == expectedReturnCode and returnCodeS2 == 0:
                    testPassed = True

        wrapper.hashTerminate(lib)
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test13_hashStopAfterTerminate():
    """check the error code - hashStop after hashTerminate"""
    expectedReturnCode = 5
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        testPassed = False

        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        returnCodeD, ID = wrapper.hashDirectory(lib, inputDirectory)
        if returnCodeD == 0:
            ret, returnCodeW = waitforHashDirectory(lib, ID)
            if ret:
                readhashLog(lib)
                wrapper.hashStop(lib, ID)
                wrapper.hashTerminate(lib)
                returnCodeS = wrapper.hashStop(lib, ID)

                if returnCodeS != expectedReturnCode:
                    log.error("{} - expected result for hashStop after hashTerminate: {}, actual result: {}".format(
                        testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeS]
                    ))
                else:
                    testPassed = True
        wrapper.hashTerminate(lib)
        return testPassed
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def test14_hashTerminateTwice():
    """check the error code after hashTerminate twice"""
    expectedReturnCode = 7
    testName = inspect.getframeinfo(inspect.currentframe()).function
    try:
        lib = wrapper.loadHashLibrary(inputLib)
        wrapper.hashInit(lib)
        wrapper.hashTerminate(lib)
        returnCodeT = wrapper.hashTerminate(lib)
        if returnCodeT != expectedReturnCode:
            log.error("{} - expected  hashTerminate: {}, actual result: {}".format(
                testName, wrapper.ReturnCodes[expectedReturnCode], wrapper.ReturnCodes[returnCodeT]
            ))
            return False
        return True
    except Exception as e:
        log.exception("{} - {}".format(testName, e))
        print(e)
        return False


def main(test_suit):
    counter = 0
    for test in test_suit:
        try:
            result = test()
            if not result:
                counter += 1
            else:
                log.info("ok")
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
