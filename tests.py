import ctypes
import os
import time
from ctypes import *
from logger import log
from enum import Enum
from pathlib import Path


class ResultTest(Enum):
    # Success
    HASH_ERROR_OK = 0
    # Unknown error
    HASH_ERROR_GENERAL = 1
    # Standard exception encountered
    HASH_ERROR_EXCEPTION = 2
    # Memory allocation failed
    HASH_ERROR_MEMORY = 3
    # Reading an empty log
    HASH_ERROR_LOG_EMPTY = 4
    # Invalid argument passed to a function
    HASH_ERROR_ARGUMENT_INVALID = 5
    # Empty argument passed to a function
    HASH_ERROR_ARGUMENT_NULL = 6
    # Library is not initialized
    HASH_ERROR_NOT_INITIALIZED = 7
    # Library is already initialized
    HASH_ERROR_ALREADY_INITIALIZED = 8


def load_library(library_name):
    """load the library"""
    return ctypes.CDLL(library_name)


def log_test_results(msg):
    """print the error message into the log"""
    log.error("{} - expected result: {}, actual result: {}".format(msg[0], msg[1], msg[2]))


def test_1_hash_init():
    """test 'uint32_t HashInit()' - positive test case"""
    library = load_library("libhash.so")

    result = library.HashInit()
    expected_result = ResultTest.HASH_ERROR_OK

    msg = "test_1_hash_init()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_2_hash_init():
    """test 'uint32_t HashInit()' - negative test case (an unexpected argument 'x')"""
    library = load_library("libhash.so")
    x = ctypes.c_size_t(1)

    result = library.HashInit(x)
    expected_result = ResultTest.HASH_ERROR_EXCEPTION

    msg = "test_2_hash_init()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_3_hash_init():
    """test 'uint32_t HashInit()' - negative test case (call the HashInit() twice)"""
    library = load_library("libhash.so")
    library.HashInit()

    result = library.HashInit()
    expected_result = ResultTest.HASH_ERROR_ALREADY_INITIALIZED

    msg = "test_3_hash_init()", expected_result.name, ResultTest(result).name
    return result == expected_result.value,  msg


def test_4_hash_terminate():
    """test 'uint32_t HashTerminate()' - positive test case"""
    library = load_library("libhash.so")
    library.HashInit()

    result = library.HashTerminate()
    expected_result = ResultTest.HASH_ERROR_OK

    msg = "test_4_hash_terminate()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_5_hash_terminate():
    """test 'uint32_t HashTerminate()' - negative test case (call the HashTerminate() without HashInit() before)"""
    library = load_library("libhash.so")

    result = library.HashTerminate()
    expected_result = ResultTest.HASH_ERROR_NOT_INITIALIZED

    msg = "test_5_hash_terminate()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_6_hash_terminate():
    """test 'uint32_t HashTerminate()' - negative test case (an unexpected argument 'x')"""
    library = load_library("libhash.so")
    library.HashInit()
    x = ctypes.c_size_t(1)

    result = library.HashTerminate(x)
    expected_result = ResultTest.HASH_ERROR_EXCEPTION

    msg = "test_6_hash_terminate()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_7_hash_directory():
    """test 'uint32_t HashDirectory(const char* directory, size_t* id)' - positive test case"""
    library = load_library("libhash.so")
    library.HashInit()

    # types of calling parameters
    library.HashDirectory.argtypes = [ctypes.c_char_p, POINTER(ctypes.c_size_t)]
    # result type
    library.HashDirectory.restype = ctypes.c_size_t

    path = "./tested_dir"
    b_path = path.encode('utf-8')
    operation_id = ctypes.c_size_t(1)

    result = library.HashDirectory(b_path, byref(operation_id))
    expected_result = ResultTest.HASH_ERROR_OK

    msg = "test_7_hash_directory()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_8_hash_directory():
    """test 'uint32_t HashDirectory(const char* directory, size_t* id)' - negative test case
    (path to directory = None)"""
    library = load_library("libhash.so")
    library.HashInit()

    # types of calling parameters
    library.HashDirectory.argtypes = [ctypes.c_char_p, POINTER(ctypes.c_size_t)]
    # result type
    library.HashDirectory.restype = ctypes.c_size_t

    operation_id = ctypes.c_size_t(1)

    result = library.HashDirectory(None, byref(operation_id))
    expected_result = ResultTest.HASH_ERROR_ARGUMENT_NULL

    msg = "test_8_hash_directory()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_9_hash_directory():
    """test 'uint32_t HashDirectory(const char* directory, size_t* id)' - negative test case (id = None)"""
    library = load_library("libhash.so")
    library.HashInit()

    # types of calling parameters
    library.HashDirectory.argtypes = [ctypes.c_char_p, POINTER(ctypes.c_size_t)]
    # result type
    library.HashDirectory.restype = ctypes.c_size_t

    path = "./tested_dir"
    b_path = path.encode('utf-8')

    result = library.HashDirectory(b_path, None)
    expected_result = ResultTest.HASH_ERROR_ARGUMENT_NULL

    msg = "test_9_hash_directory()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_10_hash_directory():
    """test 'uint32_t HashDirectory(const char* directory, size_t* id)' - negative test case
     (path to directory = None, id = None)"""
    library = load_library("libhash.so")
    library.HashInit()

    # types of calling parameters
    library.HashDirectory.argtypes = [ctypes.c_char_p, POINTER(ctypes.c_size_t)]
    # result type
    library.HashDirectory.restype = ctypes.c_size_t

    result = library.HashDirectory(None, None)
    expected_result = ResultTest.HASH_ERROR_ARGUMENT_NULL

    msg = "test_10_hash_directory()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_11_hash_directory():
    """test 'uint32_t HashDirectory(const char* directory, size_t* id)' - negative test case (operation_id = -1)"""
    library = load_library("libhash.so")
    library.HashInit()

    # types of calling parameters
    library.HashDirectory.argtypes = [ctypes.c_char_p, POINTER(ctypes.c_size_t)]
    # result type
    library.HashDirectory.restype = ctypes.c_size_t

    path = "./tested_dir"
    b_path = path.encode('utf-8')
    operation_id = ctypes.c_size_t(-1)

    result = library.HashDirectory(b_path, byref(operation_id))
    expected_result = ResultTest.HASH_ERROR_OK

    msg = "test_11_hash_directory()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


def test_12_hash_directory():
    """test 'uint32_t HashDirectory(const char* directory, size_t* id)' - negative test case
    (HashTerminate() before calling the HashDirectory())"""
    library = load_library("libhash.so")
    library.HashInit()
    library.HashTerminate()

    # types of calling parameters
    library.HashDirectory.argtypes = [ctypes.c_char_p, POINTER(ctypes.c_size_t)]
    # result type
    library.HashDirectory.restype = ctypes.c_size_t

    path = "./tested_dir"
    b_path = path.encode('utf-8')
    operation_id = ctypes.c_size_t(1)

    result = library.HashDirectory(b_path, byref(operation_id))
    expected_result = ResultTest.HASH_ERROR_NOT_INITIALIZED

    msg = "test_12_hash_directory()", expected_result.name, ResultTest(result).name
    return result == expected_result.value, msg


# def test_7_hash_directory():
#     library = load_library("libhash.so")
#     library.HashInit()
#
#     # types of calling parameters
#     library.HashDirectory.argtypes = [ctypes.c_char_p, POINTER(ctypes.c_size_t)]
#     # result type
#     library.HashDirectory.restype = ctypes.c_size_t
#
#     path = "./tested_dir"
#     # transfer strig to UTF-8
#     b_path = path.encode('utf-8')
#     operation_id = ctypes.c_size_t(1)  ####
#
#
#     result_1 = library.HashDirectory(b_path, byref(operation_id))
#     expected_result_1 = ResultTest.HASH_ERROR_OK
#
#     # types of calling parameters
#     library.HashStatus.argtypes = [ctypes.c_size_t, POINTER(ctypes.c_bool)]
#     # result type
#     library.HashStatus.restype = ctypes.c_size_t
#     running = ctypes.c_bool(True)
#     while library.HashStatus(operation_id, byref(running)) == ResultTest.HASH_ERROR_OK and running:
#         pass
#     # expected_result_2 = ResultTest.HASH_ERROR_OK
#
#     library.HashReadNextLogLine.argtypes = [POINTER(ctypes.c_char_p)]
#
#     line = ctypes.c_char_p()
#     result_x = library.HashReadNextLogLine(byref(line))
#     while result_x == 0: #########
#         line_value = str(line.value)
#         line_value_split = line_value.split(" ")
#         line_id = line_value_split[0][2:]
#         print(line_value)
#         print(line_id)
#
#         # types of calling parameters
#         library.HashFree.argtypes = [ctypes.c_void_p]
#         # result type
#         library.HashFree.restype = ctypes.c_size_t
#         result_4 = library.HashFree(line)
#         #expected_result_4 = ResultTest.HASH_ERROR_OK
#
#         time.sleep(0.1)
#         result_x = library.HashReadNextLogLine(byref(line))
#
#     # # types of calling parameters
#     # library.HashStop.argtypes = [ctypes.c_size_t]
#     # # result type
#     # library.HashStop.restype = ctypes.c_size_t
#     # result_5 = library.HashStop(operation_id)
#     # expected_result_5 = ResultTest.HASH_ERROR_OK
#     #
#     # # result_6 = library.HashTerminate()
#     # expected_result_6 = ResultTest.HASH_ERROR_OK
#
#
#     msg = "test_7_hash_directory()", expected_result_1.name, ResultTest(result_1).name
#     return result_1 == expected_result_1.value, msg
#

def main(test_suit):
    counter = 0
    for test in test_suit:
        test = test()
        if not test[0]:
            log_test_results(test[1])
            counter += 1
        else:
            log.info("OK")

    log.info("{} tests failed".format(counter))


tests_to_run = [
    test_1_hash_init,
    test_2_hash_init,
    test_3_hash_init,
    test_4_hash_terminate,
    test_5_hash_terminate,
    test_6_hash_terminate,
    # test_7_hash_directory
    test_8_hash_directory,
    test_9_hash_directory,
    test_10_hash_directory,
    # test_11_hash_directory,
    test_12_hash_directory
]

if __name__ == '__main__':
    main(tests_to_run)
