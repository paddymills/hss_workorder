
from lib import SndbConnection, DictObj
from . import config

HEATSWAP_KEYWORD = "HighHeatNum"
TRANSTYPES = DictObj(dict(
    new="SN84",
    revise="SN81",
    delete="SN82",
))

class ChangesManager:
    
    def __init__(self):
        self.db = SndbConnection(**config.db.sigmanest)

    def process_parts(self, parts):
        for part in parts:
            self.import_with_changes(part)

    def import_with_changes(self, part):
        pass

    def infer_changetype(self, part):
        pass

    def new_part(self, part):
        vals = [
            TRANSTYPES.new, config.simtrans.prd.district,
            part.wo_name, part.sn_name, part.qty, part.grade,
            part.job, part.shipment,
            part.mark, part.raw_mm, part.raw_mm_size, part.desc,
            HEATSWAP_KEYWORD
        ]

        self.db.cursor.execute("""
            INSERT INTO TransAct (
                TransType, District,
                OrderNo, ItemName, Qty, Material,
                ItemData1, ItemData2,
                ItemData9, ItemData10, ItemData11, ItemData12,
                ItemData14
            )
            Values (
                ?, ?,
                ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?,
                ?
            )
        """, *vals)
        self.db.commit()
