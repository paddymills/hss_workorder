
use std::fs;

use serde::{Serialize, Deserialize};
use toml;

#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    pub databases: Databases,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Databases {
    pub sigmanest: String,
    pub engineering: String,
}

impl Config {
    pub fn new() -> Self {
        Self {
            databases: Databases { 
                sigmanest: String::new(),
                engineering: String::new(),
            }
        }
    }

    pub fn from(file_name: &str) -> Result<Self, toml::de::Error> {
        // read file
        match fs::read_to_string(file_name) {
            Ok(text) => toml::from_str::<Self>(&text),
            _ => {
                let cfg = Self::new();

                // write to disk
                // log errors, do not propogate them (we don't care if writing fails)
                match toml::to_string(&cfg) {
                    Ok(as_toml) => match fs::write(file_name, as_toml) {
                        Ok(_) => (),
                        Err(_) => println!("Failed to write config"),
                    },
                    Err(_) => println!("Failed to write serialize config"),
                };

                Ok(cfg)
            },
        }
    }
}
