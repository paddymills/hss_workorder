
# from curses import setupterm
from pyodbc import Row
import re

PLATE_COMM = re.compile(r"PL|SHEET")
SHAPE_COMM = re.compile(r"L|C|MC|W|WT")

WO_REGEXES = {
    "WEBS": re.compile(r"[A-Z]+[0-9]+[A-Z]*-(?:W[NF]?[0-9]+|[A-Z]+)",   re.IGNORECASE),  # or clause added for backup bar (i.e. G1A-XA)
    "FLGS": re.compile(r"[A-Z]+[0-9]+[A-Z]*-[TB][0-9]+",                re.IGNORECASE),
    "G":    re.compile(r"X[0-9]+[A-Z]+",                                re.IGNORECASE),
    "M":    re.compile(r"M[0-9]+[A-Z]+",                                re.IGNORECASE),
    "S":    re.compile(r"Z[0-9]+[A-Z]+",                                re.IGNORECASE),
    "PD":   re.compile(r"PD[0-9]+-[A-Z]+",                              re.IGNORECASE),
}

DEFAULT_PUNCH_THK = 0.625
NUM_OPS = 3


class Part:

    def __init__(self, init_data=None, job=None, shipment=None, **kwargs):
        self.job = job
        self.shipment = shipment
        self._workorder = None
        self._ops = [None] * NUM_OPS

        self.raw_mm = None
        self.raw_mm_size = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        if init_data is not None:
            if isinstance(init_data, Row):
                self._init_sql(init_data)

    def _init_sql(self, row):
        self.mark = row.Piecemark

        self.qty = row.Qty
        self.comm = MatlType(row.Commodity)
        self.desc = row.Description

        self.thk = row.Thick
        self.wid = row.Width
        self.len = row.Length

        self.grade = MatlGrade(row.Specification, row.Grade, row.ImpactTest)
        self.remark = row.Remark

    @property
    def is_web(self):
        return WO_REGEXES["WEBS"].fullmatch(self.mark)

    @property
    def is_flange(self):
        return WO_REGEXES["FLGS"].fullmatch(self.mark)

    @property
    def is_main(self):
        # most jobs have more flanges than webs
        # so its more likely that it is a flange, than a web
        # that's why check flanges first
        return self.is_flange or self.is_web

    @property
    def is_secondary(self):
        return not self.is_main

    @property
    def workorder(self):
        if self._workorder is None:

            for name, regex in WO_REGEXES:
                if regex.match(self.mark):
                    self._workorder = name
                    break
            else:
                self._workorder = "MISC"

        return self._workorder

    @property
    def wo_name(self):
        if self.job is None:
            raise ValueError("No job specified")
        if self.shipment is None:
            raise ValueError("No shipment specified")

        return "-".join([self.job, self.shipment, self.workorder])

    def set_workorder_name(self, workorder):
        self.workorder = workorder

    @property
    def sn_name(self):
        if self.job is None:
            raise ValueError("No job specified")

        return "{}_{}".format(self.job, self.mark)

    @property
    def operations(self):
        if self._ops is None:
            self.infer_ops()

        return self._ops

    def infer_ops(self, min_punch=DEFAULT_PUNCH_THK, **kwargs):
        # Possible operations:
        #     - Punch
        #     - Drill
        #     - Drill/End Mill
        #     - NX
        #     - Press
        #     - Rojar
        #     - Bevel

        # TODO: find if part has holes
        has_holes = kwargs.get("has_holes", False)

        def find_remark(val):
            return re.search(val, self.remark, re.IGNORECASE)

        has_end_mill = kwargs.get("has_end_mill") or find_remark("b1e")
        bent = find_remark("bent")
        can_punch = kwargs.get("can_punch") or all([
            find_remark("fill"),
            self.grade.test is None,
            self.thk <= min_punch,
        ])

        ops = []
        # TODO: infer NX program
        nx_program = kwargs.get("nx_program", False)

        if nx_program:
            ops.append("NX")
        elif has_holes:
            if has_end_mill:
                ops.append("Drill/End Mill")
            elif can_punch:
                ops.append("Punch")
            else:
                ops.append("Drill")

        # TODO: find if part has end bevel/LSB
        elif has_end_mill:
            ops.append("Rojar")

        if bent:
            ops.append("Press")

        while len(ops) < NUM_OPS:
            ops.append(None)

        self._ops = ops

    def set_ops(self, *ops):
        assert len(ops) <= len(self._ops), "Too many operations, expected {}, got {}".format(len(self._ops), ops)
        for i, op in enumerate(ops):
            self._ops[i] = op

    @property
    def autoprocess_instruction(self):
        if self.is_main:
            return None

        op_map = {
            "Drill/End Mill": "Mill",
            "Drill": "Drill",
            "Punch": "Punch",
        }

        for op in self._ops:
            if op in op_map:
                return op_map[op]

        return "Blank"

    def add_raw_matl(self, mm, size):
        self.raw_mm = mm
        self.raw_mm_size = size


class MatlGrade:

    def __init__(self, spec, grade, test):
        self.spec = spec or None
        self.grade = grade or None
        self.test = test or None
        self.zone = 2

        self.is_charpy_appl = True

        # odd grades stored in spec only
        SPEC_MATCHES = {
            "A240 Type 304": ("A240", "304", None),
            "A606 TYPE 4": ("A606", "TYPE4", None),
        }
        if spec in SPEC_MATCHES:
            self.spec, self.grade, self.test = SPEC_MATCHES[spec]
            self.is_charpy_appl = False
            return

        # HPS -> zone 3
        if spec.startswith("HPS"):
            self.zone = 3

        if test == "FCM":
            self.test = "F"

    def __str__(self):
        if self.spec is None or self.grade is None:
            return ""

        if self.test:
            test = "{}{}".format(self.test, self.zone)
        else:
            test = ""

        return "{}-{}{}".format(self.spec, self.grade, test)

    @property
    def charpy(self):
        if self.test is None and self.is_charpy_appl:
            return MatlGrade(self.spec, self.grade, self.test or "T")

        return self


class MatlType:

    def __init__(self, comm):
        self.comm = comm

    @property
    def is_plate(self):
        return PLATE_COMM.fullmatch(self.comm)

    @property
    def is_shape(self):
        return SHAPE_COMM.fullmatch(self.comm)
