# gerardroche/sublime_color_scheme_unit

A testing framework for for Sublime Text 3 color schemes.

## Overview

* [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [Changelog](#changelog)
* [License](#license)

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

## Usage

From the command palette run: `ColorSchemeUnit: run all tests`.

Test files are files named with prefix "color_scheme_test". See [Five Easy Color Schemes](https://github.com/gerardroche/sublime_five_easy_color_schemes) for examples of usage.

## Contributing

Your issue reports and pull requests are always welcome.

**Debug messages**

Debug messages are disabled by default. To enable them set an environment variable to a non-blank value e.g. `SUBLIME_COLOR_SCHEME_UNIT_DEBUG=y`. To disable them set unset it or set it to a blank value e.g. `SUBLIME_COLOR_SCHEME_UNIT_DEBUG=`.

To enable extra color scheme unit development tools set the environment variable `SUBLIME_COLOR_SCHEME_UNIT_DEV_TOOLS` to a non blank value.

On Linux, for example, Sublime Text can be started at the Terminal with an exported environment variable.

```
$ export SUBLIME_COLOR_SCHEME_UNIT_DEBUG=y; export SUBLIME_COLOR_SCHEME_UNIT_DEV_TOOLS=y; ~/sublime_text_3/sublime_text
```

Add the folllowing to your keymaps for the show scope name and style dev helper:

```
{ "keys": ["ctrl+shift+alt+p"], "command": "show_scope_name_and_styles" },
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

Released under the [BSD 3-Clause License](LICENSE).
