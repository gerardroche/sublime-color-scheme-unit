import plistlib

from sublime import load_resource
from sublime import score_selector


def load_color_scheme_resource(color_scheme):
    return plistlib.readPlistFromBytes(bytes(load_resource(color_scheme), 'UTF-8'))


class ViewStyle():

    def __init__(self, view):
        self.view = view
        self.scope_style_cache = {}

        color_scheme = self.view.settings().get('color_scheme')

        self.plist = load_color_scheme_resource(color_scheme)

        self.default_styles = {}
        for plist_settings_dict in self.plist['settings']:
            if 'scope' not in plist_settings_dict:
                self.default_styles.update(plist_settings_dict['settings'])

    def at_point(self, point):
        scope = self.view.scope_name(point).strip()

        if scope in self.scope_style_cache:
            return self.scope_style_cache[scope]

        style = self.default_styles.copy()

        scored_styles = []
        for color_scheme_definition in self.plist['settings']:
            if 'scope' in color_scheme_definition:
                score = score_selector(scope, color_scheme_definition['scope'])
                if score:
                    color_scheme_definition.update({'score': score})
                    scored_styles.append(color_scheme_definition)

        for s in sorted(scored_styles, key=lambda k: k['score']):
            style.update(s['settings'])

        self.scope_style_cache[scope] = style

        return style
