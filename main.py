import sys
import csv
import os
import pandas as pd
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QScrollArea, QApplication, QWidget, QSpinBox, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox, QLabel, QMessageBox, QHeaderView, QMenu, QAction, QMessageBox, QProgressDialog, QCheckBox, QGroupBox, QToolBox, QTabWidget, QDoubleSpinBox
from PyQt5.QtCore import Qt
from write_exif2images import write_exif_to_images

class PosInfoReader(QWidget):
    def __init__(self):
        super().__init__()
        self.settingsCheckBoxes = {}  
        self.settingsLineEdits = {}  
        self.settingsComboBoxes = {}
        self.settingsSpinBoxes = {}
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        self.resize(450, 500)  # 设置窗口大小为宽800像素，高600像素

        # 第一行布局：用于选择图片文件夹的文本框和按钮
        topLayout = QHBoxLayout()
        self.imageFolderLineEdit = QLineEdit(self)
        self.imageFolderBrowseButton = QPushButton('浏览图片文件夹', self)
        self.imageFolderBrowseButton.clicked.connect(self.openImageFolderDialog)
        topLayout.addWidget(self.imageFolderLineEdit)
        topLayout.addWidget(self.imageFolderBrowseButton)

        # 创建GPS设置的GroupBox
        gpsSettingsGroupBox = QGroupBox("GPS设置", self)
        gpsSettingsLayout = QVBoxLayout()
        # 第二行布局：用于选择POS文件的文本框和按钮
        secondRowLayout = QHBoxLayout()
        self.lineEdit = QLineEdit(self)
        self.browseButton = QPushButton('浏览POS文件', self)
        self.browseButton.clicked.connect(self.openFileNameDialog)
        secondRowLayout.addWidget(self.lineEdit)
        secondRowLayout.addWidget(self.browseButton)
        # 创建分隔符选择布局
        delimiterLayout = QHBoxLayout()
        self.delimiterLineEdit = QLineEdit(self)
        self.delimiterLineEdit.setText(' ')  # 设置初始默认值为一个空格
        self.delimiterComboBox = QComboBox(self)
        self.delimiterComboBox.addItems(['空格 ', '逗号,', '分号;', '制表符Tab'])
        self.delimiterConfirmButton = QPushButton('确定', self)
        # 分隔符选择事件
        self.delimiterComboBox.activated[str].connect(self.onDelimiterSelected)
        self.delimiterConfirmButton.clicked.connect(self.onDelimiterConfirmed)
        # 将分隔符选择控件添加到布局中
        delimiterLayout.addWidget(QLabel('分隔符:'))
        delimiterLayout.addWidget(self.delimiterLineEdit)
        delimiterLayout.addWidget(self.delimiterComboBox)
        delimiterLayout.addWidget(self.delimiterConfirmButton)
        # 创建表格
        self.tableWidget = QTableWidget(self)
        self.setupTableWidget()
        # 将布局添加到GCP设置的GroupBox
        gpsSettingsLayout.addLayout(secondRowLayout)
        gpsSettingsLayout.addLayout(delimiterLayout)
        gpsSettingsLayout.addWidget(self.tableWidget)
        # 设置GroupBox的布局
        gpsSettingsGroupBox.setLayout(gpsSettingsLayout)

        # 创建Tab Widget
        tabWidget = QTabWidget(self)
        # # 说明Tab
        # descriptionWidget = QWidget()
        # descriptionLayout = QVBoxLayout(descriptionWidget)
        # self.addSettingItem(descriptionLayout, "标题", "titleLabel")
        # self.addSettingItem(descriptionLayout, "主题", "subjectLabel")
        # self.addSettingItem(descriptionLayout, "分级", "levelLabel")
        # self.addSettingItem(descriptionLayout, "标记", "tagLabel")
        # self.addSettingItem(descriptionLayout, "备注", "noteLabel")
        # # 使用QScrollArea
        # descriptionScrollArea = QScrollArea()
        # descriptionScrollArea.setWidgetResizable(True)
        # descriptionScrollArea.setWidget(descriptionWidget)
        # tabWidget.addTab(descriptionScrollArea, "说明")

        # 照相机设置Tab
        cameraSettingsWidget = QWidget()
        cameraSettingsLayout = QVBoxLayout(cameraSettingsWidget)
        self.addSettingItem(cameraSettingsLayout, "照相机制造商", "cameraManufacturer")
        self.addSettingItem(cameraSettingsLayout, "照相机型号", "cameraModel")
        self.addSettingItem(cameraSettingsLayout, "光圈值(f)", "apertureValue")
        self.addSettingItem(cameraSettingsLayout, "曝光时间(秒)", "exposureTime")
        self.addSettingItem(cameraSettingsLayout, "ISO速度", "isoSpeed")
        self.addSettingItem(cameraSettingsLayout, "曝光补偿", "exposureCompensation")
        self.addSettingItem(cameraSettingsLayout, "焦距", "focalLength", "mm")
        self.addSettingItem(cameraSettingsLayout, "最大光圈", "maxAperture")
        self.addSettingItem(cameraSettingsLayout, "测光模式", "meteringMode")
        self.addSettingItem(cameraSettingsLayout, "目标距离", "subjectDistance")
        self.addSettingItem(cameraSettingsLayout, "闪光灯模式", "flashMode")
        self.addSettingItem(cameraSettingsLayout, "闪光灯能量", "flashEnergy")
        self.addSettingItem(cameraSettingsLayout, "35mm焦距", "focalLength35mm")
        # 使用QScrollArea
        cameraSettingsScrollArea = QScrollArea()
        cameraSettingsScrollArea.setWidgetResizable(True)
        cameraSettingsScrollArea.setWidget(cameraSettingsWidget)
        tabWidget.addTab(cameraSettingsScrollArea, "照相机")

        # 创建输出设置的GroupBox
        outputSettingsGroupBox = QGroupBox("输出设置", self)
        outputSettingsLayout = QVBoxLayout()
        # 添加保存图像质量选择布局
        saveQualityLayout = QHBoxLayout()
        self.saveQualityCheckBox = QCheckBox("启用保存图像质量设置", self)
        self.saveQualitySpinBox = QSpinBox(self)
        self.saveQualitySpinBox.setRange(1, 100)  # 设置范围为1-100
        self.saveQualitySpinBox.setSuffix('%')  # 设置后缀为%
        # 默认禁用SpinBox
        self.saveQualitySpinBox.setEnabled(False)
        # 复选框状态改变时的行为
        self.saveQualityCheckBox.stateChanged.connect(self.toggleSaveQualitySettings)
        saveQualityLayout.addWidget(self.saveQualityCheckBox)
        saveQualityLayout.addWidget(self.saveQualitySpinBox)
        # 添加输出文件夹选择布局
        outputFolderLayout = QHBoxLayout()
        self.outputFolderLineEdit = QLineEdit(self)
        self.outputFolderBrowseButton = QPushButton('指定输出文件夹', self)
        self.outputFolderBrowseButton.clicked.connect(self.openOutputFolderDialog)
        outputFolderLayout.addWidget(self.outputFolderLineEdit)
        outputFolderLayout.addWidget(self.outputFolderBrowseButton)
        # 将布局添加到输出设置的GroupBox
        outputSettingsLayout.addLayout(saveQualityLayout)
        outputSettingsLayout.addLayout(outputFolderLayout)
        # 设置GroupBox的布局
        outputSettingsGroupBox.setLayout(outputSettingsLayout)

        # 创建按钮布局
        buttonsLayout = QHBoxLayout()
        self.runButton = QPushButton('运行', self)
        self.cancelButton = QPushButton('取消', self)
        self.runButton.clicked.connect(self.onRunButtonClicked)
        self.cancelButton.clicked.connect(self.onCancelButtonClicked)
        buttonsLayout.addWidget(self.runButton)
        buttonsLayout.addWidget(self.cancelButton)

        # 将顶部布局、分隔符选择布局和表格添加到主布局中
        # 将两行布局和其他布局添加到主布局中
        mainLayout.addLayout(topLayout)
        # 在主布局中添加GPS设置的GroupBox
        mainLayout.addWidget(gpsSettingsGroupBox)
        # 在主布局中添加照相机设置的GroupBox
        mainLayout.addWidget(tabWidget)
        # 在主布局中添加输出设置的GroupBox
        mainLayout.addWidget(outputSettingsGroupBox)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle('POS信息写入图片EXIF')

    def openImageFolderDialog(self):
        # 创建一个用于选择多个图片文件的对话框
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = QFileDialog.getOpenFileNames(self, "选择图片文件", "", "Image Files (*.jpg *.jpeg *.png *.bmp *.gif)", options=options)
        if fileNames:
            # 将选中的多个文件路径存储到数组中
            self.selectedImageFiles = fileNames
            # 将选中的多个文件路径显示在文本框中，用分号分隔
            self.imageFolderLineEdit.setText(';'.join(fileNames))

    def setupTableWidget(self):
        self.tableWidget.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.horizontalHeader().customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pos):
        menu = QMenu(self.tableWidget)
        actionName = menu.addAction("名称")
        actionLongitude = menu.addAction("经度")
        actionLatitude = menu.addAction("纬度")
        actionAltitude = menu.addAction("高度")
        action = menu.exec_(self.tableWidget.mapToGlobal(pos))

        # 获取当前点击的列
        currentColumn = self.tableWidget.horizontalHeader().logicalIndexAt(pos)

        # 检查用户选择了哪个动作，并更新表头
        if action == actionName:
            self.updateHeader(currentColumn, "名称")
        elif action == actionLongitude:
            self.updateHeader(currentColumn, "经度")
        elif action == actionLatitude:
            self.updateHeader(currentColumn, "纬度")
        elif action == actionAltitude:
            self.updateHeader(currentColumn, "高度")

    def updateHeader(self, column, newHeader):
        # 检查是否已经有列设置了这个新的表头名称
        for i in range(self.tableWidget.columnCount()):
            if self.tableWidget.horizontalHeaderItem(i).text() == newHeader:
                # 如果找到了，将其重置为默认名称
                self.tableWidget.horizontalHeaderItem(i).setText(f"列 {i+1}")
                break
        # 设置新的表头名称
        self.tableWidget.horizontalHeaderItem(column).setText(newHeader)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "选择POS文件", "", "All Files (*);;Text Files (*.txt);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls)", options=options)
        if fileName:
            self.lineEdit.setText(fileName)

    def onDelimiterSelected(self, text):
        delimiter_map = {
            '空格 ': ' ',
            '逗号,': ',',
            '分号;': ';',
            '制表符Tab': '\t'
        }
        current_delimiter = self.delimiterLineEdit.text()
        selected_delimiter = delimiter_map.get(text, ' ')
        self.delimiterLineEdit.setText(current_delimiter + selected_delimiter)  # 添加到现有分隔符后面

    def onDelimiterConfirmed(self):
        delimiter = self.delimiterLineEdit.text()
        fileName = self.lineEdit.text()
        if not delimiter:  # 如果文本框中没有任何分隔
                        delimiter = ''  # 如果文本框中没有任何分隔符，则默认为空字符串
        if fileName:
            self.loadPosInfo(fileName, delimiter)
            self.populateTable(self.posData)  # 在确认分隔符后，重新加载并显示数据

    def loadPosInfo(self, fileName, delimiters=' '):
        posData = []  # 在函数作用域内初始化posData
        if fileName.lower().endswith(('.txt', '.csv')):
            with open(fileName, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    # 对于每一行，按照用户指定的所有分隔符进行分割
                    if delimiters:  # 确保delimiters不为空
                        for delimiter in delimiters:
                            line = line.replace(delimiter, delimiters[0])
                        # 使用第一个分隔符作为最终的分隔符来分割
                        posData.append(line.strip().split(delimiters[0]))
                    else:
                        # 如果没有指定分隔符，将整行作为一个数据项
                        posData.append([line.strip()])
        elif fileName.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(fileName)
            posData = df.values.tolist()
        self.posData = posData  # 将局部变量posData赋值给类实例变量self.posData

    def populateTable(self, posData):
        self.tableWidget.setRowCount(len(posData))
        column_count = max(len(row) for row in posData) if posData else 0
        self.tableWidget.setColumnCount(column_count)
        # 在这里设置表头
        for i in range(column_count):
            headerItem = self.tableWidget.horizontalHeaderItem(i)
            if headerItem is None:  # 如果还没有表头项，就创建一个
                headerItem = QTableWidgetItem()
                self.tableWidget.setHorizontalHeaderItem(i, headerItem)
            headerItem.setText(f"列 {i+1}")  # 设置表头文本

        for row, rowData in enumerate(posData):
            for column, item in enumerate(rowData):
                if column < column_count:
                    self.tableWidget.setItem(row, column, QTableWidgetItem(str(item)))

    def addSettingItem(self, layout, label, settingName, unit=''):
        # 创建一个水平布局
        settingLayout = QHBoxLayout()
        checkBox = QCheckBox(f"设置{label}:", self)
        # 根据设置名称决定使用LineEdit还是ComboBox
        if settingName in ["meteringMode", "flashMode"]:
            # 使用ComboBox
            settingControl = QComboBox(self)
            settingControl.setEnabled(False)
            if settingName == "meteringMode":
                settingControl.addItems(["未知", "平均", "偏中心平均", "点", "多点", "图案", "部分"])
            elif settingName == "flashMode":
                settingControl.addItems(["无闪光", "闪光", "闪光，无选通返回", "闪光，选通返回", "闪光，强制", "闪光，强制，无选通返回", "闪光，强制，带选通返回", "无闪光，强制", "无闪光，自动", "人闪光，自动", "闪光，自动", "闪光，自动，无选通返回", "闪光，自动，带选通返回", "无闪光功能", "闪光，红眼", "闪光，红眼，无选通返回", "闪光，红眼，带选通返回", "闪光，强制，红眼", "闪光，强制，红眼，无选通返回", "闪光，强制，红眼，带选通返回", "闪光，自动，红眼", "闪光，自动，无选通返回，红眼", "闪光，自动，带选通返回，红眼"])
        elif settingName in ["apertureValue","isoSpeed", "exposureCompensation", "maxAperture", "exposureTime","subjectDistance", "flashEnergy", "focalLength35mm"]:
            # 使用SpinBox
            settingControl = QDoubleSpinBox(self)
            settingControl.setEnabled(False)
            settingRanges = {
                "apertureValue": (0.0000, 999999998.5, 4, 0.0001),
                "isoSpeed": (0, 65535, 0, 1),
                "exposureCompensation": (-99.99, 99.99, 2, 0.01),
                "maxAperture": (0.00, 99.99, 2, 0.01),
                "exposureTime": (0.0001, 3600.00, 4, 0.0001),
                "subjectDistance": (0.0000, 999999998.5, 4, 0.0001),
                "flashEnergy": (0.0000, 99999.9999, 4, 0.0001),
                "focalLength35mm": (0, 65535, 0, 1)
            }
            rangeValues = settingRanges.get(settingName)
            if rangeValues:
                settingControl.setRange(rangeValues[0], rangeValues[1])
                settingControl.setDecimals(rangeValues[2])
                settingControl.setSingleStep(rangeValues[3])
            settingControl.setSuffix(unit)
        else:
            # 使用LineEdit
            settingControl = QLineEdit(self)
            settingControl.setEnabled(False)
            # 根据设置名称决定输入类型（整数或小数）
            if settingName in ["focalLength"]:
                # 只接受整数输入
                validator = QIntValidator(self)
                if settingName == "focalLength":
                    validator.setRange(0, 999999999)
                settingControl.setValidator(validator)
            # elif settingName in ["flashEnergy"]:
            #     validator = QDoubleValidator(self)
            #     validator.setNotation(QDoubleValidator.StandardNotation)
            #     settingControl.setValidator(validator)
        # 复选框状态改变时的行为
        checkBox.stateChanged.connect(lambda state, sc=settingControl, sl=None: self.toggleSetting(state, sc, sl))
        # 将复选框和控件添加到水平布局中
        settingLayout.addWidget(checkBox)
        settingLayout.addWidget(settingControl)
        # 如果提供了单位标签，则创建并添加标签
        if unit:
            settingLabel = QLabel(f'{unit}', self)
            settingLabel.setEnabled(False)  # 默认禁用标签
            settingLayout.addWidget(settingLabel)
            # 更新复选框状态改变时的行为，包括标签的启用/禁用
            checkBox.stateChanged.connect(lambda state, sc=settingControl, sl=settingLabel: self.toggleSetting(state, sc, sl))
        # 将水平布局添加到传入的布局中
        layout.addLayout(settingLayout)
        # 将settingName和对应的复选框、控件存储起来
        self.settingsCheckBoxes[settingName] = checkBox
        # 根据控件类型（LineEdit或ComboBox）存储到不同的字典中
        if isinstance(settingControl, QLineEdit):
            self.settingsLineEdits[settingName] = settingControl
        elif isinstance(settingControl, QComboBox):
            self.settingsComboBoxes[settingName] = settingControl
        elif isinstance(settingControl, QDoubleSpinBox):
            self.settingsSpinBoxes[settingName] = settingControl

    def toggleSetting(self, state, lineEdit, label):
        lineEdit.setEnabled(state == Qt.Checked)
        if label:  # 如果标签存在，则根据状态启用或禁用
            label.setEnabled(state == Qt.Checked)

    def getSettingValue(self, settingName):
        # 根据settingName获取对应文本框中的内容
        lineEdit = self.settingsLineEdits.get(settingName)
        if lineEdit:
            return lineEdit.text()
        return None

    def getComboBoxValue(self, settingName):
        # 根据settingName获取对应下拉框中的选中内容
        comboBox = self.settingsComboBoxes.get(settingName)
        if comboBox:
            text = comboBox.currentText()
            if settingName == "meteringMode":
                metering_mode_map = {
                    "未知": 0,
                    "平均": 1,
                    "偏中心平均": 2,
                    "点": 3,
                    "多点": 4,
                    "图案": 5,
                    "部分": 6,
                    "其他": 255
                }
                return metering_mode_map.get(text, 255)  # 默认返回255代表其他
            elif settingName == "flashMode":
                flash_mode_map = {
                    "无闪光": 0x0000,
                    "闪光": 0x0001,
                    "闪光，无选通返回": 0x0005,
                    "闪光，选通返回": 0x0007,
                    "闪光，强制": 0x0009,
                    "闪光，强制，无选通返回": 0x000D,
                    "闪光，强制，带选通返回": 0x000F,
                    "无闪光，强制": 0x0010,
                    "无闪光，自动": 0x0018,
                    "人闪光，自动": 0x0019,
                    "闪光，自动": 0x0019,
                    "闪光，自动，无选通返回": 0x001D,
                    "闪光，自动，带选通返回": 0x001F,
                    "无闪光功能": 0x0020,
                    "闪光，红眼": 0x0041,
                    "闪光，红眼，无选通返回": 0x0045,
                    "闪光，红眼，带选通返回": 0x0047,
                    "闪光，强制，红眼": 0x0049,
                    "闪光，强制，红眼，无选通返回": 0x004D,
                    "闪光，强制，红眼，带选通返回": 0x004F,
                    "闪光，自动，红眼": 0x0059,
                    "闪光，自动，无选通返回，红眼": 0x005D,
                    "闪光，自动，带选通返回，红眼": 0x005F
                }
                return flash_mode_map.get(text, 0x0000)  # 默认返回0x0000代表无闪光
        return None

    def getSpinBoxValue(self, settingName):
        # 根据settingName获取对应SpinBox中的值
        spinBox = self.settingsSpinBoxes.get(settingName)
        if spinBox:
            return spinBox.value()
        return None

    def checkSettingEnabled(self, settingName):
        # 根据settingName判断对应的复选框是否被勾选
        checkBox = self.settingsCheckBoxes.get(settingName)
        if checkBox:
            return checkBox.isChecked()
        return False

    # 保存质量复选框控制对应的标签和文本框是否可用
    def toggleSaveQualitySettings(self, state):
        self.saveQualitySpinBox.setEnabled(state == Qt.Checked)

    def openOutputFolderDialog(self):
        # 创建一个用于选择输出文件夹的对话框
        options = QFileDialog.Options()
        folderName = QFileDialog.getExistingDirectory(self, "选择输出文件夹", options=options)
        if folderName:
            # 将选中的文件夹路径显示在文本框中
            self.outputFolderLineEdit.setText(folderName)

    def onRunButtonClicked(self):
        # 运行按钮点击事件处理逻辑
        required_headers = ["名称", "经度", "纬度", "高度"]
        header_to_index_map = {self.tableWidget.horizontalHeaderItem(i).text(): i for i in range(self.tableWidget.columnCount())}

        if any(header in header_to_index_map for header in required_headers):        
            missing_headers = [header for header in required_headers if header not in header_to_index_map]
            if missing_headers:
                QMessageBox.warning(self, "缺少列名", f"请指定以下列名: {', '.join(missing_headers)}", QMessageBox.Ok)
                return
        
        # 如果所有必需的列名都已指定，将它们的信息存入数组中
        pos_info = []
        for row in range(self.tableWidget.rowCount()):
            row_data = {}
            for header in required_headers:
                column_index = header_to_index_map[header]
                if column_index is not None:  # 仅当列存在时才读取数据
                    row_data[header] = self.tableWidget.item(row, column_index).text() if self.tableWidget.item(row, column_index) else ""
            pos_info.append(row_data)
        
        # 获取图片文件路径数组
        image_paths = getattr(self, 'selectedImageFiles', [])
        
        # 将图片路径与表格中的名称进行配对
        # matched_info结构：
        # 0: ('E:/PIE-UAV/昆明BD联勤保障培...C_4071.JPG', {'名称': 'DSC_4071.JPG', '经度': '115.18772161', '纬度': '24.86138931', '高度': '1087.86'})
        # 1: ('E:/PIE-UAV/昆明BD联勤保障培...C_4072.JPG', {'名称': 'DSC_4072.JPG', '经度': '115.1877388', '纬度': '24.86027777', '高度': '1086.972'})
        matched_info = []
        if "名称" in header_to_index_map:
            for image_path in image_paths:
                image_name = os.path.basename(image_path)  # 保留文件的完整名称，包括后缀
                for data in pos_info:
                    if data["名称"] == image_name:
                        matched_info.append((image_path, data))
                        break
        else:
            # 如果没有“名称”列，直接使用所有图片路径，不进行匹配
            for image_path in image_paths:
                matched_info.append((image_path, {}))  # 关联空的数据字典
    
        
        # 如果有图片没有匹配到POS信息，弹出提示
        if len(matched_info) != len(image_paths):
            QMessageBox.warning(self, "匹配错误", "有些图片没有找到对应的POS信息，请检查名称是否匹配。", QMessageBox.Ok)
            return
        
        # 打印匹配的信息数组和输出文件夹路径
        output_folder = self.outputFolderLineEdit.text()
        print(f"输出文件夹路径: {output_folder}")
        for info in matched_info:
            print(info)

        # 判断是否启用了焦距设置和保存图像质量，将它们组合成一个对象
        settings = {
            "camera_manufacturer": self.getSettingValue("cameraManufacturer") if self.checkSettingEnabled("cameraManufacturer") else None,
            "camera_model": self.getSettingValue("cameraModel") if self.checkSettingEnabled("cameraModel") else None,
            "aperture_value": self.getSpinBoxValue("apertureValue") if self.checkSettingEnabled("apertureValue") else None,
            "exposure_time": self.getSpinBoxValue("exposureTime") if self.checkSettingEnabled("exposureTime") else None,
            "iso_speed": self.getSpinBoxValue("isoSpeed") if self.checkSettingEnabled("isoSpeed") else None,
            "exposure_compensation": self.getSpinBoxValue("exposureCompensation") if self.checkSettingEnabled("exposureCompensation") else None,
            "focal_length": self.getSettingValue("focalLength") if self.checkSettingEnabled("focalLength") else None,
            "max_aperture": self.getSpinBoxValue("maxAperture") if self.checkSettingEnabled("maxAperture") else None,
            "metering_mode": self.getComboBoxValue("meteringMode") if self.checkSettingEnabled("getComboBoxValue") else None,
            "subject_distance": self.getSpinBoxValue("subjectDistance") if self.checkSettingEnabled("subjectDistance") else None,
            "flash_mode": self.getComboBoxValue("flashMode") if self.checkSettingEnabled("flashMode") else None,
            "flash_energy": self.getSpinBoxValue("flashEnergy") if self.checkSettingEnabled("flashEnergy") else None,
            "focal_length35mm": self.getSpinBoxValue("focalLength35mm") if self.checkSettingEnabled("focalLength35mm") else None,
            "save_quality": self.saveQualitySpinBox.value() if self.saveQualityCheckBox.isChecked() else 100
        }

        success_count = 0
        fail_count = 0
        progress_dialog = QProgressDialog("正在处理图片...", "取消", 0, len(matched_info), self)
        progress_dialog.setWindowTitle("处理进度")
        progress_dialog.setModal(True)
        progress_dialog.show()
        progress_dialog.setValue(0)
        # 调用write_exif_to_images函数，将EXIF信息写入图片
        write_exif_to_images(output_folder, matched_info, settings, success_count, fail_count ,progress_dialog ,self)

    def onCancelButtonClicked(self):
        # 取消按钮点击事件处理逻辑
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PosInfoReader()
    ex.show()
    sys.exit(app.exec_())