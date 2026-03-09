from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalScroll, Grid
from textual.widgets import Button, Digits, Footer, Header, Static
from textual.css.scalar import Scalar
from textual.reactive import reactive


# simple element widget
class Element(Button):
    def __init__(self, atomic_number: int, symbol: str, group: str):
        super().__init__(f"[dim]{atomic_number}[/dim]\n[bold]{symbol}[/bold]")
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
            with HorizontalScroll(classes="grid-scroll"):
                grid = Grid(classes="periodic-grid")
                grid.styles.grid_size_columns = 18
                grid.styles.grid_size_rows = 10
                grid.styles.grid_gutter_horizontal = 0
                grid.styles.grid_gutter_vertical = 0
                grid.styles.grid_rows = tuple(Scalar.parse("1fr") for _ in range(10))

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

            # right-hand info panel (placeholder for selected element details)
            self.info = Static(
                "[b]Selected element info will appear here.[/b]\n\n"
                "(Click an element to update this panel.)",
                classes="info",
            )
            yield self.info

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
