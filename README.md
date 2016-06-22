# gerardroche/sublime_color_scheme_unit

A testing framework for for Sublime Text 3 color schemes.

## Overview

* [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [Changelog](#changelog)
* [License](#license)

## Usage

From the command palette run: `ColorSchemeUnit: run all tests`.

Test files are files named with prefix "color_scheme_test". See [Five Easy Color Schemes](https://github.com/gerardroche/sublime_five_easy_color_schemes) for examples of usage.

## Installation

### [Package Control](https://packagecontrol.io) installation

This is the preferred method of installation. Search for "[color_scheme_unit](https://packagecontrol.io/search/color_scheme_unit)".

### Manual installation

1. Close Sublime Text.
2. Download or clone this repository to a directory named `color_scheme_unit` in the Sublime Text Packages directory for your platform:
    * Linux: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git ~/.config/sublime-text-3/Packages/color_scheme_unit`
    * OS X: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/color_scheme_unit`
    * Windows: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git %APPDATA%\Sublime/ Text/ 3/Packages/color_scheme_unit`
3. The features listed above will be available the next time Sublime Text is started.

## Contributing

Your issue reports and pull requests are always welcome.

The tests are run via [Color Scheme Unit](https://github.com/gerardroche/sublime_color_scheme_unit). Manual installation is required to run the tests because the tests are not included in production releases (Package Control installations).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

Released under the [BSD 3-Clause License](LICENSE).
