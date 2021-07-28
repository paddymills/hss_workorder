
pub mod style {
    use iced::{
        button, Color, container
    };

    #[allow(unused)]
    pub enum BootstrapColors {
        Primary,
        Secondary,
        Success,
        Danger,
        Warning,
        Info,
        Light,
        Dark,
    }

    impl BootstrapColors {
        fn rgb(&self) -> Color {
            let rgb = |r, g, b| -> Color {
                Color::from_rgb(
                    r as f32 / 255.0,
                    g as f32 / 255.0,
                    b as f32 / 255.0,
                )
            };

            match self {
                BootstrapColors::Primary    => rgb(0x0D, 0x6E, 0xFD),
                BootstrapColors::Secondary  => rgb(0x6C, 0x75, 0x7D),
                BootstrapColors::Success    => rgb(0x19, 0x87, 0x54),
                BootstrapColors::Danger     => rgb(0xDC, 0x35, 0x45),
                BootstrapColors::Warning    => rgb(0xFF, 0xC1, 0x07),
                BootstrapColors::Info       => rgb(0x0D, 0xCA, 0xF0),
                BootstrapColors::Light      => rgb(0xF8, 0xF9, 0xFA),
                BootstrapColors::Dark       => rgb(0x21, 0x25, 0x29),
            }
        }
    }

    const HOVERED: Color = Color::from_rgb(
        0x3D as f32 / 255.0,
        0x8B as f32 / 255.0,
        0xFD as f32 / 255.0,
    );

    pub struct Container;

    impl container::StyleSheet for Container {
        fn style(&self) -> container::Style {
            container::Style {
                border_color: BootstrapColors::Dark.rgb().into(),
                border_radius: 5.0,
                border_width: 1.0,
                ..container::Style::default()
            }
        }
    }

    pub struct Button;

    impl button::StyleSheet for Button {
        fn active(&self) -> button::Style {
            button::Style {
                background: BootstrapColors::Primary.rgb().into(),
                border_radius: 3.0,
                text_color: Color::WHITE,
                ..button::Style::default()
            }
        }

        fn hovered(&self) -> button::Style {
            button::Style {
                background: HOVERED.into(),
                text_color: Color::WHITE,
                ..self.active()
            }
        }

        fn pressed(&self) -> button::Style {
            button::Style {
                border_width: 1.0,
                border_color: Color::WHITE,
                ..self.hovered()
            }
        }
    }
}