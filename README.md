# ColorSchemeUnit

A testing framework for Sublime Text color schemes.

<p>
    <a href="https://github.com/gerardroche/sublime-color-scheme-unit/actions/workflows/ci.yml"><img alt="Continuous Integration" src="https://github.com/gerardroche/sublime-color-scheme-unit/actions/workflows/ci.yml/badge.svg?branch=master"></a>
    <a href="https://ci.appveyor.com/project/gerardroche/sublime-color-scheme-unit/branch/master"><img alt="Build status" src="https://img.shields.io/appveyor/ci/gerardroche/sublime-color-scheme-unit/master.svg?style=flat-square&label=appveyor"></a>
    <a href="https://codecov.io/gh/gerardroche/sublime-color-scheme-unit"><img alt="Codecov" src="https://codecov.io/gh/gerardroche/sublime-color-scheme-unit/branch/master/graph/badge.svg?token=PAaE5LdlOR"></a>
    <a href="https://packagecontrol.io/packages/ColorSchemeUnit"><img alt="Downloads" src="https://img.shields.io/packagecontrol/dt/ColorSchemeUnit.svg?style=flat-square"></a>
</p>

![ColorSchemeUnit](screenshot.png)

## Setup

Install [ColorSchemeUnit](https://packagecontrol.io/packages/ColorSchemeUnit) via Package Control.

## Commands

Command | Description
:------ |:-----------
ColorSchemeUnit:&nbsp;Test&nbsp;Suite | Run test suite of the current file.
ColorSchemeUnit:&nbsp;Test&nbsp;File | Run tests for the current file.
ColorSchemeUnit:&nbsp;Show&nbsp;Styles | Show styles at the current cursor position.
ColorSchemeUnit:&nbsp;Generate&nbsp;Assertions | Generates assertions at the current cursor position.

## Key Bindings

Key | Description
--- | -----------
`f4` | Jump to Next Failure
`shift+f4` | Jump to Previous Failure

## Settings

Setting | Description | Type | Default
:-------|:------------|:-----|:-------
`color_scheme_unit.coverage` | Enable coverage report. | `boolean` | `true`
`color_scheme_unit.debug` | Enable debug messages. | `boolean` | `false`

**Menu → Preferences → Settings**

```js
"color_scheme_unit.debug": true,
"color_scheme_unit.coverage": true,
```

## Usage

```c
// COLOR SCHEME TEST "MonokaiFree/MonokaiFree.sublime-color-scheme" "C"

#include <windows.h>
// ^^^^^ fg=#f92672 fs=
//       ^^^^^^^^^^^ fg=#e6db74 fs=

typedef int myint;
// ^^^^ fg=#66d9ef fs=italic
//      ^^^ fg=#66d9ef fs=italic
//          ^^^^^ fg=#a6e22e fs=
//               ^ fg=#f8f8f2 fs=

int main(int argc, char **argv) {}
//  ^^^^ fg=#a6e22e fs=
//      ^ fg=#f8f8f2 fs=
//       ^^^ fg=#66d9ef fs=italic
//           ^^^^ fg=#fd971f fs=italic
//               ^ fg=#f8f8f2 fs=
//                 ^^^^ fg=#66d9ef fs=italic
//                      ^^ fg=#f92672 fs=
//                        ^^^^ fg=#fd971f fs=italic
//                            ^ fg=#f8f8f2 fs=
//                              ^^ fg=#f8f8f2 fs=
```

Tests are similar to Sublime Text [syntax tests](https://www.sublimetext.com/docs/3/syntax.html).

### Test files

Test files must start with "color_scheme_test" and the first line must start:

```
<start-comment> COLOR SCHEME TEST "<color-scheme>" "<syntax>"
```

Example:

```php
// COLOR SCHEME TEST "Name/Name.sublime-color-scheme" "PHP"
```

Test files must also use spaces.

To make the test conditional on the syntax existing use the `SKIP IF NOT` keyword. If the the syntax doesn't exist the test will be skipped instead of failing.

```js
// COLOR SCHEME TEST "Name/Name.sublime-color-scheme" SKIP IF NOT "Vue"
```

### Recommended package layout:

```sh
.
├── Name.sublime-color-scheme
└── tests/
  ├── color_scheme_test.css
  ├── color_scheme_test.html
  ├── color_scheme_test.js
  └── ...
```

### Assertions

Each assertion in the color scheme test file must first start the comment token, and then a `^` (caret) token. `^` this will assert against the scope on the most recent non-test line. It will test it at the same column as the `^`. Consecutive `^`'s will test each column. What to assert is specified after the caret.

Assertion | Example
:-------- | :------
Foreground color | `fg=#f8f8f2`
Background color | `bg=#272822`
Font style (space delimited list) | `fs=italic`, `fs=italic bold`
Sublime Text build version (only `>=` is supported) | `build>=3127`

Assertions must be specified in the order: `fg`, `bg`, `fs`, `build`.

```rb
def somefunc(param1='', param2=0):
# ^ fg=#66d9ef
# ^ bg=#272822
# ^ fs=italic
# ^ fg=#66d9ef bg=#272822
# ^ fg=#66d9ef bg=#272822 fs=italic bold
# ^ fg=#66d9ef bg=#272822 fs=italic build>=3127
```

See [MonokaiFree's](https://github.com/gerardroche/sublime-monokai-free/tests) extensive test suite to see examples.

### Python example

```py
# COLOR SCHEME TEST "MonokaiFree/MonokaiFree.sublime-color-scheme" "Python" # flake8: noqa

import os
# ^ fg=#f8f8f2 bg=#272822 fs=
#  ^^^ fg=#f92672 fs=
#      ^^ fg=#f8f8f2

def f_name(arg1='', arg2=0):
# ^ fg=#66d9ef fs=italic
#   ^^^^^^ fg=#a6e22e fs=
#          ^ fg=#fd971f fs=italic
#              ^ fg=#f92672 fs=
#               ^^ fg=#e6db74 fs=
#                 ^ fg=#f8f8f2 fs=
#                   ^ fg=#fd971f fs=italic
#                       ^ fg=#f92672 fs=
#                        ^ fg=#ae81ff fs=
    if arg1 > arg2: # interesting
    #   ^ fg=#f92672 fs=
    #           ^ fg=#f92672 fs=
        print 'Gre\'ater'
        # ^ fg=#f92672 fs=
        #     ^^^^ fg=#e6db74 fs=
        #         ^^ fg=#ae81ff fs=
        #           ^^^^^ fg=#e6db74 fs=
```

### HTML example

```html
<!-- COLOR SCHEME TEST "MonokaiFree/MonokaiFree.sublime-color-scheme" "HTML" -->
<!DOCTYPE html>
<!-- ^^^^ fg=#f92672 fs= -->
<!--      ^^^^^ fg=#f8f8f2 fs= -->
<html>
    <head>

        <meta charset="utf-8">
<!--    ^ fg=#f8f8f2 fs= -->
        <!--^ fg=#f92672 fs= -->
        <!--  ^ fg=#a6e22e fs= -->
        <!--         ^ fg=#f8f8f2 fs= -->
        <!--           ^ fg=#e6db74 fs= -->
        <!--                 ^ fg=#f8f8f2 fs= -->
    </head>
    <body>
        <p class="title" id='title'>Title</p>
    <!-- ^ fg=#f92672 fs= -->
        <!-- ^ fg=#a6e22e fs= -->
        <!--    ^ fg=#f8f8f2 fs= -->
        <!--     ^^^^^^^ fg=#e6db74 fs= -->
        <!--             ^^ fg=#a6e22e fs= -->
        <!--               ^ fg=#f8f8f2 fs= -->
        <!--                ^^^^^^^ fg=#e6db74 fs= -->
        <!--                       ^ fg=#f8f8f2 fs= -->
        <!--                               ^ fg=#f92672 fs= -->
        <!--                                ^ fg=#f8f8f2 fs= -->

    </body>
<!--  ^ fg=#f92672 fs= -->
</html>
<!-- ^ fg=#f92672 fs= -->
```

### PHP example

```php
<?php // COLOR SCHEME TEST "MonokaiFree/MonokaiFree.sublime-color-scheme" "PHP"

use \Psr\Http\Message\ServerRequestInterface as Request;
//^ fg=#f92672 fs=
//  ^^^^^^^^^^^^^^^^^^ fg=#f8f8f2 fs=
//                    ^^^^^^^^^^^^^^^^^^^^^^ fg=#66d9ef fs=italic
//                                           ^^ fg=#f92672 fs=
//                                              ^^^^^^^ fg=#a6e22e fs=
//                                                     ^ fg=#f8f8f2 fs=
use \Psr\Http\Message\ResponseInterface as Response;
//^ fg=#f92672 fs=
//  ^^^^^^^^^^^^^^^^^^ fg=#f8f8f2 fs=
//                    ^^^^^^^^^^^^^^^^^ fg=#66d9ef fs=italic
//                                      ^^ fg=#f92672 fs=
//                                         ^^^^^^^^ fg=#a6e22e fs=
//                                                 ^ fg=#f8f8f2 fs=

require 'vendor/autoload.php';
// ^^^^ fg=#f92672 fs=
//      ^^^^^^^^^^^^^^^^^^^^^ fg=#e6db74 fs=
//                           ^ fg=#f8f8f2 fs=
```

## CI

To run tests in CI see [UnitTesting](https://github.com/randy3k/UnitTesting) documentation.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

Released under the [GPL-3.0-or-later License](LICENSE).
