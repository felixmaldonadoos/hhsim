# app.py
import sys
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QFormLayout, QDoubleSpinBox, QSlider, QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QGuiApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from model import Model  # Import the Model class from model.py

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Hodgkin–Huxley Simulation")
        self.setGeometry(100, 100, 800, 600)

        # --- Main Layout ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Controls Panel ---
        controls_widget = QWidget()
        controls_widget.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; }")
        controls_layout = QHBoxLayout(controls_widget)

        # Parameter Controls
        form_layout = QFormLayout()
        self.injectionAmplitudeSpinBox = QDoubleSpinBox(self)
        self.injectionAmplitudeSpinBox.setRange(-1000.0, 1000.0)
        self.injectionAmplitudeSpinBox.setDecimals(2)
        self.injectionAmplitudeSpinBox.setValue(10.0)
        self.injectionAmplitudeSpinBox.setStyleSheet("font-size: 16px;")
        form_layout.addRow("Injection Amplitude (µA/cm²):", self.injectionAmplitudeSpinBox)

        self.injectionDurationSpinBox = QDoubleSpinBox(self)
        self.injectionDurationSpinBox.setRange(0.0, 1000.0)
        self.injectionDurationSpinBox.setDecimals(2)
        self.injectionDurationSpinBox.setSuffix(" ms")
        self.injectionDurationSpinBox.setValue(1.0)
        self.injectionDurationSpinBox.setStyleSheet("font-size: 16px;")
        form_layout.addRow("Injection Duration (ms):", self.injectionDurationSpinBox)

        self.windowSlider = QSlider(Qt.Horizontal, self)
        self.windowSlider.setRange(10, 50000)
        self.windowSlider.setValue(10000)
        self.windowSlider.setTickPosition(QSlider.TicksBelow)
        self.windowSlider.setTickInterval(1000)
        self.windowSlider.valueChanged.connect(self.update_window_size)
        self.windowSlider.setStyleSheet("font-size: 16px;")
        form_layout.addRow("Plot Window (ms):", self.windowSlider)

        controls_layout.addLayout(form_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()
        self.inject_button = QPushButton("Inject Current", self)
        self.inject_button.clicked.connect(self.inject_current)
        self.inject_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.inject_button.setMinimumHeight(40)
        buttons_layout.addWidget(self.inject_button)

        self.inject_and_pause_button = QPushButton("Inject and Pause", self)
        self.inject_and_pause_button.clicked.connect(self.inject_and_pause)
        self.inject_and_pause_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.inject_and_pause_button.setMinimumHeight(40)
        buttons_layout.addWidget(self.inject_and_pause_button)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.pause_button.setMinimumHeight(40)
        buttons_layout.addWidget(self.pause_button)

        self.reset_button = QPushButton("Reset view", self)
        self.reset_button.clicked.connect(self.reset_view)
        self.reset_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.reset_button.setMinimumHeight(40)
        buttons_layout.addWidget(self.reset_button)

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
        self.dt = 0.01
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

        # Flag used for the "Inject and Pause" functionality.
        # Here, we pause automatically when the AP reaches a steady state
        # (i.e. when the voltage variation over the last 20 ms is less than 1 mV).
        self.pause_when_steady = False

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

        # If the "Inject and Pause" flag is set, check for steady state.
        # (20 ms corresponds to about 200 plotted points if plot_sampling is 10.)
        if self.pause_when_steady and len(self.Vs) >= 200:
            recent_V = self.Vs[-200:]
            if max(recent_V) - min(recent_V) < 1.0:
                self.toggle_pause()
                self.pause_when_steady = False

if __name__ == '__main__':
    # This block is not used when imported by main.py.
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
