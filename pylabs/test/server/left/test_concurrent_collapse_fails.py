"""
Copyright (2010-2014) INCUBAID BVBA

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""



from .. import system_tests_common as Common
from arakoon.ArakoonExceptions import *
import arakoon
import time
from Compat import X
from threading import Thread
from nose.tools import *
import logging

@Common.with_custom_setup(Common.setup_1_node_mini, Common.basic_teardown)
def test_concurrent_collapse_fails():
    """ assert only one collapse goes through at any time (eta : 30s) """
    zero = Common.node_names[0]
    Common.stopOne(zero)
    Common._getCluster().setCollapseSlowdown(0.3)
    Common.startOne(zero)
    n = 29876
    logging.info("going to do %i sets to fill tlogs", n)
    Common.iterate_n_times(n, Common.simple_set)
    logging.info("Did %i sets, now going into collapse scenario", n)

    class SecondCollapseThread(Thread):
        def __init__(self, sleep_time):
            Thread.__init__(self)

            self.sleep_time = sleep_time
            self.exception_received = False

        def run(self):
            logging.info('Second collapser thread started, sleeping...')
            time.sleep(self.sleep_time)

            logging.info('Starting concurrent collapse')
            rc = Common.collapse(zero, 1)

            logging.info('Concurrent collapse returned %d', rc)

            if rc == 255:
                self.exception_received = True

    s = SecondCollapseThread(1)
    assert not s.exception_received

    logging.info('Launching second collapser thread')
    s.start()

    logging.info('Launching main collapse')
    Common.collapse(zero, 1)

    logging.info("collapsing finished")
    assert_true(s.exception_received)
