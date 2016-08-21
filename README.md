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

* ColorSchemeUnit: Run Test
* ColorSchemeUnit: Run Package Tests

### Keymaps

The keymaps are disabled by default.

OS X | Windows / Linux | Description
-----|-----------------|------------
<kbd>Command</kbd>+<kbd>Shift</kbd>+<kbd>r</kbd> | <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>r</kbd> | Run Test
<kbd>Command</kbd>+<kbd>Shift</kbd>+<kbd>t</kbd> | <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>t</kbd> | Run Package Tests

### Settings

Key | Description | Type | Default
----|-------------|------|--------
`phpunit.keymaps` | Enable the default keymaps. | `boolean` | `false`

### User Settings

`Preferences > Settings - User`

```json
{
    "color_scheme_unit.{Key}": "{Value}"
}
```

### Per-Project Settings

`Project > Edit Project`

```json
{
    "settings": {
        "color_scheme_unit.{Key}": "{Value}"
    }
}
```

### Testing

Tests are very similar to [syntax definition tests](https://www.sublimetext.com/docs/3/syntax.html).

PHP

```
<?php // COLOR TEST "Packages/five_easy_color_schemes/Monokai (Dark).tmTheme" "PHP"

    // comment
//  ^^^^^^^^^^ fg=#75715e bg=#272822 fs=italic

interface Filter {
// ^ fg=#66d9ef fs=italic
//        ^ fg=#a6e22e fs=

    public function filter();
//  ^ fg=#f92672 fs=
//         ^ fg=#66d9ef fs=italic
//                  ^ fg=#a6e22e fs=
}
```

HTML

```
<!-- COLOR TEST "Packages/five_easy_color_schemes/Monokai (Dark).tmTheme" "HTML" -->
<!-- assertions... -->
```

CSS

```
/* COLOR TEST "Packages/five_easy_color_schemes/Monokai (Dark).tmTheme" "CSS" */
/* assertions... */
```

For more examples see the [Five Easy Color Schemes](https://github.com/gerardroche/sublime_five_easy_color_schemes) package tests.

#### Rules

1. Ensure the file name starts with `color_scheme_test_`.
2. Ensure the file is saved somwhere within the Packages directory. Within a directory named `test` inside the color scheme package is recommended.
  ```
  .
  ├── name.tmTheme
  └── test
      ├── color_scheme_test.css
      ├── color_scheme_test.html
      ├── color_scheme_test.js
      └── issue
          ├── color_scheme_test_104.php
          └── color_scheme_test_98.php
  ```
3. Ensure the first line of the file starts with: `<comment_token> COLOR TEST "<color_scheme_file>" "<syntax_name>"`

Once the above conditions are met, running a test or the package tests with a color sccheme test selected will run a single test or all the package tests, and show the results in an output panel. Next Result (<kbd>F4</kbd>) can be used to navigate to the first failing test, and Previous Result (<kbd>Shift</kbd>+<kbd>F4</kbd>) can be used to navigate to the previous failing test.

Each test in the syntax test file must first start the comment token (established on the first line, it doesn't have to be a comment according to the syntax), and then a `^` token.

There is one type of test:

* Caret: `^` this will test the following selector against the scope on the most recent non-test line. It will test it at the same column the `^` is in. Consecutive `^`'s will test each column against the selector. Assertions are specified after the caret. There are three types of assertions: foregound (`fg=#<color>`), background (`bg=#<color>`), and font style (`fs=<comma_delimited_list>`). One or more assertions are required, and must be specified in the order listed above.

## Installation

### Package Control installation

The preferred method of installation is via [Package Control](https://packagecontrol.io/browse/authors/gerardroche).

### Manual installation

1. Close Sublime Text.
2. Download or clone this repository to a directory named `color_scheme_unit` in the Sublime Text packages directory:
    * Linux: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git ~/.config/sublime-text-3/Packages/color_scheme_unit`
    * OS X: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/color_scheme_unit`
    * Windows: `git clone https://github.com/gerardroche/sublime_color_scheme_unit.git %APPDATA%\Sublime/ Text/ 3/Packages/color_scheme_unit`

## Contributing

Your issue reports and pull requests are always welcome.

To enable debug messages and extra development tools set a `SUBLIME_COLOR_SCHEME_UNIT_DEBUG` environment variable to a non-blank value.

Tip: Start Sublime Text at the Terminal with an exported environment variable.

```
$ export SUBLIME_COLOR_SCHEME_UNIT_DEBUG=y; subl
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

Released under the [BSD 3-Clause License](LICENSE).
