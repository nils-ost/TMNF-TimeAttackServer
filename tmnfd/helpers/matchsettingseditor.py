from curtsies import FullscreenWindow, Input
from screens import MainScreen
from helpers.config import get_config
from helpers.settings import MatchSettings
from pygbx import Gbx, GbxType
from glob import glob
import sys
import os


alphanumerical = [
    u'a', u'b', u'c', u'd', u'e', u'f', u'g', u'h', u'i', u'j', u'k', u'l', u'm', u'n', u'o',
    u'p', u'q', u'r', u's', u't', u'u', u'v', u'w', u'x', u'y', u'z', u'A', u'B', u'C', u'D',
    u'E', u'F', u'G', u'H', u'I', u'J', u'K', u'L', u'M', u'N', u'O', u'P', u'Q', u'R', u'S',
    u'T', u'U', u'V', u'W', u'X', u'Y', u'Z', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'0'
]

matchsettings_names = list()
path = os.path.normpath(get_config()['match_settings']) + '/'
for f in glob(os.path.join(path, '*.txt')):
    matchsettings_names.append(f.replace(path, '').replace('.txt', ''))


challenges = dict()
path = os.path.normpath(get_config()['challenges_path']) + '/'
for f in \
        glob(os.path.join(path, 'Campaigns', 'Nations', '**', '*.Challenge.Gbx'), recursive=True) + \
        glob(os.path.join(path, 'Challenges', '**', '*.Challenge.Gbx'), recursive=True):
    g = Gbx(f)
    challenge = g.get_class_by_id(GbxType.CHALLENGE)
    if not challenge:
        continue
    challenges[challenge.map_name] = dict({
        'id': challenge.map_uid,
        'name': challenge.map_name,
        'path': f.replace(path, '')})


def run():
    selected_ms_name = None
    with FullscreenWindow(sys.stdout) as window:
        with Input() as reactor:
            ms = MainScreen(challenges, matchsettings_names)
            active_screen = 'ms'
            reactor_event = None
            while True:
                if reactor_event:
                    # MainScreen Inputs
                    if active_screen == 'ms':
                        if reactor_event in [u'q', u'<ESC>']:
                            break
                        elif reactor_event == u'<UP>':
                            ms.mark_prev_item()
                        elif reactor_event == u'<DOWN>':
                            ms.mark_next_item()
                        elif reactor_event in [u'<LEFT>', u'<RIGHT>']:
                            if selected_ms_name is not None:
                                ms.toggle_item_column()
                        elif reactor_event == u'm':
                            ms.toggle_add_mode()
                        elif reactor_event == u'?':
                            active_screen = 'ms_help'
                            ms.display_help_overlay()
                        elif reactor_event == u'<Ctrl-j>':
                            if selected_ms_name is not None:
                                ms.add_marked_item()
                        elif reactor_event == u'<DELETE>':
                            if selected_ms_name is not None:
                                ms.remove_marked_item()
                        elif reactor_event == u'<PAGEUP>':
                            if selected_ms_name is not None:
                                ms.move_marked_item_up()
                        elif reactor_event == u'<PAGEDOWN>':
                            if selected_ms_name is not None:
                                ms.move_marked_item_down()
                        elif reactor_event == u'o':
                            active_screen = 'ms_select_ms'
                            ms.display_select_ms_overlay()
                    elif active_screen in ['ms_help', 'ms_info']:
                        if reactor_event in [u'<Ctrl-j>', u'<ESC>']:
                            active_screen = 'ms'
                            ms.display_help_overlay(False)
                            ms.display_info_overlay(False)
                    elif active_screen in ['ms_select_ms']:
                        if reactor_event == u'<ESC>':
                            active_screen = 'ms'
                            ms.display_select_ms_overlay(False)
                        elif reactor_event == u'<Ctrl-j>':
                            selected_ms_name = ms.apply_marked_matchsetting()
                            matchsettings = MatchSettings(selected_ms_name + '.txt')
                            ms.set_matchsettings_challenges(matchsettings.get_challenges())
                            active_screen = 'ms'
                            ms.display_select_ms_overlay(False)
                        elif reactor_event == u'<UP>':
                            ms.mark_prev_matchsetting()
                        elif reactor_event == u'<DOWN>':
                            ms.mark_next_matchsetting()

                window.render_to_terminal(ms.draw())
                reactor_event = reactor.send(1)
