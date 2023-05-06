from curtsies import FSArray
import os


class BaseScreen():
    def __init__(self):
        width, height = os.get_terminal_size(0)
        self._fsa = FSArray(height, width)

    def write_centered(self, row, text):
        if row < self._fsa.height:
            if len(text) > self._fsa.width:
                self._fsa[row, 0:] = [text[0:self._fsa.width]]
            else:
                w_start = int((self._fsa.width - len(text)) / 2)
                w_end = w_start + len(text)
                self._fsa[row, w_start:w_end] = [text]

    def _draw_overlay(self, text):
        dtext = []
        if type(text) == list:
            dtext = text
        else:
            for line in text.split('\n'):
                dtext.append(line)

        longest_line = 0
        for line in dtext:
            line_len = len(line)
            if line.startswith('<center>'):
                line_len -= 8
            longest_line = longest_line if longest_line > line_len else line_len

        draw_pos = max(int((self._fsa.height - (len(dtext) + 2)) / 2), 0)
        self.write_centered(draw_pos, '*' + '-' * longest_line + '*')
        draw_pos += 1
        for line in dtext:
            if line.startswith('<center>'):
                line = line[8:]
                offset = int((longest_line - len(line)) / 2)
                self.write_centered(draw_pos, '|' + ' ' * offset + line + ' ' * (longest_line - (len(line) + offset)) + '|')
            else:
                self.write_centered(draw_pos, '|' + line + ' ' * (longest_line - len(line)) + '|')
            draw_pos += 1
        self.write_centered(draw_pos, '*' + '-' * longest_line + '*')
