# gerardroche/sublime_color_scheme_unit

[![Author](http://img.shields.io/badge/author-@gerardroche-blue.svg?style=flat)](https://twitter.com/gerardroche)
[![Source Code](https://img.shields.io/badge/source-GitHub-blue.svg?style=flat)](https://github.com/gerardroche/sublime_color_scheme_unit)
[![GitHub stars](https://img.shields.io/github/stars/gerardroche/sublime_color_scheme_unit.svg?style=flat)](https://github.com/gerardroche/sublime_color_scheme_unit/stargazers)
[![License](https://img.shields.io/badge/license-BSD--3-blue.svg?style=flat)](https://raw.githubusercontent.com/gerardroche/sublime_color_scheme_unit/master/LICENSE)

[![Sublime version](https://img.shields.io/badge/sublime-v3-lightgrey.svg?style=flat)](http://sublimetext.com)
[![Latest version](https://img.shields.io/github/tag/gerardroche/sublime_color_scheme_unit.svg?maxAge=2592000?style=flat&label=release)](https://github.com/gerardroche/sublime_color_scheme_unit/tags)
[![Downloads](https://img.shields.io/packagecontrol/dt/color_scheme_unit.svg?maxAge=2592000?style=flat)](https://packagecontrol.io/packages/color_scheme_unit)

A testing framework for Sublime Text color schemes.

## Overview

* [Usage](#usage)
* [Installation](#installation)
* [Contributing](#contributing)
* [Changelog](#changelog)
* [License](#license)

## Usage

From the command palette:

* `ColorSchemeUnit: run tests`
* `ColorSchemeUnit: run test`

Or define your own keymaps:

```
{ "keys": ["ctrl+t"], "command": "run_color_scheme_tests" },
{ "keys": ["ctrl+r"], "command": "run_color_scheme_test" },
```

Test assertions are very similar to syntax tests. See [Five Easy Color Schemes](https://github.com/gerardroche/sublime_five_easy_color_schemes) for examples of test and assertion format.

*Test file names are prefixed with "color_scheme_test".*

## Installation

### Manual installation

1. Close Sublime Text.
2. Download or clone this repository to a directory named `color_scheme_unit` in the Sublime Text Packages directory for your platform:
    * Linux: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git ~/.config/sublime-text-3/Packages/color_scheme_unit`
    * OS X: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/color_scheme_unit`
    * Windows: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git %APPDATA%\Sublime/ Text/ 3/Packages/color_scheme_unit`
3. The features listed above will be available the next time Sublime Text is started.

## Contributing

Your issue reports and pull requests are always welcome.

** Debug messages & Dev tools (default=disabled)**

To enable set the debug environment environment variable to a non-blank value.

```
SUBLIME_COLOR_SCHEME_UNIT_DEBUG=y
```

On Linux Sublime Text can be started at the Terminal with an exported environment variable.

```
$ export SUBLIME_COLOR_SCHEME_UNIT_DEBUG=y; subl
```

To enable the show scope name and style helper add the following keymap:

```
{ "keys": ["ctrl+shift+alt+p"], "command": "show_scope_name_and_styles" },
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

Released under the [BSD 3-Clause License](LICENSE).
