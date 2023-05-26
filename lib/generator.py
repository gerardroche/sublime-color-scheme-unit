from ColorSchemeUnit.lib.color_scheme import ViewStyle


def generate_color_scheme_assertions(view, pt):
    line = view.line(pt)

    styles = []
    color_scheme_style = ViewStyle(view)
    for i in range(line.begin(), line.end()):
        if view.substr(i) == ' ':
            styles.append('')
        else:
            style = color_scheme_style.at_point(i)
            if 'fontStyle' not in style:
                style['fontStyle'] = ''

            styles.append('fg={} fs={}'.format(style['foreground'], style['fontStyle']))

    return _generate_assertions(styles, view, pt)


def _generate_assertions(items, view, pt):
    comment_start, comment_end = _get_comment_markers(view, pt)

    return _build_assertions(items, comment_start, comment_end)


def _build_assertions(styles, comment_start, comment_end):
    line_styles_count = len(styles)
    repeat_count = 0
    indent_count = 0
    prev_style = None
    assertions = []
    for i, style in enumerate(styles):
        if style == prev_style:
            repeat_count += 1
        else:
            if prev_style is not None:
                assertions.append((indent_count * ' ') + ('^' * repeat_count) + ' ' + prev_style)
                indent_count += repeat_count
                repeat_count = 1
            else:
                repeat_count += 1

        prev_style = style

        if line_styles_count == i + 1:
            assertions.append((indent_count * ' ') + ('^' * repeat_count) + ' ' + prev_style)

    assertions_str = ''
    for assertion in assertions:
        assertion = assertion[len(comment_start):]
        if assertion.lstrip(' ').startswith('^') and assertion.strip(' ^') != '':
            assertions_str += comment_start + assertion + comment_end + '\n'

    return assertions_str.rstrip('\n')


def _get_comment_markers(view, pt):
    comment_start = ''
    comment_end = ''
    for v in view.meta_info('shellVariables', pt):
        if v['name'] == 'TM_COMMENT_START':
            comment_start = v['value']
            if not comment_start.endswith(' '):
                comment_start = comment_start + ' '

        if v['name'] == 'TM_COMMENT_END':
            comment_end = v['value']
            if not comment_end.startswith(' '):
                comment_end = ' ' + comment_end

    return (comment_start, comment_end)
