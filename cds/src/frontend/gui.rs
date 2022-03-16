
#[allow(unused)]
use iced::{
    executor, Application, Clipboard, Command, Element,
    Align, Length,
    Column, Container, Row,
    button, Button, Text,
    pick_list, PickList,
};

use crate::frontend::style;

#[derive(Clone, Debug)]
pub enum Message {
    BtnPressed,
    SetJob(Job),
}

#[derive(Default, Debug, Clone, Copy, PartialEq, Eq)]
pub struct Job {
    job: u32,
    structure: char,
    shipments: [u32; 10]
}

impl std::fmt::Display for Job {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self.job {
            0 => write!(f, "Select Job"),
            _ => write!(f, "{}{}", self.job, self.structure)
        }
    }
}

#[derive(Default)]
pub struct CodeDeliverySystem {
    job: Option<Job>,
    shipment: u32,

    jobs: Vec<Job>,
    selected_job: Job,

    counter: i32,
    list: pick_list::State<Job>,
    btn: button::State,
}

impl CodeDeliverySystem {
    fn new() -> Self {
        Self {
            jobs: vec![
                Job { job: 1200055, structure: 'C', ..Default::default() },
                Job { job: 1180095, structure: 'A', ..Default::default() },
                Job { job: 1160105, structure: 'C', ..Default::default() },
            ],

            ..Default::default()
        }
    }
}

impl Application for CodeDeliverySystem {
    type Executor = executor::Default;
    type Message = Message;
    type Flags = ();

    fn new(_flags: ()) -> (CodeDeliverySystem, Command<Self::Message>) {
        (CodeDeliverySystem::new(), Command::none())
    }

    fn title(&self) -> String {
        let title = match &self.job {
            Some(job) => format!("{}-{}", job, self.shipment),
            None => String::from("[No Job]")
        };

        String::from(format!("Code Delivery System :: {}", title))
    }

    fn update(&mut self, message: Self::Message, _clipboard: &mut Clipboard) -> Command<Self::Message> {
        match message {
            Message::BtnPressed => self.counter += 1,
            Message::SetJob(job) => {
                self.job = Some(job);
                self.shipment = 3;
            }
        }

        Command::none()
    }

    fn view(&mut self) -> Element<Self::Message> {
        let content = match self.job {
            
            Some(_) => Column::new()
                .align_items(Align::Center)
                .spacing(10u16)
                .push(Text::new("Button count: "))
                .push(Text::new(self.counter.to_string()))
                .push(
                    Button::new(&mut self.btn, Text::new("go"))
                        .on_press(Message::BtnPressed)
                        .style(style::style::Button)
                ),
            None => Column::new()
                .align_items(Align::Center)
                .push(Text::new("Load job"))
                .push(
                    PickList::new(
                        &mut self.list,
                        &self.jobs,
                        Some(self.selected_job),
                        Message::SetJob
                    )
                ),
                // .push(
                //     Button::new(&mut self.btn, Text::new("load"))
                //         .on_press(Message::SetJob)
                //         .style(style::style::Button)
                // )
        };

        let frame = Container::new(content)
            .width(Length::Units(400))
            .height(Length::Units(400))
            .center_x()
            .center_y()
            .style(style::style::Container);

        Container::new(frame)
            .width(Length::Fill)
            .height(Length::Fill)
            .center_x()
            .center_y()
            .style(style::style::Container)
            .into()
    }
}
