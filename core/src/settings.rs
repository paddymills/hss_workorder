
use serde::{Deserialize};

#[derive(Deserialize)]
pub struct Config {
    pub database: Databases,
}

#[derive(Deserialize)]
pub struct Databases {
    pub sigmanest: String,
    pub engineering: String,
}
