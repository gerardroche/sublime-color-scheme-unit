# gerardroche/sublime_color_scheme_unit

## 0.9.0

* Added: Prints additional runtime information on test runs
* Changed: Run tests timeout uses default 0

## 0.8.1

* Fixed: Keymaps settings key typo

## 0.8.0

* Added: allow tests using CSS comments e.g.
  ```
  /* COLOR TEST "Packages/Theme - Cobalt2/cobalt2.tmTheme" "CSS" */
  @media all and (max-width: 470px) {
  /* ^ fg=#ff9d00 fs= */
  }
  ```
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

## 0.7.0

* Added: improved error handling; prints error information in test results
* Added: allow tests to begin with comments and tags e.g. `<?php // COLOR TEST ...`
* Added: ColorSchemeUnit - Run package tests command which only runs current package tests

## 0.6.0

* Added: test results are now displayed in color
* Added: tests are now run asynchronously
* Added: timer; prints the time it took to run the tests
* Removed SUBLIME_COLOR_SCHEME_UNIT_DEV_TOOLS envvar, use SUBLIME_COLOR_SCHEME_UNIT_DEBUG instead

## 0.5.1

* Fixed: environment debug variable

## 0.5.0

* Added: assertions can now be written with html style comments
* Fixed: COLOR TEST does not fallback tmLanguage syntaxes
* Fixed: incorrect style when styles have the same score

## 0.4.0

* Added: run single test command

## 0.3.0

* Added: run a single test file
* Fixed: assertion fail when a scope inherits from another scope

## 0.2.0

* Added: debug messages
* Fixed: assertions now work for # comments

## 0.1.0

* Initial import
