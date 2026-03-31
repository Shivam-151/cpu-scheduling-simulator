import tkinter as tk
from tkinter import ttk, messagebox

from models import Process
from algorithms import fcfs, sjf_non_preemptive, priority_non_preemptive, round_robin
from charts import draw_gantt_chart, draw_comparison_chart
from sample_data import get_sample_processes


class CPUSchedulingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("1300x760")
        self.root.minsize(1100, 680)

        self.processes = []

        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="CPU Scheduling Simulator and Performance Analyzer",
            font=("Arial", 18, "bold"),
            pady=10
        )
        title.pack()

        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10)

        left_panel = tk.LabelFrame(top_frame, text="Process Input", padx=10, pady=10)
        left_panel.pack(side="left", fill="y")

        tk.Label(left_panel, text="Process ID").grid(row=0, column=0, sticky="w")
        tk.Label(left_panel, text="Arrival Time").grid(row=1, column=0, sticky="w")
        tk.Label(left_panel, text="Burst Time").grid(row=2, column=0, sticky="w")
        tk.Label(left_panel, text="Priority").grid(row=3, column=0, sticky="w")
        tk.Label(left_panel, text="Time Quantum").grid(row=4, column=0, sticky="w")
        tk.Label(left_panel, text="Algorithm").grid(row=5, column=0, sticky="w")

        self.pid_var = tk.StringVar()
        self.arrival_var = tk.StringVar()
        self.burst_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="1")
        self.quantum_var = tk.StringVar(value="2")
        self.algorithm_var = tk.StringVar(value="FCFS")

        ttk.Entry(left_panel, textvariable=self.pid_var, width=18).grid(row=0, column=1, pady=3)
        ttk.Entry(left_panel, textvariable=self.arrival_var, width=18).grid(row=1, column=1, pady=3)
        ttk.Entry(left_panel, textvariable=self.burst_var, width=18).grid(row=2, column=1, pady=3)
        ttk.Entry(left_panel, textvariable=self.priority_var, width=18).grid(row=3, column=1, pady=3)
        ttk.Entry(left_panel, textvariable=self.quantum_var, width=18).grid(row=4, column=1, pady=3)

        algo_combo = ttk.Combobox(
            left_panel,
            textvariable=self.algorithm_var,
            values=["FCFS", "SJF", "Priority", "Round Robin"],
            width=16,
            state="readonly"
        )
        algo_combo.grid(row=5, column=1, pady=3)

        button_frame = tk.Frame(left_panel)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Process", command=self.add_process).grid(row=0, column=0, padx=4, pady=2)
        ttk.Button(button_frame, text="Run Simulation", command=self.run_selected_algorithm).grid(row=0, column=1, padx=4, pady=2)
        ttk.Button(button_frame, text="Compare All", command=self.compare_all_algorithms).grid(row=1, column=0, padx=4, pady=2)
        ttk.Button(button_frame, text="Load Sample", command=self.load_sample_data).grid(row=1, column=1, padx=4, pady=2)
        ttk.Button(button_frame, text="Reset All", command=self.reset_all).grid(row=2, column=0, columnspan=2, padx=4, pady=2, sticky="ew")

        tk.Label(
            left_panel,
            text="Priority: smaller number = higher priority",
            fg="gray",
            font=("Arial", 9)
        ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 0))

        right_panel = tk.Frame(top_frame)
        right_panel.pack(side="left", fill="both", expand=True, padx=(10, 0))

        process_frame = tk.LabelFrame(right_panel, text="Process Table")
        process_frame.pack(fill="x")

        columns = ("pid", "arrival", "burst", "priority")
        self.process_tree = ttk.Treeview(process_frame, columns=columns, show="headings", height=7)
        for col, width in [("pid", 100), ("arrival", 120), ("burst", 120), ("priority", 120)]:
            self.process_tree.heading(col, text=col.upper())
            self.process_tree.column(col, width=width, anchor="center")
        self.process_tree.pack(fill="x", padx=5, pady=5)

        middle_frame = tk.Frame(self.root)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=10)

        result_frame = tk.LabelFrame(middle_frame, text="Result Table")
        result_frame.pack(side="left", fill="both", expand=True)

        result_columns = ("pid", "arrival", "burst", "priority", "completion", "turnaround", "waiting", "response")
        self.result_tree = ttk.Treeview(result_frame, columns=result_columns, show="headings", height=15)

        widths = {
            "pid": 70,
            "arrival": 80,
            "burst": 70,
            "priority": 70,
            "completion": 90,
            "turnaround": 95,
            "waiting": 80,
            "response": 80,
        }

        for col in result_columns:
            self.result_tree.heading(col, text=col.upper())
            self.result_tree.column(col, width=widths[col], anchor="center")

        self.result_tree.pack(fill="both", expand=True, padx=5, pady=5)

        output_frame = tk.LabelFrame(middle_frame, text="Output")
        output_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self.summary_label = tk.Label(
            output_frame,
            text="Run an algorithm to see output.",
            justify="left",
            anchor="w",
            font=("Arial", 11)
        )
        self.summary_label.pack(fill="x", padx=10, pady=10)

        self.chart_frame = tk.Frame(output_frame, height=250)
        self.chart_frame.pack(fill="both", expand=True, padx=5, pady=5)

        compare_box = tk.LabelFrame(self.root, text="Algorithm Comparison")
        compare_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.compare_frame = tk.Frame(compare_box, height=220)
        self.compare_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def add_process(self):
        try:
            pid = self.pid_var.get().strip()
            if not pid:
                pid = f"P{len(self.processes) + 1}"

            if any(p.pid == pid for p in self.processes):
                raise ValueError("Process ID must be unique.")

            arrival = int(self.arrival_var.get())
            burst = int(self.burst_var.get())
            priority = int(self.priority_var.get())

            if arrival < 0 or burst <= 0 or priority < 0:
                raise ValueError("Arrival must be >= 0, burst > 0, priority >= 0.")

            self.processes.append(Process(pid, arrival, burst, priority))
            self.refresh_process_table()
            self.clear_inputs()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def refresh_process_table(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        for p in self.processes:
            self.process_tree.insert("", "end", values=(p.pid, p.arrival, p.burst, p.priority))

    def clear_inputs(self):
        self.pid_var.set("")
        self.arrival_var.set("")
        self.burst_var.set("")
        self.priority_var.set("1")

    def get_result(self, algo_name):
        if not self.processes:
            raise ValueError("Please add at least one process.")

        if algo_name == "FCFS":
            return fcfs(self.processes)
        elif algo_name == "SJF":
            return sjf_non_preemptive(self.processes)
        elif algo_name == "Priority":
            return priority_non_preemptive(self.processes)
        elif algo_name == "Round Robin":
            quantum = int(self.quantum_var.get())
            return round_robin(self.processes, quantum)
        else:
            raise ValueError("Invalid algorithm selected.")

    def run_selected_algorithm(self):
        try:
            result = self.get_result(self.algorithm_var.get())
            self.display_result(result)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_result(self, result):
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        for row in result["table"]:
            self.result_tree.insert(
                "",
                "end",
                values=(
                    row["pid"],
                    row["arrival"],
                    row["burst"],
                    row["priority"],
                    row["completion"],
                    row["turnaround"],
                    row["waiting"],
                    row["response"],
                ),
            )

        self.summary_label.config(
            text=(
                f"Selected Algorithm: {result['name']}\n"
                f"Average Waiting Time: {result['avg_waiting']}\n"
                f"Average Turnaround Time: {result['avg_turnaround']}\n"
                f"Average Response Time: {result['avg_response']}\n"
                f"Gantt Order: {' | '.join(seg[0] for seg in result['gantt'])}"
            )
        )

        draw_gantt_chart(self.chart_frame, result["gantt"], f"Gantt Chart - {result['name']}")

    def compare_all_algorithms(self):
        try:
            if not self.processes:
                raise ValueError("Please add at least one process.")

            quantum = int(self.quantum_var.get())

            results = [
                fcfs(self.processes),
                sjf_non_preemptive(self.processes),
                priority_non_preemptive(self.processes),
                round_robin(self.processes, quantum),
            ]

            draw_comparison_chart(self.compare_frame, results)

            best = min(results, key=lambda x: x["avg_waiting"])
            self.summary_label.config(
                text=(
                    f"Comparison Completed\n"
                    f"Best by Average Waiting Time: {best['name']}\n"
                    f"Avg Waiting: {best['avg_waiting']}\n"
                    f"Avg Turnaround: {best['avg_turnaround']}\n"
                    f"Avg Response: {best['avg_response']}"
                )
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_sample_data(self):
        self.processes = get_sample_processes()
        self.refresh_process_table()
        self.algorithm_var.set("FCFS")
        self.quantum_var.set("2")
        messagebox.showinfo("Sample Loaded", "Sample data loaded successfully.")

    def reset_all(self):
        self.processes.clear()
        self.refresh_process_table()
        self.clear_inputs()
        self.quantum_var.set("2")
        self.algorithm_var.set("FCFS")

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        self.summary_label.config(text="Run an algorithm to see output.")

        for frame in [self.chart_frame, self.compare_frame]:
            for widget in frame.winfo_children():
                widget.destroy()