import reflex as rx


class DS:
    PRIMARY = "blue-700"
    PRIMARY_HOVER = "blue-800"
    PRIMARY_LIGHT = "blue-50"
    SUCCESS = "emerald-600"
    SUCCESS_BG = "emerald-50"
    WARNING = "amber-600"
    WARNING_BG = "amber-50"
    ERROR = "red-600"
    ERROR_BG = "red-50"
    NEUTRAL = "slate-600"
    NEUTRAL_DARK = "slate-900"
    NEUTRAL_LIGHT = "slate-50"
    BORDER = "gray-200"
    H1 = "text-3xl font-extrabold tracking-tight"
    H2 = "text-2xl font-bold tracking-tight"
    H3 = "text-lg font-bold"
    BODY = "text-sm font-medium"
    LABEL = "text-[10px] font-bold uppercase tracking-widest text-slate-400"
    SHADOW = "shadow-sm"
    RADIUS = "rounded-2xl"
    SPACE = {"xs": "1", "sm": "2", "md": "4", "lg": "6", "xl": "8", "2xl": "12"}


@rx.memo
def ds_badge(label: str, variant: str = "neutral") -> rx.Component:
    colors = rx.match(
        variant,
        ("success", f"bg-{DS.SUCCESS_BG} text-{DS.SUCCESS}"),
        ("warning", f"bg-{DS.WARNING_BG} text-{DS.WARNING}"),
        ("error", f"bg-{DS.ERROR_BG} text-{DS.ERROR}"),
        ("primary", f"bg-{DS.PRIMARY_LIGHT} text-{DS.PRIMARY}"),
        f"bg-slate-100 text-slate-600",
    )
    return rx.el.span(
        label,
        class_name=f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold {colors} w-fit",
    )


@rx.memo
def ds_stat_card(
    title: str, value: rx.Var, icon: str, color_variant: str = "primary"
) -> rx.Component:
    variant_colors = rx.match(
        color_variant,
        ("primary", f"text-{DS.PRIMARY} bg-{DS.PRIMARY_LIGHT}"),
        ("success", f"text-{DS.SUCCESS} bg-{DS.SUCCESS_BG}"),
        ("warning", f"text-{DS.WARNING} bg-{DS.WARNING_BG}"),
        ("error", f"text-{DS.ERROR} bg-{DS.ERROR_BG}"),
        "text-slate-600 bg-slate-50",
    )
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(title, class_name=DS.LABEL),
                rx.el.h3(value, class_name=f"{DS.H2} text-slate-900 mt-1"),
            ),
            rx.el.div(
                rx.icon(icon, class_name="h-6 w-6"),
                class_name=f"p-3 {DS.RADIUS} {variant_colors}",
            ),
            class_name="flex justify-between items-start",
        ),
        class_name=f"bg-white p-6 {DS.RADIUS} border border-{DS.BORDER} {DS.SHADOW}",
    )


def ds_button(
    label: str | rx.Component,
    variant: str = "primary",
    size: str = "md",
    on_click: rx.event.EventType = rx.noop(),
    disabled: rx.Var[bool] = False,
    icon: str | None = None,
    loading: rx.Var[bool] = False,
    type: str = "button",
    class_name: str = "",
) -> rx.Component:
    variant_classes = rx.match(
        variant,
        (
            "primary",
            f"bg-{DS.PRIMARY} text-white hover:bg-{DS.PRIMARY_HOVER} shadow-sm",
        ),
        (
            "secondary",
            f"bg-white text-slate-700 border border-{DS.BORDER} hover:bg-slate-50",
        ),
        ("danger", f"bg-{DS.ERROR} text-white hover:bg-red-700"),
        ("ghost", "bg-transparent text-slate-600 hover:bg-slate-100"),
        f"bg-{DS.PRIMARY} text-white",
    )
    size_classes = rx.match(
        size,
        ("sm", "px-3 py-1.5 text-xs"),
        ("md", "px-4 py-2 text-sm"),
        ("lg", "px-6 py-3 text-base font-semibold"),
        "px-4 py-2 text-sm",
    )
    content = rx.cond(
        loading,
        rx.el.div(
            rx.el.div(
                class_name="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"
            ),
            "Processing...",
            class_name="flex items-center justify-center",
        ),
        rx.el.div(
            rx.cond(
                (icon != None) & (icon != ""),
                rx.icon(
                    tag=rx.cond(icon != None, icon, "").to(str),
                    class_name="h-4 w-4 mr-2",
                ),
                rx.fragment(),
            ),
            label,
            class_name="flex items-center justify-center",
        ),
    )
    return rx.el.button(
        content,
        on_click=on_click,
        disabled=disabled | loading,
        type=type,
        class_name=f"{variant_classes} {size_classes} rounded-xl transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed {class_name}",
    )


def ds_card(
    *children: rx.Component,
    padding: str = "p-6",
    shadow: str = "shadow-sm",
    class_name: str = "",
) -> rx.Component:
    return rx.el.div(
        *children,
        class_name=f"bg-white border border-{DS.BORDER} rounded-2xl {padding} {shadow} overflow-hidden {class_name}",
    )


def ds_pagination(
    current_page: rx.Var[int],
    total_pages: rx.Var[int],
    on_prev: rx.event.EventType,
    on_next: rx.event.EventType,
    on_page_change: rx.event.EventType,
    page_size: rx.Var[int],
    on_page_size_change: rx.event.EventType,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span("Show", class_name="text-xs font-bold text-slate-500 uppercase"),
            rx.el.div(
                rx.el.select(
                    rx.el.option("10", value="10"),
                    rx.el.option("25", value="25"),
                    rx.el.option("50", value="50"),
                    on_change=on_page_size_change,
                    value=str(page_size),
                    class_name="appearance-none bg-transparent pl-2 pr-8 py-1 text-sm font-bold text-slate-700 outline-none cursor-pointer",
                ),
                rx.icon(
                    "chevron-down",
                    class_name="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none",
                ),
                class_name="relative border border-slate-200 rounded-lg bg-slate-50",
            ),
            rx.el.span(
                "per page", class_name="text-xs font-bold text-slate-500 uppercase"
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("chevron-left", class_name="h-4 w-4"),
                on_click=on_prev,
                disabled=current_page <= 1,
                class_name="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors",
            ),
            rx.el.div(
                rx.el.span("Page ", class_name="text-slate-500"),
                rx.el.span(current_page, class_name="font-bold text-slate-900"),
                rx.el.span(" of ", class_name="text-slate-500"),
                rx.el.span(total_pages, class_name="font-bold text-slate-900"),
                class_name="text-sm font-medium px-4",
            ),
            rx.el.button(
                rx.icon("chevron-right", class_name="h-4 w-4"),
                on_click=on_next,
                disabled=current_page >= total_pages,
                class_name="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors",
            ),
            class_name="flex items-center",
        ),
        class_name="flex items-center justify-between py-4",
    )


def ds_input(
    label: str,
    placeholder: str = "",
    type: str = "text",
    value: rx.Var[str] = "",
    on_change: rx.event.EventType = rx.noop(),
    icon: str | None = None,
    error: rx.Var[str] = "",
    helper_text: str | None = None,
    name: str | None = None,
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5",
        ),
        rx.el.div(
            rx.cond(
                (icon != None) & (icon != ""),
                rx.icon(
                    tag=rx.cond(icon != None, icon, "help-circle").to(str),
                    class_name="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 h-5 w-5",
                ),
                None,
            ),
            rx.el.input(
                type=type,
                placeholder=placeholder,
                on_change=on_change,
                default_value=value,
                name=name,
                class_name=rx.cond(
                    error != "",
                    f"w-full {rx.cond(icon != None, 'pl-10', 'px-4')} pr-4 py-2.5 bg-{DS.ERROR_BG} border border-{DS.ERROR} rounded-xl focus:ring-4 focus:ring-red-100 outline-none transition-all text-sm",
                    f"w-full {rx.cond(icon != None, 'pl-10', 'px-4')} pr-4 py-2.5 bg-{DS.NEUTRAL_LIGHT} border border-{DS.BORDER} rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-{DS.PRIMARY} outline-none transition-all text-sm",
                ),
            ),
            class_name="relative",
        ),
        rx.cond(
            error != "",
            rx.el.p(
                error, class_name="text-[10px] font-bold text-red-500 mt-1 uppercase"
            ),
            None,
        ),
        rx.cond(
            (error == "") & (helper_text != None),
            rx.el.p(helper_text, class_name="text-[10px] text-slate-400 mt-1"),
            None,
        ),
        class_name="w-full",
    )