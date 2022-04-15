from flask import Flask, render_template
import app
import pandas as pd

prober = Flask(__name__)


@prober.route("/", methods=["GET", "POST"])
def show_page():
    table = app.probe(False, False)
    assert isinstance(table, pd.DataFrame)
    table.drop(columns=["dxscore", "ratingf"], inplace=True)
    table.reset_index(drop=True, inplace=True)
    table = table.to_html()\
        .replace('class="dataframe"', 'class="table table-responsive table-hover"')\
        .replace(' style="text-align: right;"', '')
    return render_template("template.html", table=table)


if __name__ == "__main__":
    prober.run(host="0.0.0.0", port=10835)
