
import logging

from os import scandir
from os.path import expanduser

from win32.win32api import MessageBox
from xlwings import Book, app as xl_apps
from functools import partial
from re import compile as regex

from prodctrlcore.io import HeaderParser, ProductionDemand, SNDB
from prodctrlcore.hssformats import BomDataCollector, TagSchedule, WorkOrder, WorkOrderJobData
from prodctrlcore.hssformats import workorder as HEADER_ALIASES


SSRS_REPORT_NAME = "SigmaNest Work Order"
WORKORDER_SHEET_NAME = "WorkOrders_Template"

HEAT_MARK_KEY_WORD = "HighHeatNum"

logger = logging.getLogger(__name__)


def main():
    # TODO: logging
    LOG_FILENAME = 'log.txt'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.ERROR)

    try:
        determine_processing()
    except Exception as err:
        logger.error(err)
        raise err


def determine_processing():
    for app in xl_apps:  # active excel applications
        for book in app.books:
            if book.name.startswith(SSRS_REPORT_NAME):
                book.activate()
                post_processing(book)
                return

    pre_processing()


def pre_processing():
    """
        Work order pre-processing
        Meant to be run after report has been downloaded
        but before operations are entered

        Order of operations:
            1) Open SSRS exported report
            2) Fill out any known data
                1) Get engineering BOM data (material grades)
                2) Get other work order data, if available (material grades and operations)
                3) Check for Charge Ref number
            5) Save
    """

    wb = open_ssrs_report_file()
    fill_in_data(wb.sheets[0])
    wb.save()


def post_processing(wb):
    """
        Work order pre-processing
        Meant to be run after operations are entered

        Order of operations:
            1) Save pre-subtotalled document
            2) Fill out CDS(TagSchedule)
            3) Fill out ProductionDemand spreadsheet
            4) Import WBS-split data
    """

    sheet = wb.sheets[0]

    # get header column IDs
    header = HeaderParser()
    header.add_header_aliases(HEADER_ALIASES)

    job = sheet.range(2, header.job).value
    shipment = sheet.range(2, header.shipment).value

    # open documents for writing
    workorder = WorkOrder(job, shipment)
    ts = TagSchedule(job, shipment)
    demand = ProductionDemand()
    sndb = SNDB()

    # matching regexes
    WEB_RE = regex(r"\w+-[Ww]\w+")
    FLG_RE = regex(r"\w+-[TtBb]\w+")
    PART_RE = regex(r"\A(PL|SHT|SHEET|MISC)")

    i = 2
    while sheet.range(i, 1).value:
        row = header.parse_row(sheet.range(i, 1).expand('right').value)

        # 1) Save pre-subtotalled document
        workorder.add_row(row)

        # 2) Fill out CDS(TagSchedule)
        if WEB_RE.match(row.mark):
            ts.webs.add(row)
        elif FLG_RE.match(row.mark):
            ts.flange.add(row)
        elif PART_RE.match(row.part_size):
            if row.remark and row.remark != 'Blank':
                ts.code_delivery.add(row)
        else:
            # shape items: do not push to SigmaNest
            continue

        # 3) Fill out ProductionDemand spreadsheet
        demand.add(row)

        # 4) Import WBS-split data
        sndb.updateWbsPartMapping(row)

        i += 1


def open_ssrs_report_file():
    last_modified = 0
    last_modified_path = None

    # scan through folder looking for most recent SSRS report file
    for dir_entry in scandir(expanduser(r"~\Downloads")):
        if dir_entry.name.startswith(WORKORDER_SHEET_NAME):
            if dir_entry.stat().st_mtime > last_modified:
                last_modified = dir_entry.stat().st_mtime
                last_modified_path = dir_entry.path

    # no SSRS report file found
    if last_modified_path is None:
        MessageBox(
            0, "Please download report from SSRS", "Report Not Found")
        raise FileNotFoundError

    return Book(last_modified_path)


def fill_in_data(sheet):
    # get header column IDs
    header = HeaderParser()
    header.add_header_aliases(HEADER_ALIASES)

    job = sheet.range(2, header.job).value
    shipment = sheet.range(2, header.shipment).value

    # get engineering BOM dataand previous work order data
    # TODO: fetch engineering data on demand
    #   1) read JobStandards on first occurrence (if BOM not read)
    #   2) read BOM on first occurrence of part name not matching regex
    bom = BomDataCollector(job, shipment, force_cvn=True)
    archived_data = WorkOrderJobData(job)

    i = 2
    while sheet.range(i, 1).value:
        item = partial(sheet.range, i)

        row = header.parse_row(item(1).expand('right').value)
        part_archive_data = archived_data.get_part(row.mark)

        if item(header.grade).value is None:
            if part_archive_data:
                item(header.grade).value = part_archive_data.grade
            else:
                item(header.grade).value = bom.get_part_data(row.mark).grade

        if part_archive_data:
            item(header.remark).value = part_archive_data.remark
            item(header.op1).value = part_archive_data.op1
            item(header.op2).value = part_archive_data.op2
            item(header.op3).value = part_archive_data.op3

        item(header.heat_mark_key_word).value = HEAT_MARK_KEY_WORD

        i += 1

    # verify ChargeRefNumber is valid
    if sheet.range(2, header.charge_ref_number).value is None:
        hwnd = sheet.book.app.hwnd
        MessageBox(hwnd, 'Charge Ref number needs entered.')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~ PROGRAM RUN ~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    main()
