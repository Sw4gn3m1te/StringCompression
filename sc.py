import math
from functools import lru_cache
from typing import *
from UI import UI


@lru_cache()
def _calc_compression(s: tuple, split_len: int = None, segment_len: int = 1, str_func: Callable = str) -> list[tuple[str, int]]:
    """calculates a compression cycle with a specified chunk size
    :param s: string to compress
    :param split_len: chunk size
    :param segment_len: length of individual elements of a string (if for example segment_len = 3 A32 would be treated as a single char of the string
    :return: list of tuples representing the compressed string, if no compression was applied
     due to an incompatible chunk size each tuple only contains a single letter and a count of one for each char in s
    """
    if split_len is None:
        split_len = math.floor(len(s) / 2)

    i = 0
    res = []
    count = 1
    if str_func:
        s = tuple(str_func(x) for x in s)
    while i < len(s):
        p1 = s[i:i+split_len*segment_len]
        p2 = s[i+split_len*segment_len:i+2*split_len*segment_len]

        if p1 == p2:
            count += 1
            i += split_len*segment_len
        else:

            if count >= 2:
                res.append((p1, count))
                i += split_len*segment_len
                count = 1
                continue
            else:
                res.append((s[i:i+segment_len], 1))
                i += segment_len
                count = 1

    return res


@lru_cache()
def _compress_str_rek(s: tuple, str_func: Callable = str) -> tuple:
    """calculates the string compression for each compressable substring recursively and merges redundant brackets
    this part might me greedy due to the fact that the algorithm always favors the shortest partial solution
    :param s: string to recursively compress

    :return: list of tuples representing a compressed string
    """

    split_len = math.floor(len(s)/2)
    candidates = []
    while split_len >= 1:
        res = _calc_compression(s, split_len, str_func=str_func)
        if len([x[0] for x in res]) < len(s):
            candidates.append(res)
        split_len -= 1

    if len(candidates) == 0:
        # str max compressed
        return ((s, 1),)

    else:
        # continue recursive compression
        # collect new substr to process
        res = min(candidates, key=lambda x: len(x))
        sub_str_list = []
        sub = []
        for c in res:
            if c[1] == 1:
                sub += c[0]
            else:
                sub_str_list.append((tuple(sub), 1)) if len(sub) > 0 else None
                c = (tuple(c[0]), c[1])
                sub_str_list.append(c)
                sub = []

        sub_str_list.append((tuple(sub), 1)) if len(sub) > 0 else None
        res = []
        sub_str_list = tuple(sub_str_list)
        for (sub_str, count) in sub_str_list:
            rek_res = _compress_str_rek(sub_str, str_func=str_func)
            # term has redundant brackets -> combine
            if len(rek_res) == 1:
                (rek_str, rek_count) = rek_res[0]
                res.append((rek_str, rek_count*count))
            else:
                res.append((rek_res, count))

        return tuple(res)


def _reconstruct_str(res: tuple, str_func: Callable = str) -> str:
    """helper function to get an actual string from the result of the compression function
    :param res: result of the compression function
    :return: compressed string
    """

    str_res = ""

    for (term, count) in res:
        if not isinstance(term[0], (list, tuple)):
            if count == 1:
                for item in term:
                    str_res += str_func(item)
            else:
                if len(term) == 1:
                    for item in term:
                        str_res += str_func(item)
                    str_res += str(count)
                else:
                    str_res += UI.color_text("(", "YELLOW")
                    for item in term:
                        str_res += str_func(item)
                    str_res +=  UI.color_text(f"){count}", "YELLOW")

        else:
            if len(term) > 1:
                str_res += UI.color_text("(", "YELLOW") if count > 1 else ""
            for e in term:
                str_res += _reconstruct_str((e,))
            if len(term) > 1:
                str_res += UI.color_text(f"){count}", "YELLOW") if count > 1 else ""

    return str_res


def compress_str(s: Union[tuple, list], str_func: Callable = str) -> str:

    """ compresses a string s using an extended and improved version of RLE
    :param s: string to compress
    :return: compressed string
    """
    if isinstance(s, list):
        s = tuple(s)
    res = _compress_str_rek(s, str_func)
    res = _reconstruct_str(res, str_func)
    return res

