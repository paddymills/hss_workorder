
use std::fmt::{self, Write};

pub const GET_BOM: &str = "EXEC BOM.SAP.GetBOMData @Job=@P1, @Ship=@P2";

enum CommType {
    Plate,
    Shape,
    Skip
}

#[derive(Debug, Default)]
pub struct Part {
    pub mark: String,

    pub qty: i32,
    pub comm: String,
    pub desc: String,
    pub thk: f32,
    pub wid: f32,
    pub len: f32,

    spec: Option<String>,
    grade: Option<String>,
    test: Option<String>,
    remark: Option<String>,

    can_punch: bool,
    has_holes: bool,
    has_end_mill: bool,
    nx_prog: bool,
    bent: bool,
    addl_mill: bool,
}

impl Part {

    pub fn from_sql(row: &tiberius::Row) -> Self {

        let unwrap_or_none = |x: Option<&str>| {
            match x {
                Some("") => None,
                Some(a) => Some(a.to_string()),
                None => None
            }
        };

        Self {
            mark: row.get::<&str, _>("Piecemark").unwrap_or_default().to_string(),

            qty: row.get::<i32, _>("Qty").unwrap_or_default(),
            comm: row.get::<&str, _>("Commodity").unwrap_or_default().to_string(),
            desc: row.get::<&str, _>("Description").unwrap_or_default().to_string(),

            thk: row.get::<f32, _>("Thick").unwrap_or_default(),
            wid: row.get::<f32, _>("Width").unwrap_or_default(),
            len: row.get::<f32, _>("Length").unwrap_or_default(),

            spec: unwrap_or_none(row.get::<&str, _>("Specification")),
            grade: unwrap_or_none(row.get::<&str, _>("Grade")),
            test: unwrap_or_none(row.get::<&str, _>("ImpactTest")),
            remark: unwrap_or_none(row.get::<&str, _>("Remark")),

            ..Default::default()
        }
    }

    fn comm_type(&self) -> CommType {
        match self.comm.as_str() {
            "PL" => CommType::Plate,
            "L" => CommType::Shape,
            "MC" => CommType::Shape,
            "C" => CommType::Shape,
            "W" => CommType::Shape,
            "WT" => CommType::Shape,
            _ => CommType::Skip,
        }
    }

    pub fn is_skip_comm(&self) -> bool {
        match self.comm_type() {
            CommType::Skip => true,
            _ => false,
        }
    }

    pub fn is_pl(&self) -> bool {
        match self.comm_type() {
            CommType::Plate => true,
            _ => false,
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
                    x => write!(&mut result, "{}", x).expect("Failed to write to stream"),
                }
            },
            None => return result,
        }

        write!(&mut result, "-").expect("Failed to write to stream");

        let mut zone = 2;
        match &self.grade {
            Some(g) => {
                if g.starts_with("HPS") {
                    zone = 3
                }

                write!(&mut result, "{}", g).expect("Failed to write to stream");
            },
            _ => (),
        };

        match &self.test {
            Some(s) => {
                match s.as_str() {
                    "FCM" => write!(&mut result, "F{}", zone).expect("Failed to write to stream"),
                    "T" => write!(&mut result, "T{}", zone).expect("Failed to write to stream"),
                    _ => ()
                }
            },
            None => {
                if force_cvn {
                    write!(&mut result, "T{}", zone).expect("Failed to write to stream");
                }
            },
        };

        result
    }

}

impl fmt::Display for Part {

    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} ({} x {}) [{}]", self.mark, self.desc, self.len, self.grade())
    }

}
