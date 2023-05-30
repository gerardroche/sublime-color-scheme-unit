import plistlib

from sublime import find_resources
from sublime import load_resource
from sublime import score_selector
import sublime


def load_color_scheme_resource(color_scheme):
    resources = find_resources(color_scheme)
    if resources:
        color_scheme = resources[0]

    if not color_scheme.startswith('Packages/'):
        color_scheme = 'Packages/' + color_scheme

    resource = load_resource(color_scheme)

    if not _is_new_scheme(color_scheme):
        return plistlib.readPlistFromBytes(bytes(resource, 'UTF-8'))

    return sublime.decode_value(resource)


def _is_new_scheme(color_scheme: str) -> bool:
    return color_scheme.endswith('.sublime-color-scheme') or color_scheme.endswith('.hidden-color-scheme')


class ViewStyle():

    def __init__(self, view):
        self.view = view
        self.scope_style_cache = {}

        self.color_scheme_resource = ColorSchemeResource(view)
        self.content = self.color_scheme_resource.content()

        if self.color_scheme_resource.isLegacy():
            self.default_styles = {}  # type: dict
            for plist_settings_dict in self.content['settings']:
                if 'scope' not in plist_settings_dict:
                    self.default_styles.update(plist_settings_dict['settings'])

    def at_point(self, point):
        # scope_name() needs to striped due to a bug in ST:
        # See https://github.com/SublimeTextIssues/Core/issues/657.
        scope = self.view.scope_name(point).strip()

        if scope in self.scope_style_cache:
            return self.scope_style_cache[scope]

        if self.color_scheme_resource.isLegacy():
            style = self.default_styles.copy()
            scored_styles = []
            for color_scheme_definition in self.content['settings']:
                if 'scope' in color_scheme_definition:
                    score = score_selector(scope, color_scheme_definition['scope'])
                    if score:
                        color_scheme_definition.update({'score': score})
                        scored_styles.append(color_scheme_definition)

            for s in sorted(scored_styles, key=lambda k: k['score']):
                style.update(s['settings'])
        else:
            style = self.view.style()
            scope_style = self.view.style_for_scope(scope)
            style.update(scope_style)
            fontStyle = ''
            if 'bold' in style and style['bold']:
                fontStyle += ' bold'
            if 'italic' in style and style['italic']:
                fontStyle += ' italic'
            style['fontStyle'] = fontStyle.strip()

        self.scope_style_cache[scope] = style

        return style


class ColorSchemeResource():

    def __init__(self, view):
        self.color_scheme = view.settings().get('color_scheme')
        self._content = None

    def isLegacy(self) -> bool:
        return not _is_new_scheme(self.color_scheme)

    def content(self) -> dict:
        if self._content is None:
            self._content = load_color_scheme_resource(self.color_scheme)

        return self._content
