
use std::error::Error;

use tiberius::Client;
use tokio::net::TcpStream;
use tokio_util::compat::TokioAsyncWriteCompatExt;

use workorder::db::{self, queries, Part};

#[tokio::main]
async fn main() {
    pull_bom("1200055C", 3).await.unwrap();
}

async fn pull_bom(job: &str, ship: i32) -> Result<(), Box<dyn Error>> {
    let config = db::config::eng()?;

    let tcp = TcpStream::connect(config.get_addr()).await?;
    tcp.set_nodelay(true)?;

    // Handling TLS, login and other details related to the SQL Server.
    let mut client = Client::connect(config, tcp.compat_write()).await?;
    let stream = client.query(queries::GET_BOM, &[&job, &ship]).await?;

    let res = stream.into_first_result().await?;

    let mut rows = Vec::<Part>::new();
    for row in res {

        rows.push(Part::from_sql(&row));
    }

    let mut i = 0;
    for row in rows.iter().filter(|x| x.is_pl()) {
        println!("{:}", row);

        i += 1;
        if i > 5 {
            break;
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use std::error::Error;
    use workorder::db;

    use tokio_test::assert_ok;
    use tokio::net::TcpStream;
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
        assert_ok!( test_conn(db::config::eng().unwrap()).await );
    }

    #[tokio::test]
    async fn sn_db_connection() {
        assert_ok!( test_conn(db::config::sn().unwrap()).await );
    }

    #[tokio::test]
    async fn sn_db_dev_connection() {
        assert_ok!( test_conn(db::config::sndev().unwrap()).await );
    }
}
