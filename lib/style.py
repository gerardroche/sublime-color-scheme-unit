import plistlib

from sublime import load_resource
from sublime import score_selector


class ColorSchemeStyle():

    def __init__(self, view):
        self._view = view
        self._scope_style_cache = {}

        color_scheme = self._view.settings().get('color_scheme')
        self._plist = plistlib.readPlistFromBytes(bytes(load_resource(color_scheme), 'UTF-8'))

        self._default_styles = {}
        for plist_settings_dict in self._plist['settings']:
            if 'scope' not in plist_settings_dict:
                self._default_styles.update(plist_settings_dict['settings'])

    def at_point(self, point):
        scope = self._view.scope_name(point).strip()

        if scope in self._scope_style_cache:
            return self._scope_style_cache[scope]

        style = self._default_styles.copy()
        scored_styles = []
        for color_scheme_definition in self._plist['settings']:
            if 'scope' in color_scheme_definition:
                score = score_selector(scope, color_scheme_definition['scope'])
                if score:
                    color_scheme_definition.update({'score': score})
                    scored_styles.append(color_scheme_definition)

        for s in sorted(scored_styles, key=lambda k: k['score']):
            style.update(s['settings'])

        self._scope_style_cache[scope] = style

        return style
