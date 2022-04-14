
import xlwings

from lib import Part
from lib.db import DbConnection, SndbConnection

from . import config
from change_mgmt import ChangeManager


def init_data(job, shipment):
    parts = dict()
    with DbConnection(server=config.db.engineering.server, use_win_auth=True) as db:
        cursor = db.cursor
        cursor.execute("EXEC BOM.SAP.GetBOMData @Job=?, @Ship=?", job, shipment)
        for row in cursor.fetchall():
            tmp = Part(row)

            if tmp.comm.is_plate:
                assert tmp.mark not in parts, "Part<{}> duplicated from BOM export".format(tmp.mark)
                parts[tmp.mark.upper()] = tmp

    with SndbConnection(**config.db.sigmanest) as db:
        cursor = db.cursor
        cursor.execute("""
            SELECT PartName, Data6, Data7, Data8
            FROM Part
            WHERE PartName LIKE ?
        """, job + '_%')
        for row in cursor.fetchall():
            mark = row.PartName.split("_", 1)[1].upper()
            if mark in parts:
                parts[mark].set_ops(row.Data6, row.Data7, row.Data8)

    # TODO: retrieve raw material masters, sizes and mapping

    return parts.values()


def import_workorder(parts):
    change_manager = ChangeManager()
    change_manager.process_parts(parts)


def update_charge_ref(job, shipment, charge_ref):
    with SndbConnection(**config.db.sigmanest) as db:
        db.cursor.execute("""
            UPDATE Part
            SET Data5=?
            WHERE Data1=?
            AND Data2=?
        """, charge_ref, job, shipment)
        db.commit()


if __name__ == "__main__":
    parts = init_data('1200055C', 3)

    data = [["Part", "Desc", "Grade", "Remark", "Op1", "Op2", "Op3"]]
    for part in parts.values():
        if part.is_secondary:
            ops = part.operations
        else:
            ops = [None, None, None]

        data.append([
            part.mark, part.desc, str(part.grade), part.autoprocess_instruction, *ops
        ])

    sheet = xlwings.books.active.sheets.active
    sheet.range("A1").value = data
    sheet.autofit('c')
