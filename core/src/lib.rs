
mod settings;

pub mod db;
pub mod part;

pub mod config {

    use crate::settings::Config;
    use figment::{Figment, providers::{Format, Toml}};
    
    pub fn config() -> Config {
        let config: Config = Figment::new()
            .merge(Toml::file("config/default.toml"))
            .merge(Toml::file("config/conf.toml"))
            .extract().unwrap();
    
        config
    }
    
}