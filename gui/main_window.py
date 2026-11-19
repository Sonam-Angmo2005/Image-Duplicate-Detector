import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from core.duplicate_detector import scan_folder
from utils.file_manager import get_file_size, delete_file
from utils.storage_tracker import bytes_to_mb


class ImageDuplicateDetectorDemo:

    def __init__(self, root):

        self.root = root

        self.root.title("Image Gallery Duplicate Detector - Capstone Project")
        self.root.geometry("1020x680")
        self.root.configure(bg="#F0F2F5")

        self.selected_folder = ""
        self.duplicates = {}

        self.current_preview_img = None
        self.selected_file_for_action = None

        # Storage tracker
        self.total_bytes_saved = 0

        self._build_header()
        self._build_metrics_banner()
        self._build_workspace()
        self._build_statusbar()

    # ---------------- HEADER ----------------

    def _build_header(self):

        header = tk.Frame(
            self.root,
            bg="#FFFFFF",
            bd=1,
            relief=tk.SOLID,
            padx=15,
            pady=10
        )

        header.pack(fill=tk.X, padx=15, pady=(15, 8))

        btn_browse = tk.Button(
            header,
            text="📁 Choose Image Folder",
            font=("Segoe UI", 9, "bold"),
            bg="#0288D1",
            fg="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            command=self.choose_folder
        )

        btn_browse.pack(side=tk.LEFT)

        self.lbl_path = tk.Label(
            header,
            text="No folder selected",
            font=("Segoe UI", 9, "italic"),
            fg="#616161",
            bg="#FFFFFF",
            padx=10
        )

        self.lbl_path.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.mode_var = tk.StringVar(value="md5")

        tk.Radiobutton(
            header,
            text="Exact Match (MD5)",
            variable=self.mode_var,
            value="md5",
            bg="#FFFFFF",
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=6)

        tk.Radiobutton(
            header,
            text="Perceptual (aHash)",
            variable=self.mode_var,
            value="ahash",
            bg="#FFFFFF",
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=6)

        self.btn_scan = tk.Button(
            header,
            text="⚡ Scan Duplicates",
            font=("Segoe UI", 9, "bold"),
            bg="#2E7D32",
            fg="white",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            command=self.trigger_scan
        )

        self.btn_scan.pack(side=tk.RIGHT)

    # ---------------- METRICS BANNER ----------------

    def _build_metrics_banner(self):

        self.metrics_banner = tk.Label(
            self.root,
            text="📊 Potential Reclaimable: 0.00 MB   |   🎉 Total Storage Saved: 0.00 MB",
            font=("Segoe UI", 10, "bold"),
            bg="#E8F5E9",
            fg="#1B5E20",
            relief=tk.GROOVE,
            pady=8
        )

        self.metrics_banner.pack(
            fill=tk.X,
            padx=15,
            pady=(0, 8)
        )

    # ---------------- WORKSPACE ----------------

    def _build_workspace(self):

        container = tk.Frame(
            self.root,
            bg="#F0F2F5"
        )

        container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=15,
            pady=0
        )

        # Left Column

        left_box = tk.Frame(
            container,
            bg="#FFFFFF",
            bd=1,
            relief=tk.SOLID
        )

        left_box.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=(0, 10)
        )

        tk.Label(
            left_box,
            text="Detected Duplicate Clusters",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            anchor="w",
            padx=10,
            pady=8
        ).pack(fill=tk.X)

        self.tree = ttk.Treeview(
            left_box,
            columns=("size", "path"),
            show="tree headings",
            selectmode="browse"
        )

        self.tree.heading(
            "#0",
            text="File Group & Role",
            anchor="w"
        )

        self.tree.heading(
            "size",
            text="Size",
            anchor="center"
        )

        self.tree.heading(
            "path",
            text="Disk Path",
            anchor="w"
        )

        self.tree.column("#0", width=250)
        self.tree.column("size", width=90, anchor="center")
        self.tree.column("path", width=220)

        scroll = ttk.Scrollbar(
            left_box,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scroll.set)

        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.pack(
            fill=tk.BOTH,
            expand=True,
            padx=6,
            pady=6
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_tree_select
        )

        # Right Column

        right_box = tk.Frame(
            container,
            bg="#FFFFFF",
            bd=1,
            relief=tk.SOLID,
            width=330
        )

        right_box.pack(
            side=tk.RIGHT,
            fill=tk.BOTH
        )

        right_box.pack_propagate(False)

        tk.Label(
            right_box,
            text="Visual Verification Panel",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            anchor="w",
            padx=10,
            pady=8
        ).pack(fill=tk.X)

        self.preview_box = tk.Label(
            right_box,
            text="No Image Selected\n(Select an item on the left)",
            bg="#ECEFF1",
            fg="#78909C",
            relief=tk.RIDGE,
            bd=1
        )

        self.preview_box.pack(
            fill=tk.BOTH,
            expand=True,
            padx=15,
            pady=10
        )

        self.lbl_details = tk.Label(
            right_box,
            text="Select an image from the list to view metadata.",
            font=("Segoe UI", 9),
            bg="#FFFFFF",
            fg="#37474F",
            justify=tk.LEFT,
            wraplength=290
        )

        self.lbl_details.pack(
            fill=tk.X,
            padx=15,
            pady=(0, 10)
        )

        self.btn_delete = tk.Button(
            right_box,
            text="🗑️ Delete Redundant Copy",
            font=("Segoe UI", 9, "bold"),
            bg="#D32F2F",
            fg="white",
            relief=tk.FLAT,
            state=tk.DISABLED,
            pady=8,
            command=self.delete_duplicate_file
        )

        self.btn_delete.pack(
            fill=tk.X,
            padx=15,
            pady=(0, 15)
        )

    # ---------------- STATUS BAR ----------------

    def _build_statusbar(self):

        self.status_var = tk.StringVar(
            value="Status: Ready | Select an image directory to begin."
        )

        bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg="#E0E0E0",
            fg="#424242",
            anchor="w",
            padx=10,
            pady=5
        )

        bar.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

    # ---------------- CHOOSE FOLDER ----------------

    def choose_folder(self):

        folder = filedialog.askdirectory()

        if folder:

            self.selected_folder = folder

            self.lbl_path.config(
                text=folder,
                fg="#212121"
            )

            self.status_var.set(
                f"Selected directory: {folder}"
            )

    # ---------------- START SCANNING ----------------

    def trigger_scan(self):

        if not self.selected_folder:

            messagebox.showwarning(
                "Warning",
                "Please pick an image folder first!"
            )

            return

        self.btn_scan.config(state=tk.DISABLED)

        self.status_var.set(
            "Scanning directory tree and computing hashes..."
        )

        # Capture GUI values before starting the thread
        folder = self.selected_folder
        mode = self.mode_var.get()

        threading.Thread(
            target=self._scan_thread,
            args=(folder, mode),
            daemon=True
        ).start()

    # ---------------- SCAN THREAD ----------------

    def _scan_thread(self, folder, mode):

        try:

            duplicates = scan_folder(folder, mode)

            # Update GUI through the main Tkinter thread
            self.root.after(
                0,
                lambda: self._populate_treeview(duplicates)
            )

        except Exception as err:

            self.root.after(
            0,
            lambda error=err: self._scan_failed(error)
            )
    def _scan_failed(self, err):

        self.btn_scan.config(state=tk.NORMAL)

        self.status_var.set("Scanning failed.")

        messagebox.showerror(
            "Scan Error",
            f"Unable to scan folder: {err}"
        )

    # ---------------- DISPLAY DUPLICATES ----------------

    def _populate_treeview(self, duplicates):

        self.duplicates = duplicates

        self.tree.delete(
            *self.tree.get_children()
        )

        potential_bytes = 0

        for i, (h, files) in enumerate(
            self.duplicates.items(),
            start=1
        ):

            cluster_id = self.tree.insert(
                "",
                "end",
                text=f"Duplicate Group #{i} ({len(files)} files)",
                open=True
            )

            for idx, p in enumerate(files):

                sz = get_file_size(p)

                sz_str = f"{round(sz / 1024, 1)} KB"

                if idx == 0:

                    role = "[Master/Original]"

                else:

                    role = "[Redundant Copy]"

                    potential_bytes += sz

                self.tree.insert(
                    cluster_id,
                    "end",
                    text=f"{role} {p.name}",
                    values=(sz_str, str(p)),
                    tags=(str(p), role)
                )

        # Update storage metrics

        potential_mb = bytes_to_mb(potential_bytes)

        saved_mb = bytes_to_mb(
            self.total_bytes_saved
        )

        self.metrics_banner.config(
            text=f"📊 Potential Reclaimable: {potential_mb:.2f} MB   |   🎉 Total Storage Saved: {saved_mb:.2f} MB"
        )

        self.status_var.set(
            f"Scan finished | Found {len(self.duplicates)} duplicate clusters | Reclaimable: {potential_mb:.2f} MB"
        )

        self.btn_scan.config(state=tk.NORMAL)

    # ---------------- IMAGE PREVIEW ----------------

    def on_tree_select(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        item = self.tree.item(selected[0])

        tags = item.get("tags")

        if not tags:
            return

        file_path = tags[0]
        role = tags[1]

        self.selected_file_for_action = file_path

        # Display image preview

        try:

            with Image.open(file_path) as pil_img:

                pil_img = pil_img.copy()

            pil_img.thumbnail((260, 260))

            self.current_preview_img = ImageTk.PhotoImage(
                pil_img
            )

            self.preview_box.config(
                image=self.current_preview_img,
                text=""
            )

            self.lbl_details.config(
                text=f"File: {Path(file_path).name}\n"
                     f"Type: {role}\n"
                     f"Size: {round(get_file_size(file_path) / 1024, 1)} KB\n"
                     f"Path: {file_path}"
            )

        except Exception:

            self.preview_box.config(
                image="",
                text="Preview unavailable"
            )

        # Protect the master image

        if role == "[Redundant Copy]":

            self.btn_delete.config(
                state=tk.NORMAL
            )

        else:

            self.btn_delete.config(
                state=tk.DISABLED
            )

    # ---------------- DELETE DUPLICATE ----------------

    def delete_duplicate_file(self):

        if not self.selected_file_for_action:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete this redundant copy?\n\n{self.selected_file_for_action}"
        )

        if confirm:

            try:

                freed_bytes = delete_file(
                    self.selected_file_for_action
                )

                self.total_bytes_saved += freed_bytes

                messagebox.showinfo(
                    "Success",
                    f"File deleted!\nDisk space freed: {round(freed_bytes / 1024, 1)} KB"
                )

                self.selected_file_for_action = None
                self.current_preview_img = None

                self.preview_box.config(
                    image="",
                    text="No Image Selected"
                )

                self.lbl_details.config(
                    text="Select an image from the list to view metadata."
                )

                self.btn_delete.config(
                    state=tk.DISABLED
                )

                # Scan again to update duplicate groups
                self.trigger_scan()

            except OSError as err:

                messagebox.showerror(
                    "Error",
                    f"Deletion failed: {err}"
                )