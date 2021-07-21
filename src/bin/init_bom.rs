
use std::error::Error;

use tiberius::{Client, Row};
use tokio::net::TcpStream;
use tokio_util::compat::TokioAsyncWriteCompatExt;

use workorder::db::{self, queries, Part};

#[tokio::main]
async fn main() {
    let job = "1200055C";
    let ship = 3;

    let res = pull_bom(&job, ship).await.unwrap();
    process_bom(res).await.unwrap();
}

async fn pull_bom(job: &str, ship: i32) -> Result<Vec<Row>, Box<dyn Error>> {
    let config = db::config::eng()?;

    let tcp = TcpStream::connect(config.get_addr()).await?;
    tcp.set_nodelay(true)?;

    // Handling TLS, login and other details related to the SQL Server.
    let mut client = Client::connect(config, tcp.compat_write()).await?;
    let stream = client.query(queries::GET_BOM, &[&job, &ship]).await?;

    let res = stream.into_first_result().await?;

    Ok(res)
}

async fn process_bom(rows: Vec<Row>) -> Result<(), Box<dyn Error>> {
    let mut parts = Vec::<Part>::new();
    for row in rows {

        parts.push(Part::from_sql(&row));
    }

    let mut i = 0;
    for row in parts.iter().filter(|x| x.is_pl()) {
        println!("{:}", row);

        i += 1;
        if i > 5 {
            break;
        }
    }

    if i == 0 {
        println!("No records found");
    }

    Ok(())
}