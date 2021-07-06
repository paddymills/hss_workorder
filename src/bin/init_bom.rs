 
use tiberius::{Client, Config, AuthMethod};
// use tiberius::ColumnType::{BigVarChar, Floatn, Intn};
use async_std::net::TcpStream;


use workorder::db::{queries, Part};

#[async_std::main]
async fn main() -> Result<(), tiberius::error::Error> {

    let mut config = Config::new();
    config.host("HSSSQLSERV");
    config.database("BOM");
    config.authentication(AuthMethod::Integrated);
    config.trust_cert();

    let tcp = TcpStream::connect(config.get_addr()).await?;
    tcp.set_nodelay(true)?;

    // Handling TLS, login and other details related to the SQL Server.
    let mut client = Client::connect(config, tcp).await?;
    
    let job = "1200055C";
    let ship: i32 = 3;
    let stream = client.query(queries::GET_BOM, &[&job, &ship]).await?;

    let res = stream.into_first_result().await?;

    let mut rows = Vec::<Part>::new();
    for row in res {

        // for i in 0..row.len() {
        //     let val = match row.columns()[i].column_type() {
        //         BigVarChar => String::from(row.get::<&str, usize>(i).unwrap()),
        //         Floatn => row.get::<f32, usize>(i).unwrap().to_string(),
        //         Intn => row.get::<i32, usize>(i).unwrap().to_string(),
        //         _ => unreachable!("some other type"),
        //     };

        //     println!( "\t{}: {}", row.columns()[i].name(), val );
        // }

        rows.push(Part::from_sql(&row));
    }

    for row in rows.iter().filter(|x| x.is_pl()) {
        println!("{:}", row);
    }

    Ok(())
}
