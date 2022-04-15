import json
import sys

import requests
import re
import pickle

with open("config.json", "r") as fp:
    use_cache = json.load(fp)["use_cache"]

if use_cache:
    url = 'https://sgimera.github.io/mai_RatingAnalyzer/scripts_maimai/maidx_in_lv_data_universeplus.js'
    js = requests.get(url).content
    with open('maidx_in_lv_data_universeplus.js', 'wb') as fp:
        fp.write(js)
else:
    with open('maidx_in_lv_data_universeplus.js', 'rb') as fp:
        js = fp.read()

_py = js.decode('utf-8')

_py = _py[_py.find("const lv15_rslt"):_py.find("const lv12_rslt")]
_py = re.sub(r'''<u>(.+)</u>''', "[NEW]\\1", _py)
_py = re.sub(r'''"<span class='wk_(.)'>(.+?)(?:\(std\))?</span>"''', "    ('''\\2''', '\\1')", _py)
_py = re.sub(r"const ", "", _py)
_py = re.sub(r"\n\[", "\n  [", _py)
_py = re.sub(r"\n]([\n,])", "\n  ]\\1", _py)
_py = re.sub(r"];", "]", _py)

lv15_rslt, lv14_rslt, lv13_rslt = None, None, None

abbrs = [('Sqlupp(Camellia)', """Sqlupp (Camellia's "Sqleipd*Hiytex" Remix)"""),
         ('Contrapasso', """Contrapasso -paradiso-"""),
         ('Excalibur', """Excalibur ～Revived resolution～"""),
         ('Caliburne', """Caliburne ～Story of the Legendary sword～"""),
         ('otorii INNOVATED', """otorii INNOVATED -[i]3-""")]

for abbr, full in abbrs:
    _py = _py.replace(abbr, full)


if __name__ == '__main__':
    print(_py)
    if "-f" not in sys.argv and (input("Proceed (y/N)? ").lower() in ['y', 'yes']):
        exec(_py)
        with open("database.pickle", "wb") as fp:
            pickle.dump([*lv15_rslt, *lv14_rslt, *lv13_rslt], fp)
