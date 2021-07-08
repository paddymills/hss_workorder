
pub mod db;
mod config;

pub use config::Config;

use std::io::{self, Write};

#[allow(dead_code)]
pub fn get_user_input(prompt: &str) -> Option<String> {
    let mut input = String::new();
    
    print!("{}", prompt);
    io::stdout().flush().unwrap();

    io::stdin().read_line(&mut input).unwrap();

    match input.trim() {
        "" => None, // ends input loop
        x => Some(x.to_string())
    }
}
