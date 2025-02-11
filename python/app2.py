import sys
from PyQt5 import QtWidgets, QtCore

# A default configuration dictionary for simulation widgets.
# Each key defines a unique widget name, and its value defines properties and type.
DEFAULT_WIDGET_CONFIG = {
    "injectionAmplitude": {
        "widget_type": "QDoubleSpinBox",
        "label": "Injection Amplitude",
        "min": 0.0,
        "max": 100.0,
        "default": 10.0,
        "step": 0.1
    },
    "simulationTime": {
        "widget_type": "QSpinBox",
        "label": "Simulation Time (ms)",
        "min": 0,
        "max": 10000,
        "default": 1000,
        "step": 10
    },
    # Add additional widget configurations as needed.
}

class App(QtWidgets.QMainWindow):
    def __init__(self, widget_config=None, parent=None):
        super(App, self).__init__(parent)
        # Use the provided widget configuration or fall back to the default.
        self.widget_config = widget_config if widget_config is not None else DEFAULT_WIDGET_CONFIG
        
        # Dictionary to hold references to created widgets
        self.widgets = {}
        self.initUI()

    def initUI(self):
        """Set up the main UI elements dynamically based on the widget config."""
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(central_widget)

        # Dynamically create UI elements from the configuration
        for key, config in self.widget_config.items():
            widget = self.create_widget(config)
            label = config.get("label", key)
            self.add_widget(label, widget)
            self.widgets[key] = widget

        # Example: add a button to trigger simulation
        self.run_button = QtWidgets.QPushButton("Run Simulation")
        self.run_button.clicked.connect(self.run_simulation)
        self.main_layout.addWidget(self.run_button)

    def create_widget(self, config):
        """Factory method to create a widget based on its configuration."""
        widget_type = config.get("widget_type", "QWidget")
        widget_class = getattr(QtWidgets, widget_type, QtWidgets.QWidget)
        widget = widget_class()

        # Customize properties for spin boxes
        if widget_type in ["QSpinBox", "QDoubleSpinBox"]:
            widget.setMinimum(config.get("min", 0))
            widget.setMaximum(config.get("max", 100))
            widget.setValue(config.get("default", 0))
            step = config.get("step", 1)
            widget.setSingleStep(step)
        
        # Extend this method to handle more widget types as needed.
        return widget

    def add_widget(self, label_text, widget):
        """Helper method to add a labeled widget to the main layout."""
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(label_text)
        layout.addWidget(label)
        layout.addWidget(widget)
        self.main_layout.addLayout(layout)

    def run_simulation(self):
        """
        Access widget values dynamically from the self.widgets dictionary.
        This example retrieves the injection amplitude and simulation time,
        then prints them. Replace this with your actual simulation call.
        """
        injection_amplitude = self.widgets.get("injectionAmplitude").value() \
            if "injectionAmplitude" in self.widgets else None
        simulation_time = self.widgets.get("simulationTime").value() \
            if "simulationTime" in self.widgets else None

        print("Running simulation with parameters:")
        print("Injection Amplitude:", injection_amplitude)
        print("Simulation Time:", simulation_time)
        # Insert your simulation function call here

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = App()  # You can pass a custom widget_config here if needed.
    window.show()
    sys.exit(app.exec_())
