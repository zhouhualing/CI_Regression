import os
import sys
import os.path
import argparse
import xml.etree.ElementTree as ET
import time
import math
from collections import namedtuple
import copy

from framework.config.yml_manager import YmlManager
from framework.core.singleton import Singleton

NameVals = namedtuple('NameVals', 'name vals')


class TestCase(object):
    def __init__(self, script, tags=[], params=[], emails=[]):
        self._script = script
        self._tags = tags
        self._params = params
        self._emails = emails


    def _get_support_types(self):
        all_types = set(YmlManager().application)
        tt_set=set()

        for t in self._tags:
            if t.name != 'testType':
                continue
            tt = t.vals['value']
            exclude = t.vals.get('exclude', 'false') == 'true'

            if tt == 'NONE':
                return ['NONE']

            if tt == 'ALL':
                hw_set = all_types
                continue

            if exclude:
                tt_set.discard(tt)
            else:
                tt_set.add(tt)

        if not hw_set:
            return []

        return hw_set

    def __repr__(self):
        return os.path.splitext(os.path.basename(self._script))[0]

    @staticmethod
    def create_test_cases_from_file(tag_file, quitIfFileMissing=True):
        root = os.path.dirname(tag_file)
        tags = ET.parse(tag_file)
        for s in tags.iterfind('./script'):
            f = os.path.normpath(os.path.join(root, s.get('path')))
            if not os.path.exists(f):
                if quitIfFileMissing:
                    raise RuntimeError('unable to find ' + f)

                # for certain cases we want to continue to look for more test
                # scripts
                print('unable to find', f)
                continue

            tags = [NameVals(e.tag, e.attrib)
                    for e in s.iterfind('./requiredTags/*')]
            tags.extend([NameVals(e.tag, e.attrib)
                         for e in s.iterfind('./optionalTags/*')])
            params = [NameVals(e.tag, e.attrib)
                      for e in s.iterfind('./parameters/*')]
            emails = [e.get('value') for e in s.iterfind('./email')]
            yield TestCase(f, tags, params, emails)


class TestCaseManager(object,metaclass=Singleton):

    def __init__(self, path='.'):
        self._path = os.path.abspath(path)
        self._test_cases = []
        self.scan(self._path)

    def scan(self, path):
        for root, dirs, files in os.walk(path):
            for f in files:
                if not f.endswith('_info.xml'):
                    continue

                tag_file = os.path.join(root, f)
                for tc in TestCase.create_test_cases_from_file(tag_file):
                    self.add_test_case(tc)

    def add_test_case(self, tc):
        self._test_cases.append(tc)

    def get_test_cases(self):
        for tc in self._test_cases:
            yield tc

###############################################################################
def run_thot(config, timeout=0):
    sys.stdout.flush()
    os.system('python run.py "{0}" {1}'.format(config, timeout))
    sys.stdout.flush()

###############################################################################

def run():
    parser = argparse.ArgumentParser(
        description='Run regression tests',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--id', default='ci_regression', help='id')
    parser.add_argument('--work-dir', default='.', help='work directory')
    parser.add_argument('--script-dir', default='.',
                        help='regression script base directory')

    args = parser.parse_args()

    tcs = TestCaseManager(path=args.script_dir)
    try:
        run_thot(tcs)
    finally:
        pass


###############################################################################
if __name__ == '__main__':
    run()
