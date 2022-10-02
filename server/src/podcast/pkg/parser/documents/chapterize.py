import re
from typing import List


class Chapterize:
    def __init__(self, contents: str, lang: str):
        self.contents = contents
        self.lang = lang

        self.lines = self.get_lines()
        self.headings = self.get_headings()
        self.heading_locations = self.headings
        self.ignore_toc()

    def get_lines(self):
        return self.contents.split('\n')

    @classmethod
    def get_en_rules(cls):
        arabic_numerals = '\d+'
        roman_numerals = '(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'
        number_words_by_tens = ['twenty', 'thirty', 'forty', 'fifty', 'sixty',
                                'seventy', 'eighty', 'ninety']
        number_words = ['one', 'two', 'three', 'four', 'five', 'six',
                        'seven', 'eight', 'nine', 'ten', 'eleven',
                        'twelve', 'thirteen', 'fourteen', 'fifteen',
                        'sixteen', 'seventeen', 'eighteen', 'nineteen'] + number_words_by_tens
        number_words_pat = '(' + '|'.join(number_words) + ')'
        ordinal_number_words_by_tens = ['twentieth', 'thirtieth', 'fortieth', 'fiftieth',
                                        'sixtieth', 'seventieth', 'eightieth', 'ninetieth'] + \
                                       number_words_by_tens
        ordinal_number_words = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth',
                                'seventh', 'eighth', 'ninth', 'twelfth', 'last'] + \
                               [numberWord + 'th' for numberWord in number_words] + ordinal_number_words_by_tens
        ordinals_pat = '(the )?(' + '|'.join(ordinal_number_words) + ')'
        enumerators_list = [arabic_numerals, roman_numerals, number_words_pat, ordinals_pat]
        return {
            "enumerators_list": enumerators_list,
            "roman_numerals": roman_numerals,
            "arabic_numerals": arabic_numerals,
            "unit": "chapter",
        }

    @classmethod
    def get_zh_rules(cls):
        arabic_numerals = '\d+'
        roman_numerals = '(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'
        number_words_by_tens = ['二十', '三十', '四十', '五十', '六十',
                                '七十', '八十', '九十']
        number_words = ['一', '二', '三', '四', '五', '六',
                        '七', '八', '九', '十', '十一',
                        '十二', '十三', '十四', '十五',
                        '十六', '十七', '十八', '十九'] + number_words_by_tens
        number_words_pat = '(' + '|'.join(number_words) + ')'
        ordinals_pat = '(第 )?(' + '|'.join(number_words) + ')'
        enumerators_list = [arabic_numerals, roman_numerals, number_words_pat, ordinals_pat]
        return {
            "enumerators_list": enumerators_list,
            "roman_numerals": roman_numerals,
            "arabic_numerals": arabic_numerals,
            "unit": "(章|回)",
        }

    @classmethod
    def form_with_prefix(cls, rule: dict):
        enumerators = '(' + '|'.join(rule["enumerators_list"]) + ')'
        return f'{rule["unit"]} ' + enumerators, True

    @classmethod
    def form_with_suffix(cls, rule: dict):
        enumerators = '(' + '|'.join(rule["enumerators_list"]) + ')'
        return enumerators + rule["unit"], True

    @classmethod
    def form_with_roman_numerals_title(cls, rule: dict):
        """
        # Form 3: II. The Mail
        """
        enumerators = rule["roman_numerals"]
        separators = '(\\. | )'
        title_case = '[A-Z][a-z]'
        return enumerators + separators + title_case, False,

    @classmethod
    def form_with_roman_numerals_title_uppercase(cls, rule: dict):
        """
        # Form 3: II. THE OPEN ROAD
        """
        enumerators = rule["roman_numerals"]
        separators = '(. )'
        title_case = '[A-Z][A-Z]'
        return enumerators + separators + title_case, False

    @classmethod
    def form_with_number(cls, rule: dict):
        """
        # Form 4: a number on its own, e.g. 8, VIII
        """
        enumerators_list = [rule["arabic_numerals"], rule["roman_numerals"]]
        return '(' + '|'.join(enumerators_list) + ')', False

    def get_language_forms_funcs(self):
        langs_forms = {
            "en": [self.form_with_prefix, self.form_with_roman_numerals_title,
                   self.form_with_roman_numerals_title_uppercase, self.form_with_number],
            "zh": [self.form_with_suffix, self.form_with_roman_numerals_title,
                   self.form_with_roman_numerals_title_uppercase, self.form_with_number],
        }

        return langs_forms.get(self.lang)

    def get_headings(self):
        rule = self.get_en_rules()
        forms = {}
        for form_func in self.get_language_forms_funcs():
            regex_rule, is_case_ignore = form_func(rule)
            if is_case_ignore not in forms:
                forms[is_case_ignore] = []
            forms[is_case_ignore].append(regex_rule)

        patterns = []
        if len(forms[True]) > 0:
            pattern_str = '|'.join(forms[True])
            patterns.append(re.compile(f"({pattern_str})", re.IGNORECASE))
        elif len(forms[False] > 0):
            pattern_str = '|'.join(forms[False])
            patterns.append(re.compile(f"({pattern_str})"))

        headings = []
        for i, line in enumerate(self.lines):
            for pattern in patterns:
                if pattern.match(line) is not None:
                    headings.append(i)

        if len(headings) < 3:
            return []

        return headings

    def ignore_toc(self):
        """
        Filters headings out that are too close together,
        since they probably belong to a table of contents.
        """
        pairs = zip(self.heading_locations, self.heading_locations[1:])
        to_be_deleted = []
        for pair in pairs:
            delta = pair[1] - pair[0]
            if delta < 4:
                if pair[0] not in to_be_deleted:
                    to_be_deleted.append(pair[0])
                if pair[1] not in to_be_deleted:
                    to_be_deleted.append(pair[1])
        for bad_loc in to_be_deleted:
            index = self.heading_locations.index(bad_loc)
            del self.heading_locations[index]

    def get_text_between_headings(self):
        chapters = []
        last_heading = len(self.heading_locations) - 1
        for i, heading_location in enumerate(self.heading_locations):
            if i != last_heading:
                next_heading_location = self.heading_locations[i + 1]
                chapters.append(self.lines[heading_location + 1:next_heading_location])
        return chapters

