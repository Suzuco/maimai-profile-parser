# maimai-profile-parser
A set of script files that calculate Rating for maimai DX players.

- `update_database.py` fetches inferred internal levels of (ideally) every playable song
- `app.py` fetches play records of all Master and Re:master songs calculates player Rating accordingly

## Usage

(within a `venv`, etc.:)

    $ pip install -r requirements.txt
    $ vim config.json
    $ python3 update_database.py
    $ python3 app.py

## Configuration

In configuration file `config.json`:

| Key       | Type   | Description                                                                          |
|-----------|--------|--------------------------------------------------------------------------------------|
| use_cache | bool   | Whether to use local stored lists and html\'s instead of fetching latest info        |
| segaId    | string | SEGA ID account name                                                                 |
| password  | string | SEGA ID account password                                                             |
| idx_aime  | number | # of AIME of interest. Can be identified by logging in maimaidx.jp for yourself once |

Option `use_cache` will be used by both `update_database.py` and `app.py`.