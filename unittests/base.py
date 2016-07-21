import os

import testtools


class UnittetsBaseCiCd(testtools.TestCase):

    def setUp(self):
        super(UnittetsBaseCiCd, self).setUp()
        # TODO: should be fixed future with some common approach for all tests
        root_dir = os.path.dirname(os.path.abspath(__file__)).rsplit('/', 1)[0]
        self.apps_dir = os.path.join(root_dir, 'murano-apps')
