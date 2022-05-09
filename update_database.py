import json
import sys

import requests
import re
import pickle

with open("config.json", "r") as fp:
    use_cache = json.load(fp)["use_cache"]

if not use_cache:
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
         ('otorii INNOVATED', """otorii INNOVATED -[i]3-"""),
         ('felys', """felys -final remix-"""),
         ('AMAZING MIGHTY', """AMAZING MIGHTYYYY!!!!"""),
         ('ワンダーシャッフェン', """ワンダーシャッフェンの法則"""),
         ('キミツアー', """≠彡"/了→"""),
         ('シンフォニエッタ', """渦状銀河のシンフォニエッタ"""),
         ('エンドマーク', """エンドマークに希望と涙を添えて"""),
         ('UNiVERSE 銀河鸞翔', """U&iVERSE -銀河鸞翔-"""),
         ('壊れタ人形', """ねぇ、壊れタ人形ハ何処へ棄テらレるノ？"""),
         ('バーチャルダムネーション', """バーチャルダム　ネーション"""),
         ('雷切', """雷切-RAIKIRI-"""),
         ('待チ人ハ来ズ', """待チ人ハ来ズ。"""),
         ('チルノ9周年', """チルノのパーフェクトさんすう教室　⑨周年バージョン"""),
         ('アポカリプス', """アポカリプスに反逆の焔を焚べろ"""),
         ('パラマウントショータイム', """パラマウント☆ショータイム！！"""),
         ('ミルキースター', """ミルキースター・シューティングスター"""),
         ('ソーラン節', """ソーラン☆節""")]

for abbr, full in abbrs:
    _py = _py.replace(abbr, full)


if __name__ == '__main__':
    print(_py)
    if "-f" not in sys.argv and (input("Proceed (y/N)? ").lower() in ['y', 'yes']):
        exec(_py)
        with open("database.pickle", "wb") as fp:
            pickle.dump([*lv15_rslt, *lv14_rslt, *lv13_rslt], fp)
