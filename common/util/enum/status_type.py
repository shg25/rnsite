# JSend の status の Enum
# https://github.com/omniti-labs/jsend
from enum import Enum


class StatusType(Enum):
    success = 'success'
    fail = 'fail'
    error = 'error'
