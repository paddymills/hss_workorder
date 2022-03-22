
from pyodbc import Row
import re

PLATE_COMM = re.compile(r"[PL|SHEET]")
SHAPE_COMM = re.compile(r"[L|C|MC|W|WT]")

WO_REGEXES = {
    "WEBS": re.compile(r"[A-Z]+[0-9]+[A-Z]*-(?:W[NF]?[0-9]+|X[A-Z])"),  # or clause added for backup bar (i.e. G1A-XA)
    "FLGS": re.compile(r"[A-Z]+[0-9]+[A-Z]*-[TB][0-9]+"),
    "G": re.compile(r"X[0-9]+[A-Z]+"),
    "M": re.compile(r"M[0-9]+[A-Z]+"),
    "S": re.compile(r"Z[0-9]+[A-Z]+"),
    "PD": re.compile(r"PD[0-9]+-[A-Z]+"),
}

DEFAULT_PUNCH_THK = 0.625


class Part:

    def __init__(self, init_data=None, **kwargs):
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

        self.grade = MatlGrade(row.Specification, row.Grade, row.Test)
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
    def wo_name(self):
        for name, regex in WO_REGEXES:
            if regex.match(self.mark):
                return name

        return "MISC"


    def infer_ops(self, min_punch=DEFAULT_PUNCH_THK):
        # Possible operations:
        #     - Punch
        #     - Drill
        #     - Drill/End Mill
        #     - NX
        #     - Press
        #     - Rojar
        #     - Bevel

        # TODO: find if part has holes
        has_holes = False

        find_remark = lambda x: re.search(x, self.remark, re.IGNORECASE)
        has_end_mill = find_remark("b1e")
        bent = find_remark("bent")
        can_punch = all([
            find_remark("fill"),
            self.grade.test is None,
            self.thk <= min_punch,
        ])

        ops = []
        # TODO: infer NX program
        nx_program = False

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

        while len(ops) < 3:
            ops.append(None)

        return ops


class MatlGrade:

    def __init__(self, spec, grade, test):
        self.spec = spec
        self.grade = grade
        self.test = test
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
        if self.test:
            test = self.test + self.zone
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
