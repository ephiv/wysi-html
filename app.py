import sys
import os
import tempfile
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        font = QFont('Consolas', 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                selection-background-color: #264f78;
            }
        """)
        
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        tab_width = 4
        metrics = QFontMetrics(font)
        self.setTabStopWidth(tab_width * metrics.horizontalAdvance(' '))

class HTMLEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.current_file = None
        self.is_modified = False
        
        self.auto_refresh_enabled = True
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_preview)
        self.refresh_timer.setSingleShot(True)
        
        self.init_ui()
        self.update_preview()
        
    def init_ui(self):
        self.setWindowTitle("WYSIWYG HTML Editor")
        self.setGeometry(100, 100, 1400, 900)

        self.create_menu()
        self.create_toolbar()
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(main_splitter)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.tab_widget = QTabWidget()
        left_layout.addWidget(self.tab_widget)
        
        self.html_editor = CodeEditor()
        self.html_editor.textChanged.connect(self.on_text_changed)
        self.tab_widget.addTab(self.html_editor, "HTML")
        
        self.css_editor = CodeEditor()
        self.css_editor.textChanged.connect(self.on_text_changed)
        self.tab_widget.addTab(self.css_editor, "CSS")
        
        self.js_editor = CodeEditor()
        self.js_editor.textChanged.connect(self.on_text_changed)
        self.tab_widget.addTab(self.js_editor, "JavaScript")
        
        main_splitter.addWidget(left_widget)
        
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        
        preview_header = QWidget()
        preview_header_layout = QHBoxLayout(preview_header)
        preview_header_layout.setContentsMargins(0, 0, 0, 0)
        
        preview_label = QLabel("Live Preview")
        preview_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        preview_header_layout.addWidget(preview_label)
        
        preview_header_layout.addStretch()
        
        
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh")
        self.auto_refresh_checkbox.setChecked(True)
        self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
        preview_header_layout.addWidget(self.auto_refresh_checkbox)
        
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_preview)
        preview_header_layout.addWidget(refresh_btn)
        
        
        browser_btn = QPushButton("Open in Browser")
        browser_btn.clicked.connect(self.open_in_browser)
        preview_header_layout.addWidget(browser_btn)
        
        right_layout.addWidget(preview_header)
        
        
        self.web_view = QWebEngineView()
        right_layout.addWidget(self.web_view)
        
        main_splitter.addWidget(right_widget)
        
        
        main_splitter.setSizes([700, 700])
        
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        
        self.apply_dark_theme()
        
    def apply_dark_theme(self):
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e3e;
                background-color: #2b2b2b;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #3e3e3e;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #888888;
            }
            QTabBar::tab:hover {
                background-color: #4e4e4e;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QCheckBox {
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
        """)
        
    def create_menu(self):
        menubar = self.menuBar()
        
        
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Save As', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        
        view_menu = menubar.addMenu('View')
        
        refresh_action = QAction('Refresh Preview', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.update_preview)
        view_menu.addAction(refresh_action)
        
        browser_action = QAction('Open in Browser', self)
        browser_action.setShortcut('Ctrl+B')
        browser_action.triggered.connect(self.open_in_browser)
        view_menu.addAction(browser_action)
        
    def create_toolbar(self):
        toolbar = self.addToolBar('Main')
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        
        new_action = QAction('New', self)
        new_action.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        
        open_action = QAction('Open', self)
        open_action.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        
        save_action = QAction('Save', self)
        save_action.setIcon(self.style().standardIcon(QStyle.SP_DriveHDIcon))
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        
        refresh_action = QAction('Refresh', self)
        refresh_action.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_action.triggered.connect(self.update_preview)
        toolbar.addAction(refresh_action)
    
    def on_text_changed(self):
        
        self.is_modified = True
        self.update_title()
        
        if self.auto_refresh_enabled:
            
            self.refresh_timer.stop()
            self.refresh_timer.start(1000)  
        
        self.status_bar.showMessage("Modified" + (" - Auto-refresh enabled" if self.auto_refresh_enabled else ""))
    
    def toggle_auto_refresh(self, enabled):
        
        self.auto_refresh_enabled = enabled
        if not enabled:
            self.refresh_timer.stop()
        self.status_bar.showMessage("Auto-refresh " + ("enabled" if enabled else "disabled"))
    
    def update_title(self):
        
        title = "WYSIWYG HTML Editor"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)
    
    def generate_html(self):
        
        html_content = self.html_editor.toPlainText()
        css_content = self.css_editor.toPlainText()
        js_content = self.js_editor.toPlainText()
        
        
        if 'id="custom-css"' not in html_content and 'id="custom-js"' not in html_content:
            
            preview_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <style>
{css_content}
    </style>
</head>
<body>
{html_content}
    <script>
{js_content}
    </script>
</body>
</html>"""
        else:
            
            preview_html = html_content
            preview_html = preview_html.replace(
                '<style id="custom-css">',
                f'<style id="custom-css">\n{css_content}'
            )
            preview_html = preview_html.replace(
                '<script id="custom-js">',
                f'<script id="custom-js">\n{js_content}'
            )
        
        return preview_html
    
    def update_preview(self):
        
        try:
            html_content = self.generate_html()
            
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
            
            
            file_url = QUrl.fromLocalFile(os.path.abspath(temp_file))
            self.web_view.load(file_url)
            
            self.status_bar.showMessage("Preview updated")
            
            
            QTimer.singleShot(5000, lambda: self.cleanup_temp_file(temp_file))
            
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", f"Error updating preview: {str(e)}")
    
    def cleanup_temp_file(self, file_path):
        
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass
    
    def open_in_browser(self):
        
        try:
            html_content = self.generate_html()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
            
            webbrowser.open(f'file://{os.path.abspath(temp_file)}')
            self.status_bar.showMessage("Opened in browser")
            
            
            QTimer.singleShot(10000, lambda: self.cleanup_temp_file(temp_file))
            
        except Exception as e:
            QMessageBox.critical(self, "Browser Error", f"Error opening in browser: {str(e)}")
    
    def new_file(self):
        
        if self.is_modified:
            reply = QMessageBox.question(self, "Save Changes", 
                                       "Do you want to save changes before creating a new file?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                if not self.save_file():
                    return
        
        self.html_editor.clear()
        self.css_editor.clear()
        self.js_editor.clear()
        self.current_file = None
        self.is_modified = False
        self.load_default_content()
        self.update_title()
        self.update_preview()
        self.status_bar.showMessage("New file created")
    
    def open_file(self):
        
        if self.is_modified:
            reply = QMessageBox.question(self, "Save Changes",
                                       "Do you want to save changes before opening a file?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                if not self.save_file():
                    return
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Open HTML File", "", 
                                                 "HTML files (*.html *.htm);;All files (*.*)")
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                
                self.html_editor.clear()
                self.css_editor.clear()
                self.js_editor.clear()
                
                
                self.html_editor.setPlainText(content)
                
                self.current_file = file_path
                self.is_modified = False
                self.update_title()
                self.update_preview()
                self.status_bar.showMessage(f"Opened: {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Open Error", f"Error opening file: {str(e)}")
    
    def save_file(self):
        
        if self.current_file:
            return self.save_to_file(self.current_file)
        else:
            return self.save_as_file()
    
    def save_as_file(self):
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save HTML File", "", 
                                                 "HTML files (*.html);;All files (*.*)")
        
        if file_path:
            return self.save_to_file(file_path)
        return False
    
    def save_to_file(self, file_path):
        
        try:
            
            content = self.generate_html()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_file = file_path
            self.is_modified = False
            self.update_title()
            self.status_bar.showMessage(f"Saved: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving file: {str(e)}")
            return False
    
    def closeEvent(self, event):
        
        if self.is_modified:
            reply = QMessageBox.question(self, "Save Changes",
                                       "Do you want to save changes before exiting?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            
            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.Yes:
                if not self.save_file():
                    event.ignore()
                    return
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    
    app.setApplicationName("wysi html")
    
    editor = HTMLEditor()
    editor.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
