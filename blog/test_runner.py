import json
import unittest
from pathlib import Path

from django.conf import settings
from django.test.runner import DiscoverRunner


class ReportingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.subtest_failures = set()

    def record(self, test, status, detail=''):
        self.records.append({'test': test.id(), 'status': status, 'detail': detail})

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, 'PASS')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, 'FAIL', self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, 'ERROR', self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, 'SKIP', reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.record(test, 'EXPECTED FAILURE', self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.record(test, 'UNEXPECTED SUCCESS')

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.subtest_failures.add(test.id())
            self.record(subtest, 'FAIL' if issubclass(err[0], test.failureException) else 'ERROR', self._exc_info_to_string(err, test))


class ReportingRunner(DiscoverRunner):
    def get_resultclass(self):
        return ReportingResult

    def run_suite(self, suite, **kwargs):
        result = super().run_suite(suite, **kwargs)
        output = Path(settings.BASE_DIR) / 'reports'
        output.mkdir(exist_ok=True)
        data = {'tests_run': result.testsRun, 'successful': result.wasSuccessful(), 'results': result.records}
        (output / 'test-results.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        from tools.build_report import build_report
        build_report(data)
        return result
