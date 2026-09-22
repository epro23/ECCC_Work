from app_window import AppWindow
from frames import AppFrame
from elements import Button, Table

root = AppWindow(title="Data Tool")
frame_1 = AppFrame(root, "main_frame")

def write_output(path):
    with open(path, "w") as f:
        f.write("results here")

Button.browse_file(frame_1, on_select=lambda p: print("Selected:", p), text="Load File")
Button.save_file(frame_1, on_save=write_output, text="Export")

table = Table(frame_1, columns=["Name", "Value"], name="results_table")
table.load_rows([("Sample A", 12.3), ("Sample B", 9.7)])

root.run()