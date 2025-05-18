import reflex as rx


def footer():
    return rx.box(
        rx.image(src="/logo.png", width="18px", height="auto"),
        position="sticky",
        botton="0",
        # z_index="999",
        # bg="var(--background)",
        # backdrop_filter="blur(5px)",
        # padding="1em",
        # border_bottom="1px solid var(--gray-6)",
    id="final",
    )