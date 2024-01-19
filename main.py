from customtkinter import CTk, CTkFrame, CTkLabel, CTkTextbox, CTkFont, set_appearance_mode, set_default_color_theme
from tkinter import filedialog
import re

set_appearance_mode("dark")
set_default_color_theme("dark-blue")

# ----------- APP CONFIG ----------- #

app = CTk()
app.title("GodTold")
app.geometry("900x500")

# ----------- STYLE CONFIG ----------- #
text_font = CTkFont(family="Roboto", size=14)
frame_border_size = 1
border_color_rgb = (248, 43, 255)
border_color_hex = "#{:02x}{:02x}{:02x}".format(*border_color_rgb)

# ----------- FUNCTIONS ----------- #


def on_paste(event):
  app.after(1, apply_syntax_highlighting)


def on_undo(event):
  app.after(1, apply_syntax_highlighting)


def open_file():
  file_path = filedialog.askopenfilename(defaultextension=".py",
                                         filetypes=[("Python files", "*.py"),
                                                    ("All files", "*.*")],
                                         title="Open File")

  if file_path:
    with open(file_path, 'r') as file:
      editor_text.delete("1.0", "end")
      editor_text.insert("1.0", file.read())

    location_label.configure(text=file_path)
    save_file.file_path = file_path
    apply_syntax_highlighting()


def save_file_as():
  file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                           filetypes=[("Python files", "*.py"),
                                                      ("All files", "*.*")],
                                           title="Save As")

  if file_path:
    with open(file_path, 'w') as file:
      file.write(editor_text.get("1.0", "end-1c"))

    save_file.file_path = file_path
    location_label.configure(text=file_path)
    print(f"File saved to: {file_path}")


def save_file():
  try:
    with open(save_file.file_path, 'w') as file:
      file.write(editor_text.get("1.0", "end-1c"))
    print(f"File saved to: {save_file.file_path}")
  except AttributeError:
    save_file_as()


def _from_rgb(rgb):
  return "#{:02x}{:02x}{:02x}".format(*rgb)


tag_configs = {
  "highlight": {
    "foreground": "orange"
  },
  "comment": {
    "foreground": _from_rgb((97, 199, 0))
  },
  "string_double": {
    "foreground": _from_rgb((255, 210, 61))
  },
  "string_triple": {
    "foreground": _from_rgb((255, 210, 61))
  },
  "variable": {
    "foreground": _from_rgb((171, 61, 255))
  },
  "before_method": {
    "foreground": _from_rgb((50, 142, 168))
  },
  "after_method": {
    "foreground": _from_rgb((32, 212, 209))
  },
}

# Compile static regular expressions
string_regex = re.compile(r'(["\'])((?:(?=(\\?))\3.)*?)\1', re.DOTALL)
comma_regex = re.compile(r',')
variable_regex = re.compile(r'([^\d\W]\w*)\s*=')
before_method_regex = re.compile(r'\b(\w+\.)\w+\(')
after_method_regex = re.compile(r'\.\s*(\w+)\(')


def on_tab_press(event):
  cursor_pos = editor_text.index("insert")
  current_line = editor_text.get(f"{cursor_pos} linestart",
                                 f"{cursor_pos} lineend")
  indented_line = current_line.expandtabs(4)
  editor_text.delete(f"{cursor_pos} linestart", f"{cursor_pos} lineend")
  editor_text.insert(cursor_pos, indented_line)


keywords = [
  "import ", "from ", "def ", "class ", "if ", "else ", "for ", "while ",
  "print(", "try ", "except ", "(", ")", "with", "open"
]
highlight_tags = set(tag_configs.keys())


def apply_syntax_highlighting():
  current_text = editor_text.get("1.0", "end-1c")

  for tag_type in highlight_tags:
    editor_text.tag_remove(tag_type, "1.0", "end")

  current_text = current_text.replace('\t', '    ')

  # Highlight keywords, comments, strings, commas, variables, and methods
  for keyword in keywords:
    start = "1.0"
    while start:
      start = editor_text.search(keyword, start, stopindex="end", nocase=True)
      if start:
        end = f"{start}+{len(keyword)}c"
        editor_text.tag_add("highlight", start, end)
        start = end

  for start, end, tag_type in zip(
      map(lambda x: f"1.0+{x.start(2)}c", string_regex.finditer(current_text)),
      map(lambda x: f"1.0+{x.end(2)}c", string_regex.finditer(current_text)), [
        "string_double" if x.group(1) == '"' else "string_triple"
        for x in string_regex.finditer(current_text)
      ]):
    editor_text.tag_add(tag_type, start, end)

  for match in variable_regex.finditer(current_text):
    editor_text.tag_add("variable", f"1.0+{match.start(1)}c",
                        f"1.0+{match.end(1)}c")

  for match in before_method_regex.finditer(current_text):
    editor_text.tag_add("before_method", f"1.0+{match.start(1)}c",
                        f"1.0+{match.end(1)}c")

  for match in after_method_regex.finditer(current_text):
    editor_text.tag_add("after_method", f"1.0+{match.start(1)}c",
                        f"1.0+{match.end(1)}c")

  for tag_type, config in tag_configs.items():
    editor_text.tag_config(tag_type, **config)


def on_char_type(event):
  typed_char = event.char
  if typed_char == '\t':
    on_tab_press(event)
  elif typed_char in [' ', '(', ')', '.']:
    apply_syntax_highlighting()


# ----------- MAIN FRAMES ----------- #

location_frame = CTkFrame(master=app,
                          height=25,
                          corner_radius=0,
                          border_color=border_color_hex,
                          border_width=frame_border_size)
location_frame.pack(side="top", fill="x")

location_label = CTkLabel(master=location_frame, text="", font=text_font)
location_label.pack(fill="both", expand=True)

# Editor frame
editor_frame = CTkFrame(master=app,
                        corner_radius=0,
                        border_color=border_color_hex,
                        border_width=frame_border_size)
editor_frame.pack(side="left", fill="both", expand=True)

# ----------- UI ELEMENTS ----------- #

editor_text = CTkTextbox(master=editor_frame,
                         fg_color="black",
                         corner_radius=0,
                         undo=True,
                         autoseparators=True,
                         maxundo=20,
                         font=text_font)
editor_text.pack(fill="both", expand=True)

# ----------- KEY BINDINGS ----------- #

app.bind("<Control-o>", lambda event: open_file())
app.bind("<Control-s>", lambda event: save_file())
editor_text.bind("<KeyRelease>", on_char_type)

app.bind("<Control-v>", on_paste)
app.bind("<Control-z>", on_undo)

# editor_text.bind("<Tab>", on_tab_press)

app.mainloop()
