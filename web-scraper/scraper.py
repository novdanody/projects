import requests


def scrap_web(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise("Status Code is %d" % resp.status_code)
    return resp.content

# Arabica Coffee	ODA	ODA/PCOFFOTM_USD
# Robusta Coffee	ODA	ODA/PCOFFROB_USD
# Coffee Futures	ICE	CHRIS/ICE_KC1