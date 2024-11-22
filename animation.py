from tkinter import filedialog, messagebox, Canvas, Text, NW
from PIL import Image, ImageTk, ImageEnhance
import customtkinter as ctk
import json
import os
import threading

# 設定を保存する関数
def save_settings(settings):
  try:
    with open('settings.json', 'w') as f:
      json.dump(settings, f)
  except IOError as e:
    messagebox.showerror("Error", f"Error saving settings: {e}")

# 設定を読み込む関数
def load_settings():
  if os.path.exists('settings.json'):
    try:
      with open('settings.json', 'r') as f:
        return json.load(f)
    except IOError as e:
      messagebox.showerror("Error", f"Error loading settings: {e}")
  return {}

class App(ctk.CTk):
  def __init__(self, root):

    # 初期化処理
    self.image_ids = []  # 画像のIDを格納するリスト
    self.text_ids = []   # テキストのIDを格納するリスト
    self.selected_id = None  # 選択されているID
    self.canvas = ctk.CTkCanvas(self, bg="white", width=800, height=600)
    self.canvas.pack(fill="both", expand=True)

    super().__init__()
    self.selected_id = None  # 初期値として None を設定
    self.selected_id = self.image_ids[0]  # 最初の画像を選択した状態にする
    self.root = root
    self.canvas = Canvas(root, width=800, height=600)
    self.canvas.pack()
    self.images = []
    self.selected_iamge = None
    self.fade_selected_item = None  # fade_selected_itemを初期化
    self.fade_strength = 1.0  # フェード効果の強さ

    # ウィンドウの設定
    self.title("新しいウィンドウの名前")

    # 前回の設定を読み込む
    self.settings = load_settings()
    self.geometry(self.settings.get('geometry', '800x600+100+100'))

    # 画像とテキストボックスの参照を保持するリスト
    self.images = []
    self.image_ids = []  # キャンバス上の画像IDを保持するリスト
    self.text_ids = []  # キャンバス上のテキストボックスIDを保持するリスト
    self.selected_id = None

    self.image_data = self.settings.get('image_data', [])

    # 利用可能なフォントのリスト
    self.available_fonts = ["Helvetica", "Arial",
                            "Times New Roman", "Courier New", "Comic Sans MS"]

    # ボタンのコマンド設定

    def Button_function():
      file_paths = filedialog.askopenfilenames(
          filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
      for file_path in file_paths:
        if file_path:
          threading.Thread(target=self.display_image,
                           args=(file_path,)).start()
          self.settings['image_paths'] = self.settings.get(
              'image_paths', []) + [file_path]

    # ボタンの詳細設定
    button = ctk.CTkButton(master=self, text="画像を選択",
                           command=Button_function)
    button.grid(row=0, column=0, padx=20, pady=20,
                sticky="ew", columnspan=2)
    self.grid_columnconfigure(0, weight=1)

    # テキストボックス生成ボタン
    text_button = ctk.CTkButton(
        master=self, text="テキストボックスを追加", command=self.create_text_box)
    text_button.grid(row=0, column=1, padx=20, pady=20,
                     sticky="ew", columnspan=2)

    # --- ここにフェードボタンを追加します ---
    fade_button = ctk.CTkButton(
        master=self, text="フェード", command=self.fade_selected_item)
    fade_button.grid(row=0, column=2, padx=20, pady=20,
                     sticky="ew", columnspan=2)
    # -------------------------------------

    # キャンバスを追加
    self.canvas = Canvas(
        self, bg='white', highlightthickness=1, highlightbackground='gray')
    self.canvas.grid(row=1, column=0, padx=20, pady=20,
                     sticky="nsew", columnspan=2)
    self.grid_rowconfigure(1, weight=1)
    self.grid_columnconfigure(0, weight=1)

    for image_info in self.image_data:
      self.load_image(image_info)

    # 画像削除ボタンの詳細設定
    delete_button = ctk.CTkButton(
        master=self, text="選択したアイテムを削除", command=self.delete_selected_item)
    delete_button.grid(row=2, column=0, padx=20,
                       pady=20, sticky="ew", columnspan=2)

    # --- ここにフェード機能メソッドを追加します ---
    def fade_selected_item(self):
      if self.selected_id is None:
        print("No item selected")
        return  # 何も選択されていない場合は処理を終了

      print(f"selected_id: {self.selected_id}")  # 追加: selected_id の値を表示

      # """フェードインアニメーションを開始する"""
      if self.selected_id in self.image_ids:
        self.fade_in(self.selected_id, is_image=True)
      elif self.selected_id in self.text_ids:
        self.fade_in(self.selected_id, is_image=False)

    def fade_in(self, item_id, is_image=True, alpha=0.0, step=0.1):
      """画像またはテキストのフェードインエフェクト"""
      if is_image:
        current_index = self.image_ids.index(item_id)
        original_image = Image.open(
            self.settings['image_paths'][current_index])
        faded_image = ImageEnhance.Brightness(original_image).enhance(alpha)
        self.photo = ImageTk.PhotoImage(faded_image)
        self.canvas.itemconfig(item_id, image=self.photo)
        self.images[current_index] = self.photo
      else:
        faded_color = f"#{int(255 * alpha):02x}{int(255 * alpha):02x}{int(255 * alpha):02x}"
        self.canvas.itemconfig(item_id, fill=faded_color)

      # フェードイン終了判定
      if alpha < 1.0:
        self.after(50, self.fade_in, item_id, is_image, alpha + step)
    # -------------------------------------------------

    # 入力用テキストエリアを追加
    self.text_entry = ctk.CTkEntry(master=self)
    self.text_entry.grid(row=3, column=0, padx=20,
                         pady=10, sticky="ew", columnspan=2)
    self.text_entry.bind("<Return>", self.save_text_edit)
    self.text_entry.bind("<FocusOut>", self.on_text_entry_focus_out)
    self.text_entry.grid_remove()

    # 前回表示していた画像を表示
    for file_path in self.settings.get('image_paths', []):
      if file_path:
        self.display_image(file_path)

    # 前回のテキストボックスを表示
    for text_box_info in self.settings.get('text_boxes', []):
      self.load_text_box(text_box_info)

    # ウィンドウが閉じられるときに設定を保存
    self.protocol("WM_DELETE_WINDOW", self.on_closing)

  def display_image(self, file_path):
    try:
      image = Image.open(file_path)
      photo = ImageTk.PhotoImage(image)

      self.photo = photo

      if self.image_data:
        column = len(self.image_data) % 5
        row = len(self.image_data) // 5
        x = 50 + (column * 120)
        y = 50 + (row * 120)
      else:
        x, y = 50, 50

      image_id = self.canvas.create_image(x, y, anchor='nw', image=photo)

      self.images.append(photo)
      self.image_ids.append(image_id)
# 座標も保存

      self.image_data.append({
          'path': file_path,
          'position': (x, y),
          'size': image.size
      })

      self.canvas.tag_bind(
          image_id, "<ButtonPress-1>", self.on_item_press)
      self.canvas.tag_bind(image_id, "<B1-Motion>", self.on_item_move)

      self.canvas.config(scrollregion=self.canvas.bbox("all"))
    except IOError as e:
      messagebox.showerror("Error", f"Error loading image: {e}")

  def load_image(self, image_info):
    try:
      image = Image.open(image_info['path'])
      resized_image = image.resize(image_info['size'], Image.LANCZOS)
      self.photo = ImageTk.PhotoImage(resized_image)

      x, y = image_info['position']
      image_id = self.canvas.create_image(
          x, y, anchor="nw", image=self.photo)

      self.images.append(self.photo)
      self.image_ids.append(image_id)

      self.canvas.config(scrollregion=self.canvas.bbox('all'))

      self.canvas.tag_bind(
          image_id, "<ButtonPress-1>", self.on_item_press)
      self.canvas.tag_bind(image_id, "<B1-Motion>", self.on_item_move)

    except IOError as e:
      messagebox.showerror("Error", f"Error loading image: {e}")

  def create_text_box(self):
    text_box = self.canvas.create_text(
        200, 200, anchor='nw', text="Edit me", font=("Helvetica", 32))
    self.text_ids.append(text_box)
    self.update_selection_rectangle()  # 修正：テキストボックスの選択領域を更新

    self.canvas.tag_bind(text_box, "<ButtonPress-1>", self.on_item_press)
    self.canvas.tag_bind(text_box, "<B1-Motion>", self.on_item_move)

  def load_text_box(self, text_box_info):
    text = text_box_info['text']
    font_name = text_box_info['font_name']
    font_size = text_box_info['font_size']
    x, y = text_box_info['position']

    text_box = self.canvas.create_text(
        x, y, anchor='nw', text=text, font=(font_name, font_size))
    self.text_ids.append(text_box)
    self.update_selection_rectangle()

    self.canvas.tag_bind(text_box, "<ButtonPress-1>", self.on_item_press)
    self.canvas.tag_bind(text_box, "<B1-Motion>", self.on_item_move)

  def on_item_press(self, event):
    # クリックしたアイテムのIDを取得
    item_id = self.canvas.find_closest(event.x, event.y)
    self.selected_id = item_id[0]  # アイテムIDを selected_id に設定
    # 設定されたselected_idを表示
    print(f"Item pressed, selected_id: {self.selected_id}")
    clicked_item_id = self.canvas.find_withtag("current")[0]
    self.selected_id = clicked_item_id

    self.item_start_x = event.x
    self.item_start_y = event.y

    self.update_selection_rectangle()

    # テキストボックスが選択された場合は入力エリアを表示
    if self.selected_id in self.text_ids:
      self.text_entry.grid()
      self.text_entry.delete(0, 'end')
      self.text_entry.insert(
          0, self.canvas.itemcget(self.selected_id, 'text'))
      self.text_entry.focus_set()
    else:
      self.text_entry.grid_remove()

  def on_text_entry_focus_out(self, event):
    self.save_text_edit(None)
    self.text_entry.grid_remove()

  def update_selection_rectangle(self):
    if hasattr(self, 'selection_rect'):
      self.canvas.delete(self.selection_rect)
    if hasattr(self, 'resize_handles'):
      for handle in self.resize_handles:
        self.canvas.delete(handle)

    if self.selected_id:
      x0, y0, x1, y1 = self.canvas.bbox(self.selected_id)
      self.selection_rect = self.canvas.create_rectangle(
          x0, y0, x1, y1, outline='gray', dash=(2, 2))
      self.resize_handles = [
          self.canvas.create_oval(
              x0 - 5, y0 - 5, x0 + 5, y0 + 5, fill='gray'),  # Top-left
          self.canvas.create_oval(
              x1 - 5, y0 - 5, x1 + 5, y0 + 5, fill='gray'),  # Top-right
          self.canvas.create_oval(
              x0 - 5, y1 - 5, x0 + 5, y1 + 5, fill='gray'),  # Bottom-left
          self.canvas.create_oval(
              x1 - 5, y1 - 5, x1 + 5, y1 + 5, fill='gray'),  # Bottom-right
          self.canvas.create_oval(
              # Top-center
              (x0 + x1) / 2 - 5, y0 - 5, (x0 + x1) / 2 + 5, y0 + 5, fill='gray'),
          self.canvas.create_oval(
              # Bottom-center
              (x0 + x1) / 2 - 5, y1 - 5, (x0 + x1) / 2 + 5, y1 + 5, fill='gray'),
          self.canvas.create_oval(
              # Left-center
              x0 - 5, (y0 + y1) / 2 - 5, x0 + 5, (y0 + y1) / 2 + 5, fill='gray'),
          self.canvas.create_oval(
              # Right-center
              x1 - 5, (y0 + y1) / 2 - 5, x1 + 5, (y0 + y1) / 2 + 5, fill='gray')
      ]

      for handle in self.resize_handles:
        self.canvas.tag_bind(
            handle, "<ButtonPress-1>", self.on_resize_press)
        self.canvas.tag_bind(
            handle, "<B1-Motion>", self.on_resize_item)

  def update_text_size(self, event):
    new_text = self.text_entry.get()
    self.canvas.itemconfig(self.selected_id, text=new_text)
    self.update_selection_rectangle()

  def on_item_move(self, event):
    if not self.selected_id:
      return

    dx = event.x - self.item_start_x
    dy = event.y - self.item_start_y
    self.canvas.move(self.selected_id, dx, dy)

    if self.selected_id in self.image_ids:
      current_index = self.image_ids.index(self.selected_id)
      self.image_data[current_index]['position'] = self.canvas.coords(self.selected_id)[
          :2]

    if hasattr(self, 'selection_rect'):
      self.canvas.move(self.selection_rect, dx, dy)
    if hasattr(self, 'resize_handles'):
      for handle in self.resize_handles:
        self.canvas.move(handle, dx, dy)
    self.item_start_x = event.x
    self.item_start_y = event.y

  def on_resize_press(self, event):
    self.resize_start_x = event.x
    self.resize_start_y = event.y

  def on_resize_item(self, event):
    if not self.selected_id:
      return

    dx = event.x - self.resize_start_x
    dy = event.y - self.resize_start_y

    x0, y0, x1, y1 = self.canvas.bbox(self.selected_id)

    new_x0 = x0 + dx
    new_y0 = y0 + dy
    new_x1 = x1 + dx
    new_y1 = y1 + dy

    if self.selected_id in self.image_ids:
      current_index = self.image_ids.index(self.selected_id)
      self.image_data[current_index]['size'] = (
          new_x1 - new_x0, new_y1 - new_y0)

    try:
      handle_index = self.resize_handles.index(
          self.canvas.find_withtag("current")[0])
    except ValueError:
      return  # If the handle is not found, do nothing

    if handle_index == 0:  # Top-left
      new_x0, new_y0 = x0 + dx, y0 + dy
      new_x1, new_y1 = x1, y1
    elif handle_index == 1:  # Top-right
      new_x0, new_y0 = x0, y0 + dy
      new_x1, new_y1 = x1 + dx, y1
    elif handle_index == 2:  # Bottom-left
      new_x0, new_y0 = x0 + dx, y0
      new_x1, new_y1 = x1, y1 + dy
    elif handle_index == 3:  # Bottom-right
      new_x0, new_y0 = x0, y0
      new_x1, new_y1 = x1 + dx, y1 + dy
    elif handle_index == 4:  # Top-center
      new_x0, new_y0 = x0, y0 + dy
      new_x1, new_y1 = x1, y1
    elif handle_index == 5:  # Bottom-center
      new_x0, new_y0 = x0, y0
      new_x1, new_y1 = x1, y1 + dy
    elif handle_index == 6:  # Left-center
      new_x0, new_y0 = x0 + dx, y0
      new_x1, new_y1 = x1, y1
    elif handle_index == 7:  # Right-center
      new_x0, new_y0 = x0, y0
      new_x1, new_y1 = x1 + dx, y1

    new_width = int(new_x1 - new_x0)
    new_height = int(new_y1 - new_y0)
    if new_width > 0 and new_height > 0:
      if self.selected_id in self.image_ids:
        current_index = self.image_ids.index(self.selected_id)
        image = Image.open(self.settings['image_paths'][current_index])
        resized_image = image.resize(
            (new_width, new_height), Image.LANCZOS)

        self.photo = ImageTk.PhotoImage(resized_image)
        self.canvas.itemconfig(self.selected_id, image=self.photo)
        self.images[current_index] = self.photo

        self.canvas.coords(self.selected_id, new_x0, new_y0)

      elif self.selected_id in self.text_ids:
        text_content = self.canvas.itemcget(self.selected_id, "text")
        self.canvas.coords(self.selected_id, new_x0, new_y0)
        self.canvas.itemconfig(self.selected_id, width=new_width)

      if hasattr(self, 'selection_rect'):
        self.canvas.coords(self.selection_rect,
                           new_x0, new_y0, new_x1, new_y1)

      handle_coords = [
          (new_x0, new_y0),  # Top-left
          (new_x1, new_y0),  # Top-right
          (new_x0, new_y1),  # Bottom-left
          (new_x1, new_y1),  # Bottom-right
          ((new_x0 + new_x1) / 2, new_y0),  # Top-center
          ((new_x0 + new_x1) / 2, new_y1),  # Bottom-center
          (new_x0, (new_y0 + new_y1) / 2),  # Left-center
          (new_x1, (new_y0 + new_y1) / 2)   # Right-center
      ]
      for index, handle in enumerate(self.resize_handles):
        x, y = handle_coords[index]
        self.canvas.coords(handle, x - 5, y - 5, x + 5, y + 5)

    self.resize_start_x = event.x
    self.resize_start_y = event.y

  def save_text_edit(self, event):
    new_text = self.text_entry.get()
    if self.selected_id and self.selected_id in self.text_ids:
      parts = new_text.split('*')
      text_content = parts[0].strip()
      font_name = "Helvetica"  # デフォルトのフォント
      font_size = 32  # デフォルトのフォントサイズ
      if len(parts) > 1:
        try:
          font_size = int(parts[1].strip())
        except ValueError:
          pass
      if len(parts) > 2 and parts[2].strip() in self.available_fonts:
        font_name = parts[2].strip()

      # テキスト内容に改行を追加
      text_content = text_content.replace('~~', '\n')

      self.canvas.itemconfig(
          self.selected_id, text=text_content, font=(font_name, font_size))
    self.text_entry.grid_remove()

  def delete_selected_item(self):
    if self.selected_id:
      if self.selected_id in self.image_ids:
        index = self.image_ids.index(self.selected_id)
        if index < len(self.image_data):
          if self.settings.get('image_paths') and index < len(self.settings['image_paths']):
            del self.settings['image_paths'][index]  # 画像のパスを削除
          self.image_ids.remove(self.selected_id)
          self.image_data.pop(index)
          self.canvas.delete(self.selected_id)

      elif self.selected_id in self.text_ids:
        index = self.text_ids.index(self.selected_id)
        if index < len(self.text_ids):
          self.text_ids.remove(self.selected_id)
          self.canvas.delete(self.selected_id)

      self.selected_id = None
      if hasattr(self, 'selection_rect'):
        self.canvas.delete(self.selection_rect)
      if hasattr(self, 'resize_handles'):
        for handle in self.resize_handles:
          self.canvas.delete(handle)
      save_settings(self.settings)  # 設定を保存

  def on_closing(self):
    self.settings['geometry'] = self.geometry()
    self.settings['image_data'] = self.image_data

    self.settings['image_data'] = [
        {'path': image['path'], 'position': image['position'],
         'size': image['size']}
        for image in self.image_data
    ]

    text_boxes = []
    for text_id in self.text_ids:
      x, y = self.canvas.coords(text_id)
      text = self.canvas.itemcget(text_id, 'text')
      font_info = self.canvas.itemcget(text_id, 'font')

    # フォント情報の解析
    font_parts = font_info.split()
    font_name = font_parts[0]
    font_size = None
    for part in font_parts:
      if part.isdigit():
        font_size = int(part)
        break

    text_boxes.append({
        'text': text,
        'font_name': font_name,
        'font_size': font_size,
        'position': (x, y)
    })

    self.settings['text_boxes'] = text_boxes
    save_settings(self.settings)
    self.root.destroy()

    def load_code(self):
      """保存されているコードをJSONファイルから読み込む"""
      if os.path.exists(self.code_file):
        try:
          with open(self.code_file, 'r') as f:
            data = json.load(f)
            for entry in data:
              self.add_code_cell()
              cell = self.code_cells[-1]
              if "code" in entry:
                cell['code_input'].insert(
                    tk.END, entry['code'])  # コード入力部分にテキストをセット
              if "image_index" in entry:
                # 対応する画像インデックスをセット
                cell['image_index'] = entry['image_index']
        except json.JSONDecodeError as e:
          print(f"JSONのデコードエラー: {e}")
        except Exception as e:
          print(f"コードの読み込みに失敗しました: {e}")

if __name__ == "__main__":

  # Tkinterウィンドウの作成
  root = tk.Tk()

  light = "#FFFFF0"
  root.config(bg=light)
  # 画像が格納されたフォルダのパスを指定
  image_folder = "images"  # 画像フォルダのパスに変更してください

  # アプリケーションの作成
  app = SlideShowApp(root, image_folder)

  # ウィンドウを閉じるときに位置情報を保存する
  root.protocol("WM_DELETE_WINDOW", app.on_closing)

  # Tkinterのメインループ
  root.mainloop()
