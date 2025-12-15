"""Logs the temperature of a Photometer to a file."""
from datetime import datetime
from pathlib import Path

from msl.equipment import Config
from msl.qt import QtWidgets, SpinBox, DoubleSpinBox, application, Button, QtCore, Signal, prompt, DEGREE_C
from msl.qt.convert import to_qfont


class PT104(QtCore.QObject):

    text = Signal(str)

    def __init__(self, pt104):
        super().__init__()
        self.pt104 = pt104
        self.file = None
        self._channel = -1

    def set_channel(self, channel):
        self._channel = channel
        self.pt104.set_channel(channel, self.pt104.DataType.PT100, 4)

    def read(self):
        with self.file.open("a") as f:
            now = datetime.now().replace(microsecond=0)
            temperature = self.pt104.get_value(self._channel) * 1e-3
            f.write(f"{now},{temperature}\n")
            self.text.emit(f"{now.strftime('%H:%M:%S')}    {temperature:.3f} {DEGREE_C}")


class Parameters(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        cfg = Config(Path("~/photons.xml").expanduser())
        self.pt104 = PT104(cfg.database().equipment["pt104-yy"].connect())
        self.pt104.text.connect(self.on_read)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.pt104.read)

        self.channel = SpinBox(minimum=1, maximum=4)
        self.sleep = DoubleSpinBox(minimum=0.01, maximum=100, value=1)
        self.start = Button(text="Start", left_click=self.on_start, icon='ieframe|101')
        self.abort = Button(text="Abort", left_click=self.on_abort, icon='shell32|27')
        self.text = QtWidgets.QTextEdit()

        form = QtWidgets.QFormLayout()
        form.addRow("Channel:", self.channel)
        form.addRow("Duration between readings (s):", self.sleep)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(self.start)
        buttons.addWidget(self.abort)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.text)
        layout.addLayout(buttons)
        self.setLayout(layout)

        self.setWindowTitle("Photometer Temperature Logger")
        self.setMinimumWidth(340)

    def on_start(self):
        channel = self.channel.value()

        now = datetime.now()
        directory = Path("D:/DATA") / now.strftime('%Y/%m/%d')
        directory.mkdir(parents=True, exist_ok=True)
        file = directory / f"photometer_temperature_{now.strftime('%H%M%S')}.csv"
        file.write_text(f"Channel={channel}\nTimestamp,Temperature\n")

        self.pt104.file = file
        self.pt104.set_channel(channel)

        self.text.clear()
        self.start.setEnabled(False)
        self.channel.setEnabled(False)
        self.sleep.setEnabled(False)
        self.timer.start(int(self.sleep.value()*1000))

    def on_abort(self):
        self.timer.stop()
        self.start.setEnabled(True)
        self.channel.setEnabled(True)
        self.sleep.setEnabled(True)
        if self.pt104.file is not None:
            prompt.information(f"Saved to\n{self.pt104.file}")
        self.pt104.file = None

    def on_read(self, text):
        self.text.append(text)

if __name__ == "__main__":
    app = application()
    app.setFont(to_qfont("Segoe UI", 12))
    try:
        p = Parameters()
    except Exception as e:
        import traceback, sys
        tb = ''.join(traceback.format_exception(*sys.exc_info()))
        input(f"{tb}\n\nPress ENTER to exit...")
    else:
        p.show()
        app.exec()
