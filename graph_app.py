#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import os
import sys
import platform
import math


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Algorithms Visualizer")
        self.root.geometry("1200x800")

        self.nodes = []
        self.edges = []
        self.node_radius = 25
        self.selected_node = None
        self.start_node = None
        self.end_node = None
        self.mode = "add_node"
        self.highlighted_path = []
        self.highlighted_edges = []
        self.highlight_color = "#00AA00"
        self.cpp_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "graph_algorithms.cpp"
        )
        exe_name = (
            "graph_algorithms.exe"
            if platform.system() == "Windows"
            else "graph_algorithms"
        )
        self.exe_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), exe_name
        )

        self.animation_path = []
        self.animation_edges = []
        self.animation_step = 0
        self.animation_playing = False
        self.animation_speed = 500  # milliseconds
        self.animation_job = None
        self.animation_mode = "path"
        self.animation_title = ""
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.zoom_level = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.is_panning = False

        self.setup_ui()
        self.compile_cpp()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(main_frame, padding="10", width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        mode_frame = ttk.LabelFrame(left_panel, text="Edit Mode", padding="5")
        mode_frame.pack(fill=tk.X, pady=5)
        self.mode_var = tk.StringVar(value="add_node")
        modes = [
            ("Add Node", "add_node"),
            ("Add Edge", "add_edge"),
            ("Set Start", "select_start"),
            ("Set End", "select_end"),
        ]
        for text, value in modes:
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,
                value=value,
                command=self.change_mode,
            ).pack(anchor=tk.W)

        algo_frame = ttk.LabelFrame(left_panel, text="Algorithms", padding="5")
        algo_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            algo_frame, text="Dijkstra Shortest Path", command=self.find_shortest_path
        ).pack(fill=tk.X, pady=2)
        ttk.Separator(algo_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Button(
            algo_frame, text="Minimum Spanning Tree", command=self.find_mst
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            algo_frame, text="Maximum Spanning Tree", command=self.find_max_st
        ).pack(fill=tk.X, pady=2)

        ttk.Separator(algo_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Button(
            algo_frame, text="Chinese Postman", command=self.chinese_postman
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            algo_frame, text="Traveling Salesman", command=self.traveling_salesman
        ).pack(fill=tk.X, pady=2)

        action_frame = ttk.LabelFrame(left_panel, text="Actions", padding="5")
        action_frame.pack(fill=tk.X, pady=10)

        ttk.Button(action_frame, text="Load Example", command=self.load_example).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(action_frame, text="Clear Graph", command=self.clear_graph).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(
            action_frame, text="Clear Highlights", command=self.clear_highlights
        ).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Reset View", command=self.reset_view).pack(
            fill=tk.X, pady=2
        )

        info_frame = ttk.LabelFrame(left_panel, text="Graph Info", padding="5")
        info_frame.pack(fill=tk.X, pady=10)

        self.nodes_var = tk.StringVar(value="Nodes: 0")
        self.edges_var = tk.StringVar(value="Edges: 0")
        self.start_var = tk.StringVar(value="Start: None")
        self.end_var = tk.StringVar(value="End: None")

        ttk.Label(info_frame, textvariable=self.nodes_var).pack(anchor=tk.W)
        ttk.Label(info_frame, textvariable=self.edges_var).pack(anchor=tk.W)
        ttk.Label(info_frame, textvariable=self.start_var).pack(anchor=tk.W)
        ttk.Label(info_frame, textvariable=self.end_var).pack(anchor=tk.W)

        self.status_var = tk.StringVar(value="Click to add nodes")
        ttk.Label(
            left_panel, textvariable=self.status_var, foreground="blue", wraplength=230
        ).pack(pady=5)

        right_panel = ttk.Frame(main_frame, padding="10", width=200)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        legend_frame = ttk.LabelFrame(right_panel, text="Legend", padding="5")
        legend_frame.pack(fill=tk.X, pady=5)

        legends = [
            ("🟢", "Start Node"),
            ("🔴", "End Node"),
            ("🟠", "Path/Result"),
            ("🔵", "Regular Node"),
            ("🔶", "Current (Anim)"),
            ("❤️", "Current Edge"),
        ]
        for symbol, text in legends:
            ttk.Label(legend_frame, text=f"{symbol} {text}").pack(anchor=tk.W)

        hint_frame = ttk.LabelFrame(right_panel, text="Controls", padding="5")
        hint_frame.pack(fill=tk.X, pady=10)
        ttk.Label(hint_frame, text="Left Click: Action", font=("Arial", 9)).pack(
            anchor=tk.W
        )
        ttk.Label(hint_frame, text="Right Click: Delete", font=("Arial", 9)).pack(
            anchor=tk.W
        )
        ttk.Label(hint_frame, text="Middle Drag: Pan", font=("Arial", 9)).pack(
            anchor=tk.W
        )
        ttk.Label(hint_frame, text="Scroll: Zoom", font=("Arial", 9)).pack(anchor=tk.W)
        zoom_frame = ttk.LabelFrame(right_panel, text="View", padding="5")
        zoom_frame.pack(fill=tk.X, pady=10)
        self.zoom_var = tk.StringVar(value="Zoom: 100%")
        ttk.Label(zoom_frame, textvariable=self.zoom_var).pack(anchor=tk.W)
        result_frame = ttk.LabelFrame(right_panel, text="Result", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        result_scroll = ttk.Scrollbar(result_frame)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text = tk.Text(
            result_frame,
            height=12,
            width=22,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#FFFDE7",
            yscrollcommand=result_scroll.set,
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        result_scroll.config(command=self.result_text.yview)
        center_panel = ttk.Frame(main_frame)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)
        self.canvas = tk.Canvas(
            center_panel,
            bg="white",
            highlightthickness=2,
            highlightbackground="#cccccc",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.animation_frame = ttk.Frame(center_panel)
        anim_container = ttk.Frame(self.animation_frame)
        anim_container.pack(expand=True)
        info_row = ttk.Frame(anim_container)
        info_row.pack(pady=2)
        self.step_var = tk.StringVar(value="Step: 0 / 0")
        ttk.Label(
            info_row, textvariable=self.step_var, font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=10)
        self.edge_info_var = tk.StringVar(value="")
        ttk.Label(
            info_row,
            textvariable=self.edge_info_var,
            font=("Consolas", 11, "bold"),
            foreground="#AA00AA",
        ).pack(side=tk.LEFT, padx=10)

        btn_frame = ttk.Frame(anim_container)
        btn_frame.pack(pady=5)
        self.prev_btn = ttk.Button(
            btn_frame, text="⏮ Prev", width=10, command=self.animation_prev
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        self.play_btn = ttk.Button(
            btn_frame, text="▶ Play", width=10, command=self.animation_toggle_play
        )
        self.play_btn.pack(side=tk.LEFT, padx=5)
        self.next_btn = ttk.Button(
            btn_frame, text="Next ⏭", width=10, command=self.animation_next
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="⏹ Stop", width=10, command=self.stop_animation
        ).pack(side=tk.LEFT, padx=5)
        speed_frame = ttk.Frame(anim_container)
        speed_frame.pack(pady=2)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=500)
        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=100,
            to=2000,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self.update_speed,
            length=200,
        )
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        self.speed_label = ttk.Label(speed_frame, text="500ms")
        self.speed_label.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_move)
        self.canvas.bind("<ButtonRelease-2>", self.on_pan_end)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)

    def change_mode(self):
        self.mode = self.mode_var.get()
        self.selected_node = None
        messages = {
            "add_node": "Click to add a node",
            "add_edge": "Click first node, then second to add edge",
            "select_start": "Click a node to set as START",
            "select_end": "Click a node to set as END",
        }
        self.status_var.set(messages.get(self.mode, ""))
        self.redraw()

    def on_pan_start(self, event):
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.canvas.config(cursor="fleur")

    def on_pan_move(self, event):
        if self.is_panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.canvas_offset_x += dx
            self.canvas_offset_y += dy
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.redraw()

    def on_pan_end(self, event):
        self.is_panning = False
        self.canvas.config(cursor="")

    def on_zoom(self, event):
        mouse_x = event.x
        mouse_y = event.y

        if event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
            scale_factor = 1.1
        elif event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
            scale_factor = 0.9
        else:
            return

        new_zoom = self.zoom_level * scale_factor
        if new_zoom < 0.2 or new_zoom > 5.0:
            return

        self.canvas_offset_x = mouse_x - (mouse_x - self.canvas_offset_x) * scale_factor
        self.canvas_offset_y = mouse_y - (mouse_y - self.canvas_offset_y) * scale_factor

        self.zoom_level = new_zoom
        self.zoom_var.set(f"Zoom: {int(self.zoom_level * 100)}%")
        self.redraw()

    def reset_view(self):
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.zoom_level = 1.0
        self.zoom_var.set("Zoom: 100%")
        self.redraw()

    def screen_to_world(self, sx, sy):
        wx = (sx - self.canvas_offset_x) / self.zoom_level
        wy = (sy - self.canvas_offset_y) / self.zoom_level
        return wx, wy

    def world_to_screen(self, wx, wy):
        sx = wx * self.zoom_level + self.canvas_offset_x
        sy = wy * self.zoom_level + self.canvas_offset_y
        return sx, sy

    def compile_cpp(self):
        if not os.path.exists(self.cpp_path):
            messagebox.showwarning("Warning", "graph_algorithms.cpp not found!\nAlgorithms will not work.")
            return False

        if os.path.exists(self.exe_path):
            if os.path.getmtime(self.exe_path) > os.path.getmtime(self.cpp_path):
                return True

        try:
            result = subprocess.run(
                ["g++", "-O3", "-std=c++17", "-o", self.exe_path, self.cpp_path],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                messagebox.showerror("Compilation Error", result.stderr)
                return False
            return True
        except FileNotFoundError:
            messagebox.showwarning(
                "Warning"
                "Compiler Not Found",
                "g++ compiler not found!\n\n"
                "To use graph algorithms, please install a C++ compiler:\n"
                "• Install MinGW-w64 or MSYS2\n"
                "• Or install Visual Studio Build Tools\n\n"
                "The app will still run, but algorithms won't work\n"
                "until you compile graph_algorithms.cpp manually.\n"
                "This is only a warning you can ignore it."
            )
            return False

    def get_node_at(self, x, y):
        wx, wy = self.screen_to_world(x, y)
        for i, (nx, ny) in enumerate(self.nodes):
            if math.sqrt((wx - nx) ** 2 + (wy - ny) ** 2) <= self.node_radius:
                return i
        return None

    def on_left_click(self, event):
        x, y = event.x, event.y
        wx, wy = self.screen_to_world(x, y)
        clicked = self.get_node_at(x, y)

        if self.mode == "add_node":
            if clicked is None:
                self.nodes.append((wx, wy))
                if len(self.nodes) == 1:
                    self.start_node = 0
                if len(self.nodes) == 2:
                    self.end_node = 1
                self.clear_highlights()
                self.redraw()

        elif self.mode == "add_edge":
            if clicked is not None:
                if self.selected_node is None:
                    self.selected_node = clicked
                    self.status_var.set(f"Node {clicked} selected. Click another node.")
                else:
                    if self.selected_node != clicked:
                        exists = any(
                            (e[0] == self.selected_node and e[1] == clicked)
                            or (e[0] == clicked and e[1] == self.selected_node)
                            for e in self.edges
                        )
                        if not exists:
                            x1, y1 = self.nodes[self.selected_node]
                            x2, y2 = self.nodes[clicked]
                            weight = max(
                                1, int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / 10)
                            )

                            custom = simpledialog.askinteger(
                                "Edge Weight",
                                f"Weight for edge {self.selected_node} → {clicked}:",
                                initialvalue=weight,
                                minvalue=1,
                                maxvalue=999,
                            )
                            if custom:
                                self.edges.append((self.selected_node, clicked, custom))
                                self.clear_highlights()

                    self.selected_node = None
                    self.status_var.set("Click first node, then second to add edge")
                self.redraw()

        elif self.mode == "select_start":
            if clicked is not None:
                self.start_node = clicked
                self.clear_highlights()
                self.redraw()

        elif self.mode == "select_end":
            if clicked is not None:
                self.end_node = clicked
                self.clear_highlights()
                self.redraw()

        self.update_info()

    def on_right_click(self, event):
        clicked = self.get_node_at(event.x, event.y)
        if clicked is not None:
            self.edges = [e for e in self.edges if e[0] != clicked and e[1] != clicked]
            self.edges = [
                (
                    e[0] - (1 if e[0] > clicked else 0),
                    e[1] - (1 if e[1] > clicked else 0),
                    e[2],
                )
                for e in self.edges
            ]
            self.nodes.pop(clicked)

            if self.start_node == clicked:
                self.start_node = 0 if self.nodes else None
            elif self.start_node and self.start_node > clicked:
                self.start_node -= 1

            if self.end_node == clicked:
                self.end_node = len(self.nodes) - 1 if self.nodes else None
            elif self.end_node and self.end_node > clicked:
                self.end_node -= 1

            self.clear_highlights()
            self.redraw()
            self.update_info()

    def update_info(self):
        self.nodes_var.set(f"Nodes: {len(self.nodes)}")
        self.edges_var.set(f"Edges: {len(self.edges)}")
        self.start_var.set(
            f"Start: {self.start_node if self.start_node is not None else 'None'}"
        )
        self.end_var.set(
            f"End: {self.end_node if self.end_node is not None else 'None'}"
        )

    def clear_highlights(self):
        self.highlighted_path = []
        self.highlighted_edges = []
        self.result_text.delete(1.0, tk.END)

    def redraw(self):
        self.canvas.delete("all")

        current_anim_edge = None
        if (
            self.animation_mode == "path"
            and self.animation_path
            and self.animation_step > 0
        ):
            current_anim_edge = (
                self.animation_path[self.animation_step - 1],
                self.animation_path[self.animation_step],
            )
        elif (
            self.animation_mode == "edges"
            and self.animation_edges
            and self.animation_step > 0
        ):
            current_anim_edge = self.animation_edges[self.animation_step - 1]

        scaled_radius = self.node_radius * self.zoom_level
        font_size = max(8, int(12 * self.zoom_level))
        weight_font_size = max(7, int(9 * self.zoom_level))

        for e in self.edges:
            n1, n2, weight = e
            wx1, wy1 = self.nodes[n1]
            wx2, wy2 = self.nodes[n2]

            x1, y1 = self.world_to_screen(wx1, wy1)
            x2, y2 = self.world_to_screen(wx2, wy2)

            in_highlight = (n1, n2) in self.highlighted_edges or (
                n2,
                n1,
            ) in self.highlighted_edges

            in_path = False
            if self.animation_mode == "path" and len(self.highlighted_path) > 1:
                for i in range(len(self.highlighted_path) - 1):
                    if (
                        self.highlighted_path[i] == n1
                        and self.highlighted_path[i + 1] == n2
                    ) or (
                        self.highlighted_path[i] == n2
                        and self.highlighted_path[i + 1] == n1
                    ):
                        in_path = True
                        break

            is_current_edge = False
            if current_anim_edge:
                if (n1 == current_anim_edge[0] and n2 == current_anim_edge[1]) or (
                    n1 == current_anim_edge[1] and n2 == current_anim_edge[0]
                ):
                    is_current_edge = True

            if is_current_edge:
                color = "#FF0000"
                width = max(3, int(6 * self.zoom_level))
            elif in_highlight or in_path:
                color = self.highlight_color
                width = max(2, int(4 * self.zoom_level))
            else:
                color = "#888888"
                width = max(1, int(2 * self.zoom_level))

            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            oval_size = max(8, 12 * self.zoom_level)
            self.canvas.create_oval(
                mx - oval_size,
                my - oval_size * 0.8,
                mx + oval_size,
                my + oval_size * 0.8,
                fill="white",
                outline=color,
            )
            self.canvas.create_text(
                mx,
                my,
                text=str(weight),
                font=("Arial", weight_font_size, "bold"),
                fill=color,
            )

        for i, (wx, wy) in enumerate(self.nodes):
            x, y = self.world_to_screen(wx, wy)

            is_current_node = False
            if self.animation_mode == "path" and self.animation_path and len(self.highlighted_path) > 0:
                is_current_node = i == self.highlighted_path[-1]
            elif self.animation_mode == "edges" and self.animation_edges and self.animation_step > 0:
                current_edge = self.animation_edges[self.animation_step - 1]
                is_current_node = i == current_edge[0] or i == current_edge[1]

            if is_current_node and (self.animation_path or self.animation_edges):
                color, outline = "#FF5500", "#CC3300"
            elif i == self.start_node:
                color, outline = "#00CC00", "#008800"
            elif i == self.end_node:
                color, outline = "#CC0000", "#880000"
            elif i in self.highlighted_path:
                color, outline = "#FFAA00", "#CC8800"
            elif i == self.selected_node:
                color, outline = "#00AAFF", "#0088CC"
            else:
                color, outline = "#4488FF", "#2266CC"

            r = scaled_radius
            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=color,
                outline=outline,
                width=max(2, int(3 * self.zoom_level)),
            )
            self.canvas.create_text(
                x, y, text=str(i), font=("Arial", font_size, "bold"), fill="white"
            )

    def run_algorithm(self, mode, extra_input=""):
        if not os.path.exists(self.exe_path):
            if not self.compile_cpp():
                return None

        n, m = len(self.nodes), len(self.edges)
        input_data = f"{mode}\n{n} {m}\n"
        for e in self.edges:
            input_data += f"{e[0]} {e[1]} {e[2]}\n"
        input_data += extra_input

        try:
            result = subprocess.run(
                [self.exe_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

    def find_shortest_path(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Warning", "Add at least 2 nodes!")
            return
        if self.start_node is None or self.end_node is None:
            messagebox.showwarning("Warning", "Set start and end nodes!")
            return

        self.cancel_animation()
        self.highlight_color = "#00AA00"
        output = self.run_algorithm("dijkstra", f"{self.start_node} {self.end_node}\n")
        self.highlighted_path = []
        self.highlighted_edges = []

        if output == "NO_PATH":
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No path found!")
            self.redraw()
        else:
            self.animation_path = list(map(int, output.split()))

            total = 0
            path_details = []
            for i in range(len(self.animation_path) - 1):
                n1, n2 = self.animation_path[i], self.animation_path[i + 1]
                weight = self.get_edge_weight(n1, n2)
                total += weight
                path_details.append(f"{n1} → {n2} (weight: {weight})")

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Dijkstra Shortest Path\n\n")
            self.result_text.insert(tk.END, f"Total Distance: {total}\n\n")
            self.result_text.insert(
                tk.END, f"Path ({len(self.animation_path)} nodes):\n"
            )
            for detail in path_details:
                self.result_text.insert(tk.END, f"  {detail}\n")

            if len(self.animation_path) > 1:
                self.animation_mode = "path"
                self.animation_title = "Dijkstra"
                self.start_animation()

    def find_mst(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Warning", "Add at least 2 nodes!")
            return

        self.cancel_animation()
        self.highlight_color = "#009900"
        self.highlighted_path = []
        self.highlighted_edges = []

        output = self.run_algorithm("mst")

        if output:
            lines = output.strip().split("\n")
            weight = int(lines[0])

            self.animation_edges = []
            for line in lines[1:]:
                parts = line.split()
                if len(parts) == 2:
                    self.animation_edges.append((int(parts[0]), int(parts[1])))

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Minimum Spanning Tree\n\n")
            self.result_text.insert(tk.END, f"Total Weight: {weight}\n\n")
            self.result_text.insert(tk.END, f"Edges ({len(self.animation_edges)}):\n")
            for e in self.animation_edges:
                w = self.get_edge_weight(e[0], e[1])
                self.result_text.insert(tk.END, f"  {e[0]} — {e[1]} (weight: {w})\n")

            if len(self.animation_edges) > 0:
                self.animation_mode = "edges"
                self.animation_title = "MST"
                self.start_animation()
            else:
                self.redraw()

    def find_max_st(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Warning", "Add at least 2 nodes!")
            return

        self.cancel_animation()
        self.highlight_color = "#CC6600"
        self.highlighted_path = []
        self.highlighted_edges = []

        output = self.run_algorithm("maxst")

        if output:
            lines = output.strip().split("\n")
            weight = int(lines[0])

            self.animation_edges = []
            for line in lines[1:]:
                parts = line.split()
                if len(parts) == 2:
                    self.animation_edges.append((int(parts[0]), int(parts[1])))

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Maximum Spanning Tree\n\n")
            self.result_text.insert(tk.END, f"Total Weight: {weight}\n\n")
            self.result_text.insert(tk.END, f"Edges ({len(self.animation_edges)}):\n")
            for e in self.animation_edges:
                w = self.get_edge_weight(e[0], e[1])
                self.result_text.insert(tk.END, f"  {e[0]} — {e[1]} (weight: {w})\n")

            if len(self.animation_edges) > 0:
                self.animation_mode = "edges"
                self.animation_title = "Max ST"
                self.start_animation()
            else:
                self.redraw()

    def chinese_postman(self):
        if len(self.edges) == 0:
            messagebox.showwarning("Warning", "Add some edges first!")
            return

        self.cancel_animation()

        self.highlight_color = "#AA00AA"
        self.highlighted_path = []
        self.highlighted_edges = []

        output = self.run_algorithm("chinese")

        if output:
            lines = output.strip().split("\n")
            cost = int(lines[0])

            if len(lines) > 1 and lines[1].strip():
                self.animation_path = list(map(int, lines[1].split()))
            else:
                self.animation_path = []

            base_cost = sum(e[2] for e in self.edges)
            extra_cost = cost - base_cost
            path_details = []
            for i in range(len(self.animation_path) - 1):
                u, v = self.animation_path[i], self.animation_path[i + 1]
                weight = self.get_edge_weight(u, v)
                path_details.append(f"{u} → {v} (weight: {weight})")

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Chinese Postman Problem\n\n")
            self.result_text.insert(tk.END, f"Minimum Tour Cost: {cost}\n\n")
            self.result_text.insert(tk.END, f"Base cost: {base_cost}\n")
            self.result_text.insert(tk.END, f"Extra cost: {extra_cost}\n\n")
            self.result_text.insert(
                tk.END, f"Tour ({len(self.animation_path)} nodes):\n"
            )
            for detail in path_details:
                self.result_text.insert(tk.END, f"  {detail}\n")

            if len(self.animation_path) > 1:
                self.start_animation()
            else:
                self.redraw()

    def get_edge_weight(self, u, v):
        for e in self.edges:
            if (e[0] == u and e[1] == v) or (e[0] == v and e[1] == u):
                return e[2]
        return 0

    def start_animation(self):
        self.animation_step = 0
        self.animation_playing = False
        self.animation_frame.pack_forget()
        self.animation_frame.pack(fill=tk.X, pady=5)
        self.play_btn.config(text="▶ Play")
        self.update_animation_display()

    def stop_animation(self):
        self.animation_playing = False
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.animation_frame.pack_forget()
        self.animation_path = []
        self.animation_edges = []
        self.animation_step = 0
        self.highlighted_path = []
        self.highlighted_edges = []
        self.redraw()

    def cancel_animation(self):
        self.animation_playing = False
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.animation_frame.pack_forget()
        self.animation_path = []
        self.animation_edges = []
        self.animation_step = 0

    def get_animation_total_steps(self):
        if self.animation_mode == "path":
            return len(self.animation_path) - 1
        else:
            return len(self.animation_edges)

    def animation_toggle_play(self):
        if self.animation_playing:
            self.animation_playing = False
            if self.animation_job:
                self.root.after_cancel(self.animation_job)
                self.animation_job = None
            self.play_btn.config(text="▶ Play")
        else:
            self.animation_playing = True
            self.play_btn.config(text="⏸ Pause")
            self.animation_tick()

    def animation_tick(self):
        if not self.animation_playing:
            return

        total_steps = self.get_animation_total_steps()
        if self.animation_step < total_steps:
            self.animation_step += 1
            self.update_animation_display()
            self.animation_job = self.root.after(
                self.animation_speed, self.animation_tick
            )
        else:
            self.animation_step = 0
            self.update_animation_display()
            self.animation_job = self.root.after(
                self.animation_speed, self.animation_tick
            )

    def animation_next(self):
        total_steps = self.get_animation_total_steps()
        if self.animation_step < total_steps:
            self.animation_step += 1
            self.update_animation_display()

    def animation_prev(self):
        if self.animation_step > 0:
            self.animation_step -= 1
            self.update_animation_display()

    def update_speed(self, value):
        self.animation_speed = int(float(value))
        self.speed_label.config(text=f"{self.animation_speed}ms")

    def update_animation_display(self):
        total_steps = self.get_animation_total_steps()

        if self.animation_mode == "path":
            if not self.animation_path:
                return

            self.step_var.set(f"Step: {self.animation_step} / {total_steps}")
            self.highlighted_path = self.animation_path[: self.animation_step + 1]

            self.highlighted_edges = []
            for i in range(self.animation_step):
                n1, n2 = self.animation_path[i], self.animation_path[i + 1]
                self.highlighted_edges.append((n1, n2))

            if self.animation_step > 0:
                u = self.animation_path[self.animation_step - 1]
                v = self.animation_path[self.animation_step]
                weight = self.get_edge_weight(u, v)
                self.edge_info_var.set(
                    f"{self.animation_title}: {u} → {v} (weight: {weight})"
                )
            else:
                self.edge_info_var.set(f"Start: Node {self.animation_path[0]}")

        else:
            if not self.animation_edges:
                return

            self.step_var.set(f"Edge: {self.animation_step} / {total_steps}")
            self.highlighted_edges = self.animation_edges[: self.animation_step]
            self.highlighted_path = []
            for e in self.highlighted_edges:
                if e[0] not in self.highlighted_path:
                    self.highlighted_path.append(e[0])
                if e[1] not in self.highlighted_path:
                    self.highlighted_path.append(e[1])

            if self.animation_step > 0:
                u, v = self.animation_edges[self.animation_step - 1]
                weight = self.get_edge_weight(u, v)
                self.edge_info_var.set(
                    f"{self.animation_title}: {u} — {v} (weight: {weight})"
                )
            else:
                self.edge_info_var.set(f"Building {self.animation_title}...")

        self.redraw()

    def traveling_salesman(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Warning", "Add at least 2 nodes!")
            return

        if len(self.nodes) > 15:
            if not messagebox.askyesno(
                "Warning",
                f"TSP with {len(self.nodes)} nodes may take a while.\nContinue?",
            ):
                return

        self.cancel_animation()
        start = self.start_node if self.start_node is not None else 0
        self.highlight_color = "#0066CC"
        self.highlighted_path = []
        self.highlighted_edges = []

        output = self.run_algorithm("tsp", f"{start}\n")

        if output == "NO_PATH":
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(
                tk.END, "No valid tour found!\nGraph may be disconnected."
            )
            self.redraw()
        elif output:
            lines = output.strip().split("\n")
            cost = int(lines[0])

            if len(lines) > 1:
                self.animation_path = list(map(int, lines[1].split()))

                path_details = []
                for i in range(len(self.animation_path) - 1):
                    n1, n2 = self.animation_path[i], self.animation_path[i + 1]
                    weight = self.get_edge_weight(n1, n2)
                    path_details.append(f"{n1} → {n2} (weight: {weight})")

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Traveling Salesman\n\n")
            self.result_text.insert(tk.END, f"Starting from node: {start}\n")
            self.result_text.insert(tk.END, f"Minimum Tour Cost: {cost}\n\n")
            self.result_text.insert(
                tk.END, f"Tour ({len(self.animation_path)} nodes):\n"
            )
            for detail in path_details:
                self.result_text.insert(tk.END, f"  {detail}\n")

            if len(self.animation_path) > 1:
                self.animation_mode = "path"
                self.animation_title = "TSP"
                self.start_animation()

    def clear_graph(self):
        self.nodes = []
        self.edges = []
        self.start_node = None
        self.end_node = None
        self.selected_node = None
        self.clear_highlights()
        self.redraw()
        self.update_info()

    def load_example(self):
        self.clear_graph()

        self.nodes = [
            (150, 150),
            (300, 80),
            (300, 220),
            (450, 80),
            (450, 220),
            (600, 150),
            (375, 350),
        ]

        self.edges = [
            (0, 1, 4),
            (0, 2, 2),
            (1, 2, 1),
            (1, 3, 5),
            (2, 3, 8),
            (2, 4, 10),
            (2, 6, 6),
            (3, 4, 2),
            (3, 5, 6),
            (4, 5, 3),
            (4, 6, 4),
            (5, 6, 7),
        ]

        self.start_node = 0
        self.end_node = 5

        self.redraw()
        self.update_info()
        self.status_var.set("Example loaded! Try the algorithms.")


def main():
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()