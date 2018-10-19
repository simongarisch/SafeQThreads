import pytest
from safeqthreads import errors, descriptors


def test_stop_running_descriptor():
    ''' check to see that the can set and get from 
        this descriptor correctly
    '''
    class Tester(object):
        stop_running = descriptors.StopRunning()

    tester = Tester()
    # test that stop_running is False by default
    assert tester.stop_running is False
    
    # test that it must be a boolean
    with pytest.raises(errors.StopRunningNotBoolError):
        tester.stop_running = 22
    
    # and that we can change its value
    tester.stop_running = True
    assert tester.stop_running is True
    tester.stop_running = False
    assert tester.stop_running is False
