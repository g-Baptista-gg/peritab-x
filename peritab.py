from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll, Grid
from textual.widgets import Button, Digits, Footer, Header, Static
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


class PeriodicTable(App):

    CSS_PATH = "peritab.tcss"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit_app", "Quit App")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        self.grid = Grid()
        # yield self.grid

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
                [3, "Li", "alkali"],
                [4, "Be", "actinides"],
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
                [11, "Na", "alkali"],
                [12, "Mg", "actinides"],
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
                [19, "K", "alkali"],
                [20, "Ca", "actinides"],
                [21, "Sc", "transmetals"],
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
            ],
            [
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
            ],
            [
                "Cs",
                "Ba",
                ["", None],
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
            ],
            [
                "Fr",
                "Ra",
                ["", None],
                "Rf",
                "Db",
                "Sg",
                "Bh",
                "Hs",
                "Mt",
                "Ds",
                "Rg",
                "Cn",
                "Nh",
                "Fl",
                "Mc",
                "Lv",
                "Ts",
                "Og",
            ],
        ]

        for row in elements:
            for item in row:
                if not isinstance(item[0], int):
                    yield Static()
                else:
                    try:
                        at_no, symbol, group = item
                        yield Element(at_no, symbol, group)
                    except:
                        yield Element(0, symbol, "ERROR")

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
