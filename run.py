import pytest
import os.path
import sys

if __name__ == '__main__':

    def _opt_present(opt):
        for a in sys.argv:
            if a.startswith(opt + '='):
                return True
        return False

    base_path = os.path.abspath(os.path.dirname(__file__))
    base_tmp = os.path.join(base_path, 'tmp').replace('\\', '/')

    opt = sys.argv
    opt.append(base_path.replace('\\', '/'))

    if not _opt_present('--basetemp'):
        opt .append( '--basetemp=' + base_tmp)

    if not _opt_present('--junitxml'):
        opt .append('--junitxml=result.junit.xml')
    opt.append('-v')
    exit_code = pytest.main(opt)
    sys.exit(exit_code)

