from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Static,
    MarkdownViewer,
    Input,
    Label,
    TabbedContent,
    TabPane,
)
from textual_plotext import PlotextPlot
import numpy as np

import xraydb

# All elements with valid xraydb data (Z=1..92)
ALL_SYMBOLS = [
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
]

# Line families: label -> initial_level arg for xray_lines()
LINE_FAMILIES = {
    "K": "K",
    "L": "L",
    "M": "M",
}


def xray_lines_to_markdown(lines_dict: dict) -> str:
    """Convert X-ray lines dictionary to markdown table format."""
    if not lines_dict:
        return "No X-ray lines data available"

    table = "## X ray lines\n\n"
    table += "| Line | Energy (keV) | Intensity | Initial Level | Final Level |\n"
    table += "|------|-------------|-----------|----------------|-------------|\n"

    for line_name, line_data in lines_dict.items():
        table += f"| {line_name} | {line_data.energy / 1000:.3f} | {line_data.intensity:.6g} | {line_data.initial_level} | {line_data.final_level} |\n"

    return table


def xray_edges_to_markdown(edges_dict: dict) -> str:
    """Convert X-ray edges dictionary to markdown table format."""
    if not edges_dict:
        return "No X-ray edges data available"

    table = "## X ray edges\n\n"
    table += "| Edge | Energy (keV) | Fluorescence Yield | Jump Ratio |\n"
    table += "|------|-------------|-------------------|------------|\n"

    for edge_name, edge_data in edges_dict.items():
        table += (
            f"| {edge_name} "
            f"| {edge_data.energy / 1000:.3f} "
            f"| {edge_data.fyield:.6g} "
            f"| {edge_data.jump_ratio:.4g} |\n"
        )

    return table


class Element(Button):
    def __init__(self, atomic_number: int, symbol: str, group: str):
        super().__init__(
            f"[dim]{atomic_number}[/dim]\n[bold]{symbol}[/bold]", id=symbol
        )
        try:
            self.add_class(group)
        except Exception:
            self.add_class("ERROR")


class NoElement(Static):
    def __init__(self, group: str):
        super().__init__("")
        self.add_class(group)


class PeriodicTable(App):

    CSS_PATH = "peritab.tcss"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit_app", "Quit App")]

    _chosen_element: str = "Fe"

    # ------------------------------------------------------------------ #
    #  Element click / info panel                                          #
    # ------------------------------------------------------------------ #

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle element button clicks — update info panel and plot."""
        self._chosen_element = event.button.id
        symbol = self._chosen_element

        lines_md = xray_lines_to_markdown(xraydb.xray_lines(symbol))
        edges_md = xray_edges_to_markdown(xraydb.xray_edges(symbol))

        md_content = f"# {xraydb.atomic_name(symbol).title()}\n\n"
        md_content += lines_md + "\n\n" + edges_md
        self.md.document.update(md_content)
        self.update_plot_from_inputs()

    # ------------------------------------------------------------------ #
    #  Attenuation plot                                                    #
    # ------------------------------------------------------------------ #

    @on(Input.Changed, ".energy-input")
    def on_energy_changed(self) -> None:
        """Auto-update the plot whenever either energy input changes."""
        self.update_plot_from_inputs()

    def update_plot_from_inputs(self) -> None:
        """Recompute and redraw the attenuation length plot."""
        try:
            min_energy = float(self.min_energy_input.value)
            max_energy = float(self.max_energy_input.value)

            if min_energy >= max_energy:
                self.notify(
                    "Min energy must be less than max energy.", severity="warning"
                )
                return

            x_data = np.linspace(min_energy, max_energy, 100) * 1000
            try:
                y_data = (
                    1
                    / (
                        xraydb.mu_elam(self._chosen_element, x_data, kind="total")
                        * xraydb.atomic_density(self._chosen_element)
                    )
                    * 10000
                )
            except Exception as e:
                self.notify(f"Could not compute attenuation: {e}", severity="error")
                y_data = np.zeros_like(x_data)

            self.plotting_widget.plt.clf()
            self.plotting_widget.plt.plot(
                x_data / 1000, y_data, marker="braille", color="white"
            )
            self.plotting_widget.plt.xlabel("Energy (keV)")
            self.plotting_widget.plt.title(
                f"Attenuation length for {self._chosen_element} [um]"
            )
            self.plotting_widget.plt.xlim(min_energy, max_energy)
            self.plotting_widget.refresh()

        except ValueError:
            pass

    # ------------------------------------------------------------------ #
    #  Line search tool                                                    #
    # ------------------------------------------------------------------ #

    @on(Input.Changed, ".search-energy-input")
    def on_search_input_changed(self) -> None:
        """Rerun the line search when energy range inputs change."""
        self.update_line_search()

    @on(Checkbox.Changed)
    def on_search_checkbox_changed(self) -> None:
        """Rerun the line search when a family checkbox is toggled."""
        self.update_line_search()

    def update_line_search(self) -> None:
        """Search all elements for lines within the energy range and families."""
        try:
            min_ev = float(self.search_min_input.value) * 1000
            max_ev = float(self.search_max_input.value) * 1000
        except ValueError:
            return

        if min_ev >= max_ev:
            return

        # Which families are toggled on?
        active_families = [
            fam for fam, cb in self._family_checkboxes.items() if cb.value
        ]
        if not active_families:
            self.line_table.clear()
            return

        results = []
        for symbol in ALL_SYMBOLS:
            try:
                lines = xraydb.xray_lines(symbol)
            except Exception:
                continue
            for line_name, line_data in lines.items():
                if (
                    min_ev <= line_data.energy <= max_ev
                    and line_name[0] in active_families
                ):
                    results.append(
                        (
                            symbol,
                            line_name,
                            line_data.energy / 1000,
                            line_data.intensity,
                            line_data.initial_level,
                            line_data.final_level,
                        )
                    )

        # Sort by energy
        results.sort(key=lambda r: r[2])

        self.line_table.clear()
        for symbol, line_name, energy_kev, intensity, initial, final in results:
            self.line_table.add_row(
                symbol,
                line_name,
                f"{energy_kev:.3f}",
                f"{intensity:.4g}",
                initial,
                final,
            )

    # ------------------------------------------------------------------ #
    #  Layout                                                              #
    # ------------------------------------------------------------------ #

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        elements = [
            [
                [1, "H", "nonmetals"],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                [2, "He", "nobles"],
            ],
            [
                [3, "Li", "alkalimetals"],
                [4, "Be", "alkaliearthmetals"],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                [5, "B", "metalloids"],
                [6, "C", "nonmetals"],
                [7, "N", "nonmetals"],
                [8, "O", "nonmetals"],
                [9, "F", "nonmetals"],
                [10, "Ne", "nobles"],
            ],
            [
                [11, "Na", "alkalimetals"],
                [12, "Mg", "alkaliearthmetals"],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                ["", None],
                [13, "Al", "posttransmetals"],
                [14, "Si", "metalloids"],
                [15, "P", "nonmetals"],
                [16, "S", "nonmetals"],
                [17, "Cl", "nonmetals"],
                [18, "Ar", "nobles"],
            ],
            [
                [19, "K", "alkalimetals"],
                [20, "Ca", "alkaliearthmetals"],
                [21, "Sc", "transmetals"],
                [22, "Ti", "transmetals"],
                [23, "V", "transmetals"],
                [24, "Cr", "transmetals"],
                [25, "Mn", "transmetals"],
                [26, "Fe", "transmetals"],
                [27, "Co", "transmetals"],
                [28, "Ni", "transmetals"],
                [29, "Cu", "transmetals"],
                [30, "Zn", "transmetals"],
                [31, "Ga", "posttransmetals"],
                [32, "Ge", "metalloids"],
                [33, "As", "metalloids"],
                [34, "Se", "nonmetals"],
                [35, "Br", "nonmetals"],
                [36, "Kr", "nobles"],
            ],
            [
                [37, "Rb", "alkalimetals"],
                [38, "Sr", "alkaliearthmetals"],
                [39, "Y", "transmetals"],
                [40, "Zr", "transmetals"],
                [41, "Nb", "transmetals"],
                [42, "Mo", "transmetals"],
                [43, "Tc", "transmetals"],
                [44, "Ru", "transmetals"],
                [45, "Rh", "transmetals"],
                [46, "Pd", "transmetals"],
                [47, "Ag", "transmetals"],
                [48, "Cd", "transmetals"],
                [49, "In", "posttransmetals"],
                [50, "Sn", "posttransmetals"],
                [51, "Sb", "metalloids"],
                [52, "Te", "metalloids"],
                [53, "I", "nonmetals"],
                [54, "Xe", "nobles"],
            ],
            [
                [55, "Cs", "alkalimetals"],
                [56, "Ba", "alkaliearthmetals"],
                [-1, "", "group_lanthanoids"],
                [72, "Hf", "transmetals"],
                [73, "Ta", "transmetals"],
                [74, "W", "transmetals"],
                [75, "Re", "transmetals"],
                [76, "Os", "transmetals"],
                [77, "Ir", "transmetals"],
                [78, "Pt", "transmetals"],
                [79, "Au", "transmetals"],
                [80, "Hg", "transmetals"],
                [81, "Tl", "posttransmetals"],
                [82, "Pb", "posttransmetals"],
                [83, "Bi", "posttransmetals"],
                [84, "Po", "posttransmetals"],
                [85, "At", "metalloids"],
                [86, "Rn", "nobles"],
            ],
            [
                [87, "Fr", "alkalimetals"],
                [88, "Ra", "alkaliearthmetals"],
                [-1, "", "group_actinoids"],
                [104, "Rf", "transmetals"],
                [105, "Db", "transmetals"],
                [106, "Sg", "transmetals"],
                [107, "Bh", "transmetals"],
                [108, "Hs", "transmetals"],
                [109, "Mt", "unknown"],
                [110, "Ds", "unknown"],
                [111, "Rg", "unknown"],
                [112, "Cn", "unknown"],
                [113, "Nh", "unknown"],
                [114, "Fl", "unknown"],
                [115, "Mc", "unknown"],
                [116, "Lv", "unknown"],
                [117, "Ts", "unknown"],
                [118, "Og", "unknown"],
            ],
        ]

        with Horizontal(classes="main"):
            with Vertical(classes="table-section"):
                from textual.containers import Grid

                grid: Grid = Grid(classes="periodic-grid")

                with grid:
                    for row in elements:
                        for item in row:
                            if not isinstance(item[0], int):
                                yield NoElement("empty")
                            else:
                                at_no, symbol, group = item
                                if at_no == -1:
                                    yield NoElement(group)
                                else:
                                    yield Element(at_no, symbol, group)

                with Horizontal(classes="plot-area"):
                    self.plotting_widget = PlotextPlot(classes="plotting")
                    self.plotting_widget.plt.xlabel("Energy (keV)")
                    yield self.plotting_widget

                    with Vertical(classes="plot-controls"):
                        yield Label("En. range", classes="control-label")
                        yield Label("Min:", classes="input-label")
                        self.min_energy_input = Input(
                            value="0.0", placeholder="0.0", classes="energy-input"
                        )
                        yield self.min_energy_input
                        yield Label("Max:", classes="input-label")
                        self.max_energy_input = Input(
                            value="20.0", placeholder="0.0", classes="energy-input"
                        )
                        yield self.max_energy_input

            # Right panel: tabbed between element info and line search
            with TabbedContent(classes="info"):
                with TabPane("Element", id="tab-element"):
                    self.info_panel = VerticalScroll()
                    self.md = MarkdownViewer("`Click an element to update this panel.`")
                    with self.info_panel:
                        yield self.md
                    yield self.info_panel

                with TabPane("Line Search", id="tab-search"):
                    yield Label("Min (keV):", classes="search-label")
                    self.search_min_input = Input(
                        placeholder="0.0", value="0.0", classes="search-energy-input"
                    )
                    yield self.search_min_input
                    yield Label("Max (keV):", classes="search-label")
                    self.search_max_input = Input(
                        placeholder="20.0", value="20.0", classes="search-energy-input"
                    )
                    yield self.search_max_input
                    yield Label("Families:", classes="search-label")
                    self._family_checkboxes: dict[str, Checkbox] = {}
                    for fam in LINE_FAMILIES:
                        cb = Checkbox(fam, value=True, classes="family-cb")
                        self._family_checkboxes[fam] = cb
                        yield cb
                    self.line_table = DataTable(classes="line-search-table")
                    self.line_table.add_columns(
                        "Element",
                        "Line",
                        "Energy (keV)",
                        "Intensity",
                        "Initial",
                        "Final",
                    )
                    yield self.line_table

    def on_mount(self) -> None:
        """Populate the line search table with default range on startup."""
        self.update_line_search()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit_app(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = PeriodicTable()
    app.run()
