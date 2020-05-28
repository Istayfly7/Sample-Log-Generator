import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
from tkcalendar import Calendar, DateEntry
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import math
from functools import partial
from cryptography.fernet import Fernet
from time import ctime

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('Where/Ever/Your/FilesAre/credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open('Sample Log')

#MUST CREATE YOUR OWN KEY FROM ENCRYPTION
#Example key below (Not Usable, just for looks)
#key = b'Xpbrsdfijgosifg8sadfgsaf7yTqYTqjWQ6NU='

def makeNewSheet():
    time = ctime()
    time = time.split()
    month = time[1]
    year = time[4]
    date = month + " " + year
    #create new  sheet with new month and year
    #print("Month is:", month)
    #print("Year is:", year)
    spreadsheet.add_worksheet(title=date, rows="1000", cols="26")
    spreadsheet.worksheet(date).append_row(['Date', 'SonEX Labs Prod. Name', 'Botanacor Submitted Name', 'Submitted By', 'In House/3rd Party', 'Comments(Analysis Needed)', 'Approved By'], table_range='A1')
    
    sheetId = spreadsheet.worksheet(date)._properties['sheetId']
    body = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheetId,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 7
                    },
                    "properties": {
                        "pixelSize": 200
                    },
                    "fields": "pixelSize"
                }
            }
        ]
    }
    res = spreadsheet.batch_update(body)
    spreadsheet.worksheet(date).format('A1:G1', {"horizontalAlignment":"CENTER"})
    
    return spreadsheet.worksheet(date)

def openCorrectSheet():
    time = ctime()
    time = time.split()
    month = time[1]
    year = time[4]
    date = month + " " + year
    try:
        return spreadsheet.worksheet(date)
    except:
        return makeNewSheet()

sheet = openCorrectSheet()

#################################################Backbone code for logger###########################

def addEntry(entry):
    #entry = [init, date(xx/xx/xx), Item  Description, In/out, Quantity, In Kanha]
    sheet.append_row(entry, table_range='A1')

def addEntrytoNAFile(entry):
    na = open("NotApproved.txt", "a")
    na.write(entry + '\n')
    na.close()

def getLastRow():
    return len(sheet.get_all_values())

def removeEntryByRow(row):
    lastRow = getLastRow()
    if(lastRow >= row+1 and row+1 > 1):
        sheet.delete_rows(row+1)

def removeAll():
    lastRow = getLastRow()
    sheet.delete_rows(2, lastRow)

def removeLastEntry():
    lastRow = getLastRow()
    if(lastRow > 1):
        sheet.delete_rows(lastRow)

def viewLastEntries(amt):
    lastRow = getLastRow()
    rangeEnd = 'G' + str(lastRow)
    if(lastRow > amt and amt > 0):
        #if want to view amt within limits and greater than 0
        rSt = lastRow - amt + 1
        rangeStart = 'A' + str(rSt)
        
        rang = rangeStart + ':' + rangeEnd
        values = sheet.get(rang)
        #print("Range:", rangeStart, '-', rangeEnd)
    elif(amt == 0):
        #if want to view 0 entires
        rangeStart = 'A' + str(lastRow)

        rang = rangeStart + ':' + rangeEnd
        values = sheet.get(rang)
        #print("Range:", rangeStart, '-', rangeEnd)
    else:
        #if viewing more than posib
        rangeStart = 'A2'

        rang = rangeStart + ':' + rangeEnd

        if(lastRow > 1):
            values = sheet.get(rang)
        else:
            return list()
        #print("Range:", rangeStart, '-', rangeEnd)

    #adding row numbers
    if(amt >= lastRow):
        amt = lastRow
        for ent in values:
            ent.append(str(lastRow - (amt-1)))
            amt = amt-1
    else:
        for ent in values:
            ent.append(str(lastRow - amt))
            amt = amt-1
    return values

def getRowEntry(row):
    row = row + 1
    cells = 'A' + str(row) + ':G' + str(row)
    return sheet.get(cells)

#####OPTIMIZE##############
def editByRowOptionFile(row, data):
    values = getAllValuesFile()

    newvalues = list()
    for i in range(len(values)):
        if(i != row):
            newvalues = list(newvalues) + [list(values[i])]
        else:
            newvalues = list(newvalues) + [list(data)]
    #print("newvalues:", newvalues)

    na = open("NotApproved.txt", "w")
    for value in newvalues:
        na.write(value[0] + " " + value[1] + " " + value[2] + " " + value[3] + " " + value[4] + " " + value[5] + " " + value[6] + "\n")
    na.close()

def editByRowOption(row, data=None):
    lastRow = getLastRow()
    #options: all, init, date, item, check, quan, afik
    if(lastRow > 1 and row + 1 > 1):
        row = row + 1
        cells = 'A' + str(row) + ':G' + str(row)
        sheet.update(cells, [data])

def getLastValuesFile(amt):
    na = open("NotApproved.txt", "r")
    lines = na.read()
    na.close()
    lastRow = len(lines.split("\n")) - 1
    startRow = lastRow - amt + 1
    #print("startRow:", startRow)
    #print("lastRow:", lastRow)

    values = list()
    na = open("NotApproved.txt", "r")
    for i in range(lastRow):
        if(i + 1 >= startRow and i <= lastRow):
            values = list(values) + [list(na.readline().split())]
        else:
            na.readline()
    na.close()
    #print("values:", values)

    #adding row numbers
    if(amt >= lastRow):
        amt = lastRow
        for ent in values:
            ent.append(str(lastRow - (amt - 1)))
            amt = amt-1
    else:
        for ent in values:
            ent.append(str(lastRow - amt + 1))
            amt = amt-1
    return values

def getValuesFile(row):
    na = open("NotApproved.txt", "r")
    lines = na.read()
    na.close()
    lastRow = len(lines.split("\n")) - 1
    startRow = lastRow - row + 1
    #print("startRow:", startRow)
    #print("lastRow:", lastRow)

    values = list()
    na = open("NotApproved.txt", "r")
    for i in range(lastRow):
        if(i + 1 >= startRow and i <= lastRow):
            values = list(values) + [list(na.readline().split())]
        else:
            na.readline()
    na.close()
    #print("values:", values)

    #adding row numbers
    if(row >= lastRow):
        row = lastRow
        for ent in values:
            ent.append(str(lastRow - (row - 1)))
            row -= 1
    else:
        for ent in values:
            ent.append(str(lastRow - row + 1))
            row -= 1
    return values

def getAllValuesFile():
    values = list()
    na = open("NotApproved.txt", "r")
    lines = na.readlines()
    
    for i in range(len(lines)):
        values = list(values) + [list(((lines[i])[:-1]).split())]

    return values

#####OPTIMIZE#############
def removeByRowFile(row):
    values = getAllValuesFile()

    newvalues = list()
    for i in range(len(values)):
        if(i != row):
            newvalues = list(newvalues) + [list(values[i])]
    #print("newvalues:", newvalues)

    na = open("NotApproved.txt", "w")
    for value in newvalues:
        na.write(value[0] + " " + value[1] + " " + value[2] + " " + value[3] + " " + value[4] + " " + value[5] + " " + value[6] + "\n")
    na.close()



#####################################################Gui code for Logger#############################################
class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._master = None
        self.switch_frame(StartPage)
        self.option = None

    def switch_frame(self, frame_class):
        #go to next screen to choose options and upload
        new_frame = frame_class(self)
        if self._master is not None:
            self._master.destroy()
        self._master = new_frame
        self._master.pack()
        
class StartPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="The Sample Logger", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=20)
        #start screen button
        tk.Button(self, text="Click Here To Start", command=lambda: _master.switch_frame(OptionPage)).pack(side="top", fill="x", padx=20, pady=20)
        tk.Button(self, text="Click Here To Sign In As Approver", command=lambda: _master.switch_frame(AppSignInPage)).pack(side="top", fill="x", padx=20, pady=(0,20))

###for APPROVERS
class ChooseRemovePage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Remove Entry Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=20)

        tk.Button(self, text="Remove Entry from Not Approved List", command=lambda: _master.switch_frame(RemoveEntriesFilePage)).pack(side="top", fill="x", padx=20, pady=5)
        tk.Button(self, text="Remove Entry from Approved List", command=lambda: _master.switch_frame(RemoveEntriesPage)).pack(side="top", fill="x", padx=20, pady=5)

        tk.Button(self, text="Back", command=lambda: _master.switch_frame(AppOptionPage)).pack(side="top", fill="x", padx=20, pady=5)

class RemoveEntriesFilePage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Remove Entries From Not Approved List", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=20)
        tk.Label(self, text="What row would you like to remove?", font=('Helvetica', 14)).pack(side="top", fill="x", padx=20, pady=20)
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")
        self.lis = tk.Listbox(self, yscrollcommand=self.scrollbar.set)

        self.values = getAllValuesFile()
        strVals = np.array([])
        strTit = "Row" + "   " + "Date" + "        " + "SonEX Labs Prod. Name" + "        "  + "Botanacor Submitted Name" + "                     " + "Submitted By" + "                         " + "In House/3rd Party" + "         " + "Comments" + "         " + "Approved By"
        strVals = np.append(strVals, strTit)

        if(len(self.values) > 0):
            i = 1
            for val in self.values:
                s = str(i) + "       " + val[0] + "        " + val[1] + "        " + val[2] + "                     " + val[3] + "                         " + val[4] + "                 " + val[5] + "             " + val[6]
                strVals = np.append(strVals, s)
                i += 1

        self.scrollbar.config(command = strVals)
        self.lis.config(width=100)
        self.lis.pack(side="left", fill="x", padx=(5, 20), pady=(0, 15), expand=True)
        self.lis.insert(0, *strVals)
        
        tk.Button(self, text="Submit", command=lambda: self.callRemoveRow(_master, self.lis.get(self.lis.curselection()))).pack(side="top", fill="x", padx=20, pady=5)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(ChooseRemovePage)).pack(side="top", fill="x", padx=20, pady=5)

    def callRemoveRow(self, _master, row):
        row = int((row.split())[0])
        lastRow = len(getAllValuesFile())
        #print("row:", row)

        if(row <= lastRow and row > 0):
            removeByRowFile(row-1)
            tk.Label(self, text="Removed Entry", font=('Helvetica', 11)).pack(side="bottom")
            _master.switch_frame(RemoveEntriesFilePage)
        else:
            tk.Label(self, text="Cannot Remove, Row Doesn't Exist", font=('Helvetica', 11)).pack(side="bottom") 

class RemoveEntriesPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Remove Entries From Approved List", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=20)

        self.rEntry = tk.Button(self, text="Remove By Row", command=lambda: self.removeREntry(_master))
        self.rEntry.pack(side="top", fill="x", padx=20, pady=5)
        self.lEntry = tk.Button(self, text="Remove Last Entry", command=lambda: self.removeLEntry())
        self.lEntry.pack(side="top", fill="x", padx=20, pady=5)

        self.b = tk.Button(self, text="Back", command=lambda: _master.switch_frame(ChooseRemovePage))
        self.b.pack(side="top", fill="x", padx=20, pady=5)

    def removeLEntry(self):
        lastRow = getLastRow()
        removeLastEntry()
        #rang = 'A' + str(lastRow) + ':F' + str(lastRow)
        #tex = "Removed Entry: " + str(sheet.get(rang))
        #print("Text:", tex)
        #print("Range:", rang)
        if(lastRow > 1):
            tk.Label(self, text='Removed Entry', font=('Helvetica', 11)).pack(side="bottom")
        else:
            tk.Label(self, text="Cannot Remove, Row Doesn't Exist", font=('Helvetica', 11)).pack(side="bottom") 

    def removeREntry(self, _master):
        #unpacking
        self.lEntry.pack_forget()
        self.rEntry.pack_forget()
        self.b.pack_forget()

        #packing --- changing to selection
        tk.Label(self, text="What row would you like to remove?", font=('Helvetica', 14)).pack(side="top", fill="x", padx=20, pady=20)
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")
        self.lis = tk.Listbox(self, yscrollcommand=self.scrollbar.set)

        self.values = viewLastEntries(getLastRow()-1)
        strVals = np.array([])
        strTit = "Row" + "   " + "Date" + "        " + "SonEX Labs Prod. Name" + "         " + "Botanacor Submitted Name" + "          " + "Submitted By" + "      " + "In House/3rd Party" + "         " + "Comments" + "         " + "Approved By"
        strVals = np.append(strVals, strTit)

        if(getLastRow() > 1):
            i = 1
            for val in self.values:
                s = str(i) + "       " + val[0] + "     " + val[1] + "               " + val[2] + "                     " + val[3] + "                         " + val[4] + "                 " + val[5] + "             " + val[6]
                strVals = np.append(strVals, s)
                i += 1

        self.scrollbar.config(command = strVals)
        self.lis.config(width=100)
        self.lis.pack(side="left", fill="x", padx=(5, 20), pady=(0, 15), expand=True)
        self.lis.insert(0, *strVals)
        
        tk.Button(self, text="Submit", command=lambda: self.callRemoveRow(_master, self.lis.get(self.lis.curselection()))).pack(side="top", fill="x", padx=20, pady=5)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(RemoveEntriesPage)).pack(side="top", fill="x", padx=20, pady=5)

    def callRemoveRow(self, _master, row):
        row = int((row.split())[0])
        lastRow = getLastRow()
        #print("row:", row)

        if(row < lastRow and row > 0):
            #rang = 'A' + str(lastRow) + ':F' + str(lastRow)
            #tex = "Removed Entry: " + str(sheet.get(rang))
            removeEntryByRow(row)
            tk.Label(self, text="Removed Entry", font=('Helvetica', 11)).pack(side="bottom")
            _master.switch_frame(RemoveEntriesPage)
        else:
            tk.Label(self, text="Cannot Remove, Row Doesn't Exist", font=('Helvetica', 11)).pack(side="bottom") 

class AppSPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Approval Status Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=20)

        self.rEntry = tk.Button(self, text="Approve A Sample", command=lambda: _master.switch_frame(ApprovalPage))
        self.rEntry.pack(side="top", fill="x", padx=20, pady=5)
        self.lEntry = tk.Button(self, text="Unapprove A Sample", command=lambda: _master.switch_frame(UnapprovalPage))
        self.lEntry.pack(side="top", fill="x", padx=20, pady=5)

        self.b = tk.Button(self, text="Back", command=lambda: _master.switch_frame(AppOptionPage))
        self.b.pack(side="top", fill="x", padx=20, pady=5)

class UnapprovalPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Unapproval Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(20,5))

        #packing
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")
        self.lis = tk.Listbox(self, yscrollcommand=self.scrollbar.set)

        self.values = viewLastEntries(getLastRow()-1) if getLastRow() > 1 else list()
        strTit = "Row" + "   " + "Date" + "        " + "SonEX Labs Prod. Name" + "        " + "Botanacor Submitted Name" + "          " + "Submitted By" + "      " + "In House/3rd Party" + "         " + "Comments" + "         " + "Approved By"
        strVals = np.array(strTit)

        i = 1
        for val in self.values:
            s = str(i) + "       " + val[0] + "     " + val[1] + "               " + val[2] + "                     " + val[3] + "                         " + val[4] + "                 " + val[5] + "         " + val[6]
            strVals = np.append(strVals, s)
            i += 1

        #print("values:", self.values)
        #print("strVals:", strVals)
        self.scrollbar.config(command = strVals)
        self.lis.config(width=100)
        self.lis.pack(side="left", fill="x", padx=(5, 20), pady=(0, 15), expand=True)
        try:
            self.lis.insert(0, *strVals)
        except:
            tk.Label(self, text="No Samples to Unapprove", font=('Helvetica', 11)).pack(side="bottom")

        self.submitB = tk.Button(self, text="Submit", command=lambda: self.submitData(_master, self.lis.get(self.lis.curselection())))
        self.submitB.pack(side="top", fill="x", padx=20, pady=0)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(AppSPage)).pack(side="top", fill="x", padx=20, pady=5)

    def submitData(self, _master, row):
        row = int((row.split())[0])-1
        data = (self.values[row])[0] + " " + (self.values[row])[1] + " " + (self.values[row])[2] + " " + (self.values[row])[3] + " " + (self.values[row])[4] + " " + (self.values[row])[5] + " Not-Approved"

        #remove from google sheets
        removeEntryByRow(row+1)

        #add to file
        addEntrytoNAFile(data)
        tk.Label(self, text="Saved Status", font=('Helvetica', 11)).pack(side="bottom")
        _master.switch_frame(AppSPage)

class ApprovalPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Approval Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(20,5))

        self.values = getAllValuesFile()
        #print("values:", self.values)

        #packing
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")
        self.lis = tk.Listbox(self, yscrollcommand=self.scrollbar.set)

        strTit = "Row" + "   " + "Date" + "        " + "SonEX Labs Prod. Name" + "              " + "Botanacor Submitted Name" + "          " + "Submitted By" + "      " + "In House/3rd Party" + "         " + "Comments" + "         " + "Approved By"
        strVals = np.array(strTit)

        i = 1
        for val in self.values:
            s = str(i) + "       " + val[0] + "     " + val[1] + "               " + val[2] + "                     " + val[3] + "                         " + val[4] + "                 " + val[5] + "        " + val[6]
            strVals = np.append(strVals, s)
            i += 1

        #print("values:", self.values)
        #print("strVals:", strVals)
        self.scrollbar.config(command = strVals)
        self.lis.config(width=100)
        self.lis.pack(side="left", fill="x", padx=(5, 20), pady=(0, 15), expand=True)
        try:
            self.lis.insert(0, *strVals)
        except:
            tk.Label(self, text="No Samples to Unapprove", font=('Helvetica', 11)).pack(side="bottom")

        self.submitB = tk.Button(self, text="Submit", command=lambda: self.editForm(_master, self.lis.get(self.lis.curselection())))
        self.submitB.pack(side="top", fill="x", padx=20, pady=0)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(AppSPage)).pack(side="top", fill="x", padx=20, pady=5)

    def editForm(self, _master, row):
        self.values = getAllValuesFile()
        row = int((row.split())[0]) - 1

        #unpacking
        self.scrollbar.pack_forget()
        self.lis.pack_forget()
        self.submitB.pack_forget()

        #packing
        tk.Label(self, text="Approved By", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.apps = tk.Entry(self)
        self.apps.pack(side="top", fill="x", padx=100, pady=5)

        tk.Button(self, text="Submit", command=lambda: self.submitData(_master, row)).pack(side="top", fill="x", padx=20, pady=(5, 10))

    def submitData(self, _master, row):
        data = [(self.values[row])[0], (self.values[row])[1], (self.values[row])[2], (self.values[row])[3], (self.values[row])[4], (self.values[row])[5], self.apps.get()]
        #remove from file
        removeByRowFile(row)

        #add to google sheets
        addEntry(data)
        tk.Label(self, text="Saved Status", font=('Helvetica', 11)).pack(side="bottom")
        _master.switch_frame(AppSPage)

class AppLogSamplePage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        self.sn = None
        self.bn = None
        self.sub = None
        self.dat = None
        self.v = None
        self.com = None
        self.app = None

        tk.Label(self, text="Log Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=20)
        
        #enter SonEX Labs Prod. Name
        tk.Label(self, text="Enter the SonEX Labs\' Product Name", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.sn = tk.Entry(self)
        self.sn.pack(side="top", fill="x", padx=100, pady=5)

        #enter Botanacor Submitted Name
        tk.Label(self, text="Enter The Botanacor Submit Name", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.bn = tk.Entry(self)
        self.bn.pack(side="top", fill="x", padx=100, pady=5)

        #type in who it was submitted by
        tk.Label(self, text="Who Was it Submitted By?", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.sub = tk.Entry(self)
        self.sub.pack(side="top", fill="x", padx=100, pady=5)

        #choose date from calendar
        tk.Label(self, text="Choose Date", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.dat = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, year=2020)
        self.dat.pack(padx=50, pady=5)

        #select made in house or 3rd party
        self.v = tk.StringVar(_master, "In-House")
        tk.Label(self, text="Made In House or 3rd Party?", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        check = [("In-House", "In-House"), ("3rd-Party", "3rd-Party")]
        for op, val in (check):
            tk.Radiobutton(self, text=op, variable=self.v, value=val).pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)

        #type in comments
        tk.Label(self, text="Comments (Analysis Needed)", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.com = tk.Entry(self)
        self.com.pack(side="top", fill="x", padx=100, pady=5)

        #type in who its approved by
        tk.Label(self, text="Approved By", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.app = tk.Entry(self)
        self.app.pack(side="top", fill="x", padx=100, pady=5)

        tk.Button(self, text="Submit", command=lambda: self.submitValues()).pack(side="top", fill="x", padx=20, pady=0)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(AppOptionPage)).pack(side="top", fill="x", padx=20, pady=5)

    def submitValues(self):
        flag = False
        if(self.bn.get() != ""and self.sn.get() != "" and self.dat.get() != "" and self.sub.get() != "" and self.com.get() != "" and self.app.get() != ""):
            subm = (self.sub.get())[0].upper() + (self.sub.get())[1:]
            sn = (self.sn.get())[0].upper() + (self.sn.get())[1:]
            bn = (self.bn.get())[0].upper() + (self.bn.get())[1:]
            ent = [self.dat.get(), sn, bn, subm, self.v.get(), self.com.get(), self.app.get()]
            addEntry(ent)
            tex = "Added Entry: " + str(ent)
            tk.Label(self, text=tex, font=('Helvetica', 11)).pack(side="bottom")
            self.clearEntryValues(flag)
        else:
            self.blabel = tk.Label(self, text="No Blanks Allowed", font=('Helvetica', 11))
            self.blabel.pack(side="bottom")
            flag = True

    def clearEntryValues(self, flag):
        self.bn.delete(0, len(self.bn.get()))
        self.sn.delete(0, len(self.sn.get()))
        self.sub.delete(0, len(self.sub.get()))
        self.com.delete(0, len(self.com.get()))
        self.app.delete(0, len(self.app.get()))
        if(flag):
            self.blabel.pack_forget()

class ChangeDefaultPassword(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Change Password", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(20, 10))

        #password label and password entry box
        self.usernameLabel = tk.Label(self,text="Enter Username")
        self.usernameLabel.pack(side="top", fill="x", padx=20, pady=5)  
        #self.password = tk.StringVar(_master)
        self.usernameEntry = tk.Entry(self)
        self.usernameEntry.pack(side="top", fill="x", padx=20, pady=5)

        #password label and password entry box
        self.npasswordLabel = tk.Label(self,text="New Password (8 or more characters)")
        self.npasswordLabel.pack(side="top", fill="x", padx=20, pady=5)  
        #self.password = tk.StringVar(_master)
        self.npasswordEntry = tk.Entry(self, show='*')
        self.npasswordEntry.pack(side="top", fill="x", padx=20, pady=5)  

        #password label and password entry box
        self.cpasswordLabel = tk.Label(self,text="Confirm New Password")
        self.cpasswordLabel.pack(side="top", fill="x", padx=20, pady=5)  
        #self.password = tk.StringVar(_master)
        self.cpasswordEntry = tk.Entry(self, show='*')
        self.cpasswordEntry.pack(side="top", fill="x", padx=20, pady=5)

        tk.Button(self, text="Confirm Password Change", command=lambda: self.validate(_master, self.usernameEntry.get(), self.npasswordEntry.get(), self.cpasswordEntry.get())).pack(side="top", fill="x", padx=20, pady=5)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(StartPage)).pack(side="top", fill="x", padx=20, pady=5)

    def validate(self, _master, username, npassword, cpassword):
        flag = False
        cipher_suite = Fernet(key)
        uf = open("Username_Emails.txt", "r")

        for line in uf.readlines():
            line = line.split()
            line = [cipher_suite.decrypt(bytes(line[0], 'utf-8')).decode("utf-8"), cipher_suite.decrypt(bytes(line[1], 'utf-8')).decode("utf-8")]
            if(username == line[0] or username == line[1]):
                flag = True

        if(npassword == cpassword and len(npassword) >= 8 and flag):
            self.replaceDefaultPassword(_master, username, npassword)

    def replaceDefaultPassword(self, _master, username, password):
        cipher_suite = Fernet(key)
        uf = open("Username_Emails.txt", "r")
        pf = open("Passwords.txt", "r")
        pfile = np.array([])
        
        for line in uf.readlines():
            line = line.split()
            line = [cipher_suite.decrypt(bytes(line[0], 'utf-8')).decode("utf-8"), cipher_suite.decrypt(bytes(line[1], 'utf-8')).decode("utf-8")]
            
            if(username == line[0] or username == line[1]):
                for pline in pf.readlines():
                    pline = pline.split()
                    pline = [cipher_suite.decrypt(bytes(pline[0], 'utf-8')).decode("utf-8"), cipher_suite.decrypt(bytes(pline[1], 'utf-8')).decode("utf-8")]
                    if(pline[0] == line[1]):
                        pline[1] = password
                        uf.close()
                    pfile = np.append(pfile, pline)
        pf.close()

        #print("new password file:", pfile)
        i = 0
        pf = open("Passwords.txt", "w")
        for token in pfile:
            if(i == 0):
                entok = cipher_suite.encrypt(bytes(token, 'utf-8'))
                pf.write(str(entok.decode('utf-8')) + " ")
                #pf.write(token + " ")
                i += 1
            else:
                entok = cipher_suite.encrypt(bytes(token, 'utf-8'))
                pf.write(str(entok.decode('utf-8')) + "\n")
                #pf.write(token + "\n")
                i = 0
        pf.close()
        _master.switch_frame(AppOptionPage)

#change for any admin to gain access************
class AppSignInPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Sign In Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(20, 10))

        self.usernameLabel = tk.Label(self, text="User Name")
        self.usernameLabel.pack(side="top", fill="x", padx=20, pady=(20,5))
        #self.username = tk.StringVar()
        self.usernameEntry = tk.Entry(self)
        self.usernameEntry.pack(side="top", fill="x", padx=20, pady=5)  

        #password label and password entry box
        self.passwordLabel = tk.Label(self,text="Password")
        self.passwordLabel.pack(side="top", fill="x", padx=20, pady=5)  
        #self.password = tk.StringVar(_master)
        self.passwordEntry = tk.Entry(self, show='*')
        self.passwordEntry.pack(side="top", fill="x", padx=20, pady=5)

        tk.Button(self, text="Sign-In", command=lambda: self.validate(_master, self.usernameEntry.get(), self.passwordEntry.get())).pack(side="top", fill="x", padx=20, pady=5)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(StartPage)).pack(side="top", fill="x", padx=20, pady=5)

    #change for any admin************
    def validate(self, _master, username, password):
        cipher_suite = Fernet(key)
        flag = True
        uf = open("Username_Emails.txt", "r")
        pf = open("Passwords.txt", "r")
        
        for line in uf.readlines():
            line = line.split()
            line = [cipher_suite.decrypt(bytes(line[0], 'utf-8')).decode("utf-8"), cipher_suite.decrypt(bytes(line[1], 'utf-8')).decode("utf-8")]
            
            if(username == line[0] or username == line[1]):
                for pline in pf.readlines():
                    pline = pline.split()
                    pline = [cipher_suite.decrypt(bytes(pline[0], 'utf-8')).decode("utf-8"), cipher_suite.decrypt(bytes(pline[1], 'utf-8')).decode("utf-8")]
                    if(pline[0] == line[1]):
                        #just so admin doesn't have to keep changing passwords - change the name and email to current admin
                        #add admin encrytped username and email to username_emails.txt and passwords using key
                        #format Username_Emails.txt = user email , Passwords.txt = email password
                        if(password == 'password' and username != 'rico' and username != 'rico@sonexlabs.us'):
                            flag = False
                            _master.switch_frame(ChangeDefaultPassword)
                            uf.close()
                            pf.close()
                        elif(password == pline[1]):
                            flag = False
                            _master.switch_frame(AppOptionPage) 
                            uf.close()
                            pf.close()   

        if(flag):
            tk.Label(self,text="Username or Password is Incorrect").pack(side="bottom", fill="x", padx=20, pady=5)
            self.passwordEntry.delete(0, len(self.passwordEntry.get()))
            self.usernameEntry.delete(0, len(self.usernameEntry.get()))

class AppOptionPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Options Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(10,20))

        tk.Button(self, text="Log A Sample", command=lambda: _master.switch_frame(AppLogSamplePage)).pack(side='top', fill='x', padx=20, pady=(5,0))
        tk.Button(self, text="View Samples", command=lambda: _master.switch_frame(AppViewEntriesPage)).pack(side="top", fill="x", padx=20, pady=(5,0))
        tk.Button(self, text="Edit a Sample Entry", command=lambda: _master.switch_frame(AppEditEntriesPage)).pack(side='top', fill='x', padx=20, pady=(30,0))
        tk.Button(self, text="Remove Sample Entries", command=lambda: _master.switch_frame(ChooseRemovePage)).pack(side="top", fill="x", padx=20, pady=(5, 0))
        tk.Button(self, text="Approval Page", command=lambda: _master.switch_frame(AppSPage)).pack(side='top', fill='x', padx=20, pady=5)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(AppSignInPage)).pack(side="top", fill="x", padx=20, pady=5)

class AppViewEntriesPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        self.amt = None
        self.values = None

        self.eplabel = tk.Label(self, text="Entries Page", font=('Helvetica', 18, "bold"))
        self.eplabel.pack(side="top", fill="x", padx=20, pady=15)

        #edit how many rows to view
        self.hlabel = tk.Label(self, text="How many rows do you want to view", font=('Helvetica', 14))
        self.hlabel.pack(side="top", fill="x", padx=20, pady=5)
        self.elabel = tk.Label(self, text="(For Example, To view the last 3 entries just enter \"3\")", font=('Helvetica', 10))
        self.elabel.pack(side="top", fill="x", padx=20, pady=0)

        self.amt = tk.Entry(self)
        self.amt.pack(side="top", fill="x", padx=100, pady=5)

        self.appType = tk.StringVar(_master, "Not-Approved")
        self.appLab = tk.Label(self, text="View Approved or Not Approved Samples?", font=('Helvetica', 11))
        self.appLab.pack(side="top", fill="x", padx=20, pady=0)
       
        self.aaBut = tk.Radiobutton(self, text="Approved", variable=self.appType, value="Approved")
        self.aaBut.pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)
        self.naBut = tk.Radiobutton(self, text="Not Approved", variable=self.appType, value="Not-Approved")
        self.naBut.pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)

        self.submit = tk.Button(self, text="Submit", command=lambda: self.submitValues())
        self.submit.pack(side="top", fill="x", padx=20, pady=0)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(AppOptionPage)).pack(side="top", fill="x", padx=20, pady=5)

    def packList(self):
        #unpacking
        self.hlabel.pack_forget()
        self.elabel.pack_forget()
        self.amt.pack_forget()
        self.submit.pack_forget()
        self.appLab.pack_forget()
        self.aaBut.pack_forget()
        self.naBut.pack_forget()
        self.eplabel.pack_forget()


        #packing
        tk.Label(self, text="List of Entries", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(15, 5))
        if(self.appType.get() == "Approved"):
            tk.Label(self, text="Approved List", font=('Helvetica', 12)).pack(side="top", fill="x", padx=20, pady=(0,15))
        else:
            tk.Label(self, text="Not Approved List", font=('Helvetica', 12)).pack(side="top", fill="x", padx=20, pady=(0, 15))

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side="left", fill="y")

        lis = tk.Listbox(self, yscrollcommand=scrollbar.set)
        #print("values:", self.values)

        strVals = np.array([])
        strTit = "Row" + "   " + "Date" + "        "  + "SonEX Labs Prod. Name" + "        " + "Botanacor Submitted Name" + "          " + "Submitted By" + "      " + "In House/3rd Party" + "         " + "Comments" + "         " + "Approved By"
        strVals = np.append(strVals, strTit)

        if((getLastRow() > 1 and self.appType.get() == "Approved") or (self.appType.get() == "Not-Approved" and len(self.values) > 0)):
            for val in self.values:
                s = val[7] + "       " + val[0] + "     " + val[1] + "               " + val[2] + "                     " + val[3] + "                         " + val[4] + "                 " + val[5] + "             " + val[6]
                strVals = np.append(strVals, s)
            
        lis.insert(0, *strVals)

        scrollbar.config(command = strVals)
        lis.config(width=150)
        lis.pack(side="right", fill="x", padx=(5, 20), pady=(0, 15), expand=True)
        #print("strVals:", strVals)

    def submitValues(self):
        try:
            self.values = viewLastEntries(int(self.amt.get())) if self.appType.get() == "Approved" else getValuesFile(int(self.amt.get()))
            self.clearEntryValues()
            self.packList()
        except:
            tk.Label(self, text="Value Must Be a Number", font=('Helvetica', 11)).pack(side="bottom")

    def clearEntryValues(self):
        self.amt.delete(0, len(self.amt.get()))

class AppEditEntriesPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Edit Entries Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(20,5))

        self.appType = tk.StringVar(_master, "Approved")
        self.appLab = tk.Label(self, text="Edit Approved or Not Approved Samples?", font=('Helvetica', 11))
        self.apbut = tk.Radiobutton(self, text="Approved", variable=self.appType, value="Approved")
        self.napbut = tk.Radiobutton(self, text="Not Approved", variable=self.appType, value="Not Approved")

        self.appLab.pack(side="top", fill="x", padx=20, pady=0)
        self.apbut.pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)
        self.napbut.pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)

        self.subm = tk.Button(self, text="Submit", command=lambda: self.packing_list(_master, self.appType.get()))
        self.subm.pack(side="top", fill="x", padx=20, pady=(5, 5))
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(AppOptionPage)).pack(side="top", fill="x", padx=20, pady=(5, 10))

    def packing_list(self, _master, appType):
        self.values = getAllValuesFile() if self.appType.get() == "Not Approved" else viewLastEntries(getLastRow()-1)

        #unpacking
        self.appLab.pack_forget()
        self.apbut.pack_forget()
        self.napbut.pack_forget()
        self.subm.pack_forget()

        #packing
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")
        self.lis = tk.Listbox(self, yscrollcommand=self.scrollbar.set)

        strTit = "Row" + "   " + "Date" + "        " + "SonEX Labs Prod. Name" + "            " + "Botanacor Submitted Name" + "          " + "Submitted By" + "      " + "In House/3rd Party" + "         " + "Comments" + "         " + "Approved By"
        strVals = np.array(strTit)

        if(self.appType.get() == "Not Approved"):
            i = 1
            for val in self.values:
                s = str(i) + "       " + val[0] + "     " + val[1] + "               " + val[2] + "                     " + val[3] + "                         " + val[4] + "                 " + val[5] + "        " + val[6]
                strVals = np.append(strVals, s)
                i += 1
        else:
            for val in self.values:
                s = val[7] + "       " + val[0] + "     " + val[1] + "               " + val[2] + "                     " + val[3] + "                         " + val[4] + "                 " + val[5] + "        " + val[6]
                strVals = np.append(strVals, s)

        self.scrollbar.config(command = strVals)
        self.lis.config(width=100)
        self.lis.pack(side="left", fill="x", padx=(5, 20), pady=(0, 15), expand=True)

        self.lis.insert(0, *strVals)
        self.submitb = tk.Button(self, text="Submit", command=lambda: self.formData(_master, self.lis.get(self.lis.curselection())))
        self.submitb.pack(side="bottom", fill="x", padx=20, pady=(5, 5))

    def formData(self, _master, row):
        #unpacking
        self.lis.pack_forget()
        self.scrollbar.pack_forget()
        self.submitb.pack_forget()

        #getting values to pack
        #row = int((row.split())[0]) if self.appType.get() == "Approved" else int((row.split())[0]) - 1
        row = int((row.split())[0]) - 1
        print("row:", row)

        #packing
        #enter SonEX Labs Prod. Name
        tk.Label(self, text="Enter The SonEX Labs\' Product Name", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.sn = tk.Entry(self)
        self.sn.pack(side="top", fill="x", padx=100, pady=5)
        self.sn.insert(0, (self.values[row])[1])
        self.sn.config(width=50)

        #enter Botanacor Submitted Name
        tk.Label(self, text="Enter The Botanacor Submit Name", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.bn = tk.Entry(self)
        self.bn.pack(side="top", fill="x", padx=100, pady=5)
        self.bn.insert(0, (self.values[row])[2])# if self.appType.get() == "Approved" else self.id.insert(0, (self.values[row])[1])

        #type in who it was submitted by
        tk.Label(self, text="Who Was it Submitted By?", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.sub = tk.Entry(self)
        self.sub.pack(side="top", fill="x", padx=100, pady=5)
        self.sub.insert(0, (self.values[row])[3])# if self.appType.get() == "Approved" else self.sub.insert(0, (self.values[row])[2])

        #choose date from calendar
        tk.Label(self, text="Choose Date", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.dat = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, year=2020)
        self.dat.pack(padx=50, pady=5)
        self.dat.delete(0, len(self.dat.get()))
        self.dat.insert(0, (self.values[row])[0])# if self.appType.get() == "Approved" else self.dat.insert(0, (self.values[row])[0])

        #select made in house or 3rd party
        self.v = tk.StringVar(_master, (self.values[row])[4])# if self.appType.get() == "Approved" else tk.StringVar(_master, (self.values[row])[3])
        tk.Label(self, text="Made In House or 3rd Party?", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        check = [("In-House", "In-House"), ("3rd-Party", "3rd-Party")]
        for op, val in (check):
            tk.Radiobutton(self, text=op, variable=self.v, value=val).pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)

        #type in comments
        tk.Label(self, text="Comments (Analysis Needed)", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.com = tk.Entry(self)
        self.com.pack(side="top", fill="x", padx=100, pady=5)
        self.com.insert(0, (self.values[row])[5])# if self.appType.get() == "Approved" else self.com.insert(0, (self.values[row])[4])

        if(self.appType.get() == "Approved"):
            #type in approved
            tk.Label(self, text="Approved By", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
            self.apps = tk.Entry(self)
            self.apps.pack(side="top", fill="x", padx=100, pady=5)
            self.apps.insert(0, (self.values[row])[6])


            
        self.submitb2 = tk.Button(self, text="Submit", command=lambda: self.submitRow(_master, row))
        self.submitb2.pack(side="bottom", fill="x", padx=20, pady=(5, 5))

    def submitRow(self, _master, row):
        if(self.appType.get() == "Approved"):
            data = [self.dat.get(), self.sn.get(), self.bn.get(), self.sub.get(), self.v.get(), self.com.get(), self.apps.get()]
        else:
            data = [self.dat.get(), self.sn.get(), self.bn.get(), self.sub.get(), self.v.get(), self.com.get(), "Not-Approved"]
        
        editByRowOption(row+1, data=data) if self.appType.get() == "Approved" else editByRowOptionFile(row, data)
        tk.Label(self, text="Saved Edit", font=('Helvetica', 11)).pack(side="bottom")
        _master.switch_frame(AppEditEntriesPage)


### for SAMPLERS
class OptionPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Options Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(10,20))

        tk.Button(self, text="Log A Sample", command=lambda: _master.switch_frame(LogSamplePage)).pack(side='top', fill='x', padx=20, pady=(5,0))
        tk.Button(self, text="View Samples", command=lambda: _master.switch_frame(ViewEntriesPage)).pack(side="top", fill="x", padx=20, pady=(5,0))
        tk.Button(self, text="Edit the Most Recent Not Approved Sample", command=lambda: _master.switch_frame(EditRecentPage)).pack(side="top", fill="x", padx=20, pady=(5,10))
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(StartPage)).pack(side="top", fill="x", padx=20, pady=5)

class ViewEntriesPage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        self.amt = None
        self.values = None

        self.eplabel = tk.Label(self, text="Entries Page", font=('Helvetica', 18, "bold"))
        self.eplabel.pack(side="top", fill="x", padx=20, pady=15)

        #edit how many rows to view
        self.hlabel = tk.Label(self, text="How many rows do you want to view", font=('Helvetica', 14))
        self.hlabel.pack(side="top", fill="x", padx=20, pady=5)
        self.elabel = tk.Label(self, text="(For Example, To view the last 3 entries just enter \"3\")", font=('Helvetica', 10))
        self.elabel.pack(side="top", fill="x", padx=20, pady=0)

        self.amt = tk.Entry(self)
        self.amt.pack(side="top", fill="x", padx=100, pady=5)

        self.appType = tk.StringVar(_master, "Not-Approved")
        self.appLab = tk.Label(self, text="View Approved or Not Approved Samples?", font=('Helvetica', 11))
        self.appLab.pack(side="top", fill="x", padx=20, pady=0)
       
        self.aaBut = tk.Radiobutton(self, text="Approved", variable=self.appType, value="Approved")
        self.aaBut.pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)
        self.naBut = tk.Radiobutton(self, text="Not Approved", variable=self.appType, value="Not-Approved")
        self.naBut.pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)

        self.submit = tk.Button(self, text="Submit", command=lambda: self.submitValues())
        self.submit.pack(side="top", fill="x", padx=20, pady=0)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(OptionPage)).pack(side="top", fill="x", padx=20, pady=5)

    def packList(self):
        #unpacking
        self.hlabel.pack_forget()
        self.elabel.pack_forget()
        self.amt.pack_forget()
        self.submit.pack_forget()
        self.appLab.pack_forget()
        self.aaBut.pack_forget()
        self.naBut.pack_forget()
        self.eplabel.pack_forget()


        #packing
        tk.Label(self, text="List of Entries", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(15, 5))
        if(self.appType.get() == "Approved"):
            tk.Label(self, text="Approved List", font=('Helvetica', 12)).pack(side="top", fill="x", padx=20, pady=(0,15))
        else:
            tk.Label(self, text="Not Approved List", font=('Helvetica', 12)).pack(side="top", fill="x", padx=20, pady=(0, 15))

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side="left", fill="y")

        lis = tk.Listbox(self, yscrollcommand=scrollbar.set)
        #print("values:", self.values)
        #print("self.appType.get():", self.appType.get())
        
        strVals = np.array([])
        strTit = "Row" + "   " + "Date" + "        "  + "SonEX Labs Prod. Name" + "        " + "Botanacor Submitted Name" + "          " + "Submitted By" + "      " + "In House/3rd Party" + "         " + "Comments" + "         " + "Approved By"
        strVals = np.append(strVals, strTit)

        if((getLastRow() > 1 and self.appType.get() == "Approved") or (self.appType.get() == "Not-Approved" and len(self.values) > 0)):
            for val in self.values:
                s = val[7] + "       " + val[0] + "     " + val[1] + "                  " + val[2] + "                     " + val[3] + "                         " + val[4] + "                 " + val[5] + "             " + val[6]
                strVals = np.append(strVals, s)
            
        lis.insert(0, *strVals)       
        #print("strVals:", strVals)

        scrollbar.config(command = strVals)
        lis.config(width=150)
        lis.pack(side="right", fill="x", padx=(5, 20), pady=(0, 15), expand=True)

    def submitValues(self):
        try:
            #print("appType:", self.appType.get())
            self.values = viewLastEntries(int(self.amt.get())) if self.appType.get() == "Approved" else getLastValuesFile(int(self.amt.get()))
            #print("values:", self.values)
            self.clearEntryValues()
            self.packList()
        except:
            tk.Label(self, text="Value Must Be a Number", font=('Helvetica', 11)).pack(side="bottom")

    def clearEntryValues(self):
        self.amt.delete(0, len(self.amt.get()))

class LogSamplePage(tk.Frame):
    def __init__(self, _master):
        tk.Frame.__init__(self, _master)
        self.sn = None
        self.bn = None
        self.sub = None
        self.dat = None
        self.v = None
        self.com = None

        tk.Label(self, text="Log Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=20)
        
        #enter sample id
        tk.Label(self, text="Enter The SonEX Labs\' Product Name", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.sn = tk.Entry(self)
        self.sn.pack(side="top", fill="x", padx=100, pady=5)

        #enter sample id
        tk.Label(self, text="Enter The Botanacor Submit Name", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.bn = tk.Entry(self)
        self.bn.pack(side="top", fill="x", padx=100, pady=5)

        #type in who it was submitted by
        tk.Label(self, text="Who Was it Submitted By?", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.sub = tk.Entry(self)
        self.sub.pack(side="top", fill="x", padx=100, pady=5)

        #choose date from calendar
        tk.Label(self, text="Choose Date", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.dat = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, year=2020)
        self.dat.pack(padx=50, pady=5)

        #select made in house or 3rd party
        self.v = tk.StringVar(_master, "In-House")
        tk.Label(self, text="Made In House or 3rd Party?", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        check = [("In-House", "In-House"), ("3rd-Party", "3rd-Party")]
        for op, val in (check):
            tk.Radiobutton(self, text=op, variable=self.v, value=val).pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)

        #type in comments
        tk.Label(self, text="Comments (Analysis Needed)", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
        self.com = tk.Entry(self)
        self.com.pack(side="top", fill="x", padx=100, pady=5)

        tk.Button(self, text="Submit", command=lambda: self.submitValues()).pack(side="top", fill="x", padx=20, pady=0)
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(OptionPage)).pack(side="top", fill="x", padx=20, pady=5)

    def submitValues(self):
        flag = False
        if(self.sn.get() != "" and self.bn.get() != "" and self.dat.get() != "" and self.sub.get() != "" and self.com.get() != ""):
            subm = (self.sub.get())[0].upper() + (self.sub.get())[1:]
            sn = (self.sn.get())[0].upper() + (self.sn.get())[1:]
            bn = (self.bn.get())[0].upper() + (self.bn.get())[1:]
            ent = self.dat.get() + " " + sn + " " + bn + " " + subm + " " + self.v.get() + " " + self.com.get() +  " Not-Approved"
            addEntrytoNAFile(ent)
            tex = "Added Entry To Not Yet Approved List"
            tk.Label(self, text=tex, font=('Helvetica', 11)).pack(side="bottom")
            self.clearEntryValues(flag)
        else:
            self.blabel = tk.Label(self, text="No Blanks Allowed", font=('Helvetica', 11))
            self.blabel.pack(side="bottom")
            flag = True

    def clearEntryValues(self, flag):
        self.sn.delete(0, len(self.sn.get()))
        self.bn.delete(0, len(self.bn.get()))
        self.sub.delete(0, len(self.sub.get()))
        self.com.delete(0, len(self.com.get()))
        if(flag):
            self.blabel.pack_forget()        

#############optimize
class EditRecentPage(tk.Frame):
    def __init__(self, _master):
        Flag = True

        tk.Frame.__init__(self, _master)
        tk.Label(self, text="Edit Entries Page", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=(20,5))

        na = open("NotApproved.txt", "r")
        read = na.read()
        if(read != ""):
            values = ((read.split('\n'))[-2]).split()
        else:
            tk.Label(self, text="No Not Approved Samples", font=('Helvetica', 11)).pack(side="bottom", fill="x", padx=20, pady=0)
            Flag = False
        na.close()
        #print("values:", values)

        if(Flag):
            #enter SonEX Labs Prod. Name
            tk.Label(self, text="Enter The SonEX Labs\' Product Name", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
            self.sn = tk.Entry(self)
            self.sn.pack(side="top", fill="x", padx=100, pady=5)
            self.sn.insert(0, values[1])
            self.sn.config(width=50)

            #enter Botanacor Submitted Name
            tk.Label(self, text="Enter The Botanacor Submit Name", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
            self.bn = tk.Entry(self)
            self.bn.pack(side="top", fill="x", padx=100, pady=5)
            self.bn.insert(0, values[2])

            #type in who it was submitted by
            tk.Label(self, text="Who Was it Submitted By?", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
            self.sub = tk.Entry(self)
            self.sub.pack(side="top", fill="x", padx=100, pady=5)
            self.sub.insert(0, values[3])

            #choose date from calendar
            tk.Label(self, text="Choose Date", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
            self.dat = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2, year=2020)
            self.dat.pack(padx=50, pady=5)
            self.dat.delete(0, len(self.dat.get()))
            self.dat.insert(0, values[0])

            #select made in house or 3rd party
            self.v = tk.StringVar(_master, values[4])
            tk.Label(self, text="Made In House or 3rd Party?", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
            check = [("In-House", "In-House"), ("3rd-Party", "3rd-Party")]
            for op, val in (check):
                tk.Radiobutton(self, text=op, variable=self.v, value=val).pack(side="top", fill="x", padx=20, pady=5, anchor=tk.W)

            #type in comments
            tk.Label(self, text="Comments (Analysis Needed)", font=('Helvetica', 11)).pack(side="top", fill="x", padx=20, pady=0)
            self.com = tk.Entry(self)
            self.com.pack(side="top", fill="x", padx=100, pady=5)
            self.com.insert(0, values[5])

            tk.Button(self, text="Submit", command=lambda: self.formData()).pack(side="top", fill="x", padx=20, pady=(5, 5))
        tk.Button(self, text="Back", command=lambda: _master.switch_frame(OptionPage)).pack(side="top", fill="x", padx=20, pady=(5, 10))

    def formData(self):
        data = self.dat.get() + " "  + self.sn.get() + " " + self.bn.get() + " " + self.sub.get() + " " + self.v.get() + " " + self.com.get() + " Not-Approved"
        self.submitRow(data)

        tk.Label(self, text="Saved Edit", font=('Helvetica', 11)).pack(side="bottom")

    #************OPTIMIZE*****************
    def submitRow(self, data):
        #always last file in not approved txt
        na = open("NotApproved.txt", "r")
        ef = na.read()
        na.close()
        lines = ef.split("\n")
        s = "\n".join(lines[:-2])
        na = open("NotApproved.txt", "w")
        for i in range(len(s)):
            na.write(s[i])
        na.write("\n" + data + "\n")
        na.close()



###########TEST####################

class Test():
    def testAddEntry(self):
        #e = ['5/24/20', 'Iso-D-NHom' , 'LBF-052420-001:Iso', 'Rico P.', 'In-House', 'Potency', 'Wendy']
        #d = ['5/15/20', 'Wax-D-NHom' , 'LBF-051520-001:Wax', 'Shawn F.', 'In-House', 'Potency', 'Wendy']
        #f = ['5/25/20', 'Oleo-D-Wx-NHom' , 'LBF-052520-001:Oleo', 'Robbie K.', 'In-House', 'Potency', 'Derek']
        #g = ['5/25/20', 'Oleo-D-DeWx-NHom' , 'LBF-052520-002:Oleo', 'Rico P.', 'In-House', 'Potency', 'Derek']
        
        e = '5/24/20' + ' ' + 'Iso-D-NHom' + ' ' + 'LBF-052420-001:Iso' + ' ' + 'Rico' + ' ' + 'In-House' + ' ' + 'Potency' + ' Not-Approved'
        d = '5/15/20' + ' ' + 'Wax-D-NHom' + ' ' + 'LBF-051520-001:Wax' + ' ' + 'Shawn' + ' ' + 'In-House' + ' ' + 'Potency' + ' Not-Approved'
        f = '5/25/20' + ' ' + 'Oleo-D-Wx-NHom' + ' ' + 'LBF-052520-001:Oleo' + ' ' + 'Robbie' + ' ' + 'In-House' + ' ' + 'Potency' + ' Not-Approved'
        g = '5/25/20' + ' ' + 'Oleo-D-DeWx-NHom' + ' ' + 'LBF-052520-002:Oleo' + ' ' + 'Rico' + ' ' + 'In-House' + ' ' + 'Potency' + ' Not-Approved'

        addEntrytoNAFile(e)
        addEntrytoNAFile(d)
        addEntrytoNAFile(f)
        addEntrytoNAFile(g)

    def testRemove(self):
        removeLastEntry()

    def testRemoveAll(self):
        removeAll()

    def testViewEntries(self):
        viewLastEntries(1)
        viewLastEntries(2)
        viewLastEntries(3)
        viewLastEntries(4)
        viewLastEntries(5)

    def testEditEntries(self):
        editByRowOption(1)

####################################

if __name__ == '__main__':
    app = Application()
    app.wm_title('The Sample Logger')
    app.mainloop()
