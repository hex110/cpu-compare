import sys
import re
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QCompleter  # <-- Add QCompleter here
from PySide6.QtCore import Qt, QEvent
import qdarktheme

class SearchableComboBox(QWidget):
    def __init__(self, options, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.line_edit = QLineEdit(self)
        self.list_widget = QListWidget(self)

        # Set up the completer to show the filtered CPU names in the list widget
        self.completer = QCompleter(options, self)
        self.completer.setFilterMode(Qt.MatchContains)  # Filter options by containing text
        self.completer.setCompletionMode(QCompleter.PopupCompletion)  # Only show completion when there's something to complete
        self.line_edit.setCompleter(self.completer)

        layout.addWidget(self.line_edit)
        layout.addWidget(self.list_widget)

        # Hide the list widget and set its size
        self.list_widget.hide()
        self.list_widget.setMaximumHeight(self.line_edit.height() * 4)  # Adjust the maximum height as needed

        # Set the same font for the line edit as the entry boxes
        font = self.line_edit.font()
        font.setPointSize(int(font.pointSize() * 1.75))
        self.line_edit.setFont(font)

        # Connect signals for filtering the list based on the line edit's text
        self.line_edit.textChanged.connect(self.filter_list)
        self.line_edit.installEventFilter(self)

        # Connect signal for item selection
        self.list_widget.itemClicked.connect(self.on_item_selected)

    def eventFilter(self, obj, event):
        if obj == self.line_edit and event.type() == QEvent.FocusIn:
            # Show the list widget when the line edit gets focus
            self.list_widget.show()
        return super().eventFilter(obj, event)

    def filter_list(self, text):
        self.list_widget.clear()
        if text:
            filtered_items = [item for item in self.completer.model().stringList() if text.lower() in item.lower()]
            self.list_widget.addItems(filtered_items)
            self.list_widget.setCurrentRow(0)

    def on_item_selected(self, item):
        self.line_edit.setText(item.text())
        self.list_widget.hide()

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CPU Compare')
        self.setGeometry(100, 100, 1280, 720)

        # Center the window on the screen
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QHBoxLayout(self.central_widget)

        # Table Widget to display CPU names and scores
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["CPU Name", "Score"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_widget)

        # Increase font size for the table widget
        font = self.table_widget.font()
        font.setPointSize(int(font.pointSize() * 1.75))
        self.table_widget.setFont(font)

        # Set selection mode to SingleSelection to allow only one item to be selected
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)

        # Load CPU data from file and populate the table
        self.populate_table("cpu_ranking.txt")

        # CPU Score Display Widget
        self.score_display = QLabel(self)
        self.score_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.score_display)

        # Right-side layout for CPU details, score input, and button
        right_layout = QVBoxLayout()

        self.cpu_name_label = QLabel(self)
        self.cpu_name_label.setStyleSheet("font-size: 20px;")  # Increase font size for labels
        right_layout.addWidget(self.cpu_name_label)

        self.cpu_score_label = QLabel(self)
        self.cpu_score_label.setStyleSheet("font-size: 20px;")  # Increase font size for labels
        right_layout.addWidget(self.cpu_score_label)

        # Create the searchable combo boxes for CPU selection
        cpu_names = [self.table_widget.item(row, 0).text() for row in range(self.table_widget.rowCount())]
        self.cpu_combobox1 = SearchableComboBox(cpu_names, self)
        self.cpu_combobox2 = SearchableComboBox(cpu_names, self)

        right_layout.addWidget(self.cpu_combobox1)
        right_layout.addWidget(self.cpu_combobox2)

        # Increase font size for the button
        self.compare_button = QPushButton("Compare Scores", self)
        self.compare_button.setStyleSheet("font-size: 20px;")
        right_layout.addWidget(self.compare_button)

        right_layout.addStretch()

        # Add splitter to allow resizing
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.table_widget)
        splitter.addWidget(self.score_display)

        right_widget = QWidget(self)
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        layout.addWidget(splitter)

        self.table_widget.itemClicked.connect(self.show_cpu_score)
        self.table_widget.itemDoubleClicked.connect(self.show_cpu_score)  # Double-clicking to show score as well

        self.compare_button.clicked.connect(self.compare_scores)

        # Install the event filter to the central widget to handle deselection
        self.central_widget.installEventFilter(self)

        # Set NoSelection to prevent making the text bold on item selection
        self.table_widget.setSelectionMode(QTableWidget.NoSelection)

    def populate_table(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        self.table_widget.clearContents()  # Clear any existing data in the table
        self.table_widget.setRowCount(0)  # Reset the row count

        for i in range(0, len(lines), 2):  # Process two lines at a time
            cpu_name = lines[i].strip()
            score = int(lines[i + 1].strip())

            row_count = self.table_widget.rowCount()
            self.table_widget.insertRow(row_count)

            # Create a QTableWidgetItem and set its flags to make it read-only
            item_name = QTableWidgetItem(cpu_name)
            item_name.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # Read-only flags
            self.table_widget.setItem(row_count, 0, item_name)

            item_score = QTableWidgetItem(str(score))
            item_score.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # Read-only flags
            self.table_widget.setItem(row_count, 1, item_score)

    def show_cpu_score(self, item):
        cpu_name = self.table_widget.item(item.row(), 0).text()
        score = self.table_widget.item(item.row(), 1).text()
        self.cpu_name_label.setText(cpu_name)
        self.cpu_score_label.setText(score)

    def compare_scores(self):
        cpu1_name = self.cpu_combobox1.line_edit.text()
        cpu2_name = self.cpu_combobox2.line_edit.text()

        if not cpu1_name or not cpu2_name:
            self.score_display.setText("Please select two CPUs to compare.")
            return

        cpu1_row = -1
        cpu2_row = -1

        for row in range(self.table_widget.rowCount()):
            if cpu1_name == self.table_widget.item(row, 0).text():
                cpu1_row = row
            if cpu2_name == self.table_widget.item(row, 0).text():
                cpu2_row = row

        if cpu1_row == -1 or cpu2_row == -1:
            self.score_display.setText("One or both CPUs not found in the table.")
            return

        score1 = int(self.table_widget.item(cpu1_row, 1).text())
        score2 = int(self.table_widget.item(cpu2_row, 1).text())

        if score1 > score2:
            result = f"{cpu1_name} has a higher score than {cpu2_name}."
        elif score1 < score2:
            result = f"{cpu2_name} has a higher score than {cpu1_name}."
        else:
            result = "Both CPUs have the same score."

        self.score_display.setText(result)

    def eventFilter(self, obj, event):
        if obj == self.central_widget and event.type() == QEvent.MouseButtonPress:
            self.deselect_elements(event)
        return super().eventFilter(obj, event)

    def deselect_elements(self, event):
        # This function is called when the central widget is clicked.
        # It deselects the entry boxes, the selected list item, and clears the CPU score label.
        self.score1_input.clearFocus()
        self.score2_input.clearFocus()
        self.table_widget.clearSelection()
        self.score_display.setText("")

    # Override focusOutEvent for the entry boxes to clear the selection
    def focusOutEvent(self, event):
        self.table_widget.clearSelection()
        return super().focusOutEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    qdarktheme.setup_theme()
    sys.exit(app.exec())
