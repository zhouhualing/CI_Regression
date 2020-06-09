import pytest
import py
import os
import os.path
import subprocess
import shutil
import time
import errno
import stat
import getpass
import logging
from regression import TestCase


###############################################################################
class _Harness(object):
    def __init__(self):
        self.option = None
        self.tc_names = {}
        self.logger = {}
        self.config = None

    def getLogger(self, pid):
        if pid not in self.logger:
            logger = logging.getLogger(str(pid))
            logger.setLevel(logging.INFO)
            fh = logging.FileHandler("pid_" + str(pid) + ".log")
            formatter = logging.Formatter('%(asctime)s - %(process)d - %(thread)d - %(levelname)s : %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            self.logger[pid] = logger
            return logger

        return self.logger[str(pid)]


###############################################################################
_harness = _Harness()

###############################################################################
def pytest_addoption(parser):
    group = parser.getgroup('wd options')
    group.addoption('--timeout', action='store', type='int',
       default=600, dest='timeout',
       help='fail a test module after the given timeout. '
            'specify in seconds; 0 to disable timeout')

    group.addoption('--keep-all-tmpdir', action='store_true',
       default=False, dest='keep_all_tmpdir',
       help='keep all tmpdir; default keep only failed tmpdir')

    group.addoption('--archive-tmpdir', action='store_true',
       default=False, dest='archive_tmpdir',
       help='archive tmpdir')

    # group.addoption('--log-level', action='store', type='string',
    #     default='DEBUG', dest='log_level',
    #     help='Regression log level (DEBUG, INFO, WARN)')

    group.addoption('--check-in-delay', action='store', type='int',
                    default=0, dest='check_in_delay', help='Check in delay')

    group.addoption('--testexecuter', action='store', type='string',
                    default=None, dest='testexecuter', help='Path to test executer binary/script')


logger = logging.getLogger('regression')


###############################################################################
def pytest_configure(config):
    _harness.option = config.option

    if config.option.log_level == 'INFO':
        level = logging.INFO
    elif config.option.log_level == 'WARN':
        level = logging.WARN
    else:
        level = logging.DEBUG
    logger.setLevel(level)

###############################################################################
def pytest_cmdline_main(config):
    config.option.orig_basetemp = config.option.basetemp
    _harness.config = config
    print("execute main")

    #TODO hualing
    #do sth

###############################################################################
@pytest.mark.tryfirst
def pytest_unconfigure(config):
    #TODO hualing
    #undo sth
    if config.option.archive_tmpdir and os.path.exists(config.option.orig_basetemp):
        logging.shutdown()
        arch = shutil.make_archive('tmpdir', 'gztar', config.option.orig_basetemp)
        print('archive tmpdir to %s' % arch)


###############################################################################
def pytest_collect_file(path, parent):
    _filter = '_info.xml'
    if path.basename.endswith(_filter):
        return TestCaseFile(path, parent)

###############################################################################
class TestCaseFile(pytest.File):
    def collect(self):
        i = 0
        for tc in TestCase.create_test_cases_from_file(str(self.fspath), quitIfFileMissing=False):
            # reneable after we shorten the output path
            base_name = str(tc)
            name = base_name
            suffix = 1
            while name in _harness.tc_names:
                name = base_name + '_' + str(suffix)
                suffix += 1
            _harness.tc_names[name] = True

            yield PythonItem(name, self, tc, i)
            i += 1

###############################################################################
def pytest_collection_modifyitems(items, config):
    # TODO: add advance filter
    matchexpr = None
    if not matchexpr:
        return

###############################################################################
class PythonItem(pytest.Item):
    def __init__(self, name, parent, testcase, entry):
        super(PythonItem, self).__init__(name, parent)
        self.entry = entry
        self.testcase = testcase
        self.funcargs = {}
        self.keywords = {}

        # TODO: move to TestCase
        for name,vals in self.testcase._tags:
            if name not in set(['tag', 'package', 'regressionType']):
                continue
            if 'value' in vals and 'exclude' not in vals:
                self.keywords[vals['value']] = 1

        class _dummy_markers:
            pass
        self.markers = _dummy_markers()
        self.markers.__dict__.update(self.keywords)

        self.obj = self.markers

    def _makeid(self):
        return str(self.parent.nodeid).replace('/script_info.xml', '').replace('_info.xml', '') + '::' + self.name

    def setup(self):
        self.discard_tmpdir = False
        self.check_in_delay = _harness.option.check_in_delay
        self.testexecuter = _harness.option.testexecuter
        self.tmpdir = _harness.config.option.basetemp
        self.capfd = _harness.capfd

    def teardown(self):
        if self.discard_tmpdir:
            time.sleep(1)
            shutil.rmtree(str(self.tmpdir), onerror=self._handle_remove_readonly)


    def _handle_remove_readonly(self, func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
            func(path)
        else:
            raise

    def blltestargs(self):
        cwd = str(self.tmpdir)

        #TODO hualing
        if not os.path.exists(cwd):
            os.mkdir(cwd)

        tc = self.testcase
        args = ['python', tc._script]
        for p in tc._params:
            args.append('--' + p.name)
            value = p.vals.get('value', '')
            args.append(value)
        return {'args':args , 'cwd':cwd}

    def runtest(self):
        logger = _harness.getLogger(str(os.getpid()))
        base_path = os.path.abspath(os.path.dirname(__file__))

        env = {}
        env.update(os.environ)
        env['LOG_OUTPUT_DIRECTORY'] = str(self.tmpdir)
        env['INIT_ARGS'] = '--testresultsetting.saveOutputFilesInCwd=1'

        args_cwd = self.blltestargs()

        args = args_cwd['args']
        cwd = args_cwd['cwd']

        # add cwd to PATH environment variable
        env["PATH"] += os.pathsep + str(cwd)



        logger.info("Running %s with args: %s", self.name, str(args))

        p = subprocess.Popen(args, cwd=cwd, env=env)
        # TODO: add per test case timeout
        timeout = _harness.option.timeout
        rc = self.wait_for_script(p, timeout)

        logger.info("%s finished" , self.name)

        return


        script_out,script_err = self.capfd.readouterr()

        # Save the stdout/stderr to output.txt
        file_name = os.path.join(str(self.tmpdir), 'output.txt')
        with open(file_name, 'w') as fd:
            fd.write('-'*31+ 'Stdout' +'-'*31 +" \n\n")
            fd.write(script_out)
            fd.write("\n\n")
            fd.write('-'*31+ 'Stderr' +'-'*31 +" \n\n")

            fd.write(script_err)

        error_str = ""
        if script_err != "":
            error_str = "FAILED:\n" + script_err
        elif rc is None:
            error_str = "ERROR: test timed out after " + str(timeout) + " sec \n "
        elif rc != 0:
            error_str = "ERROR: test returned with exit code: " + str(rc)

        if error_str != "":
            raise TestCaseException(self, error_str, script_out)

        if not _harness.option.keep_all_tmpdir:
            self.discard_tmpdir = True

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, TestCaseException):
            s = '\n' + excinfo.value.args[1] + \
                    '\n\n' + '-'*31 + ' Captured stdout ' + '-'*31 + '\n\n' \
                    + excinfo.value.args[2]
            s += '\n\n'

            # format email string
            for email in self.testcase._emails:
                s += '@@@Email:' + email + '@@@\n'
            return s
        else:
            return "HARNESS ERROR: \n" + str(excinfo)

    def reportinfo(self):
        return self.fspath, self.entry, "test: %s" % self.name

    def wait_for_script(self, proc, timeout):
        """function to wait for a script, return return code of the process"""
        rc = None
        if timeout <= 0:
            rc = proc.wait()
        else:
            # TODO: enhance this
            start_time = time.time()
            rc = None
            while True:
                rc = proc.poll()
                if rc is not None:
                    break
                if (time.time() - start_time) > timeout:
                    #if sys.platform.startswith("win"):
                    #    subprocess.Popen("taskkill /T /PID %i"%p.pid , shell=True).wait()
                    #    time.sleep(5)
                    proc.kill()
                    break
                time.sleep(1)

        return rc

###############################################################################
class TestCaseException(Exception):
    pass



@pytest.fixture(autouse=True)
def _configure_application(request,capfd, monkeypatch):
    _harness.request = request
    _harness.capfd=capfd
    print("hello")
    out, err = capfd.readouterr()
    assert out == "hello\n"
