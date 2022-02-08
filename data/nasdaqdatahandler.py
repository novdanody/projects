import nasdaqdatalink
import pandas as pd

from data.sqlitedatahandler import SQLiteDataHandler


class NasdaqDataHandler(SQLiteDataHandler):
    def __init__(self, tag):
        self.tag = tag
        SQLiteDataHandler.__init__(self, tag)

    def obtain(self):
        data = nasdaqdatalink.get(self.tag)
        data = pd.DataFrame(data)
        data = data.reset_index(drop=False)
        data = self.post_process(data)
        self.save(data, insertion_method='replace')
        return data

# Arabica Coffee	ODA	ODA/PCOFFOTM_USD
# Robusta Coffee	ODA	ODA/PCOFFROB_USD
# Coffee Futures	ICE	CHRIS/ICE_KC1
