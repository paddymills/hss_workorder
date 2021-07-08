
#[derive(Debug, Default)]
pub struct TransAct {
    trans_type: String,
    district: i32,
    order_no: String,
    item_name: String,
    qty: i32,
    thickness: f32,
    due_date: String,
    dwg_number: String,
    priority: i32,
    remark: String,
    item_data1: String,
    item_data2: String,
}