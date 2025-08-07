import reflex as rx


def navbar():
    return rx.box(
        rx.flex(
            rx.image(src="/logo.png", width="48px", height="auto"),
            rx.badge(
                rx.icon(tag="banana", size=28),
                rx.heading("Save your ass - Selfhosted", size="6"),
                radius="large",
                align="center",
                #color_scheme="pink",
                variant="surface",
                padding="0.65rem",
            ),
            rx.spacer(),
            rx.hstack(
                rx.color_mode.button(),
                align="center",
                spacing="3",
            ),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            justify="center",
            width="100%",
        ),
        position="sticky",
        top="0",
        z_index="999",
        bg="var(--background)",
        backdrop_filter="blur(5px)",
        padding="0.5em 0 0 0",
    )
