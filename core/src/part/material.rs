
use std::fmt::{self, Display, Formatter};
use tiberius;

#[derive(Debug, PartialEq)]
pub enum CommType<T> {
    Plate(T),
    Shape(T),
    Skip(T)
}

impl From<Option<&str>> for CommType<String> {
    fn from(value: Option<&str>) -> Self {
        match value {
            Some(val) => val.into(),
            None => Default::default()
        }
    }
}

impl From<&str> for CommType<String> {
    fn from(value: &str) -> Self {
        match value {
            "PL" => CommType::Plate(value.into()),
            "L" => CommType::Shape(value.into()),
            "MC" => CommType::Shape(value.into()),
            "C" => CommType::Shape(value.into()),
            "W" => CommType::Shape(value.into()),
            "WT" => CommType::Shape(value.into()),
            _ => Default::default(),
        }
    }
}

impl<T: Default> Default for CommType<T> {
    fn default() -> Self {
        CommType::Skip(T::default())
    }
}

pub struct Grade {
    pub spec: Option<String>,
    pub grade: Option<String>,
    pub test: Option<String>,
    pub zone: u8
}

impl From<&tiberius::Row> for Grade {
    fn from(row: &tiberius::Row) -> Self {
        Self {
            // convert Option<&str> -> Option<String>
            // https://users.rust-lang.org/t/convert-option-str-to-option-string/20533
            spec:   row.get::<&str, _>("Specification").map(Into::into),
            grade:  row.get::<&str, _>("Grade").map(Into::into),
            test:   row.get::<&str, _>("ImpactTest").map(Into::into),
            zone:   2
        }
    }
}

#[allow(dead_code)]
pub enum Test {
    Fcm,
    Charpy,
    None,
    NotApplicable
}

// impl From<Option<String>> for Test {
//     from(test: Option<String>) -> Test {
//         match test {
//             Some(s) => match &s as &str {
//                 "A240-304" => Test::NotApplicable,
//                 "A606-TYPE4" => Test::NotApplicable,
//                 "FCM" => Test::Fcm,
//                 "T" => Test::Charpy,
//                 _ => Test::None
//             },
//             None => Test::None
//         }
//     }
// }

impl Display for Test {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        let val = match self {
            Test::Fcm => "F",
            Test::Charpy => "T",
            Test::None => "",
            Test::NotApplicable => ""
        };

        write!(f, "{}", val)
    }
}
