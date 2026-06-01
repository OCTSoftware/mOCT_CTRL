import subprocess
import customtkinter as ctk

from controllers.oct_controller import OctController


class RecordingFrame(ctk.CTkFrame):
    def __init__(self, parent):

        super().__init__(parent)

        self.recording_active = False

        self.set_recording_ui_parts()

        self.ctrl = OctController()

    def set_recording_ui_parts(self):
        """
        Exact old recording UI structure
        """

        self.recording_lb = ctk.CTkLabel(
            self,
            width=75,
            height=20,
            font=("Cosmic Sans MS", 18, "normal"),
            text="Record",
        )
        self.recording_lb.grid(row=1, column=1, padx=(5, 5), pady=(5, 5))

        self.f3b = ctk.CTkFrame(self, border_width=1, fg_color="transparent")
        self.f3b.grid(row=2, column=1, padx=(5, 5), pady=(0, 25), sticky="nw")

        # destination path
        self.dest_dir = ctk.CTkButton(
            self.f3b,
            width=75,
            height=20,
            text="Dest dir",
            command=lambda: self.select_path(1),
        )
        self.dest_dir.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))

        self.dest_dir_entry = ctk.CTkEntry(
            self.f3b, width=200, height=20, justify="center"
        )
        self.dest_dir_entry.grid(
            row=1, column=1, columnspan=3, padx=(5, 5), pady=(5, 5)
        )
        self.dest_dir_entry.insert(0, "")

        # recording settings
        self.nbr_of_records_lb = ctk.CTkLabel(
            self.f3b, width=50, height=20, text="Nbr Records"
        )
        self.nbr_of_records_lb.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))
        self.nbr_of_records = ctk.CTkEntry(
            self.f3b, width=50, height=20, justify="center"
        )
        self.nbr_of_records.grid(row=2, column=1, padx=(5, 5), pady=(5, 5))
        self.nbr_of_records.insert(0, "42")

        self.delay_between_rec_lb = ctk.CTkLabel(
            self.f3b, width=50, height=20, text="Delay BScans"
        )
        self.delay_between_rec_lb.grid(row=2, column=2, padx=(5, 5), pady=(5, 5))

        self.delay_between_rec = ctk.CTkEntry(
            self.f3b, width=50, height=20, justify="center"
        )
        self.delay_between_rec.grid(row=2, column=3, padx=(5, 5), pady=(5, 5))
        self.delay_between_rec.insert(0, "0")

        self.nbr_of_bscans_lb = ctk.CTkLabel(
            self.f3b, width=50, height=20, text="Nbr BScans"
        )
        self.nbr_of_bscans_lb.grid(row=3, column=0, padx=(5, 5), pady=(5, 5))

        self.nbr_of_bscans = ctk.CTkEntry(
            self.f3b, width=50, height=20, justify="center"
        )
        self.nbr_of_bscans.grid(row=3, column=1, padx=(5, 5), pady=(5, 5))
        self.nbr_of_bscans.insert(0, "100")

        # control buttons
        self.start_rec = ctk.CTkButton(
            self.f3b,
            width=75,
            height=20,
            text="Start Rec",
            command=self.start_recording,
        )
        self.start_rec.grid(row=4, column=0, padx=(5, 5), pady=(5, 5))

        self.current_record_lb = ctk.CTkLabel(
            self.f3b, width=50, height=20, text="Current Rec"
        )
        self.current_record_lb.grid(row=4, column=2, padx=(5, 5), pady=(5, 5))

        self.current_record = ctk.CTkLabel(
            self.f3b, width=50, height=20, text="0 of 42"
        )
        self.current_record.grid(row=4, column=3, padx=(5, 5), pady=(5, 5))

        self.stop_rec = ctk.CTkButton(
            self.f3b, width=75, height=20, text="Stop Rec", command=self.stop_recording
        )
        self.stop_rec.grid(row=5, column=0, padx=(5, 5), pady=(5, 5))

    # ----------------------------------------------------------
    # callbacks
    # ----------------------------------------------------------
    def select_path(self, target):

        ps_script = r"""
        Add-Type -AssemblyName System.Windows.Forms
        $f = New-Object System.Windows.Forms.FolderBrowserDialog
        $f.ShowNewFolderButton = $true

        if ($f.ShowDialog() -eq 'OK') {
            Write-Output $f.SelectedPath
        }
        """

        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
        )

        path = result.stdout.strip()

        if not path:
            return

        elif target == 1:
            self.dest_dir_entry.delete(0, "end")
            self.dest_dir_entry.insert(0, path)

    def start_recording(self):

        self.recording_active = True

        dest_dir = self.dest_dir_entry.get()
        total = int(self.nbr_of_records.get())
        delay = float(self.delay_between_rec.get())
        bscans = int(self.nbr_of_bscans.get())

        self.current_record.configure(text=f"1 of {total}")

        self.ctrl.start_recording(
            dest_dir=dest_dir,
            nbr_of_records=total,
            delay_between_rec=delay,
            nbr_of_bscans=bscans,
        )

    def stop_recording(self):

        self.recording_active = False

        self.ctrl.stop_recording()

        self.current_record.configure(text="stopped")
