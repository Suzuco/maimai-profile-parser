
import json
import sys

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import pickle
import numpy as np
import pandas as pd
from PIL import Image, ImageFont, ImageDraw, ImageFile


def factors(_score):
    if _score >= 100.5:                 # ランク  達成率(%)  Rank係数
        return 22.4 * 100.5 / _score    # SSS+    100.50      22.4
    if _score >= 100:
        return 21.6                     # SSS     100.00      21.6
    elif _score >= 99.5:
        return 21.1                     # SS+     99.50       21.1
    elif _score >= 99:
        return 20.8                     # SS      99.00       20.8
    elif _score >= 98:
        return 20.3                     # S+      98.00       20.3
    elif _score >= 97:
        return 20.0                     # S       97.00       20.0
    elif _score >= 94:
        return 16.8                     # AAA     94.00       16.8
    else:
        return 0


def probe(save=None):
    # REGION: fetch
    # script configuration
    if save is None:
        save = []
    with open("config.json") as fp:
        config = json.load(fp)
        use_cache = config["use_cache"]
        session_account = config["account_info"]
        idx_aime = config["idx_aime"]
        show_played_only = config["show_played_only"]

    if use_cache:
        with open("cache_http_mas.pickle", "rb") as fp:
            http_mas = pickle.load(fp)
        with open("cache_http_rem.pickle", "rb") as fp:
            http_rem = pickle.load(fp)
    else:
        # https session
        s = requests.session()
        s.get("https://maimaidx.jp/maimai-mobile/", verify=False)
        # session cookie: token
        s_token = s.cookies['_t']
        session_account['token'] = s_token

        # attempt login
        s.post("https://maimaidx.jp/maimai-mobile/submit/", data=session_account)

        # select specific aime
        s.get("https://maimaidx.jp/maimai-mobile/aimeList/submit/?idx={}".format(idx_aime))

        # getting contents
        s.get("https://maimaidx.jp/maimai-mobile/home/")
        http_mas = s.get("https://maimaidx.jp/maimai-mobile/record/musicGenre/search/?genre=99&diff=3")
        http_rem = s.get("https://maimaidx.jp/maimai-mobile/record/musicGenre/search/?genre=99&diff=4")

        with open("cache_http_mas.pickle", "wb") as fp:
            pickle.dump(http_mas, fp)
        with open("cache_http_rem.pickle", "wb") as fp:
            pickle.dump(http_rem, fp)

        # try mimicking web client logout by clicking userOption first
        s.get("https://maimaidx.jp/maimai-mobile/home/userOption/")
        s.headers['Referer'] = "https://maimaidx.jp/maimai-mobile/home/userOption/"
        s.get("https://maimaidx.jp/maimai-mobile/")
        s.close()

    # REGION: html_parse
    soup_mas = BeautifulSoup(http_mas.content, "html.parser")
    soup_rem = BeautifulSoup(http_rem.content, "html.parser")

    # REGION: read_database
    with open("database.pickle", "rb") as fp:
        db = pickle.load(fp)

    # REGION: parse_html
    inner_html = [*soup_rem.findAll("div", {"class": "w_450 m_15 p_r f_0"}),
                  *soup_mas.findAll("div", {"class": "w_450 m_15 p_r f_0"})]

    records = pd.DataFrame({"type": str(),
                            "new": str(),
                            "title": str(),
                            "difficulty": str(),
                            "lv": str(),
                            "ilv": float(),
                            "score": float(),
                            "dxscore": str(),
                            "ratingf": float(),
                            "rating": int()},
                           index=[])

    for save_html in inner_html:
        assert isinstance(save_html, Tag)
        kind = "dx" if save_html.findAll("img")[-1]["src"] == \
                       'https://maimaidx.jp/maimai-mobile/img/music_dx.png' else "std"
        title = save_html.find("div", {"class": "music_name_block"}).text
        new = "NO"
        difficulty = "r" if save_html.findAll("img")[0]["src"] == \
                              'https://maimaidx.jp/maimai-mobile/img/diff_remaster.png' else "m"
        lv = save_html.find("div", {"class": "music_lv_block"}).text
        ilv = 0
        score, dxscore = -1, ""
        img = save_html.find("div", {"class": "music_score_block w_120 t_r f_l f_12"})
        if img:
            score = float(img.text.strip()[:-1])
        else:
            if show_played_only:
                continue
        img = save_html.find("div", {"class": "music_score_block w_180 t_r f_l f_12"})
        if img:
            dxscore = img.text.strip()

        # records = records.append({"type": kind, "new": new, "title": title, "difficulty": difficulty,
        #     "lv": lv, "ilv": ilv, "score": score, "dxscore": dxscore, "ratingf": 0, "rating": 0},
        #     ignore_index=True)

        item = pd.DataFrame(data=[{"type": kind, "new": new, "title": title, "difficulty": difficulty,
                                   "lv": lv, "ilv": ilv, "score": score, "dxscore": dxscore,
                                   "ratingf": 0, "rating": 0}],
                            columns=records.columns)
        records = pd.concat([records, item], ignore_index=True)

    for img in range(len(db)):
        _ilv = (150. - img) / 10
        for j in db[img]:
            k = j[0]
            x = "std"
            y = "NO"
            if k.startswith("[NEW]"):
                k = k[5:]
                y = "YES"
            if k.endswith("[dx]"):
                k = k[:-4]
                x = "dx"
            conditions = (records["title"] == k) & (records["difficulty"] == j[1]) & (records["type"] == x)
            records.loc[conditions, "new"] = y
            records.loc[conditions, "ilv"] = _ilv

    records = records.assign(ratingf=lambda r: (r["ilv"] * r["score"] * r["score"].apply(factors) / 100))
    records = records.assign(rating=lambda r: (np.floor(r["ratingf"]).astype(int)))

    records = records.sort_values(by=['new', 'ratingf'], ascending=False)

    if "csv" in save:
        records.to_csv("miaomiaodx_ratings_{}_{}.csv".format(session_account["segaId"], idx_aime), index=False)
    if "html" in save:
        records.to_html("miaomiaodx_ratings_{}_{}.html".format(session_account["segaId"], idx_aime), index=False)
    if "png" in save:
        table_new = records.loc[records['new'] == 'YES'][["title", "ilv", "score", "rating"]][0:15]\
            .reset_index(drop=True)
        table_old = records.loc[records['new'] == 'NO'][["title", "ilv", "score", "rating"]][0:35]\
            .reset_index(drop=True)
        dxr_new, dxr_old = np.sum(table_new["rating"]), np.sum(table_old["rating"])
        dxr = dxr_old + dxr_new

        img = Image.new("RGB", (540, 980), "#d4f1ff")
        fnt = ImageFont.truetype("sarasa-gothic-sc-regular.ttf", 14)
        d = ImageDraw.Draw(img)
        d.text((14, 14), "[NEW]{} + {} = {}".format(dxr_new, dxr_old, dxr), font=fnt, fill=(0, 0, 0))
        d.text((170, 32), "==== 最新最热 BEST 15 ====", font=fnt, fill=(0, 0, 0))

        for i in range(15):
            if i >= len(table_new):
                break
            d.text((14, 50 + i * 18), str(table_new.iloc[i]["title"]), font=fnt, fill=(0, 0, 0))
            d.text((320, 50 + i * 18), str(table_new.iloc[i]["ilv"]), font=fnt, fill=(0, 0, 0))
            d.text((366, 50 + i * 18), str(table_new.iloc[i]["score"]), font=fnt, fill=(0, 0, 0))
            d.text((462, 50 + i * 18), str(table_new.iloc[i]["rating"]), font=fnt, fill=(0, 0, 0))

        d.text((170, 320), "==== 最冷最旧 BEST 35 ====", font=fnt, fill=(0, 0, 0))
        for i in range(35):
            if i >= len(table_old):
                break
            d.text((14, 338 + i * 18), str(table_old.iloc[i]["title"]), font=fnt, fill=(0, 0, 0))
            d.text((320, 338 + i * 18), str(table_old.iloc[i]["ilv"]), font=fnt, fill=(0, 0, 0))
            d.text((366, 338 + i * 18), str(table_old.iloc[i]["score"]), font=fnt, fill=(0, 0, 0))
            d.text((462, 338 + i * 18), str(table_old.iloc[i]["rating"]), font=fnt, fill=(0, 0, 0))

        with open("miaomiaodx_ratings_{}_{}.png".format(session_account['segaId'], idx_aime), "wb") as fp:
            img.save(fp)

    return records


if __name__ == "__main__":
    if len(sys.argv) > 1:
        probe(save=sys.argv[1:])
