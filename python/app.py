# app.py
import sys
import matplotlib
from helpers.timer import Timer

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QFormLayout, QDoubleSpinBox, QSlider, QSizePolicy
)
import qdarktheme

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QGuiApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from model import Model  # Import the Model class from model.py

class App(QMainWindow):
    def __init__(self, dark_mode=True):
        if dark_mode:
            qdarktheme.setup_theme()
        super().__init__()
        self.setWindowTitle("Real-Time Hodgkin–Huxley Simulation")
        self.setGeometry(100, 100, 1280, 1080)

        # --- Main Layout ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Controls Panel ---
        controls_widget = QWidget()
        controls_widget.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; }")
        controls_layout = QHBoxLayout(controls_widget)
        
        self.slow_mode = False
        self.slow_mode_multiplier = 5


        # Parameter Controls
        form_layout = QFormLayout()
        self.injectionAmplitudeSpinBox = self._create_spinbox_(text="Injection Amplitude (µA/cm²):",
                                                               suffix='ms',
                                                               style='font-size: 16px;',
                                                               layout=form_layout, 
                                                               range=(-1000.0, 1000.0),
                                                               decimals=2, 
                                                               default_value=10.0)

        self.injectionDurationSpinBox = self._create_spinbox_(text="Injection Duration (ms):",
                                                                suffix='ms',
                                                                style='font-size: 16px;',
                                                                layout=form_layout, 
                                                                range=(0.0, 1000.0),
                                                                decimals=2, 
                                                                default_value=1.0)

        self.windowSlider = self._create_slider_(text="Plot Window (ms):",
                                                    callback=self.update_window_size,
                                                    style='font-size: 16px;',
                                                    range=(10, 50000),
                                                    default_value=10000,
                                                    tick_interval=1000,
                                                    orientation=Qt.Horizontal,
                                                    layout=form_layout)
        controls_layout.addLayout(form_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        
        # self.slow_mode_button = self._create_button_( text="Slow Mode: OFF", parent=self, enabled=True, callback=self.toggle_slow_mode, layout=buttons_layout)

        self.inject_button = self._create_button_(text="Inject Current", parent=self, enabled=True, callback=self.inject_current, layout=buttons_layout)

        self.inject_and_pause_button = self._create_button_(text="Inject and Pause", parent=self, enabled=True, callback=self.inject_and_pause, layout=buttons_layout)

        self.pause_button = self._create_button_(text="Pause", parent=self, enabled=True, callback=self.toggle_pause, layout=buttons_layout)
        
        self.reset_button = self._create_button_(text="Reset view", parent=self, enabled=True, callback=self.reset_view, layout=buttons_layout)
        
        self.dbg_button = self._create_button_(text="Debug", parent=self, enabled=True, callback=self._debug_button_callback_, layout=buttons_layout)

        buttons_layout.addStretch(1)
        controls_layout.addLayout(buttons_layout)
        main_layout.addWidget(controls_widget, 0)

        # --- Plot Canvas ---
        self.canvas = FigureCanvas(plt.Figure(figsize=(8, 6)))
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.canvas, 1)
        self.ax = self.canvas.figure.subplots()
        # Plot text is not bold.
        self.ax.set_xlabel("Time (ms)", fontsize=16)
        self.ax.set_ylabel("Membrane Potential (mV)", fontsize=16)
        self.ax.set_title("Hodgkin–Huxley Real-Time Simulation", fontsize=18)
        self.ax.grid(True)
        self.ax.set_ylim(-90, 60)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)

        # --- Simulation State ---
        self.model = Model()  # Create an instance of the Model class
        self.sim_time = 0.0
        self.dt = 0.025 # ~75-85 fps with 0.025 ms | 0.05ms ~ 160-170 fps | 0.01 ~ 30 fps
        self.times = []
        self.Vs = []

        self.injection_amplitude = 10.0
        self.injection_duration = 1.0
        self.injection_end_time = 0.0

        self.window_size_ms = self.windowSlider.value()
        self.auto_zoom = True

        self.plot_sampling = 10
        self.simulation_counter = 0
        self.plot_update_interval = 50
        self.last_plot_update_time = 0.0

        self.line, = self.ax.plot([], [], color='b', lw=1.5)

        self.timer_interval = 20  # ms
        self.timer = QTimer()
        self.timer.setInterval(self.timer_interval)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start()

        self.pause_when_steady = False
        self.buttons = None
        
    def _debug_button_callback_(self):
        print("Debug button clicked")
    
    def _create_slider_(self,
                        text='DefaultText', 
                        callback=None, 
                        style='font-size: 16px;',
                        range=(0,10),
                        tick_interval=1000, 
                        default_value=10000,
                        orientation=Qt.Horizontal, 
                        parent=None,
                        layout=None)->QSlider:
        
        if parent is None: 
            parent = self
        
        slider = QSlider(orientation, parent)
        slider.setRange(range[0], range[1])
        slider.setValue(default_value)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(tick_interval)
        slider.setStyleSheet(style)
        if callback: 
            slider.valueChanged.connect(self.update_window_size)
        if layout: 
            layout.addRow("Plot Window (ms):", slider)
        
        return slider
        
    def _create_button_(self, 
                         text="DefaultBtn", 
                         callback=None, 
                         style="font-size: 16px; font-weight: bold;", 
                         enabled=True, 
                         parent=None,
                         min_height=40,
                         layout=None)->QPushButton:
        if parent is None:
            parent = self
        btn = QPushButton(text, parent)
        btn.setEnabled(enabled)
        btn.setStyleSheet(style)
            
        if callback is None: 
            raise ValueError("callback must be a function")
        btn.clicked.connect(callback)
        btn.setMinimumHeight(min_height)
        if layout is not None:
            layout.addWidget(btn)
        return btn

    def _create_spinbox_(self,
                         text="DefaultSpinBox",
                         callback=None,
                         style="font-size: 16px; font-weight: bold;",
                         suffix="",
                         enabled=True,
                         parent=None,
                         min_height=40,
                         layout=None, 
                         range = (0,100), 
                         decimals=2, 
                         default_value=10)->QDoubleSpinBox:
        if parent is None:
            parent = self
        
        spinbox = QDoubleSpinBox(parent)
        spinbox.setRange(range[0], range[1])
        spinbox.setDecimals(decimals)
        spinbox.setSuffix(suffix)
        spinbox.setValue(default_value)
        spinbox.setStyleSheet(style)
        if layout is not None:
            layout.addRow(text, spinbox)
        
        return spinbox
        
    def  _init_buttons_(self, bdict:dict=None):
        if not isinstance(bdict, dict):
            raise ValueError("button_dic must be a dictionary")
        for key, value in bdict.items():
            return
   
    def update_window_size(self, value):
        self.window_size_ms = value
        self.auto_zoom = True
        if self.sim_time > self.window_size_ms:
            self.ax.set_xlim(self.sim_time - self.window_size_ms, self.sim_time)
        else:
            self.ax.set_xlim(0, self.window_size_ms)
        self.canvas.draw_idle()

    def on_scroll(self, event):
        if hasattr(event, 'guiEvent') and event.guiEvent is not None:
            modifiers = event.guiEvent.modifiers()
        else:
            modifiers = QGuiApplication.keyboardModifiers()

        if modifiers & Qt.ControlModifier:
            if event.button == 'up':
                zoom_factor = 0.9
            elif event.button == 'down':
                zoom_factor = 1.1
            else:
                return
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            xdata = event.xdata
            ydata = event.ydata
            if xdata is None or ydata is None:
                return
            current_width = xlim[1] - xlim[0]
            new_width = current_width * zoom_factor
            rel_x = (xdata - xlim[0]) / current_width
            new_xlim_left = xdata - new_width * rel_x
            new_xlim_right = new_xlim_left + new_width
            current_height = ylim[1] - ylim[0]
            new_height = current_height * zoom_factor
            rel_y = (ydata - ylim[0]) / current_height
            new_ylim_bottom = ydata - new_height * rel_y
            new_ylim_top = new_ylim_bottom + new_height
            self.ax.set_xlim(new_xlim_left, new_xlim_right)
            self.ax.set_ylim(new_ylim_bottom, new_ylim_top)
            self.canvas.draw_idle()
            self.auto_zoom = False
            new_x_width = self.ax.get_xlim()[1] - self.ax.get_xlim()[0]
            self.windowSlider.blockSignals(True)
            self.windowSlider.setValue(int(new_x_width))
            self.windowSlider.blockSignals(False)
        elif modifiers & Qt.ShiftModifier:
            current_xlim = self.ax.get_xlim()
            width = current_xlim[1] - current_xlim[0]
            pan_amount = width * 0.1
            if event.button == 'up':
                new_xlim = (current_xlim[0] + pan_amount, current_xlim[1] + pan_amount)
            elif event.button == 'down':
                new_xlim = (current_xlim[0] - pan_amount, current_xlim[1] - pan_amount)
            else:
                return
            self.ax.set_xlim(new_xlim)
            self.canvas.draw_idle()
            self.auto_zoom = False
            new_x_width = self.ax.get_xlim()[1] - self.ax.get_xlim()[0]
            self.windowSlider.blockSignals(True)
            self.windowSlider.setValue(int(new_x_width))
            self.windowSlider.blockSignals(False)
        elif modifiers & Qt.AltModifier:
            current_ylim = self.ax.get_ylim()
            height = current_ylim[1] - current_ylim[0]
            pan_amount = height * 0.1
            if event.button == 'up':
                new_ylim = (current_ylim[0] + pan_amount, current_ylim[1] + pan_amount)
            elif event.button == 'down':
                new_ylim = (current_ylim[0] - pan_amount, current_ylim[1] - pan_amount)
            else:
                return
            self.ax.set_ylim(new_ylim)
            self.canvas.draw_idle()
            self.auto_zoom = False
        else:
            return

    def reset_view(self):
        if self.sim_time > self.window_size_ms:
            self.ax.set_xlim(self.sim_time - self.window_size_ms, self.sim_time)
        else:
            self.ax.set_xlim(0, self.window_size_ms)
        self.ax.set_ylim(-90, 60)
        self.canvas.draw_idle()
        self.auto_zoom = True

    def external_current(self, t):
        return self.injection_amplitude if t < self.injection_end_time else 0.0

    def inject_current(self):
        self.injection_amplitude = self.injectionAmplitudeSpinBox.value()
        self.injection_duration = self.injectionDurationSpinBox.value()
        self.injection_end_time = self.sim_time + self.injection_duration

    def inject_and_pause(self):
        """
        Injects current and then sets a flag so that when the AP reaches steady state—
        defined as less than 1 mV variation over the last 20 ms—the simulation automatically pauses.
        """
        self.inject_current()
        self.pause_when_steady = True

    def toggle_slow_mode(self):
        """Toggle the slow mode flag and update button text."""
        self.slow_mode = not self.slow_mode
        if self.slow_mode:
            self.slow_mode_button.setText("Slow Mode: ON")
        else:
            self.slow_mode_button.setText("Slow Mode: OFF")
    
    def toggle_pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setText("Resume")
            self.inject_button.setEnabled(False)
            self.inject_and_pause_button.setEnabled(False)
        else:
            self.timer.start()
            self.pause_button.setText("Pause")
            self.inject_button.setEnabled(True)
            self.inject_and_pause_button.setEnabled(True)
            self.pause_when_steady = False
    
    def update_simulation(self):
        timer_update = Timer(text="Outer update")
        steps = int(self.timer_interval / self.dt)
        for _ in range(steps):
            I_ext = self.external_current(self.sim_time)
            self.model.step(self.dt, I_ext)
            self.sim_time += self.dt
            self.simulation_counter += 1  
            if self.simulation_counter % self.plot_sampling == 0:
                self.times.append(self.sim_time)
                self.Vs.append(self.model.V)
        if self.auto_zoom:
            if self.sim_time > self.window_size_ms:
                self.ax.set_xlim(self.sim_time - self.window_size_ms, self.sim_time)
            else:
                self.ax.set_xlim(0, self.window_size_ms)
        else:
            current_xlim = self.ax.get_xlim()
            if self.sim_time > current_xlim[1]:
                width = current_xlim[1] - current_xlim[0]
                self.ax.set_xlim(self.sim_time - width, self.sim_time)
        self.line.set_data(self.times, self.Vs)
        self.canvas.draw_idle()
        self.last_plot_update_time = self.sim_time

        # If the "Inject and Pause" flag is set, check for steady state. after 20ms
        if self.pause_when_steady and len(self.Vs) >= 20*100:
            recent_V = self.Vs[-200:]
            if max(recent_V) - min(recent_V) < 1.0:
                self.toggle_pause()
                self.pause_when_steady = False
                
        print(f'fps: {(1/timer_update.get_elapsed()):0.4}')
                
if __name__ == '__main__':
    # This block is not used when imported by main.py.
    # qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    import qdarktheme
    window = App()
    window.show()
    sys.exit(app.exec_())
