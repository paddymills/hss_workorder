
use iced::{Application, Settings};

use cds::CodeDeliverySystem;

fn main() -> iced::Result {
    CodeDeliverySystem::run(Settings::default())
}
