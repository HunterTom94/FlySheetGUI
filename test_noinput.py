import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QTableWidget, QTableWidgetItem, QLineEdit
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore
import os
import pandas as pd
import numpy as np
from datetime import datetime


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
                           'Alert Days', 'Condition Start',
                           'Hatch Time', 'Position']
        self.read_df()
        self.current_vial = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.vialGroupBox = self.createVialButtons()
        self.tableGroupBox = self.createTable()
        self.inputGroupBox = self.createInput()

        self.windowLayout = QVBoxLayout()
        self.windowLayout.addWidget(self.vialGroupBox)
        self.windowLayout.addWidget(self.tableGroupBox)
        self.windowLayout.addWidget(self.inputGroupBox)
        self.setLayout(self.windowLayout)

        self.show()

    def createInput(self):
        inputGroupBox = QGroupBox("Input")
        inputLayout = QHBoxLayout()
        hatch_button = QPushButton('Hatch')
        flip_button = QPushButton('Flip')
        condition_button = QPushButton('Condition')
        transfer_button = QPushButton('Transfer From')
        flip_button.clicked.connect(self.flip)
        condition_button.clicked.connect(self.condition_start)
        transfer_button.clicked.connect(self.transfer)
        hatch_button.clicked.connect(self.hatch)
        inputLayout.addWidget(hatch_button)
        inputLayout.addWidget(flip_button)
        inputLayout.addWidget(condition_button)
        inputLayout.addWidget(transfer_button)
        inputGroupBox.setLayout(inputLayout)
        self.transfer_to = []
        return inputGroupBox

    def createVialButtons(self):
        vialGroupBox = QGroupBox("Vials")
        layout = QGridLayout()
        for button_ind in range(100):
            row_ind = button_ind % 10
            col_ind = int(button_ind / 10)
            button = QPushButton('{} - {}'.format(row_ind + 1, col_ind + 1))
            button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            if self.fly_sheet['Position'].isin(['{} - {}'.format(row_ind + 1, col_ind + 1)]).any():
                setuptime_str = str(self.fly_sheet.loc[self.fly_sheet['Position'] == '{} - {}'.format(row_ind + 1,
                                                                                                      col_ind + 1), 'Setup Time'].values[
                                        0])
                setuptime_obj = datetime.strptime(setuptime_str, "%m/%d/%Y, %H:%M")
                lastflip_obj = datetime.now() - setuptime_obj
                lastflip_day = lastflip_obj.days
                if lastflip_day >= int(self.fly_sheet.loc[self.fly_sheet['Position'] == '{} - {}'.format(row_ind + 1,
                                                                                                         col_ind + 1), 'Alert Days'].values[
                                           0]):
                    button.setStyleSheet("background-color:rgb(255,0,0)")
                else:
                    button.setStyleSheet("background-color:rgb(0,255,0)")
            button.clicked.connect(self.show_info)
            layout.addWidget(button, row_ind, col_ind)
        vialGroupBox.setLayout(layout)
        return vialGroupBox

    def createTable(self):
        GroupBox = QGroupBox("Information")
        GroupBox.setMaximumHeight(110)
        self.table_layout = QHBoxLayout()
        self.tableWidget = QTableWidget()
        self.col_num = len(self.label_list) - 3
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(self.col_num)
        self.tableWidget.setHorizontalHeaderLabels(self.label_list)
        if self.fly_sheet['Position'].isin([self.current_vial]).any():
            assert np.sum(self.fly_sheet['Position'].isin([self.current_vial])) == 1
            vial_info = self.fly_sheet.loc[self.fly_sheet['Position'].isin([self.current_vial])]
            for col in vial_info:
                col_index = vial_info.columns.get_loc(col)
                if col == 'Age' and (not pd.isna(vial_info.iloc[0, self.label_list.index('Hatch Time')])):
                    hatchtime_str = vial_info.iloc[0, self.label_list.index('Hatch Time')]
                    hatchtime_obj = datetime.strptime(hatchtime_str, "%m/%d/%Y, %H:%M")
                    age_obj = datetime.now() - hatchtime_obj
                    age_day = str(age_obj.days)
                    age_hour = str(int(age_obj.seconds / 3600))
                    item_value = age_day + 'days ' + age_hour + 'hours'
                elif col == 'Condition Time' and (
                not pd.isna(vial_info.iloc[0, self.label_list.index('Condition Start')])):
                    hatchtime_str = vial_info.iloc[0, self.label_list.index('Condition Start')]
                    hatchtime_obj = datetime.strptime(hatchtime_str, "%m/%d/%Y, %H:%M")
                    age_obj = datetime.now() - hatchtime_obj
                    age_day = str(age_obj.days)
                    age_hour = str(int(age_obj.seconds / 3600))
                    item_value = age_day + 'days ' + age_hour + 'hours'
                else:
                    if pd.isna(vial_info.iloc[0, col_index]):
                        item_value = ""
                    else:
                        item_value = vial_info.iloc[0, col_index]
                item = QTableWidgetItem(item_value)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                if col == 'Age':
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
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
        if col == self.label_list.index('Setup Time'):
            setuptime_obj = datetime.now()
            setuptime_str = setuptime_obj.strftime("%m/%d/%Y, %H:%M")

            if self.fly_sheet['Position'].isin([self.current_vial]).any():

                assert np.sum(self.fly_sheet['Position'].isin([self.current_vial])) == 1
                self.fly_sheet.at[self.fly_sheet['Position'] == self.current_vial, 'Setup Time'] = setuptime_str
                if pd.isna(self.fly_sheet.loc[self.fly_sheet['Position'] == self.current_vial, 'Hatch Time']).any():
                    self.fly_sheet.at[self.fly_sheet['Position'] == self.current_vial, 'Hatch Time'] = setuptime_str
            else:
                self.fly_sheet = self.fly_sheet.append(
                    {'Position': self.current_vial, 'Setup Time': setuptime_str, 'Hatch Time': setuptime_str,
                     'Alert Days': '2'},
                    ignore_index=True)


        else:
            if self.fly_sheet['Position'].isin([self.current_vial]).any():
                assert np.sum(self.fly_sheet['Position'].isin([self.current_vial])) == 1
                self.fly_sheet.at[self.fly_sheet['Position'] == self.current_vial, self.label_list[col]] = item.text()
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
        # print('refresh')
        self.windowLayout.removeWidget(self.vialGroupBox)
        self.windowLayout.removeWidget(self.tableGroupBox)
        self.windowLayout.removeWidget(self.inputGroupBox)
        self.vialGroupBox = self.createVialButtons()
        self.tableGroupBox = self.createTable()
        self.windowLayout.addWidget(self.vialGroupBox)
        self.windowLayout.addWidget(self.tableGroupBox)
        self.windowLayout.addWidget(self.inputGroupBox)

    def show_info(self):

        sending_button = self.sender()
        self.current_vial = sending_button.text()
        if self.transfer_to != []:
            temp_dict = self.fly_sheet.loc[self.fly_sheet['Position'] == self.current_vial, :].to_dict('r')[0]
            temp_dict['Position'] = self.transfer_to
            self.fly_sheet = self.fly_sheet.append(temp_dict, ignore_index=True)
            self.transfer_to = []

        self.refresh()

        # print(str(sending_button.setStyleSheet("background-color:rgb(0,255,0)")))
        # print(sending_button.text())

    def read_df(self):
        if os.path.exists(self.folder + "fly_sheet.pkl"):
            self.fly_sheet = pd.read_pickle(self.folder + 'fly_sheet.pkl')
        else:
            self.fly_sheet = pd.DataFrame(
                columns=self.label_list)

    def transfer(self, from_vial):
        self.transfer_to = self.current_vial
        # from_vial_split = from_vial.split(' ')
        # assert from_vial_split[0].isdigit() and from_vial_split[2].isdigit() and from_vial_split[1] == '-', 'From Vial Wrong Format'

    def flip(self):
        self.tableWidget.setItem(0, self.label_list.index('Setup Time'), QTableWidgetItem(QTableWidgetItem("")))

    def condition_start(self):
        self.flip()
        self.fly_sheet.at[self.fly_sheet['Position'] == self.current_vial, 'Condition Start'] = self.fly_sheet.loc[
            self.fly_sheet['Position'] == self.current_vial, 'Setup Time']

    def hatch(self):
        self.flip()
        self.fly_sheet.at[self.fly_sheet['Position'] == self.current_vial, 'Alert Days'] = '5'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App('Z:\\#Yinan\\')
    sys.exit(app.exec_())
