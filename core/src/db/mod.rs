
pub mod schema;

pub mod config {

    fn config(server: String) -> Result<tiberius::Config, Box<dyn std::error::Error>> {
    
        let mut config = tiberius::Config::new();

        config.host(&server);
        config.authentication(tiberius::AuthMethod::Integrated);
        config.trust_cert();
    
        Ok(config)
    }

    pub fn eng() -> Result<tiberius::Config, Box<dyn std::error::Error>> {
        config(crate::config::config().database.engineering)
    }

    pub fn sn() -> Result<tiberius::Config, Box<dyn std::error::Error>> {
        config(crate::config::config().database.sigmanest)
    }
}

#[cfg(test)]
mod tests {
    use std::error::Error;
    use super::config;

    use tokio::net::TcpStream;
    use tokio_test::assert_ok;
    use tokio_util::compat::TokioAsyncWriteCompatExt;
    use tiberius::{Client, Config};

    async fn test_conn(config: Config) -> Result<(), Box<dyn Error>> {

        let tcp = TcpStream::connect(config.get_addr()).await?;
        tcp.set_nodelay(true)?;

        // Handling TLS, login and other details related to the SQL Server.
        let mut client = Client::connect(config, tcp.compat_write()).await?;
        let mut stream = client.query("SELECT @P1", &[&0i32]).await?;

        assert!(stream.next_resultset(), "no results returned");
        assert_eq!(Some(0i32), stream.into_row().await?.unwrap().get(0));

        Ok(())
    }

    #[tokio::test]
    async fn eng_db_connection() {
        assert_ok!( test_conn(config::eng().unwrap()).await );
    }

    #[tokio::test]
    async fn sn_db_connection() {
        assert_ok!( test_conn(config::sn().unwrap()).await );
    }
}
