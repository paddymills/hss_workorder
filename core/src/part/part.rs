
use std::{
    convert::TryInto,
    fmt::{self, Display, Formatter}
};

use crate::part::CommType;

const DEFAULT_PUNCH_THK: f32 = 0.625;

#[derive(Debug, Default)]
pub struct Part {
    pub mark: String,

    pub qty: i32,
    pub comm: CommType<String>,
    pub desc: String,
    pub thk: f32,
    pub wid: f32,
    pub len: f32,

    spec: Option<String>,
    grade: Option<String>,
    test: Option<String>,
    remark: Option<String>,

    // TODO: implement operations
    can_punch: bool,
    has_holes: bool,
    has_end_mill: bool,
    nx_prog: bool,
    bent: bool,
    addl_mill: bool,
}

impl Part {
    
    pub fn is_pl(&self) -> bool {
        match self.comm {
            CommType::Plate(_) => true,
            _ => false
        }
    }

    pub fn grade(&self) -> String {
        self._grade(false)
    }

    pub fn grade_cvn(&self) -> String {
        self._grade(true)
    }

    fn _grade(&self, force_cvn: bool) -> String {

        let mut result = String::new();

        match &self.spec {
            Some(s) => {
                match s.as_str() {
                    "A240 Type 304" => return String::from("A240-304"),
                    x => result += x,
                }
            },
            None => return result,
        }

        result += "-";

        let mut zone = "2";
        match &self.grade {
            Some(g) => {
                if g.starts_with("HPS") {
                    zone = "3"
                }

                result += g;
            },
            _ => (),
        };

        match &self.test {
            Some(s) => {
                match s.as_str() {
                    "FCM" => result += &("F{}".to_owned() + zone),
                    "T" =>   result += &("T{}".to_owned() + zone),
                    _ => ()
                }
            },
            None => {
                if force_cvn {
                    result += &("T".to_owned() + zone);
                }
            },
        };

        result
    }

    pub fn infer_ops(&mut self) {
        // TODO: punch thickness 5/8" or 3/4"
        let punch_thk = DEFAULT_PUNCH_THK;

        if let Some(remark) = &self.remark {
            let uremark = remark.to_lowercase();
            if uremark.contains("b1e") {
                self.has_end_mill = true;
            }
            else if self.has_holes && self.thk <= punch_thk && uremark.contains("fill") {
                self.can_punch = true;
            }

            if uremark.contains("bent") {
                self.bent = true
            }
        }
    }

    pub fn ops(&self) -> [String; 3] {
        /*
            Possible operations:
                - Punch
                - Drill
                - Drill/End Mill
                - NX
                - Press
                - Rojar
        */

        let mut ops: Vec<&str> = Vec::with_capacity(3);

        if self.has_holes {
            ops.push({
                if self.has_end_mill {      "Drill/End Mill" }
                else if self.can_punch {    "Punch" }
                else {                      "Drill" }
            });
        }

        if self.nx_prog {       ops.push("NX"); }
        if self.addl_mill {     ops.push("Rojar")}
        if self.bent {          ops.push("Press"); }

        while ops.len() < 3 {
            ops.push("");
        }

        ops.iter().map(|x| x.to_string()).collect::<Vec<_>>().try_into().unwrap()
    }
}

impl From<&tiberius::Row> for Part {
    fn from(row: &tiberius::Row) -> Self {
        let unwrap_or_none = |x: Option<&str>| {
            match x {
                Some("") => None,
                Some(a) => Some(a.to_string()),
                None => None
            }
        }; 

        Self {
            mark: row.get::<&str, _>("Piecemark").unwrap_or_default().into(),

            qty:  row.get::<i32, _>("Qty").unwrap_or_default(),
            comm: row.get::<&str, _>("Commodity").into(),
            desc: row.get::<&str, _>("Description").unwrap_or_default().into(),

            thk: row.get::<f32, _>("Thick").unwrap_or_default(),
            wid: row.get::<f32, _>("Width").unwrap_or_default(),
            len: row.get::<f32, _>("Length").unwrap_or_default(),

            spec:   unwrap_or_none(row.get::<&str, _>("Specification")),
            grade:  unwrap_or_none(row.get::<&str, _>("Grade")),
            test:   unwrap_or_none(row.get::<&str, _>("ImpactTest")),
            remark: unwrap_or_none(row.get::<&str, _>("Remark")),

            ..Default::default()
        }
    }
}

impl Display for Part {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{} ({} x {}) [{}]", self.mark, self.desc, self.len, self.grade())
    }
}
