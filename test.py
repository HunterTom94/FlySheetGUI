import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QTableWidget, QTableWidgetItem
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore
import os
import pandas as pd
import numpy as np


class App(QDialog):

    def __init__(self, folder):
        super().__init__()
        self.title = 'PyQt5 layout - pythonspot.com'
        self.left = 500
        self.top = 100
        self.width = 800
        self.height = 800
        self.folder = folder
        self.label_list = ["Age", "Genotype", "Sex", 'Setup Time', 'Number', 'Condition', 'Condition Time',
                           'Hatch Time', 'Position']
        self.read_df()
        self.current_vial = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.vialGroupBox = self.createVialButtons()
        self.tableGroupBox = self.createTable()

        self.windowLayout = QVBoxLayout()
        self.windowLayout.addWidget(self.vialGroupBox)
        self.windowLayout.addWidget(self.tableGroupBox)
        self.setLayout(self.windowLayout)

        self.show()

    def createVialButtons(self):
        vialGroupBox = QGroupBox("Vials")
        layout = QGridLayout()
        for button_ind in range(100):
            row_ind = button_ind % 10
            col_ind = int(button_ind / 10)
            button = QPushButton('{} - {}'.format(row_ind + 1, col_ind + 1))
            button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            # print(row_ind)
            # print(col_ind)
            # print(self.fly_sheet['Position'])
            # exit()
            if self.fly_sheet['Position'].isin(['{} - {}'.format(row_ind + 1, col_ind + 1)]).any():
                button.setStyleSheet("background-color:rgb(255,0,0)")
            button.clicked.connect(self.show_info)
            layout.addWidget(button, row_ind, col_ind)
        vialGroupBox.setLayout(layout)
        return vialGroupBox

    def createTable(self):
        GroupBox = QGroupBox("Information")
        GroupBox.setMaximumHeight(110)
        self.table_layout = QHBoxLayout()
        self.tableWidget = QTableWidget()
        self.col_num = len(self.label_list) - 1
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(self.col_num)
        self.tableWidget.setHorizontalHeaderLabels(self.label_list)
        if self.fly_sheet['Position'].isin([self.current_vial]).any():
            assert np.sum(self.fly_sheet['Position'].isin([self.current_vial])) == 1
            vial_info = self.fly_sheet.loc[self.fly_sheet['Position'].isin([self.current_vial])]
            for col in vial_info:

                col_index = vial_info.columns.get_loc(col)
                if pd.isna(vial_info.iloc[0, col_index]):
                    item_value = ""
                else:
                    item_value = vial_info.iloc[0, col_index]
                item = QTableWidgetItem(item_value)
                # if col_index == self.position_label_index:
                #     item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(0, col_index, QTableWidgetItem(item))

        else:
            for cell_ind in range(self.col_num):
                item = QTableWidgetItem("")
                self.tableWidget.setItem(0, cell_ind, item)

        # self.tableWidget.doubleClicked.connect(self.on_click)
        self.tableWidget.itemChanged.connect(self.update_df)
        self.table_layout.addWidget(self.tableWidget)
        GroupBox.setLayout(self.table_layout)
        return GroupBox

    def update_df(self, item):
        col = item.column()
        if self.fly_sheet['Position'].isin([self.current_vial]).any():
            assert np.sum(self.fly_sheet['Position'].isin([self.current_vial])) == 1
            self.fly_sheet.at[self.fly_sheet['Position'] == self.current_vial, col] = item.text()
        else:
            self.fly_sheet = self.fly_sheet.append(
                {'Position': self.current_vial, self.label_list[col]: item.text()},
                ignore_index=True)
        self.fly_sheet.to_pickle(self.folder + 'fly_sheet.pkl')
        self.refresh()

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            # print(self.tableWidget.cellChanged)
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

    def refresh(self):
        self.windowLayout.removeWidget(self.vialGroupBox)
        self.vialGroupBox = self.createVialButtons()
        self.windowLayout.addWidget(self.vialGroupBox)

        self.windowLayout.removeWidget(self.tableGroupBox)
        self.tableGroupBox = self.createTable()
        self.windowLayout.addWidget(self.tableGroupBox)

    def show_info(self):

        sending_button = self.sender()
        self.current_vial = sending_button.text()

        self.refresh()

        # print(str(sending_button.setStyleSheet("background-color:rgb(0,255,0)")))
        # print(sending_button.text())

    def read_df(self):
        if os.path.exists(self.folder + "fly_sheet.pkl"):
            self.fly_sheet = pd.read_pickle(self.folder + 'fly_sheet.pkl')
        else:
            self.fly_sheet = pd.DataFrame(
                columns=self.label_list)
            print(self.fly_sheet)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App('Z:\\#Yinan\\')
    sys.exit(app.exec_())
