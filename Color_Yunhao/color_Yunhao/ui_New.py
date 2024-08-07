import tkinter as tk
from tkinter import Frame, Label, Entry, Button, Radiobutton, StringVar
import threading
import time
from tkinter import messagebox
from os import path
from camera import Camera

TICK_RATE_FPS = 70  # Update rate in milliseconds
TICK_RATE_MS = int(1000 / TICK_RATE_FPS)


class MainFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.setup_ui()

    def setup_ui(self):
        self.setup_camera()

    def setup_camera(self):
        self.camera_label = Label(self, text="Camera")
        self.camera_label.grid(sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


class CreateExperiment(Frame):
    def __init__(self, parent):
        super().__init__(parent, padx=10, pady=10)
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.setup_grid()

    def create_widgets(self):
        self.bacteria_label = Label(self, text="Bacteria Name:")
        self.bacteria_entry = Entry(self)
        self.antibiotic_label = Label(self, text="Antibiotic Type:")
        self.antibiotic_entry = Entry(self)
        self.dosage_label = Label(self, text="Dosage:")
        self.dosage_entry = Entry(self)
        self.create_experiment_button = Button(self, text="Create Experiment")

        

        self.bacteria_label.grid(row=0, column=0, sticky="e")
        self.bacteria_entry.grid(row=0, column=1, columnspan=2)
        self.antibiotic_label.grid(row=1, column=0, sticky="e")
        self.antibiotic_entry.grid(row=1, column=1, columnspan=2)
        self.dosage_label.grid(row=2, column=0, sticky="e")
        self.dosage_entry.grid(row=2, column=1, columnspan=2)
        self.create_experiment_button.grid(row=3, column=0, columnspan=3)

    def setup_grid(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


class ControlsFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, padx=10, pady=10)
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.setup_grid()

    def create_widgets(self):
        button_width = 20
        self.camera_title = Label(self, text="Camera Settings", pady=20)
        self.focus_in_button = Button(self, text="Focus In (Up)",width=button_width)
        self.focus_out_button = Button(self, text="Focus Out (Down)",width=button_width)

        self.start_test_button = Button(self, text="Start Test", width=button_width, command=self.start_test,)
        self.stop_test_button = Button(self, text="Stop Test",width=button_width, command=self.stop_test, state=tk.DISABLED)

        # 添加用于显示结果的标签
        self.result_label = Label(self, text="Result: Waiting...", bg='gray', fg='white', font=('Arial', 14))
    

    def start_test(self):
        # 启动测试逻辑
        self.start_test_button.config(state=tk.DISABLED)
        self.stop_test_button.config(state=tk.NORMAL)
        # 假设可以在这里设置结果
        self.result_label.config(text="Result: Testing...", bg='blue')
        print("Test started...")  # 测试开始的逻辑

    def stop_test(self):
        # 停止测试逻辑
        self.start_test_button.config(state=tk.NORMAL)
        self.stop_test_button.config(state=tk.DISABLED)
        # 模拟测试结果
        self.result_label.config(text="Result: Positive", bg='green')
        print("Test stopped.")  # 测试停止的逻辑

    def setup_grid(self):
        #self.grid_rowconfigure(0, weight=1)
        #self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  # 第一列
        self.grid_columnconfigure(1, weight=1)  # 第二列（可能用于保持布局均衡）
        self.grid_columnconfigure(2, weight=1)  # 第三列
        # Camera
        self.camera_title.grid(row=4, column=0, columnspan=3)
        self.focus_in_button.grid(row=5, column=0, columnspan=1)
        self.focus_out_button.grid(row=5, column=2, columnspan=1)
    
        # Buttons to start and stop the test
        self.start_test_button.grid(row=1, column=0, columnspan=1, sticky="ew")
        self.stop_test_button.grid(row=1, column=2, columnspan=1, sticky="ew")  

        self.result_label.grid(row=6, column=0, columnspan=3, sticky="ew")  # 将结果标签放置在下方


class ControlPanel(Frame):
    def __init__(self, parent):
        super().__init__(parent, padx=10, pady=10)
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.configure_grid()

    def create_widgets(self):
        self.create_buttons()
        self.controls = ControlsFrame(self)
        self.create_experiment_frame = CreateExperiment(self)

    def create_buttons(self):
        
        self.record_button = Button(self, text="Start Recording")
        self.custom_routine_button = Button(self, text="Start Custom Routine")
    
    
         

    def configure_grid(self):
        self.create_experiment_frame.grid(row=1, column=1, sticky="ns")
        self.controls.grid(row=2, column=1, sticky="ns")
        self.record_button.grid(row=4, column=1, columnspan=2, sticky="ew")
        self.custom_routine_button.grid(row=5, column=1, columnspan=2, sticky="ew")
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Automated Paper Test Reader")
        self.geometry("800x600")
        self.camera = Camera("other", fps=TICK_RATE_FPS)
        self.recording = False
        self.setup_frames()
        self.bind("<KeyPress>", self.on_keypress)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.configure_ui()
        self.image_ref = None  # Keep a reference to the image

    def get_image_path(self, timestamp):
        return path.abspath(path.join(self.experiment.images_path, f"{timestamp}.tiff"))

    def setup_frames(self):
        self.main_frame = MainFrame(self)
        self.control_panel = ControlPanel(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.control_panel.grid(row=0, column=1, sticky="ns")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

    def configure_ui(self):
        self.control_panel.create_experiment_frame.create_experiment_button.config(
            command=self.create_experiment
        )
        self.control_panel.controls.focus_in_button.config(command=self.focus_in)
        self.control_panel.controls.focus_out_button.config(command=self.focus_out)
        
        self.control_panel.record_button.config(command=self.start_recording)
        

        self.after(TICK_RATE_MS, self.tick)  # Adjust to match the desired FPS


    def create_experiment(self):
        create_experiment = self.control_panel.create_experiment_frame
        bacteria_name = create_experiment.bacteria_entry.get()
        antibiotic = create_experiment.antibiotic_entry.get()
        dosage = create_experiment.dosage_entry.get()

        if bacteria_name and antibiotic and dosage:
            
            self.title(self.experiment.folder_name)
            self.experiment.log_event("Experiment created", "Initial setup complete")
            self.control_panel.create_experiment_frame.grid_remove()
        else:
            messagebox.showerror(
                "Error",
                "Please enter the Bacteria Name, Antibiotic Type, and Dosage to create an experiment.",
            )

    def quit_application(self):
        self.quit()

    def on_keypress(self, event):
        if event.keysym == "q":
            self.quit_application()
        elif event.keysym == "Up":
            self.focus_in()
        elif event.keysym == "Down":
            self.focus_out()

    def on_closing(self):
        self.stop_event.set()  # Signal all threads to stop
        if not self.camera.save_queue.empty():
            messagebox.showinfo(
                "Saving Images",
                "Please wait while the images are saved. Do not close the application.",
            )
        while not self.camera.save_queue.empty():
            time.sleep(0.1)
        self.camera.release()
        self.destroy()

    def focus_in(self):
        if self.flow_controller:
            self.flow_controller.focus_in(1)

    def focus_out(self):
        if self.flow_controller:
            self.flow_controller.focus_out(1)

    def start_test(self):
        if not hasattr(self, "experiment"):
            messagebox.showerror(
                "Error", 
                "Please set up an experiment before starting the test."
            )
            return

       # 假设需要特定的设置来启动测试，比如开始记录或启动某些传感器
        self.camera.start_recording(self.experiment.images_path)
        self.recording = True
        self.experiment.log_event("Test started", "Data recording has started.")
        print("Test started...")  # 在控制台输出测试开始的信息
        self.control_panel.record_button.config(text="Stop Test", command=self.stop_test)


    def stop_test(self):
        self.recording = False
        self.camera.stop_recording()
        if hasattr(self, "experiment"):
           self.experiment.log_event("Test stopped", "Data recording has stopped.")
           print("Test stopped.")  # 在控制台输出测试停止的信息
        self.control_panel.record_button.config(text="Start Test", command=self.start_test)


    def start_recording(self):
        if not hasattr(self, "experiment"):
            messagebox.showerror(
                "Error",
                "Please create an experiment before starting the recording.",
            )
            return
        self.camera.start_recording(self.experiment.images_path)
        self.recording = True
        self.experiment.log_event("Recording started", "Data recording has started.")
        self.control_panel.record_button.config(
            text="Stop Recording", command=self.stop_recording
        )

    def stop_recording(self):
        self.recording = False
        self.camera.stop_recording()
        if hasattr(self, "experiment"):
            self.experiment.log_event(
                "Recording stopped", "Data recording has stopped."
            )
        self.control_panel.record_button.config(
            text="Start Recording", command=self.start_recording
        )



    def tick(self):
        width = self.winfo_width() - self.control_panel.winfo_width()
        frame, timestamp = self.camera.get_latest_frame(width=width)
        mode = self.control_panel.controls.pump_mode.get()
        pressure = 0
        flow = 0
        self.control_panel.controls.frames_to_save.config(
            text=f"{self.camera.save_queue.qsize()}"
        )
        if self.recording:
            self.experiment.log_data(timestamp, pressure, flow, mode)
            
        if frame:
            self.image_ref = frame  # Update the stored image reference
            self.main_frame.camera_label.configure(
                image=self.image_ref,
                width=width,
                height=self.winfo_height(),
            )
        if not self.stop_event.is_set():
            self.after(TICK_RATE_MS, self.tick)  # Re-schedule the update


if __name__ == "__main__":
    app = Application()
    app.mainloop()
