from curtsies import FSArray, fmtfuncs
import os
from .BaseScreen import BaseScreen


class MainScreen(BaseScreen):
    def __init__(self, challenges, ms_names):
        self._challenges = challenges
        self._ms_names = ms_names
        self._selected_matchsettings = None
        BaseScreen.__init__(self)
        self._set_frames()
        self._display_help_overlay = False
        self._display_info_overlay = False
        self._display_select_ms_overlay = False
        self._redraw_frame = True
        self._marked_item = [0, 0, 0]
        self._marked_matchsetting = 0
        self._matchsettings_challenges = list()

    def _set_frames(self):
        self._avail_lines = self._fsa.height
        self._draw_start = 0
        self._set_header()
        self._set_footer()
        self._draw_start += 1
        first_half = int((self._fsa.width - 3) / 2) + (self._fsa.width - 3) % 2
        second_half = int((self._fsa.width - 3) / 2)
        self._fsa[self._draw_start, 0:] = ['+' + '-' * first_half + '+' + '-' * second_half + '+']
        self._draw_start += 1
        challenges_title = 'Challenges'
        matchsettings_title = f'MatchSettings: {self._selected_matchsettings if self._selected_matchsettings else "<NONE>"}'
        fhf = int((first_half - len(challenges_title)) / 2)
        fhs = int((first_half - len(challenges_title)) / 2) + (first_half - len(challenges_title)) % 2
        shf = int((second_half - len(matchsettings_title)) / 2)
        shs = int((second_half - len(matchsettings_title)) / 2) + (second_half - len(matchsettings_title)) % 2
        self._fsa[self._draw_start, 0:] = ['|' + ' ' * fhf + challenges_title + ' ' * fhs + '|' + ' ' * shf + matchsettings_title + ' ' * shs + '|']
        self._draw_start += 1
        self._fsa[self._draw_start, 0:] = ['+' + '-' * first_half + '+' + '-' * second_half + '+']
        self._draw_start += 1
        self._fsa[self._fsa.height - 3, 0:] = ['+' + '-' * first_half + '+' + '-' * second_half + '+']
        self._avail_lines -= 5
        for i in range(self._avail_lines):
            self._fsa[self._draw_start + i, 0:] = ['|' + ' ' * first_half + '|' + ' ' * second_half + '|']
        self._redraw_frame = False

    def _set_header(self):
        self.write_centered(self._draw_start, '--== MatchSettings Editor ==--')
        self.write_centered(self._draw_start + 1, 'edit your MatchSettings in a convenient way')
        self._avail_lines -= 2
        self._draw_start += 2

    def _set_footer(self):
        q = fmtfuncs.bold('ENTER') + ' to continue; ' + fmtfuncs.bold('q') + ' or ' + fmtfuncs.bold('ESC') + ' to exit; ' + fmtfuncs.bold('?') + ' for Help'
        self.write_centered(self._fsa.height - 1, q)
        self._avail_lines -= 2

    def draw(self):
        width, height = os.get_terminal_size(0)
        if not self._fsa.width == width or not self._fsa.height == height or self._redraw_frame:
            del self._fsa
            self._fsa = FSArray(height, width)
            self._set_frames()

        challenges_by_id = dict()
        if len(self._matchsettings_challenges) > 0:
            for challenge in self._challenges.values():
                challenges_by_id[challenge['id']] = challenge
        avail_top_half = int(self._avail_lines / 2)
        avail_bottom_half = self._avail_lines - avail_top_half
        list_half = (int((self._fsa.width - 3) / 2) + (self._fsa.width - 3) % 2) - 1

        # first column
        startline = 0
        marked_item = self._marked_item[1]
        marked_col = self._marked_item[0] == 0
        if len(self._challenges) > self._avail_lines:
            if marked_item > avail_top_half:
                startline = marked_item - avail_top_half
            if len(self._challenges) - marked_item < avail_bottom_half:
                startline = len(self._challenges) - self._avail_lines
        if startline > 0:
            self._fsa[5, 2:10] = ['\u2B9D ' * 4]
        else:
            self._fsa[5, 2:10] = ['--' * 4]
        if marked_item < len(self._challenges) - avail_bottom_half:
            self._fsa[self._fsa.height - 3, 2:10] = ['\u2B9F ' * 4]
        else:
            self._fsa[self._fsa.height - 3, 2:10] = ['--' * 4]
        draw_line = self._draw_start
        for i in range(startline, min(len(self._challenges), self._avail_lines + startline)):
            item = sorted(self._challenges.keys())[i]
            if len(item) > list_half:
                item = item[0:list_half - 3] + '...'
            if i == marked_item and marked_col:
                item = fmtfuncs.invert(item)
            elif i == marked_item:
                item = fmtfuncs.on_gray(item)
            self._fsa[draw_line, 2:list_half + 2] = [item]
            draw_line += 1

        # second column
        startline = 0
        marked_item = self._marked_item[2]
        marked_col = self._marked_item[0] == 1
        if len(self._matchsettings_challenges) > self._avail_lines:
            if marked_item > avail_top_half:
                startline = marked_item - avail_top_half
            if len(self._matchsettings_challenges) - marked_item < avail_bottom_half:
                startline = len(self._matchsettings_challenges) - self._avail_lines
        if startline > 0:
            self._fsa[5, list_half + 4:list_half + 12] = ['\u2B9D ' * 4]
        else:
            self._fsa[5, list_half + 4:list_half + 12] = ['--' * 4]
        if marked_item < len(self._matchsettings_challenges) - avail_bottom_half:
            self._fsa[self._fsa.height - 3, list_half + 4:list_half + 12] = ['\u2B9F ' * 4]
        else:
            self._fsa[self._fsa.height - 3, list_half + 4:list_half + 12] = ['--' * 4]
        draw_line = self._draw_start
        for i in range(startline, min(len(self._matchsettings_challenges), self._avail_lines + startline)):
            c = self._matchsettings_challenges[i]
            item = challenges_by_id[c[0]]['name']
            if len(item) > list_half:
                item = item[0:list_half - 3] + '...'
            if i == marked_item and marked_col:
                item = fmtfuncs.invert(item)
            elif i == marked_item:
                item = fmtfuncs.on_gray(item)
            self._fsa[draw_line, list_half + 4:list_half * 2 + 2] = [item]
            draw_line += 1

        if self._display_help_overlay:
            self._draw_overlay('<center>--== HELP ==--\n\n\n\
  <UP>, <DOWN>: Navigate trough Lists \n\
       <SPACE>: add/remove marked Challenge to MatchSetting \n\
<PAGE-UP/DOWN>: move marked Challenge in MatchSetting \n\n\
             ?: This Help\n\
      q, <ESC>: Exit \n\n\n\
<center>Hit <ENTER>/<ESC> to return')
        elif self._display_info_overlay:
            self._draw_overlay('<center> --== INFO ==-- \n\n<center> ' + self._display_info_overlay + ' \n\n<center> Hit <ENTER>/<ESC> to return ')
        elif self._display_select_ms_overlay:
            lines = list()
            lines.append('<center> --==Select MatchSettings File ==-- ')
            lines.append('')
            for i in range(len(self._ms_names)):
                ms = sorted(self._ms_names)[i]
                if i == self._marked_matchsetting:
                    ms = fmtfuncs.invert(ms)
                lines.append('<center> ' + ms + ' ')
            lines.append('')
            lines.append('<center> Hit <ESC> to return ')
            self._draw_overlay(lines)
        return self._fsa

    def display_info_overlay(self, text=False):
        self._display_info_overlay = text

    def display_help_overlay(self, enabled=True):
        self._display_help_overlay = enabled
        if not enabled:
            self._redraw_frame = True

    def display_select_ms_overlay(self, enabled=True):
        self._display_select_ms_overlay = enabled
        if not enabled:
            self._redraw_frame = True

    def mark_next_item(self):
        if self._marked_item[0] == 0:
            self._marked_item[1] += 1
            self._marked_item[1] %= len(self._challenges)
        else:
            self._marked_item[2] += 1
            self._marked_item[2] %= len(self._matchsettings_challenges)

    def mark_prev_item(self):
        if self._marked_item[0] == 0:
            self._marked_item[1] -= 1
            self._marked_item[1] %= len(self._challenges)
        else:
            self._marked_item[2] -= 1
            self._marked_item[2] %= len(self._matchsettings_challenges)

    def toggle_item_column(self):
        self._marked_item[0] += 1
        self._marked_item[0] %= 2
        self._marked_item[1] %= len(self._challenges)
        self._marked_item[2] %= len(self._matchsettings_challenges)

    def mark_next_matchsetting(self):
        self._marked_matchsetting += 1
        self._marked_matchsetting %= len(self._ms_names)

    def mark_prev_matchsetting(self):
        self._marked_matchsetting -= 1
        self._marked_matchsetting %= len(self._ms_names)

    def apply_marked_matchsetting(self):
        self._selected_matchsettings = sorted(self._ms_names)[self._marked_matchsetting]
        return self._selected_matchsettings

    def set_matchsettings_challenges(self, challenges):
        self._matchsettings_challenges = challenges
