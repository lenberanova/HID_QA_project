import ctypes
import wrapper
import sys
from logger import log


def readhashLog(library):
    print('')
    while True:
        returnCode, logLine = wrapper.hashReadNextLogLine(library)
        if (int(returnCode) == 0): 
            print('HashReadNextLogLine: {}.'.format(logLine))
        else:
            break
    return 


def waitforHashDirectory(library, opID:int):
    while True:
        returnCode, opRunning = wrapper.hashStatus(library, opID)
        if ((int(returnCode) != 0) or (opRunning != True)): 
            break
    print('\nHashDirectory has finished.')
    return True


def logTestResults(testName, expRes, actRes):
    log.error("{} - expected result: {}, actual result: {}".format(testName, wrapper.ReturnCodes[expRes], wrapper.ReturnCodes[actRes]))


def test1():
    lib = wrapper.loadHashLibrary("libhash.so")

    # Try to load a non-existing library
    # lib = wrapper.loadHashLibrary("./libhashNone.so")

    wrapper.hashInit(lib)
    returnCode, ID = wrapper.hashDirectory(lib, ".tested_dir")
    expectedReturnCode = 0
    if (returnCode == expectedReturnCode):
        ret = waitforHashDirectory(lib, ID)
        if (ret):
            readhashLog(lib)
            wrapper.hashStop(lib, ID)
    else:
        wrapper.hashTerminate(lib)
        return False, expectedReturnCode, returnCode
    wrapper.hashTerminate(lib)

    return True, None, None


def test2():
    lib = wrapper.loadHashLibrary("libhash.so")
    returnCode, ID = wrapper.hashDirectory(lib, ".tested_dir")
    wrapper.hashTerminate(lib)
    expectedReturnCode = 7
    if (returnCode == expectedReturnCode):
        pass
    else:
        return False, expectedReturnCode, returnCode
    return True, None, None


def test3():
    lib = wrapper.loadHashLibrary("libhash.so")
    returnCode, ID = wrapper.hashDirectory(lib, ".tested_dir")
    wrapper.hashTerminate(lib)
    expectedReturnCode = 7
    if (returnCode == expectedReturnCode):
        # ret = waitforHashDirectory(lib, ID)
        # if (ret):
        #     readhashLog(lib)
        #     wrapper.hashStop(lib, ID)
        pass
    else:
        return False, expectedReturnCode, returnCode
    return True, None, None



def main(test_suit):
    counter = 0
    for test in test_suit:
        try:
            result, expectedResultCode, resultCode = test()
            if not result:
                logTestResults(test.__name__, expectedResultCode, resultCode)
                counter += 1
            # else - for better debugging, will be removed
            else:
                log.info("OK")
        except Exception as e:
            print(e)
            log.exception(e)

    log.info("{} tests failed".format(counter))


tests_to_run = [
    test1,
    test2
]


if __name__ == '__main__':
    main(tests_to_run)
