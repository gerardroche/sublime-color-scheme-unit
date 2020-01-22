# COLOR SCHEME UNIT CHANGELOG

## [1.10.4] - 2020-01-21

* Fixed: Support for ST4 and Python 3.8

## [1.10.3] - 2020-01-13

* Fixed: Consecutive failures

## [1.10.2] - 2017-11-30

* Fixed: Should be able to specify package name in syntax test parameter

## [1.10.1] - 2017-11-23

* Fixed: Workaround https://github.com/SublimeTextIssues/Core/issues/2044

## [1.10.0] - 2017-10-30

### Added

* Added [#18](https://github.com/gerardroche/sublime-color-scheme-unit/issues/18): Run ColorSchemeUnit when a package name is given
* Added: AppVeyor support

### Fixed

* Fixed: Error running single test

## [1.9.0] - 2017-10-15

### Added

* Added [#10](https://github.com/gerardroche/sublime-color-scheme-unit/issues/10): Test output in new tab like BuildView
* Added: Travis CI support

## [1.8.1] - 2017-10-06

### Fixed

* Fixed: Fallback to hidden-tmLanguage syntax for legacy syntaxes

## [1.8.0] - 2017-09-25

### Added

* Added: Insert Syntax Assertions command
* Added: Allow skipping a test if syntax is not found

### Changed

* Plugin has been renamed from color_scheme_unit to ColorSchemeUnit

### Fixed

* Fixed: Don't print minimal tests coverage running single test case
* Fixed: Many progress report issues
* Fixed: Several code coverage issues
* Fixed: Several performance issues; more than 50% improvement!

## [1.7.0] - 2017-09-19

### Added

* Added: Insert Assertions command
* Added: Backwards compatability with older builds `<=3083`

## [1.6.0] - 2017-09-12

### Added

* Added: Code coverage report
* Added: `build>={NUMBER}` assertion parameter
* Added: SQL comment support

## [1.5.0] - 2017-08-29

* Added: Basic code coverage report
* Added: Performance improvements
* Added: More debug mode messages

## [1.4.2] - 2017-08-29

### Fixed

* Fixed: Doc: [Test](https://github.com/gerardroche/sublime-test) support
* Fixed: Update metadata
* Fixed: Update licence year

## [1.4.1] - 2017-08-27

### Fixed

* Fixed: Can't run single test when package is symlinked

## [1.4.0] - 2017-08-23

### Fixed

* Fixed: Can't run tests when package is symlinked

### Removed

* The default key bindings have been removed, instead add your preferred key bindings:

  `Menu > Preferences > Key Bindings`

  ```json
  [
      { "keys": ["ctrl+shift+a"], "command": "color_scheme_unit_test_suite" },
      { "keys": ["ctrl+shift+f"], "command": "color_scheme_unit_test_file" },
      { "keys": ["ctrl+shift+r"], "command": "color_scheme_unit_test_results" },
      { "keys": ["ctrl+shift+alt+p"], "command": "color_scheme_unit_show_scope_name_and_styles" },
  ]
  ```

  The following key bindings remain the same:

  Key | Description
  --- | -----------
  `F4` | Jump to Next Failure
  `Shift+F4` | Jump to Previous Failure

## [1.3.0] - 2017-06-19

## Added

* Added: A percentage indicator has also been added to the end of each progress
* Added: Command "ColorSchemeUnit: Test Results" for opening the test results panel
* Added: Command "ColorSchemeUnit: Show Scope and Colors" for showing the scope name and applied colors of scheme at point under cursor

## Changed

* Debugging is now enabled via a `color_scheme_unit.debug` setting instead of an environment variable
* Debugging messages are now printed in the tests results panel instead of the console
* Copying colors from the "Show Scope and Colors" popup no longer copies the # (hash) character

## Fixed

* Fixed: Several result progress printing issues e.g. progress lines were not wrapping correctly
* Fixed [#17](https://github.com/gerardroche/sublime-color-scheme-unit/issues/17): Assertions don't work when prefixed with whitespace

## [1.2.0] - 2017-06-13

### Changed

* Auto applying the color scheme when tests are opened is now enabled by default

## [1.1.0] - 2017-05-17

### Added

* Added: Some additional status messages when there are errors
* Added: Debug setting to enable debug messages

## [1.0.0]

* Prepared release

## [0.13.2]

### Fixed

* Fixed [#13](https://github.com/gerardroche/sublime-color-scheme-unit/pull/13): Edge case test assertion failures

## [0.13.1]

### Fixed

* Fixed: row:column failure off by 1 row

## [0.13.0]

### Removed

* Removed [#8](https://github.com/gerardroche/sublime-color-scheme-unit/issues/8): Deprecated code

## [0.12.2]

### Fixed

* Fixed [#9](https://github.com/gerardroche/sublime-color-scheme-unit/issues/9): IndexError: list index out of range

## [0.12.1]

### Fixed

* Fixed: Show styles popup helper not working

## [0.12.0]

### Deprecated

* Deprecated [#7](https://github.com/gerardroche/sublime-color-scheme-unit/issues/7): Color scheme tests should use the keyword "COLOR SCHEME TEST" instead of "COLOR TEST"

### Fixed

* Fixed [#5](https://github.com/gerardroche/sublime-color-scheme-unit/issues/5): PHP test definition with trailing `?>` does not work
* Deprecated [#6](https://github.com/gerardroche/sublime-color-scheme-unit/issues/6): Color scheme paths should no longer be prefixed with "Packages/"

## [0.11.0]

### Added

* Added: Colors in the Show Scope Name and Styles can now be copied with mouse click

## [0.10.0]

### Added

* Changed: Test views are no longer listed in the panel switcher

### Fixed

* Fixed: Keymaps are disabled by default

## [0.9.1]

### Fixed

* Fixed: test output panel syntax tests

## [0.9.0]

### Added

* Added: Prints additional runtime information on test runs

### Changed

* Changed: Run tests timeout uses default `0`

## [0.8.1]

### Fixed

* Fixed: Keymaps settings key typo

## [0.8.0]

### Added

* Added: allow tests using CSS comments
* Added: Default keymaps (disabled by default)
* Added: Tests are now run in background
* Added: File or Package details is printed in test results output

### Removed

* Removed: "run_color_scheme_package_tests" command. Use  "run_color_scheme_tests" command instead which now runs packages tests.

### Changed

* Changed: Reworded some run color tests commands
* Changed: "run_color_scheme_tests" command now runs the current package tests by default. Previously it ran all tests including tests from other packages. Color scheme tests are slow and it doesn't make sense to run all test.

### Fixed

* Fixed: Set Color Scheme On Load development helper
* Fixed: allow trailing HTML comment tag on first line i.e. `COLOR TEST ... -->`

## [0.7.0]

### Added

* Added: improved error handling; prints error information in test results
* Added: allow tests to begin with comments and tags e.g. `<?php // COLOR TEST ...`
* Added: ColorSchemeUnit - Run package tests command which only runs current package tests

## [0.6.0]

### Added

* Added: test results are now displayed in color
* Added: tests are now run asynchronously
* Added: timer; prints the time it took to run the tests

### Removed

* Removed `SUBLIME-COLOR-SCHEME-UNIT_DEV_TOOLS` environment variable, use `SUBLIME-COLOR-SCHEME-UNIT_DEBUG` instead.

## [0.5.1]

### Fixed

* Fixed: environment debug variable

## [0.5.0]

### Added

* Added: assertions can now be written with html style comments

### Fixed

* Fixed: COLOR TEST does not fallback tmLanguage syntaxes
* Fixed: incorrect style when styles have the same score

## [0.4.0]

### Added

* Added: run single test command

## [0.3.0]

### Added

* Added: run a single test file

### Fixed

* Fixed: assertion fail when a scope inherits from another scope

## [0.2.0]

### Added

* Added: debug messages

### Fixed

* Fixed: assertions now work for # comments

## 0.1.0

* Initial import

[1.10.4]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.10.3...1.10.4
[1.10.3]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.10.2...1.10.3
[1.10.2]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.10.1...1.10.2
[1.10.1]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.10.0...1.10.1
[1.10.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.9.0...1.10.0
[1.9.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.8.1...1.9.0
[1.8.1]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.8.0...1.8.1
[1.8.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.7.0...1.8.0
[1.7.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.6.0...1.7.0
[1.6.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.5.0...1.6.0
[1.5.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.4.2...1.5.0
[1.4.2]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.4.1...1.4.2
[1.4.1]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.4.0...1.4.1
[1.4.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.3.0...1.4.0
[1.3.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.2.0...1.3.0
[1.2.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.13.2...1.0.0
[0.13.2]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.13.1...0.13.2
[0.13.1]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.13.0...0.13.1
[0.13.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.12.2...0.13.0
[0.12.2]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.12.1...0.12.2
[0.12.1]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.12.0...0.12.1
[0.12.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.11.0...0.12.0
[0.11.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.10.0...0.11.0
[0.10.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.9.0...0.10.0
[0.9.1]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.9.0...0.9.1
[0.9.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.8.0...0.9.0
[0.8.1]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.8.0...0.8.1
[0.8.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.5.0...0.6.0
[0.5.1]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/gerardroche/sublime-color-scheme-unit/compare/0.1.0...0.2.0
