
import toml
import xlwings

from lib import Part, DictObj
from lib.db import DbConnection, SndbConnection

config = DictObj(toml.load("config.toml"))

def generate(job, shipment):
    parts = list()
    with DbConnection(server=config.db.engineering.server, use_win_auth=True) as db:
        cursor = db.cursor
        cursor.execute("EXEC BOM.SAP.GetBOMData @Job=?, @Ship=?", job, shipment)
        for row in cursor.fetchall():
            tmp = Part(row)

            if tmp.comm.is_plate:
                parts.append(tmp)

    data = [["Part", "Desc", "Grade", "Op1", "Op2", "Op3"]]
    for part in parts:
        if part.comm.is_plate:
            data.append([
                part.mark, part.desc, part.grade, *part.infer_ops()
            ])

    xlwings.Book().sheets.active.range("A1").value = data


def update_charge_ref(job, shipment, charge_ref):
    with SndbConnection() as db:
        cursor = db.cursor
        cursor.execute("""
            UPDATE Part
            SET Data5=?
            WHERE Data1=?
            AND Data2=?
        """, charge_ref, job, shipment)
        cursor.commit()


if __name__ == "__main__":
    generate('1200055L', 8)
