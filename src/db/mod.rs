

mod schema;

pub use schema::*;

pub mod queries {
    pub use super::schema::GET_BOM;
}

pub mod config {

    fn config(server: String) -> Result<tiberius::Config, Box<dyn std::error::Error>> {
    
        let mut config = tiberius::Config::new();

        config.host(&server);
        config.authentication(tiberius::AuthMethod::Integrated);
        config.trust_cert();
    
        Ok(config)
    }

    pub fn eng() -> Result<tiberius::Config, Box<dyn std::error::Error>> {
        config(crate::Config::from("conf.toml")?.databases.engineering)
    }

    pub fn sn() -> Result<tiberius::Config, Box<dyn std::error::Error>> {
        config(crate::Config::from("conf.toml")?.databases.sigmanest)
    }

    pub fn sndev() -> Result<tiberius::Config, Box<dyn std::error::Error>> {
        config(crate::Config::from("conf.toml")?.databases.sn_dev)
    }
}