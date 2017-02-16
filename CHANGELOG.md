# COLOR SCHEME UNIT CHANGELOG

* Fixed [#13](https://github.com/gerardroche/sublime_color_scheme_unit/pull/13): Edge case test assertion failures

## [0.13.1]

* Fixed: row:column failure off by 1 row

## [0.13.0]

* Removed [#8](https://github.com/gerardroche/sublime_color_scheme_unit/issues/8): Deprecated code
* Minor fixes

## [0.12.2]

* Fixed [#9](https://github.com/gerardroche/sublime_color_scheme_unit/issues/9): IndexError: list index out of range

## [0.12.1]

* Fixed: Show styles popup helper not working

## [0.12.0]

* Fixed [#5](https://github.com/gerardroche/sublime_color_scheme_unit/issues/5): PHP test definition with trailing `?>` does not work
* Deprecated [#6](https://github.com/gerardroche/sublime_color_scheme_unit/issues/6): Color scheme paths should no longer be prefixed with "Packages/"
* Deprecated [#7](https://github.com/gerardroche/sublime_color_scheme_unit/issues/7): Color scheme tests should use the keyword "COLOR SCHEME TEST" instead of "COLOR TEST"

## [0.11.0]

* Added: Colors in the Show Scope Name and Styles can now be copied with mouse click

## [0.10.0]

* Changed: Test views are no longer listed in the panel switcher
* Fixed: Keymaps are disabled by default

## [0.9.1]

* Fixed: test output panel syntax tests

## [0.9.0]

* Added: Prints additional runtime information on test runs
* Changed: Run tests timeout uses default `0`

## [0.8.1]

* Fixed: Keymaps settings key typo

## [0.8.0]

* Added: allow tests using CSS comments
* Added: Default keymaps (disabled by default)
* Added: Tests are now run in background
* Added: File or Package details is printed in test results output
* Changed: Reworded some run color tests commands
* Changed: "run_color_scheme_tests" command now runs the current package tests
  by default. Previously it ran all tests including tests from other packages.
  Color scheme tests are slow and it doesn't make sense to run all test.
* Fixed: Set Color Scheme On Load development helper
* Fixed: allow trailing HTML comment tag on first line i.e. `COLOR TEST ... -->`
* Removed: "run_color_scheme_package_tests" command. Use
  "run_color_scheme_tests" command instead which now runs packages tests.

## [0.7.0]

* Added: improved error handling; prints error information in test results
* Added: allow tests to begin with comments and tags e.g. `<?php // COLOR TEST ...`
* Added: ColorSchemeUnit - Run package tests command which only runs current package tests

## [0.6.0]

* Added: test results are now displayed in color
* Added: tests are now run asynchronously
* Added: timer; prints the time it took to run the tests
* Removed `SUBLIME_COLOR_SCHEME_UNIT_DEV_TOOLS` environment variable, use
  `SUBLIME_COLOR_SCHEME_UNIT_DEBUG` instead.

## [0.5.1]

* Fixed: environment debug variable

## [0.5.0]

* Added: assertions can now be written with html style comments
* Fixed: COLOR TEST does not fallback tmLanguage syntaxes
* Fixed: incorrect style when styles have the same score

## [0.4.0]

* Added: run single test command

## [0.3.0]

* Added: run a single test file
* Fixed: assertion fail when a scope inherits from another scope

## [0.2.0]

* Added: debug messages
* Fixed: assertions now work for # comments

## [0.1.0]

* Initial import

[0.13.1]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.13.0...0.13.1
[0.13.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.12.2...0.13.0
[0.12.2]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.12.1...0.12.2
[0.12.1]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.12.0...0.12.1
[0.12.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.11.0...0.12.0
[0.11.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.10.0...0.11.0
[0.10.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.9.0...0.10.0
[0.9.1]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.9.0...0.9.1
[0.9.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.8.0...0.9.0
[0.8.1]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.8.0...0.8.1
[0.8.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.5.0...0.6.0
[0.5.1]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/gerardroche/sublime_color_scheme_unit/compare/0.1.0...0.2.0
