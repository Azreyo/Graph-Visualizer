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
        self.cpp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graph_algorithms.cpp")
        exe_name = "graph_algorithms.exe" if platform.system() == "Windows" else "graph_algorithms"
        self.exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), exe_name)
        self.setup_ui()
        self.compile_cpp()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        left_panel = ttk.Frame(main_frame, padding="10", width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        mode_frame = ttk.LabelFrame(left_panel, text="Edit Mode", padding="5")
        mode_frame.pack(fill=tk.X, pady=5)       
        self.mode_var = tk.StringVar(value="add_node")
        modes = [
            ("Add Node", "add_node"),
            ("Add Edge", "add_edge"),
            ("Set Start", "select_start"),
            ("Set End", "select_end")
        ]
        for text, value in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var,
                           value=value, command=self.change_mode).pack(anchor=tk.W)
        algo_frame = ttk.LabelFrame(left_panel, text="Algorithms", padding="5")
        algo_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(algo_frame, text="Dijkstra Shortest Path",
                  command=self.find_shortest_path).pack(fill=tk.X, pady=2)
        ttk.Separator(algo_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        ttk.Button(algo_frame, text="Minimum Spanning Tree",
                  command=self.find_mst).pack(fill=tk.X, pady=2)
        ttk.Button(algo_frame, text="Maximum Spanning Tree",
                  command=self.find_max_st).pack(fill=tk.X, pady=2)
        
        ttk.Separator(algo_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        ttk.Button(algo_frame, text="Chinese Postman",
                  command=self.chinese_postman).pack(fill=tk.X, pady=2)
        ttk.Button(algo_frame, text="Traveling Salesman",
                  command=self.traveling_salesman).pack(fill=tk.X, pady=2)
        
        action_frame = ttk.LabelFrame(left_panel, text="Actions", padding="5")
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Load Example",
                  command=self.load_example).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Clear Graph",
                  command=self.clear_graph).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Clear Highlights",
                  command=self.clear_highlights).pack(fill=tk.X, pady=2)
        
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
        ttk.Label(left_panel, textvariable=self.status_var, 
                 foreground="blue", wraplength=250).pack(pady=5)
        
        result_frame = ttk.LabelFrame(left_panel, text="Result", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, height=8, width=30, wrap=tk.WORD,
                                   font=("Consolas", 9))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        legend_frame = ttk.LabelFrame(left_panel, text="Legend", padding="5")
        legend_frame.pack(fill=tk.X, pady=5)
        
        legends = [
            ("🟢", "Start Node"),
            ("🔴", "End Node"),
            ("🟠", "Path/Result"),
            ("🔵", "Regular Node")
        ]
        for symbol, text in legends:
            ttk.Label(legend_frame, text=f"{symbol} {text}").pack(anchor=tk.W)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(right_panel, bg="white", highlightthickness=2,
                               highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
    
    def change_mode(self):
        self.mode = self.mode_var.get()
        self.selected_node = None
        messages = {
            "add_node": "Click to add a node",
            "add_edge": "Click first node, then second to add edge",
            "select_start": "Click a node to set as START",
            "select_end": "Click a node to set as END"
        }
        self.status_var.set(messages.get(self.mode, ""))
        self.redraw()
    
    def compile_cpp(self):
        if not os.path.exists(self.cpp_path):
            messagebox.showerror("Error", "graph_algorithms.cpp not found!")
            return False
        
        if os.path.exists(self.exe_path):
            if os.path.getmtime(self.exe_path) > os.path.getmtime(self.cpp_path):
                return True
        
    
        result = subprocess.run(
            ["g++", "-O3", "-std=c++17", "-o", self.exe_path, self.cpp_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            messagebox.showerror("Compilation Error", result.stderr)
            return False
        return True
    
    def get_node_at(self, x, y):
        for i, (nx, ny) in enumerate(self.nodes):
            if math.sqrt((x - nx) ** 2 + (y - ny) ** 2) <= self.node_radius:
                return i
        return None
    
    def on_left_click(self, event):
        x, y = event.x, event.y
        clicked = self.get_node_at(x, y)
        
        if self.mode == "add_node":
            if clicked is None:
                self.nodes.append((x, y))
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
                            (e[0] == self.selected_node and e[1] == clicked) or
                            (e[0] == clicked and e[1] == self.selected_node)
                            for e in self.edges
                        )
                        if not exists:
                            x1, y1 = self.nodes[self.selected_node]
                            x2, y2 = self.nodes[clicked]
                            weight = max(1, int(math.sqrt((x2-x1)**2 + (y2-y1)**2) / 10))
                            
                            custom = simpledialog.askinteger(
                                "Edge Weight",
                                f"Weight for edge {self.selected_node} → {clicked}:",
                                initialvalue=weight, minvalue=1, maxvalue=999
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
                (e[0] - (1 if e[0] > clicked else 0),
                 e[1] - (1 if e[1] > clicked else 0), e[2])
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
        self.start_var.set(f"Start: {self.start_node if self.start_node is not None else 'None'}")
        self.end_var.set(f"End: {self.end_node if self.end_node is not None else 'None'}")
    
    def clear_highlights(self):
        self.highlighted_path = []
        self.highlighted_edges = []
        self.result_text.delete(1.0, tk.END)
    
    def redraw(self):
        self.canvas.delete("all")
        
        for e in self.edges:
            n1, n2, weight = e
            x1, y1 = self.nodes[n1]
            x2, y2 = self.nodes[n2]
            
            in_highlight = (n1, n2) in self.highlighted_edges or (n2, n1) in self.highlighted_edges
            
            in_path = False
            if len(self.highlighted_path) > 1:
                for i in range(len(self.highlighted_path) - 1):
                    if (self.highlighted_path[i] == n1 and self.highlighted_path[i+1] == n2) or \
                       (self.highlighted_path[i] == n2 and self.highlighted_path[i+1] == n1):
                        in_path = True
                        break
            
            color = self.highlight_color if (in_highlight or in_path) else "#888888"
            width = 4 if (in_highlight or in_path) else 2
            
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
            
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.create_oval(mx-12, my-10, mx+12, my+10, fill="white", outline=color)
            self.canvas.create_text(mx, my, text=str(weight), font=("Arial", 9, "bold"), fill=color)
        
        for i, (x, y) in enumerate(self.nodes):
            if i == self.start_node:
                color, outline = "#00CC00", "#008800"
            elif i == self.end_node:
                color, outline = "#CC0000", "#880000"
            elif i in self.highlighted_path:
                color, outline = "#FFAA00", "#CC8800"
            elif i == self.selected_node:
                color, outline = "#00AAFF", "#0088CC"
            else:
                color, outline = "#4488FF", "#2266CC"
            
            r = self.node_radius
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=outline, width=3)
            self.canvas.create_text(x, y, text=str(i), font=("Arial", 12, "bold"), fill="white")
    
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
                [self.exe_path], input=input_data,
                capture_output=True, text=True, timeout=10
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
        
        self.highlight_color = "#00AA00"
        output = self.run_algorithm("dijkstra", f"{self.start_node} {self.end_node}\n")
        self.highlighted_path = []
        self.highlighted_edges = []
        
        if output == "NO_PATH":
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No path found!")
        else:
            self.highlighted_path = list(map(int, output.split()))
            
            total = 0
            for i in range(len(self.highlighted_path) - 1):
                n1, n2 = self.highlighted_path[i], self.highlighted_path[i+1]
                for e in self.edges:
                    if (e[0] == n1 and e[1] == n2) or (e[0] == n2 and e[1] == n1):
                        total += e[2]
                        break
            
            path_str = " → ".join(map(str, self.highlighted_path))
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Dijkstra Shortest Path\n\n")
            self.result_text.insert(tk.END, f"Path: {path_str}\n\n")
            self.result_text.insert(tk.END, f"Total Distance: {total}")
        
        self.redraw()
    
    def find_mst(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Warning", "Add at least 2 nodes!")
            return
        
        self.highlight_color = "#009900"
        self.highlighted_path = []
        self.highlighted_edges = []
        
        output = self.run_algorithm("mst")
        
        if output:
            lines = output.strip().split('\n')
            weight = int(lines[0])
            
            for line in lines[1:]:
                parts = line.split()
                if len(parts) == 2:
                    self.highlighted_edges.append((int(parts[0]), int(parts[1])))
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Minimum Spanning Tree\n\n")
            self.result_text.insert(tk.END, f"Total Weight: {weight}\n\n")
            self.result_text.insert(tk.END, f"Edges ({len(self.highlighted_edges)}):\n")
            for e in self.highlighted_edges:
                self.result_text.insert(tk.END, f"  {e[0]} — {e[1]}\n")
        
        self.redraw()
    
    def find_max_st(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Warning", "Add at least 2 nodes!")
            return
        
        self.highlight_color = "#CC6600"
        self.highlighted_path = []
        self.highlighted_edges = []
        
        output = self.run_algorithm("maxst")
        
        if output:
            lines = output.strip().split('\n')
            weight = int(lines[0])
            
            for line in lines[1:]:
                parts = line.split()
                if len(parts) == 2:
                    self.highlighted_edges.append((int(parts[0]), int(parts[1])))
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Maximum Spanning Tree\n\n")
            self.result_text.insert(tk.END, f"Total Weight: {weight}\n\n")
            self.result_text.insert(tk.END, f"Edges ({len(self.highlighted_edges)}):\n")
            for e in self.highlighted_edges:
                self.result_text.insert(tk.END, f"  {e[0]} — {e[1]}\n")
        
        self.redraw()
    
    def chinese_postman(self):
        if len(self.edges) == 0:
            messagebox.showwarning("Warning", "Add some edges first!")
            return
        
        self.highlight_color = "#AA00AA"
        self.highlighted_path = []
        self.highlighted_edges = []
        
        output = self.run_algorithm("chinese")
        
        if output:
            lines = output.strip().split('\n')
            cost = int(lines[0])
            
            if len(lines) > 1 and lines[1].strip():
                self.highlighted_path = list(map(int, lines[1].split()))
            
            base_cost = sum(e[2] for e in self.edges)
            extra_cost = cost - base_cost
            
            path_str = " → ".join(map(str, self.highlighted_path)) if self.highlighted_path else "N/A"
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Chinese Postman Problem\n\n")
            self.result_text.insert(tk.END, f"Minimum Tour Cost: {cost}\n\n")
            self.result_text.insert(tk.END, f"Base cost: {base_cost}\n")
            self.result_text.insert(tk.END, f"Extra cost: {extra_cost}\n\n")
            self.result_text.insert(tk.END, f"Tour:\n{path_str}")
        
        self.redraw()
    
    def traveling_salesman(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Warning", "Add at least 2 nodes!")
            return
        
        if len(self.nodes) > 15:
            if not messagebox.askyesno("Warning", 
                f"TSP with {len(self.nodes)} nodes may take a while.\nContinue?"):
                return
        
        start = self.start_node if self.start_node is not None else 0
        self.highlight_color = "#0066CC"
        self.highlighted_path = []
        self.highlighted_edges = []
        
        output = self.run_algorithm("tsp", f"{start}\n")
        
        if output == "NO_PATH":
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No valid tour found!\nGraph may be disconnected.")
        elif output:
            lines = output.strip().split('\n')
            cost = int(lines[0])
            
            if len(lines) > 1:
                self.highlighted_path = list(map(int, lines[1].split()))
                
                for i in range(len(self.highlighted_path) - 1):
                    n1, n2 = self.highlighted_path[i], self.highlighted_path[i+1]
                    self.highlighted_edges.append((n1, n2))
            
            path_str = " → ".join(map(str, self.highlighted_path))
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Traveling Salesman\n\n")
            self.result_text.insert(tk.END, f"Starting from node: {start}\n\n")
            self.result_text.insert(tk.END, f"Minimum Tour Cost: {cost}\n\n")
            self.result_text.insert(tk.END, f"Tour:\n{path_str}")
        
        self.redraw()
    
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
