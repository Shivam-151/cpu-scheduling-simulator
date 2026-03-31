from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def draw_gantt_chart(frame, gantt, title="Gantt Chart"):
    for widget in frame.winfo_children():
        widget.destroy()

    fig = Figure(figsize=(6, 2.8), dpi=100)
    ax = fig.add_subplot(111)

    y = 10

    for pid, start, end in gantt:
        width = end - start
        ax.broken_barh([(start, width)], (y, 8))
        ax.text(start + width / 2, y + 4, pid, ha="center", va="center", fontsize=9)
        ax.text(start, y - 1.5, str(start), ha="center", va="top", fontsize=8)

    if gantt:
        ax.text(gantt[-1][2], y - 1.5, str(gantt[-1][2]), ha="center", va="top", fontsize=8)

    max_time = max(seg[2] for seg in gantt) if gantt else 10

    ax.set_ylim(5, 25)
    ax.set_xlim(0, max_time + 1)
    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    return canvas


def draw_comparison_chart(frame, results):
    for widget in frame.winfo_children():
        widget.destroy()

    fig = Figure(figsize=(10, 3), dpi=100)
    ax = fig.add_subplot(111)

    names = [r["name"] for r in results]
    waiting = [r["avg_waiting"] for r in results]
    turnaround = [r["avg_turnaround"] for r in results]
    response = [r["avg_response"] for r in results]

    x = list(range(len(names)))
    w = 0.25

    ax.bar([i - w for i in x], waiting, width=w, label="Avg Waiting")
    ax.bar(x, turnaround, width=w, label="Avg Turnaround")
    ax.bar([i + w for i in x], response, width=w, label="Avg Response")

    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Time")
    ax.set_title("Algorithm Performance Comparison")
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    return canvas