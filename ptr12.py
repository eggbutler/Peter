#!/usr/bin/env python
#!file: ptr12.pyw
###############################################################################
#                                DON'T PANIC                                  #
#stardate:  2014.05.23                              SWVersion:             1.0#
#Name:      ptr12.pyw                               SWPlatform:     Python 2.7#
#Author:    Dave at eggbutler com                   AKA:         David D. Choi#
#Desc:      This is my first step at making a timer for work that will keep   #
#           track of the time I spend on projects.                            #
###############################################################################
#---0----|--- 10---|--- 20---|--- 30---|--- 40---|--- 50---|--- 60---|--- 70---|
print '\n\
     Say hi to...         \n\
  _____  _______   _____  \n\
 |  __ \\|__   __| |  __ \\ \n\
 | |__) |__| | ___| |__) |\n\
 |  ___/ _ \\ |/ _ \\  _  / \n\
 | |  |  __/ |  __/ | \\ \\ \n\
 |_|   \\___|_|\\___|_|  \\_\\\n\
\n\
Project Time Recorder \n\
                          '
import datetime
from Tkinter import *
import time
import csv
import tkMessageBox
import os
from operator import itemgetter

bgColor = '#9AA'
if os.name == 'posix': #Should add 'mac' also?  MBA prints posix.
    bgColor2 = '#FFFFFF'
else:
    bgColor2 = '#EFF'
pGreen = '#66FF66'
pRed = '#FF4D4D'
pYellow = '#FFFF66'
pBlue = '#3399FF'
framePadding = 5

#widths
winWidth = 46 #general Width of window in characters
JLBWidth = 12  #jobListbox width in characters
DLBWidth = winWidth-JLBWidth #Description Listbox is remaining in characters
jobQTY = 15 #number of jobs to show (height of Listbox's) in characters

#main list of job numbers, descriptions, and number of uses
global inRecord
#inRecord   list of jobs

buttonPaddingXY = 2 #padding for all the buttons X and Y for all 10 buttons in pixels.
fatPadding = buttonPaddingXY*6 #padding for all the edges inside of a frame in pixels
sortButtonFactor = 4.2 #Inverse factor width of the sort buttons (it's winWidth/sortButtonFactor for button width)
commandButtonFactor = 5.2 #Inverse factor width of the (bottom 6) command buttons (it's commandButtonFactor/sortButtonFactor for button width)

sortButtonHeight = 1

folderName = 'jobFolder'

class Dialog(Frame): #frame for lisboxes and functions to happen to listboxes
    def __init__(self, master):
        leftSet = Frame(master)
        middleSet = Frame(master)
        rightSet = Frame(master)
        
        for x in [leftSet, middleSet, rightSet]:
            x.configure(bg= bgColor2)
            x.pack(side= LEFT, anchor= N)
        
        self.scrollbary = Scrollbar(rightSet, orient=VERTICAL)
        self.scrollbary.config(command=self.yview)
        self.scrollbarx = Scrollbar(middleSet, orient=HORIZONTAL)

        #note that yscrollcommand is set to a custom method for each listbox
        self.jobListbox= Listbox(leftSet, 
          yscrollcommand= self.yscroll1, 
          height= jobQTY, 
          width= JLBWidth)
        fakeListbox1= Listbox(leftSet) #to balance out fakeListbox2 in terms of width
        fakeListbox2= Listbox(rightSet) #to get scroll bar to be the correct height
        for flb in [fakeListbox1, fakeListbox2]:
            flb.configure(
              height= jobQTY, 
              background= bgColor2, 
              width= 0, 
              border= 0 , 
              highlightthickness= 0, 
              relief= FLAT, 
              takefocus= 0, 
              state= DISABLED)
        self.descListbox= Listbox(middleSet, yscrollcommand=self.yscroll2, 
          xscrollcommand= self.scrollbarx.set, height=jobQTY, width=DLBWidth)
        self.descListbox.bind ("<Return>", lambda x :self.startCount())
        self.jobListbox.bind ("<Return>", lambda x :self.startCount())
        self.scrollbarx.config(command=self.descListbox.xview)
        
        #leftSet Frame
        fakeListbox1.pack     (side = LEFT, pady = 2)
        self.jobListbox.pack  (side = LEFT)
        #middleSet Frame                    
        self.descListbox.pack (side = TOP)
        self.scrollbarx.pack  (side = TOP,  fill = X)
        #rightSet Frame                     
        self.scrollbary.pack  (side = LEFT, fill = Y)
        fakeListbox2.pack     (side = LEFT, pady = 2)

        for item in range(len(inRecord)): #fill Listboxes with inRecord
            self.jobListbox.insert(END, inRecord[item][0])
            self.descListbox.insert(END, inRecord[item][1])
        self.scrollbary.config(command=self.yview)

    def yscroll1(self, *args):
        if self.descListbox.yview() != self.jobListbox.yview():
            self.descListbox.yview_moveto(args[0])
        self.scrollbary.set(*args)

    def yscroll2(self, *args):
        if self.jobListbox.yview() != self.descListbox.yview():
            self.jobListbox.yview_moveto(args[0])
        self.scrollbary.set(*args)

    def yview(self, *args):
        apply(self.jobListbox.yview, args)
        apply(self.descListbox.yview, args)

    def addJob(self):
        global inRecord
        print 'Adding'
        jobNum = mainFrame.jobNumberEntry.get()
        jobDesc = mainFrame.jobDescriptionEntry.get()
        if jobNum == '' or jobDesc == '':
            tkMessageBox.showerror('Oops!','Please, no blank entries!')
            print 'Oops-Blank entry problem'
        elif jobNum.len() != '8' and jobNum[3:].isdigit():
            tkMessageBox.showerror('Try again?','I don\'t think that was a valid format.\nI need something like: "AAA#####"')
            print 'invalid project format'
        else:
            self.jobListbox.insert(END, jobNum)
            self.descListbox.insert(END, jobDesc)
            inRecord.append([jobNum,jobDesc,1,str(datetime.date.today())])
            self.jobListbox.selection_clear(0,END)
            self.jobListbox.selection_set(END)
            self.jobListbox.activate(END)
            self.jobListbox.yview(END)
            self.jobListbox.focus_set()
            saveJobs()
            
            print 'Added'

    def remJob(self):
        print 'Removing'
        jobListItem = map(int, self.jobListbox.curselection())
        descListItem = map(int, self.descListbox.curselection())
        if len(jobListItem) == 0 and len(descListItem) == 1:
            #Description is hightlighted
            self.descListbox.delete(ACTIVE)
            self.jobListbox.delete(descListItem[0])
            inRecord.pop(descListItem[0])
            saveJobs()
            print 'Removed slot number ' + str(descListItem[0])
        elif len(jobListItem) == 1 and len(descListItem) == 0:
            #Job is hightlighted
            self.jobListbox.delete(ACTIVE)
            self.descListbox.delete(jobListItem[0])
            inRecord.pop(jobListItem[0])
            saveJobs()
            print 'Removed slot number ' + str(jobListItem[0])
        else:
            tkMessageBox.showerror('Darn it', 'You must select a job number or description first!')

    def sortUsage(self):
        global inRecord
        print 'Sorting by Usage'
        inRecord.sort(key= lambda x: int(x[2]), reverse = True)
        #=itemgetter(2))
        self.clearNload()
        
    def sortNum(self):
        global inRecord
        print 'Sorting by Job Number'
        inRecord.sort(key= lambda k: k[0].lower())
        self.clearNload()

    def sortDesc(self):
        global inRecord
        print 'Sorting by Description'
        inRecord.sort(key= lambda k: k[1].lower())
        self.clearNload()

    def sortDate(self):
        global inRecord
        print 'Sorting by Date'
        inRecord.sort(key=itemgetter(3), reverse = True)
        self.clearNload()
    
    def clearNload(self):  #this is where I repopulate the job list 
        self.jobListbox.delete(0,END)
        self.descListbox.delete(0,END)
        for item in range(len(inRecord)):
            self.jobListbox.insert(END, inRecord[item][0])
            self.descListbox.insert(END, inRecord[item][1])
        saveJobs()
        print 'Sorted'

    def startCount(self):
        print 'Starting'
        jobListItem = map(int, self.jobListbox.curselection())
        descListItem = map(int, self.descListbox.curselection())
        if len(jobListItem) == 0 and len(descListItem) == 1:
            #Description is hightlighted
            timerWin(self.jobListbox.get(descListItem[0]), 
              self.descListbox.get(ACTIVE)) 
            #update the inRecord to today:
            inRecord[descListItem[0]][3] = str(datetime.date.today())
            inRecord[descListItem[0]][2] = int(inRecord[descListItem[0]][2]) + 1
        elif len(jobListItem) == 1 and len(descListItem) == 0:
            #Job is hightlighted
            timerWin(self.jobListbox.get(ACTIVE), self.descListbox.get(jobListItem[0]))
            #update the inRecord to today:
            inRecord[jobListItem[0]][3] = str(datetime.date.today())
            inRecord[jobListItem[0]][2] = int(inRecord[jobListItem[0]][2]) + 1
        else:
            tkMessageBox.showerror('Egad', 'You must select a job number or description first!')

    def addTimeQual(self):#check that a project is highlighted before adding time
        jobListItem = map(int, self.jobListbox.curselection())
        descListItem = map(int, self.descListbox.curselection())
        if len(jobListItem) == 0 and len(descListItem) == 1:
            #Description is hightlighted
            jobNum = self.jobListbox.get(descListItem[0]) #job number
            jobDesc = self.descListbox.get(ACTIVE) #job Description...I should add something here to denote manaul????
            addTime(jobNum, jobDesc)
            inRecord[descListItem[0]][3] = str(datetime.date.today())
            inRecord[descListItem[0]][2] = int(inRecord[descListItem[0]][2]) + 1
            #update the inRecord to today:
        elif len(jobListItem) == 1 and len(descListItem) == 0:
            #Job is hightlighted
            jobNum = self.jobListbox.get(ACTIVE) #job number
            jobDesc = self.descListbox.get(jobListItem[0]) #job Description...I should add something here to denote manaul????
            addTime(jobNum, jobDesc)
            #update the inRecord to today:
            inRecord[jobListItem[0]][3] = str(datetime.date.today())
            inRecord[jobListItem[0]][2] = int(inRecord[jobListItem[0]][2]) + 1
        else:
            tkMessageBox.showerror('Egad', 'You must select a job number or description first!')

def addTime(jobNum, jobDesc):  #OK we qualified that something is highlighted, lets check some other stuff.
    print 'I am adding time here'
    minToAdd = addTimeMinute.get()
    hrToAdd = addTimeHour.get()
    if minToAdd.isdigit() and hrToAdd.isdigit(): #OK...so they didn't put in funny characters
        if int(minToAdd)== 0 and int(hrToAdd)== 0 :
            tkMessageBox.showerror('Oof!', 'I don\'t want to add 0 time')
        elif minToAdd >= 60:#If they did something stupid like add 90 minutes
            hrToAdd = int(minToAdd)/60 + int(hrToAdd)
            minToAdd = int(minToAdd)%60
            logTime(jobNum, jobDesc, hrToAdd, minToAdd)
            tkMessageBox.showinfo('Don\'t forget', 'Try not to forget to start the timer next time.')
            print 'I added time here'
        else:
            logTime(jobNum, jobDesc, hrToAdd, minToAdd)
            tkMessageBox.showinfo('Don\'t forget', 'Try not to forget to start the timer next time.')
            print 'If added time here'
    else:
        tkMessageBox.showerror('Blargh!', 'You can only put in whole integers for hours and minutes!!!')

def loadJobs(): #Go find the CSV, Read it and put the contents into inRecord
    global inRecord
    csvFile = open('jobs.csv', 'rb')
    newRecord = csv.reader(csvFile, dialect = 'excel')
    inRecord = []
    for row in newRecord:
        inRecord.append(row)

def saveJobs(): #Take inRecord and save it to jobs.CSV
    print 'Saving'
    csvFile = open('jobs.csv', 'w')
    try:
        with open('jobs.csv', 'r+b') as logData:
            writer = csv.writer(logData, dialect = "excel")
            for row in inRecord:
                writer.writerow(row)
            logData.close()
    except:
        # logErrorCode('writeSample error ' + labID)
        with open('job-error.csv', 'wb') as logErrorData:
            writer = csv.writer('job-error.csv', dialect = "excel")
            for row in inRecord:
                writer.writerow(row)
            tkMessageBox.showerror('FileError!','Unknown Error! data saved to job-error.csv\nPlease inform the IT staff of your problems!')
            logErrorData.close()
    print 'Saved'

def timerWin(jobNum, jobDesc): #While timing open this popup.
    global refWin
    saveJobs()
    timeStart = datetime.datetime.now()
    refWin = Toplevel()
    refWin.title('Timing in Progress')
    refWin.wm_attributes("-topmost", 1)
    refWin.resizable(0,0)
    header=Label(refWin, text = jobNum + ' - ' + jobDesc)
    Description = jobNum + ' - ' + jobDesc + '\nStarted :' + str(timeStart)
    stopButton = Button(refWin, text = 'Stop', command = lambda:stopCount(
      timeStart,jobNum, jobDesc), background= pRed)
    header.pack()
    stopButton.pack()
    stopButton.focus_set()
        
def stopCount(timeStart, jobNum, jobDesc): #Check if logged time is less than a minute
    global inRecord
    print 'Stopping'
    today = datetime.date.today()
    tSpent = datetime.datetime.now()-timeStart
    hours, minutes = tSpent.seconds//3600, (tSpent.seconds//60)%60
    
    if hours == 0 and minutes == 0:
        print 'less than a minute'
    else:
        logTime(jobNum, jobDesc, hours, minutes)
    refWin.destroy()

def logTime(jobNum, jobDesc, hours, minutes):  #Record time in latest Log sheet
    today = datetime.date.today()
    nextSunday = today + datetime.timedelta(6-today.weekday())
    jobRecord = os.path.join(folderName, str(nextSunday) + '.csv')
    if os.path.isfile(jobRecord): #File was already started
        with open(jobRecord, 'ab') as weekRecord:
            writer = csv.writer(weekRecord, dialect = 'excel')
            writer.writerow((today, jobNum, jobDesc, hours, minutes)) #can't leave blanks :(
        weekRecord.close()


    else:           #File is not there so start one:
        with open(jobRecord, 'wb') as weekRecord:
            writer = csv.writer(weekRecord, dialect = "excel")
            writer.writerow(('Date Worked', 'Project Number', 'Project Desc', 
              'Hours','Minutes'))
            #can't leave blanks :(
            writer.writerow((today, jobNum, jobDesc, hours, minutes)) 
        weekRecord.close()
    print 'Stopped' 
    
class mFrame (Frame): #mframe is the Main Frame and the Main Window 
    loadJobs()

    def openLog(self):
        print 'Open Log'
        today = datetime.date.today()
        nextSunday = today + datetime.timedelta(6-today.weekday())
        jobRecord = os.path.join(folderName, str(nextSunday) + '.csv')
        if os.path.isfile(jobRecord):
            os.startfile(jobRecord)
        else:
            tkMessageBox.showerror('Nooo!!!', 'You haven\'t done anything this week so there is nothing to open.\nTry and stop being so lazy and log some work already.')

    def openJobs(self):
        print 'Open Jobs'
        os.startfile('jobs.csv')

    def __init__(self, master):
        global addTimeMinute, addTimeHour
        inputFrameHolder=   Frame(master)
        
        listboxFrameHolder= Frame(master)
        listboxFrame=       Frame(listboxFrameHolder)
        
        sortFrameHolder= Frame(master)
        sortFrame=       Frame(sortFrameHolder)
        
        buttonFrameHolder  = Frame(master)
        buttonFrame  = Frame(buttonFrameHolder)

        inputFrame1  = Frame(inputFrameHolder)
        inputFrame2  = Frame(inputFrameHolder)

        for x in [inputFrameHolder, listboxFrameHolder, listboxFrame, sortFrameHolder, sortFrame, buttonFrameHolder, buttonFrame, inputFrame1, inputFrame2, inputFrameHolder]:
            x.configure(bg= bgColor2)

        for x in [inputFrameHolder, listboxFrameHolder, sortFrameHolder, buttonFrameHolder]:
            x.pack(padx= framePadding, pady= framePadding, ipadx = buttonPaddingXY, ipady = fatPadding, fill= X)
        
        for x in [listboxFrame, sortFrame, buttonFrame, inputFrame1, inputFrame2]:
            x.pack(expand = TRUE)
            
        mainLB = Dialog(listboxFrame)

        #Add Job inputFrame1
        jobNumberLabel = Label(inputFrame1, text = 'Job No.', background= bgColor2)
        jobDescriptionLabel = Label(inputFrame1, text = 'Description',background= bgColor2)
        self.jobNumberEntry = Entry(inputFrame1, width = JLBWidth)
        self.jobDescriptionEntry = Entry(inputFrame1, width = DLBWidth)
        self.jobDescriptionEntry.bind ("<Return>", lambda x : mainLB.addJob())
        jobNumberLabel.grid      (row = 0, column = 0, padx = buttonPaddingXY, pady = (buttonPaddingXY,0))
        jobDescriptionLabel.grid (row = 0, column = 1, padx = buttonPaddingXY, pady = (buttonPaddingXY,0))
        self.jobNumberEntry.grid      (row = 1, column = 0, padx = buttonPaddingXY, pady = (0,buttonPaddingXY))
        self.jobDescriptionEntry.grid (row = 1, column = 1, padx = buttonPaddingXY, pady = (0,buttonPaddingXY))

        #Add Job inputFrame2
        addJobButton = Button(inputFrame2, text = 'Add Job', command = lambda : mainLB.addJob(), background= pBlue, fg = 'white', width = int(winWidth/2.2), height = 1)
        addJobButton.pack (side = LEFT, padx = buttonPaddingXY*2, pady = (buttonPaddingXY*4,fatPadding))

        #Sorting buttons:
        sortLabel = Label(sortFrame, text = 'Sort list contents by...', background= bgColor2)
        sortPopButton = Button(sortFrame, text = 'Usage', command = lambda: mainLB.sortUsage())
        sortJobNumButton = Button(sortFrame, text = 'Job No.', command = lambda: mainLB.sortNum())
        sortDescButton = Button(sortFrame, text = 'Description', command = lambda: mainLB.sortDesc())
        sortDateButton = Button(sortFrame, text = 'Last Used', command = lambda: mainLB.sortDate())
        
        sortLabel.pack(side = TOP)
        for x in [sortPopButton, sortJobNumButton, sortDescButton, sortDateButton]:
            x.configure(width = int(winWidth/sortButtonFactor), height = int(sortButtonHeight))
            x.pack(side = LEFT, padx = buttonPaddingXY, pady = buttonPaddingXY)

        #Command buttons:
        commandButtonLabel = Label(buttonFrame, text= 'Do something!', background= bgColor2)
        startButton= Button(buttonFrame, text= 'Start', command= lambda:mainLB.startCount(), background= pGreen)
        openLogButton = Button(buttonFrame, text = 'Edit Log', command = lambda : self.openLog(), background= pBlue, fg = 'white')
        openJobsButton = Button(buttonFrame, text = 'Edit Jobs', command = lambda : self.openJobs(), background= pBlue, fg = 'white')
        remJobButton = Button(buttonFrame, text = 'Delete Job', command = lambda : mainLB.remJob(), background= pRed, fg = 'white')
        quitButton = Button(buttonFrame, text ='Quit', command = root.quit, background= pRed, fg = 'white')

        #just add time button
        addTimeSpace = Canvas(buttonFrame, background = bgColor, height = 5)
        addTimeLabel = Label(buttonFrame, text = 'Were you bad? Need to add some time, after the fact?', background = bgColor2)
        addMinLabel = Label(buttonFrame, text = 'Minutes:', background = bgColor2)
        addTimeMinute = Entry(buttonFrame, width = 4)
        addTimeMinute.insert(0,'0')
        addHourLabel = Label(buttonFrame, text = 'Hours:', background = bgColor2)
        addTimeHour = Entry(buttonFrame, width = 4)
        addTimeHour.insert(0,'0')
        addTimeButton = Button(buttonFrame, text = 'Add Time', command = lambda : mainLB.addTimeQual(), background = pYellow, fg = 'black')

#this is row one in the buttonFrame
        commandButtonLabel.grid (row = 0, columnspan = 5) 
        colCounter = 0
        for x in [startButton, openLogButton, openJobsButton, remJobButton, quitButton]:
            x.configure (width= int(winWidth/commandButtonFactor), height= 2, wraplength= 50)
            x.grid (row = 1, column = colCounter)
            colCounter +=1
#[addTimeMinute, addTimeHour, addTimeButton]:
        addTimeSpace.grid (row = 2, columnspan = 5, sticky = 's', pady = 5)
        addTimeLabel.grid (row = 3, columnspan = 5)
        addTimeButton.configure (width= int(winWidth/commandButtonFactor), height= 2, wraplength= 50)
        colCounter = 0
        for x in [addMinLabel, addTimeMinute, addHourLabel, addTimeHour, addTimeButton]:
            x.grid (row = 4, column = colCounter)
            colCounter +=1

#addMinLabel, addTimeMinute, addHourLabel, addTimeHour, addTimeButton

            # addMinLabel.grid     (row = 2, column = 0)
            # addTimeMinute.grid   (row = 2, column = 1)
            # addHourLabel.grid    (row = 2, column = 2)
            # addTimeHour.grid     (row = 2, column = 3)
            # addTimeButton.grid   (row = 2, column = 4)

root = Tk()
root.configure(background= bgColor)
root.title('Project Time Recorder')
root.resizable(0,0)
if os.name == 'nt':
    root.iconbitmap(default = 'Peter-icon2.ico') #code only for windows!!
mainFrame = mFrame(root)
if __name__ == "__main__":
    root.mainloop()