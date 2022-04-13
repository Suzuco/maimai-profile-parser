import json
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

src = js.decode('utf-8')

src = src[src.find("const lv15_rslt"):src.find("const lv12_rslt")]
src = re.sub(r'''<u>(.+)</u>''', "[NEW]\\1", src)
src = re.sub(r'''"<span class='wk_(.)'>(.+?)(?:\(std\))?</span>"''', "    ('''\\2''', '\\1')", src)
src = re.sub(r"const ", "", src)
src = re.sub(r"\n\[", "\n  [", src)
src = re.sub(r"\n]([\n,])", "\n  ]\\1", src)
src = re.sub(r"];", "]", src)

lv15_rslt, lv14_rslt, lv13_rslt = None, None, None

abbrs = [('Sqlupp(Camellia)', """Sqlupp (Camellia's "Sqleipd*Hiytex" Remix)"""),
         ('Contrapasso', """Contrapasso -paradiso-"""),
         ('Excalibur', """Excalibur ～Revived resolution～"""),
         ('Caliburne', """Caliburne ～Story of the Legendary sword～"""),
         ('otorii INNOVATED', """otorii INNOVATED -[i]3-""")]

for abbr, full in abbrs:
    src = src.replace(abbr, full)

print(src)

if input("Proceed (y/N)? ").lower() in ['y', 'yes']:
    exec(src)
    with open("database.pickle", "wb") as fp:
        pickle.dump([*lv15_rslt, *lv14_rslt, *lv13_rslt], fp)
