from timeit import default_timer as timer


class ResultPrinter():

    def __init__(self, output, debug=False):
        self.output = output
        self.debug = debug
        self.assertions = 0
        self.progress_count = 0
        self.tests = 0
        self.tests_total = 0

    def on_tests_start(self, tests):
        self.tests_total = len(tests)
        self.start_time = timer()
        if self.debug:
            self.output.write('Starting {} test{}:\n\n'.format(
                len(tests),
                's' if len(tests) > 1 else ''
            ))

            for i, test in enumerate(tests, start=1):
                self.output.write('%d) %s\n' % (i, test))

    def on_tests_end(self, errors, skipped, failures, total_assertions):
        self.output.write('\n\n')
        self.output.write('Time: %.2f secs\n' % (timer() - self.start_time))
        self.output.write('\n')

        # ERRORS
        if len(errors) > 0:
            self.output.write("There %s %s error%s:\n" % (
                'was' if len(errors) == 1 else 'were',
                len(errors),
                '' if len(errors) == 1 else 's',
            ))
            self.output.write("\n")
            for i, error in enumerate(errors, start=1):
                self.output.write("%d) %s\n" % (i, error['message']))
                self.output.write("\n%s:%d:%d\n" % (error['file'], error['row'], error['col']))
                self.output.write("\n")

        # FAILURES
        if len(failures) > 0:
            if len(errors) > 0:
                self.output.write("--\n\n")

            self.output.write("There %s %s failure%s:\n\n" % (
                'was' if len(failures) == 1 else 'were',
                len(failures),
                '' if len(failures) == 1 else 's',
            ))

            for i, failure in enumerate(failures, start=1):
                self.output.write("%d) %s\n" % (i, failure['assertion']))
                self.output.write("Failed asserting %s equals %s\n" % (
                    str(failure['actual']), str(failure['expected'])))
                # TODO failure diff
                # self.output.write("--- Expected\n")
                # self.output.write("+++ Actual\n")
                # self.output.write("@@ @@\n")
                # self.output.write("{{diff}}\n\n")
                self.output.write("%s:%d:%d\n" % (failure['file'], failure['row'], failure['col']))
                self.output.write("\n")

        # SKIPPED
        if len(skipped) > 0:
            if (len(errors) + len(failures)) > 0:
                self.output.write("--\n\n")

            self.output.write("There %s %s skipped test%s:\n" % (
                'was' if len(skipped) == 1 else 'were',
                len(skipped),
                '' if len(skipped) == 1 else 's',
            ))
            self.output.write("\n")
            for i, skip in enumerate(skipped, start=1):
                self.output.write("%d) %s\n" % (i, skip['message']))
                self.output.write("\n%s:%d:%d\n" % (skip['file'], skip['row'], skip['col']))
                self.output.write("\n")

        # TOTALS
        if len(errors) == 0 and len(failures) == 0:
            self.output.write("OK (%d tests, %d assertions" % (self.tests, total_assertions))
            if len(skipped) > 0:
                self.output.write(", %d skipped" % (len(skipped)))
            self.output.write(")\n")
        else:
            self.output.write("FAILURES!\n")
            self.output.write("Tests: %d, Assertions: %d" % (self.tests, total_assertions))
            if len(errors) > 0:
                self.output.write(", Errors: %d" % (len(errors)))
            self.output.write(", Failures: %d" % (len(failures)))
            if len(skipped) > 0:
                self.output.write(", Skipped: %d" % (len(skipped)))

            self.output.write(".")
            self.output.write("\n")

    def on_test_start(self, test, data):
        if self.debug:
            settings = data.settings()
            color_scheme = settings.get('color_scheme')
            syntax = settings.get('syntax')
            self.output.write('\nStarting test \'{}\'\n  color scheme: \'{}\'\n  syntax: \'{}\'\n'
                              .format(test, color_scheme, syntax))

    def _writeProgress(self, c):
        self.output.write(c)
        self.progress_count += 1
        if self.progress_count % 80 == 0:
            self.output.write(' %d / %s (%3.1f%%)\n' % (
                self.tests,
                self.tests_total,
                (self.tests / self.tests_total) * 100))

    def on_test_end(self):
        self.tests += 1

    def addError(self, test, data):
        self._writeProgress('E')

    def addSkippedTest(self, test, data):
        self._writeProgress('S')

        if self.debug:
            settings = data.settings()
            color_scheme = settings.get('color_scheme')
            syntax = settings.get('syntax')
            self.output.write('\nSkipping test \'{}\'\n  color scheme: \'{}\'\n  syntax: \'{}\'\n'
                              .format(test, color_scheme, syntax))

    def addException(self, exception):
        self.output.write("\nAn error occurred: %s\n" % str(exception))

    def on_test_success(self):
        self._writeProgress('.')

    def on_test_failure(self):
        self._writeProgress('F')

    def on_assertion(self):
        self.assertions += 1
