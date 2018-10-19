'''
test that all of the errors are getting raised correctly
'''
import pytest
from safeqthreads import errors


def test_errors():
    ''' make sure these can all be raised without issue '''
    errors_list = [errors.SafeQThreadsError,
                   errors.StopRunningNotBoolError,
                   errors.WorkerTypeError,
                   errors.WorkerAlreadyRegisteredError,
                   errors.SafeQThreadTypeError,
                   errors.MaxWaitSecondsTypeError]

    for error in errors_list:
        # make sure there is no problem raising the error
        with pytest.raises(error):
            raise error