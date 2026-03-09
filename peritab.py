from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalScroll, Grid, Vertical
from textual.widgets import (
    Button,
    Digits,
    Footer,
    Header,
    Static,
    MarkdownViewer,
    Input,
    Label,
)
from textual.css.scalar import Scalar
from textual.reactive import reactive
from textual_plotext import PlotextPlot
import numpy as np

import xraydb

xdb = xraydb.get_xraydb()


def xray_lines_to_markdown(lines_dict: dict) -> str:
    """Convert X-ray lines dictionary to markdown table format."""
    if not lines_dict:
        return "No X-ray lines data available"

    table = "# X ray lines\n\n"
    table += "| Line | Energy (keV) | Intensity | Initial Level | Final Level |\n"
    table += "|------|-------------|-----------|----------------|-------------|\n"

    for line_name, line_data in lines_dict.items():
        table += f"| {line_name} | {line_data.energy:.1f} | {line_data.intensity:.6g} | {line_data.initial_level} | {line_data.final_level} |\n"

    return table


# simple element widget
class Element(Button):
    def __init__(self, atomic_number: int, symbol: str, group: str):
        super().__init__(
            f"[dim]{atomic_number}[/dim]\n[bold]{symbol}[/bold]", id=symbol
        )
        try:
            self.add_class(group)
        except:
            self.add_class("ERROR")

    # def on_mount(self):
    #     self.styles.grid_rows = self.row
    #     self.styles.grid_columns = self.col


class NoElement(Static):
    def __init__(self, group: str):
        super().__init__(f"[dim][/dim]\n[bold][/bold]")
        self.add_class(group)


class PeriodicTable(App):

    CSS_PATH = "peritab.tcss"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit_app", "Quit App")]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "update-plot":
            self.update_plot_from_inputs()
        else:
            # Handle element clicks
            self._chosen_element = event.button.id
            symbol = self._chosen_element

            xray_lines = xdb.xray_lines(symbol)
            table = xray_lines_to_markdown(xray_lines)

            md_content = f"# {xraydb.atomic_name(symbol).title()}\n\n"
            md_content += f"#{table}"
            self.md.document.update(md_content)

    def update_plot_from_inputs(self) -> None:
        """Update the plot based on the energy range inputs."""
        try:
            min_energy = float(self.min_energy_input.value)
            max_energy = float(self.max_energy_input.value)

            # x_data = [min_energy, (min_energy + max_energy) / 2, max_energy]
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
                y_data = np.zeros_like(x_data)

            self.plotting_widget.plt.clf()
            self.plotting_widget.plt.plot(
                x_data / 1000, y_data, marker="braille", color="white"
            )
            self.plotting_widget.plt.xlabel("Energy (keV)")
            # self.plotting_widget.plt.ylabel(r"Attenuation length (cm)")
            # self.plotting_widget.plt.xscale("log")
            # self.plotting_widget.plt.xscale("log")
            self.plotting_widget.plt.title(
                f"Attenuation length for {self._chosen_element} [um]"
            )

            self.plotting_widget.plt.xlim(min_energy, max_energy)
            self.plotting_widget.refresh()

        except ValueError:
            self.plotting_widget.plt.clf()
            self.plotting_widget.plt.text("Invalid energy range")

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

                # plotting area with controls
                with Horizontal(classes="plot-area"):
                    # plotting widget on the left
                    self.plotting_widget = PlotextPlot(classes="plotting")
                    # Initialize with some basic data to avoid issues

                    self.plotting_widget.plt.xlabel("Energy (keV)")
                    # self.plotting_widget.plt.ylabel(r"Attenuation length (cm)")

                    yield self.plotting_widget

                    # input controls on the right
                    with Vertical(classes="plot-controls"):
                        yield Label("Energy Range (keV)", classes="control-label")

                        # Min energy input
                        yield Label("Min Energy:", classes="input-label")
                        self.min_energy_input = Input(
                            placeholder="0.0", value="0.0", classes="energy-input"
                        )
                        yield self.min_energy_input

                        # Max energy input
                        yield Label("Max Energy:", classes="input-label")
                        self.max_energy_input = Input(
                            placeholder="20.0", value="20.0", classes="energy-input"
                        )
                        yield self.max_energy_input

                        # Update plot button
                        self.update_plot_btn = Button(
                            "Update Plot", id="update-plot", classes="update-btn"
                        )
                        yield self.update_plot_btn

            # right-hand info panel (container for selected element details)
            # Using a scrollable container so we can add multiple widgets later
            from textual.containers import VerticalScroll

            self.info_panel = VerticalScroll(classes="info")
            # main markdown viewer inside the panel
            self.md = MarkdownViewer("`Click an element to update this panel.`")
            with self.info_panel:
                yield self.md
            yield self.info_panel

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""

        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit_app(self) -> None:
        self.exit()


if __name__ == "__main__":

    app = PeriodicTable()

    app.run()
