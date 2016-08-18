# color_scheme_unit

[![Author](https://img.shields.io/badge/author-@gerardroche-blue.svg?style=flat)](https://twitter.com/gerardroche)
[![Source Code](https://img.shields.io/badge/source-GitHub-blue.svg?style=flat)](https://github.com/gerardroche/sublime_color_scheme_unit)
[![License](https://img.shields.io/badge/license-BSD--3-blue.svg?style=flat)](https://raw.githubusercontent.com/gerardroche/sublime_color_scheme_unit/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/gerardroche/sublime_color_scheme_unit.svg?style=flat)](https://github.com/gerardroche/sublime_color_scheme_unit/stargazers)

[![Sublime version](https://img.shields.io/badge/sublime-v3-lightgrey.svg?style=flat)](https://sublimetext.com)
[![Latest version](https://img.shields.io/github/tag/gerardroche/sublime_color_scheme_unit.svg?label=release&style=flat&maxAge=2592000)](https://github.com/gerardroche/sublime_color_scheme_unit/tags)
[![Downloads](https://img.shields.io/packagecontrol/dt/color_scheme_unit.svg?style=flat&maxAge=2592000)](https://packagecontrol.io/packages/color_scheme_unit)

A testing framework for Sublime Text color schemes.

![Screenshot](screenshot.png)

## Overview

* [Usage](#usage)
* [Installation](#installation)
* [Contributing](#contributing)
* [Changelog](#changelog)
* [License](#license)

## Usage

### Commands

* ColorSchemeUnit: Run Package Tests
* ColorSchemeUnit: Run All Tests
* ColorSchemeUnit: Run Test

### Keymaps

*The keymaps are disabled by default.*

OS X | Windows / Linux | Description
-----|-----------------|------------
<kbd>Command</kbd>+<kbd>Shift</kbd>+<kbd>r</kbd> | <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>r</kbd> | Run single test
<kbd>Command</kbd>+<kbd>Shift</kbd>+<kbd>t</kbd> | <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>t</kbd> | Run package tests

### User Settings

```json
{
    "color_scheme_unit.keymaps": true
}
```

### Per-Project Settings

```json
{
    "settings": {
        "color_scheme_unit.keymaps": true
    }
}
```

### Test File Syntax

Tests are very similar to syntax tests.

1. Ensure the file name starts with `color_scheme_test`.
2. Ensure the first line of the file starts with: `COLOR TEST "<color_scheme_file>" "<syntax_name>"`

Each test in the syntax test file must first start the comment token (established on the first line, it doesn't actually have to be a comment according to the syntax), and then a `^` token.

There is one type of test:

* Caret: `^` this will test the following selector against the scope on the most recent non-test line. It will test it at the same column the `^` is in. Consecutive `^`'s will test each column against the selector. Assertions are specified after the caret. There are three types of assertions: `fg=#<color>`, `bg=#<color>`, and `fs=<comma_delimited_list>` e.g `fs=bold,italic` or none `fs=`. *One or more assertions are required, and must be specified in the order listed above.*

Once the above conditions are met, running the tests will show the results in an output panel. Next Result (F4) can be used to navigate to the first failing test and Previous Result (Shift+F4) to navigate to the previous failing test.

#### Example

```
<?php // COLOR TEST "Packages/five_easy_color_schemes/Monokai (Dark).tmTheme" "PHP"

    // comment
//  ^^^^^^^^^^ fg=#75715e fs=italic

echo 'str';
// ^ fg=#dc322f fs=
//   ^ fg=#839496 fs=
//    ^^^ fg=#2aa198 fs=
//       ^ fg=#839496 fs=
```

For more examples see the [Five Easy Color Schemes](https://github.com/gerardroche/sublime_five_easy_color_schemes) package tests.

## Installation

### Package Control installation

The preferred method of installation is via [Package Control].

### Manual installation

1. Close Sublime Text.
2. Download or clone this repository to a directory named `color_scheme_unit` in the Sublime Text packages directory:
    * Linux: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git ~/.config/sublime-text-3/Packages/color_scheme_unit`
    * OS X: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/color_scheme_unit`
    * Windows: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git %APPDATA%\Sublime/ Text/ 3/Packages/color_scheme_unit`

## Contributing

Your issue reports and pull requests are always welcome.

To enable **debug messages** and extra **development tools** set the package debug environment variable to a non-blank value: `SUBLIME_COLOR_SCHEME_UNIT_DEBUG=y`.

Tip: Start Sublime Text at the Terminal with an exported environment variable: `
$ export SUBLIME_COLOR_SCHEME_UNIT_DEBUG=y; subl`.

To enable the show style development tool add a keymap: `{ "keys": ["ctrl+shift+alt+p"], "command": "show_scope_name_and_styles" }`.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

Released under the [BSD 3-Clause License](LICENSE).

[Package Control]: https://packagecontrol.io/browse/authors/gerardroche
