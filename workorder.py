
import os
import logging

import xlwings

from win32.win32api import MessageBox
from functools import partial

from prodctrlcore.io import HeaderParser
from prodctrlcore.hssformats import BomDataCollector, TagSchedule, WorkOrder
from prodctrlcore.hssformats.workorder import HEADER_ALIASES, get_job_data


SSRS_REPORT_NAME = "SigmaNest Work Order"
WORKORDER_SHEET_NAME = "WorkOrders_Template"

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
    for app in xlwings.apps:  # active excel applications
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
            2) Get engineering BOM data (material grades)
            3) Get other work order data, if available (material grades and operations)
            4) Check for Charge Ref number
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
            2) Fill out ProductionDemand spreadsheet
            3) Fill out CDS(TagSchedule)
            4) Import WBS-split data
    """

    job_shipment = '-'.join(wb.sheets[0].range('K2:L2').value)

    # 1) Save pre-subtotalled document

    # 2) Fill out ProductionDemand spreadsheet

    # 3) Fill out CDS(TagSchedule)
    ts = TagSchedule(job_shipment)
    ts.webs = []
    ts.flanges = []
    ts.code_delivery = []

    # 4) Import WBS-split data


def open_ssrs_report_file():
    last_modified = 0
    last_modified_path = None

    # scan through folder looking for most recent SSRS report file
    for dir_entry in os.scandir(os.path.expanduser(r"~\Downloads")):
        if dir_entry.name.startswith(WORKORDER_SHEET_NAME):
            if dir_entry.stat().st_mtime > last_modified:
                last_modified = dir_entry.stat().st_mtime
                last_modified_path = dir_entry.path

    # no SSRS report file found
    if last_modified_path is None:
        MessageBox(
            0, "Please download report from SSRS", "Report Not Found")
        raise FileNotFoundError

    return xlwings.Book(last_modified_path)


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
    archived_data = get_job_data(job)

    i = 2
    while sheet.range(i, 1).value:
        item = partial(sheet.range, i)

        row = header.parse_row(item(1).expand('right').value)
        part_archive_data = archived_data.get(row.mark, None)

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

        i += 1

    # verify ChargeRefNumber is valid
    if sheet.range(2, header.charge_ref_number).value is None:
        hwnd = sheet.book.app.hwnd
        MessageBox(hwnd, 'Charge Ref number needs entered.')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~ PROGRAM RUN ~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    main()
