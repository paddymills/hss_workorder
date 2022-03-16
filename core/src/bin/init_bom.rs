

use workorder_core::db::schema::{pull_bom, process_bom};

#[tokio::main]
async fn main() {
    let job = "1200055C";
    let ship = 3;

    let res = pull_bom(&job, ship).await.unwrap();
    process_bom(res).await.unwrap();
}
