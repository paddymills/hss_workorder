
from collections import namedtuple
from lib import SndbConnection, DictObj
from . import config

HEATSWAP_KEYWORD = "HighHeatNum"
TRANSTYPES = DictObj(dict(
    new="SN84",
    revise="SN81",
    delete="SN82",
))

class ChangesManager:
    
    def __init__(self, dev=False):
        self.db = SndbConnection(**config.db.sigmanest)

        self.simtrans_district = config.simtrans.prd.district
        if dev:
            self.simtrans_district = config.simtrans.dev.district

    def process_parts(self, parts):
        for part in parts:
            self.import_with_changes(part)

    def import_with_changes(self, part):
        state = NestingState(part)

        # part not in an active work order
        if state.current_qty_req == 0:
            self.new_part(part)
        
        # quantity matches
        elif part.qty == state.current_qty_req:
            return

        # quantity increase
        elif part.qty > state.current_qty_req:
            self.update(part)

        # qty decrease and there are open quantities to nest
        elif state.to_nest > 0:
            self.update(part)

        # qty decrease and everything is nested
        else:
            # TODO: advise user to remove open nests (infer which ones?)
            pass
        

    def new_part(self, part):
        self.db.cursor.execute("""
            INSERT INTO TransAct (
                TransType, District,
                OrderNo, ItemName, Qty, Material,
                ItemData1, ItemData2,
                ItemData9, ItemData10, ItemData11, ItemData12,
                ItemData14
            ) Values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )
        """, (
            TRANSTYPES.new, self.simtrans_district,
            part.wo_name, part.sn_name, part.qty, part.grade,
            part.job, part.shipment,
            part.mark, part.raw_mm, part.raw_mm_size, part.desc,
            HEATSWAP_KEYWORD
        ))
        self.db.commit()

    # TODO: change_part_material
    def change_part_qty(self, part, override_qty=None):
        self.db.cursor.execute("""
            INSERT INTO TransAct (
                TransType, District,
                OrderNo, ItemName,
                Qty
            ) Values ( ?, ?, ?, ?, ? )
        """, (
            TRANSTYPES.revise, self.simtrans_district,
            part.wo_name, part.sn_name,
            override_qty or part.qty
        ))
        self.db.commit()

    def delete_part(self, part):
        self.db.cursor.execute("""
            INSERT INTO TransAct (
                TransType, District,
                OrderNo, ItemName
            ) Values ( ?, ?, ?, ? )
        """, (
            TRANSTYPES.delete, self.simtrans_district,
            part.wo_name, part.sn_name
        ))
        self.db.commit()

class NestingState:

    def __init__(self, part, **kwargs):
        Program = namedtuple("Program", ["name", "qty"])
        
        self.current_qty_req = 0
        self.grade = None

        self.in_process = list()
        self.complete = list()

        self.__dict__.update(kwargs)

        with SndbConnection(**config.db.sigmanest) as db:
            # get current work order quantity
            db.cursor.execute("""
                SELECT
                    QtyInProcess AS qty,
                    Material as grade
                FROM Part
                WHERE PartName=?
                    AND WONumber=?
            """, part.sn_name, part.wo_name)
            row = db.cursor.fetchone()
            if row:
                self.current_qty_req = row.qty
                self.grade = row.grade


            db.cursor.execute("""
                SELECT
                    'IN_PROCESS' AS state,
                    QtyInProcess AS qty,
                    Material AS grade,
                    ProgramName as prog
                FROM PIP
                WHERE PartName=?
                    AND WONumber=?

                UNION

                SELECT
                    'COMPLETE' AS state,
                    QtyInProcess AS qty,
                    Material AS grade,
                    ProgramName as prog
                FROM PIP
                WHERE PartName=?
                    AND WONumber=?
                    AND TransType='SN102'
            """, part.sn_name, part.wo_name)
            for row in db.cursor.fetchall():
                if row.state == "IN_PROCESS":
                    self.in_process.append(Program(row.prog, row.qty))
                elif row.state == "COMPLETE":
                    self.complete.append(Program(row.prog, row.qty))

    @property
    def nested(self):
        return sum([x.qty for x in (*self.in_process, *self.complete)])

    @property
    def to_nest(self):
        return self.current_qty_req - self.nested
