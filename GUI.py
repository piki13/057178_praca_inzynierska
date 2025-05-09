import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
from classes.character import Character
from mcts_optimize_enemy_stats import mcts_optimize_enemy, test_battle
from modyfications_dict import input_stats_range
import threading


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        x = self.widget.winfo_rootx() - 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        if hasattr(self, "custom_offset"):
            x_offset, y_offset = self.custom_offset
            x = self.widget.winfo_rootx() + x_offset
            y = self.widget.winfo_rooty() + y_offset

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw, text=self.text, background="#ffffff", relief="solid",
            borderwidth=1, font=("TkDefaultFont", 9)
        )
        label.pack(ipadx=5, ipady=2)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class OptimizeEnemyGUI:
    instance = None

    def __init__(self, root):
        OptimizeEnemyGUI.instance = self
        self.root = root
        self.root.state('zoomed')
        self.root.title("MCTS Optimize Enemy")
        self.best_stats = None
        self.characters = []
        self.players = []
        self.max_players = 4
        self.default_font = ("TkDefaultFont", 10)
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20, padx=(10, 40), fill="x")
        self.frame.pack_propagate(False)
        self.delete_tooltips = []
        self.field_tooltips = {}
        self.testing = False
        self.create_labels()

        self.add_player_button = tk.Button(self.frame, text="Dodaj", command=self.add_player)
        self.add_player_button.grid(row=1000, column=0, columnspan=13, pady=(15, 5), padx=(30, 0))
        self.warn_tooltip = tk.Label(self.frame, text="", fg="#ff4f4f",
                                     font=("TkDefaultFont", 10))

        self.warn_tooltip.grid(row=1001, column=0, columnspan=13, rowspan=1, pady=(0, 10), padx=(30, 0))
        self.generate_button = tk.Button(self.frame, text="Generuj", command=self.generate_characters)
        self.generate_button.grid(row=1002, column=0, columnspan=13, rowspan=1, padx=(30, 0))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=100, variable=self.progress_var,
                                            maximum=100)
        self.progress_bar_visible = False

        self.enemy_frame = tk.Frame(self.root)
        self.enemy_frame.pack(pady=30, padx=(10, 60), fill="x")
        self.test_panel = tk.Frame(self.root)
        self.add_player()
        self.add_player()

    def validate_entry_on_focus_out(self, entry, stat_name):
        value = entry.get().strip()
        stat_range = input_stats_range[stat_name]
        tooltip_text = f"Zakres: {stat_range['min']}–{stat_range['max']}"
        if entry in self.field_tooltips:
            self.field_tooltips[entry].hide_tooltip()
            del self.field_tooltips[entry]

        try:
            val_int = int(value)
            if stat_range["min"] <= val_int <= stat_range["max"]:
                entry.config(bg="white")
            else:
                entry.config(bg="#ffe6e6")
                tip = Tooltip(entry, tooltip_text)
                self.field_tooltips[entry] = tip
        except ValueError:
            entry.config(bg="#ffe6e6")
            tip = Tooltip(entry, tooltip_text)
            self.field_tooltips[entry] = tip

    def create_labels(self):
        label_names = [
            ("WW", "weapon_skill", "Walka Wręcz"),
            ("US", "ballistic_skill", "Umiejętności Strzeleckie"),
            ("Zr", "agility", "Zręczność"),
            ("S", "strength", "Siła"),
            ("Żyw", "health", "Żywotność"),
            ("R", "movement", "Ruch"),
            ("Wt + P", "armor_and_toughness", "Wytrzymałość i pancerz"),
            ("Broń Wręcz", "melee_weapon_mod", "Modyfikator broni wręcz"),
            ("Broń Dystansowa", "ranged_weapon_mod", "Modyfikator broni dystansowej")
        ]

        labels = [("Gracze", "")]

        for short_name, key, full_name in label_names:
            r = input_stats_range[key]
            tooltip = f"{full_name} \nw zakresie {r['min']}–{r['max']}"
            labels.append((short_name, tooltip))

        for i in range(len(labels)):
            if i <= 11:
                self.frame.grid_columnconfigure(i, weight=1, uniform="equal")

        for col, (text, tooltip_text) in enumerate(labels):
            if text:
                label = tk.Label(self.frame, text=text, anchor="center", font=self.default_font)
                label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
                Tooltip(label, tooltip_text)

    def _run_test_battle(self, count):
        test_battle(self.characters, self.best_stats, graphic_mode=True, print_logs=False, num_simulations=count)

    def start_testing(self):
        self.testing = True
        self._animate_testing_dots(step=0)

    def _animate_testing_dots(self, step):
        if not self.testing:
            return

        dots = "." * (step % 4)
        self.test_status_label.config(text=f"Trwa testowanie{dots}")
        self.root.after(500, lambda: self._animate_testing_dots(step + 1))

    def stop_testing_animation(self):
        self.testing = False
        self.test_status_label.config(text="")

    def _on_optimization_finished(self):
        self.enable_generate_button()
        self.remove_progress_bar()
        self.display_enemy_stats()

    def _run_enemy_optimization(self):
        self.best_stats, best_avg_reward = mcts_optimize_enemy(self.characters, iterations=150,
                                                               simulations_per_node=100, graphic_mode=True, debug=False)

        self.root.after(0, self._on_optimization_finished)

    def add_player(self):

        if len(self.players) >= self.max_players:
            return

        player_id = len(self.players) + 1
        row = 1 + len(self.players)

        label = tk.Label(self.frame, text=f"Gracz {player_id}", font=self.default_font)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="ew")

        inputs = []
        input_order = list(input_stats_range.keys())
        for i in range(9):
            entry = tk.Entry(self.frame, width=6, justify="center", font=self.default_font)
            stat_name = input_order[i]

            entry.bind("<FocusOut>",
                       lambda e, ent=entry, stat_n=stat_name: self.validate_entry_on_focus_out(ent, stat_n))
            inputs.append(entry)

        for col in range(1, 10):
            inputs[col - 1].grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        delete_button = tk.Button(self.frame, text="X", command=lambda remove_p=player_id: self.remove_player(remove_p))
        delete_button.grid(row=row, column=10, padx=5, pady=5)

        self.players.append({
            'id': player_id,
            'label': label,
            'inputs': inputs,
            'button': delete_button
        })

        self.check_max_players()
        self.update_delete_buttons_state()

    def remove_player(self, player_id):
        if len(self.players) <= 2:
            return
        for index, player in enumerate(self.players):
            if player['id'] == player_id:
                player['label'].destroy()
                for entry in player['inputs']:
                    entry.destroy()
                player['button'].destroy()
                self.players.pop(index)
                break

        self.update_labels()
        self.update_delete_buttons_state()
        self.check_max_players()

    def update_delete_buttons_state(self):
        min_players = 2
        if hasattr(self, "delete_tooltips"):
            for tip in self.delete_tooltips:
                tip.hide_tooltip()

        for player in self.players:
            button = player['button']
            if len(self.players) <= min_players:
                button.config(state="disabled")
                tip = Tooltip(button, "Musi być przynajmniej 2 graczy")
                tip.custom_offset = (-140, 20)
                self.delete_tooltips.append(tip)
            else:
                button.config(state="normal")
                for tip in self.delete_tooltips:
                    tip.hide_tooltip()
                    tip.widget.unbind("<Enter>")
                    tip.widget.unbind("<Leave>")

                self.delete_tooltips.clear()

    def update_labels(self):
        for idx, player in enumerate(self.players):
            new_id = idx + 1
            row = 1 + idx
            player['id'] = new_id
            player['label'].config(text=f"Gracz {new_id}")
            player['label'].grid(row=row, column=0)

            for col in range(1, 10):
                player['inputs'][col - 1].grid(row=row, column=col)

            player['button'].config(command=lambda new=new_id: self.remove_player(new))
            player['button'].grid(row=row, column=10)
        self.update_delete_buttons_state()

    def check_max_players(self):
        if len(self.players) >= self.max_players:
            self.add_player_button.config(state="disabled")
            Tooltip(self.add_player_button, "Maksymalna liczba graczy to 4")
        else:
            self.add_player_button.config(state="normal")

    def display_enemy_stats(self):

        labels = [
            ("", ""),
            ("WW", "Walka Wręcz"),
            ("US", "Umiejętności Strzeleckie"),
            ("Zr", "Zręczność"),
            ("S", "Siła"),
            ("Żyw", "Żywotność"),
            ("R", "Ruch"),
            ("Wt + P", "Wytrzymałość i pancerz"),
            ("Broń Wręcz", "Modyfikator broni"),
            ("Broń Dystansowa", "Modyfikator broni")
        ]

        for i in range(10):
            self.enemy_frame.grid_columnconfigure(i, weight=1, uniform="grid")

        for col, (text, tooltip_text) in enumerate(labels):
            label = tk.Label(self.enemy_frame, text=text, anchor="center", font=self.default_font)
            label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            Tooltip(label, tooltip_text)

        spacer = tk.Label(self.enemy_frame, text="")
        spacer.grid(row=0, column=10)

        name_label = tk.Label(self.enemy_frame, text="Przeciwnik", font=self.default_font)
        name_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        values = list(self.best_stats.values())

        inputs = []

        for i in range(9):
            entry = tk.Entry(self.enemy_frame, width=6, justify="center", font=self.default_font)

            entry.insert(0, str(values[i]))
            entry.grid(row=1, column=i + 1, padx=5, pady=5, sticky="ew")
            inputs.append(entry)

        self.test_panel.pack(pady=(5, 10))

        tk.Label(self.test_panel, text="Ilość symulacji:", font=self.default_font).grid(row=0, column=0, padx=6, pady=2,
                                                                                        sticky="e")
        self.simulations_entry = tk.Entry(self.test_panel, width=8, font=self.default_font)
        self.simulations_entry.insert(0, "1000")
        self.simulations_entry.grid(row=0, column=1, padx=4, pady=2)

        test_button = tk.Button(self.test_panel, text="Testuj", command=self.run_simulation)
        test_button.grid(row=0, column=2, padx=10, pady=2)

        tk.Label(self.test_panel, text="Gracze wygrali:", font=self.default_font).grid(row=0, column=3, padx=6, pady=2,
                                                                                       sticky="e")
        self.result_entry = tk.Entry(self.test_panel, width=8, justify="center", state="readonly",
                                     font=self.default_font)
        self.result_entry.grid(row=0, column=4, padx=4, pady=2)
        self.test_status_label = tk.Label(self.test_panel, text="", font=("TkDefaultFont", 9, "italic"), width=22,
                                          anchor="w")
        self.test_status_label.grid(row=0, column=5, padx=(20, 0), sticky="w")

    def finish_simulation(self, result_percent):
        self.stop_testing_animation()
        result_percent = int(round(result_percent, 2) * 100)
        self.result_entry.config(state="normal")
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, f"{result_percent}%")
        self.result_entry.config(state="readonly")
        self.testing = False

    def run_simulation(self):
        try:
            count = int(self.simulations_entry.get())
            if count <= 0 or count > 10000:
                raise ValueError

            self.result_entry.config(state="normal")
            self.result_entry.delete(0, tk.END)
            self.result_entry.config(state="readonly")

            self.start_testing()
            threading.Thread(target=self._run_test_battle, args=(count,), daemon=True).start()

        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowa wartość w ilości symulacji.")

    def update_progress(self, value):
        value = max(0, min(100, value))
        self.progress_var.set(value)
        self.root.update_idletasks()

    def remove_progress_bar(self):
        """Usuń pasek postępu z GUI."""
        if self.progress_bar_visible:
            self.progress_bar.pack_forget()
            self.progress_bar_visible = False

    def enable_generate_button(self):
        self.generate_button.config(state="normal")

    def generate_characters(self):
        self.characters.clear()
        if self.enemy_frame.winfo_exists():
            self.enemy_frame.destroy()

        if self.test_panel.winfo_exists():
            self.test_panel.destroy()

        self.enemy_frame = tk.Frame(self.root)
        self.enemy_frame.pack(pady=30, padx=(10, 60), fill="x")

        self.test_panel = tk.Frame(self.root)

        any_invalid = False
        validated_inputs = []

        for index, player in enumerate(self.players):
            inputs_raw = player['inputs']
            inputs = [entry.get().strip() for entry in inputs_raw]
            player_valid = True

            for entry in inputs_raw:
                entry.config(bg="white")

            input_order = list(input_stats_range.keys())

            for i, value in enumerate(inputs):
                stat_name = input_order[i]
                stat_range = input_stats_range[stat_name]

                try:
                    val_int = int(value)
                    if not (stat_range["min"] <= val_int <= stat_range["max"]):
                        inputs_raw[i].config(bg="#ffe6e6")
                        self.validate_entry_on_focus_out(inputs_raw[i], stat_name)
                        player_valid = False
                except ValueError:
                    inputs_raw[i].config(bg="#ffe6e6")
                    self.validate_entry_on_focus_out(inputs_raw[i], stat_name)
                    player_valid = False

            if not player_valid:
                any_invalid = True
            else:
                validated_inputs.append((player['id'], inputs))

        if any_invalid:
            self.warn_tooltip.configure(text="Wprowadź poprawne dane graczy.")
            self.root.after(5000, lambda: self.warn_tooltip.configure(text=""))
            return

        for player_id, inputs in validated_inputs:
            char = Character(
                char_id=player_id,
                is_enemy=False,
                weapon_skill=int(inputs[0]),
                ballistic_skill=int(inputs[1]),
                agility=int(inputs[2]),
                strength=int(inputs[3]),
                health=int(inputs[4]),
                movement=int(inputs[5]),
                armor_and_toughness=int(inputs[6]),
                melee_weapon_mod=int(inputs[7]),
                ranged_weapon_mod=int(inputs[8])
            )
            self.characters.append(char)

        if len(self.characters) > 1:
            self.generate_button.config(state="disabled")
            self.update_progress(0)
            if not self.progress_bar_visible:
                self.progress_bar.pack(fill="x", padx=40, pady=(20, 10))
                self.progress_bar_visible = True
            threading.Thread(target=self._run_enemy_optimization, daemon=True).start()
