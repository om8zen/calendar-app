from time import localtime, mktime, strptime
from calendar import weekday, monthrange
from Tkinter import Tk, Toplevel, Frame, Label, Button, Entry, Listbox, Scrollbar
from tkFileDialog import askopenfilename, asksaveasfilename

ONCE, DAILY, WEEKLY = 0, 1, 2
MON, TUE, WED, THU, FRI, SAT, SUN = 0, 1, 2, 3, 4, 5, 6
WORKDAYS = [MON, TUE, WED, THU, FRI]

# times of day on which school "blocks" fall
BLOCKS = [
    { "a" : (9, 0), "b" : (10, 20), "c" : (12, 35), "d" : (13, 55) }, ## Monday
    { "b" : (9, 0), "a" : (10, 20), "d" : (12, 35), "c" : (13, 55) }, ## Tuesday
    { "c" : (9, 0), "d" : (10, 20), "a" : (12, 35), "b" : (13, 55) }, ## Wednesday
    { "d" : (9, 0), "c" : (10, 20), "b" : (12, 35), "a" : (13, 55) }, ## Thursday
    { "a" : (9, 0), "b" : (10, 20), "c" : (12, 35), "d" : (13, 55) }, ## Friday
    ]

MONTHS_DISPLAY = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DAYS_DISPLAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

class Cal:
    
    def __init__(self):
        self.tasks = []

    def __repr__(self):
        return "\n".join(repr(task) for task in self.tasks)

    def add_task(self, text):
        task = Task(self, text)
        self.tasks.append(task)
        return task

    def get_routines(self):
        return sorted([task for task in self.tasks if task.freq != ONCE], key = task_key)

    def get_events(self):
        return sorted([task for task in self.tasks if task.freq == ONCE], key = task_key)

class Task:
    def __init__(self, cal, text):
        self.read(text)

    def __repr__(self):
        return self.write()

    def refresh(self):
        self.events = []
        if self.freq == ONCE:
            self.events = [Event(self, self.info, self.year, self.month, self.day, self.hour, self.minute)]
        
        else:
            num_days = 0

            for year in range(2015, 2018):
                for month in range(1, 13):
                    days_in_month = monthrange(year, month)[1]
                    for day in range(1, days_in_month + 1):
                        do_perform = False
                        
                        if self.freq == DAILY:
                            do_perform = True
                        elif self.freq == WEEKLY:
                            wday = weekday(year, month, day)
                            if wday in self.wdays:
                                if num_days/7 % self.wfreq == 0:
                                    do_perform = True
                                    
                        if do_perform:
                            self.events.append(
                                Event(self, self.info, year, month, day, self.hour, self.minute)
                                )
                            
                        num_days += 1

    def write_date(self):
        """ Formats:
        %wday, %month %day, %year
        Daily
        Every %wday[, %wday, ...] and %wday
        Every %freq th %wday
        Every %freq th workday """
        
        if self.freq == ONCE:
            return self.events[0].write_date()
        
        elif self.freq == DAILY:
            return "Every day"
        
        else:
            freq_str = "Every "
            
            if self.wfreq > 1:
                if self.wfreq == 2:
                    freq_str += "2nd "
                elif self.wfreq == 3:
                    freq_str += "3rd "
                elif self.wfreq == 4:
                    freq_str += "4th "
                    
            if self.wdays == WORKDAYS:
                freq_str += "workday"
                
            else:
                freq_str += DAYS_DISPLAY[self.wdays[0]]
                for day in self.wdays[1:-1]:
                    freq_str += ", " + DAYS_DISPLAY[day]
                if self.wdays[-1] != self.wdays[0]:
                    freq_str += " and " + DAYS_DISPLAY[self.wdays[-1]]
                    
            return freq_str

    def write_time(self):
        return self.events[0].write_time()

    def write(self):
        return self.write_date() + " at " + self.write_time() + " - " + self.info

    def read_date(self, text):
        text = text.lower()

        now = localtime()
        self.month = now.tm_mon
        self.day = now.tm_mday
        self.year = now.tm_year

        self.freq = DAILY
        self.wdays = []
        self.wfreq = 1

        if "today" in text:
            self.freq = ONCE
            today = localtime()
            self.day = today.tm_mday
            self.month = today.tm_mon
            self.year = today.tm_year
        if "tomorrow" in text:
            self.freq = ONCE
            tomorrow = localtime(mktime(localtime()) + 86400)
            self.day = tomorrow.tm_mday
            self.month = tomorrow.tm_mon
            self.year = tomorrow.tm_year
            
        if "this" in text or "next" in text:
            nextday = localtime()
            if "next" in text:
                nextday = localtime(mktime(nextday) + 86400 * 7)

            for i in range(7):
                nextday = localtime(mktime(nextday) + 86400)
                if DAYS[nextday.tm_wday] in text:
                    self.freq = ONCE
                    self.day = nextday.tm_mday
                    self.month = nextday.tm_mon
                    self.year = nextday.tm_year

        for month in MONTHS:
            if month in text:
                self.freq = ONCE
                self.month = MONTHS.index(month) + 1
                for day in range(1, 32):
                    if " " + repr(day) + " " in (" " + text + " ") or " " + repr(day) + "," in text:
                        self.day = day
                for year in range(2015, 2020):
                    if " " + repr(year) + " " in (" " + text + " "):
                        self.year = year

        if self.freq == DAILY:
            if "workday" in text:
                self.freq = WEEKLY
                self.wdays = WORKDAYS
                
            for day in DAYS:
                if day in text:
                    self.freq = WEEKLY
                    self.wdays.append(DAYS.index(day))
                    
            for f in ["2nd", "3rd", "4th"]:
                if f in text:
                    self.freq = WEEKLY
                    self.wfreq = ["2nd", "3rd", "4th"].index(f) + 2

        # if all these searches fail, the event occurs daily

    def read_time(self, text):
        text = text.lower()

        if ":" in text:
            self.hour = eval(text[:text.index(":")])
            
            if "p" in text:
                self.min_str = text[text.index(":")+1:text.index("p")]
                if self.hour < 12:
                    self.hour += 12
                    
            elif "a" in text:
                self.min_str = text[text.index(":")+1:text.index("a")]
                if self.hour == 12:
                    self.hour = 0
                    
            else:
                self.min_str = text[text.index(":")+1:]
                if self.hour < 7:
                    self.hour += 12
                    
            if self.min_str[0] == "0":
                self.minute = eval(self.min_str[1])
            else:
                self.minute = eval(self.min_str[0:2])
                
        else:

            done = False
            for block in "abcd":
                if block + " block" in text:
                    if self.freq == ONCE:
                        wday = weekday(self.year, self.month, self.day)
                    elif self.freq == WEEKLY:
                        wday = self.wdays[0]
                    time = BLOCKS[wday][block]
                    self.hour, self.minute = time
                    done = True

            if not done:
                if "p" in text:
                    self.hour = eval(text[:text.index("p")])
                    if self.hour < 12:
                        self.hour += 12
                        
                elif "a" in text:
                    self.hour = eval(text[:text.index("a")])
                    if self.hour == 12:
                        self.hour = 0
                        
                else:
                    self.hour = eval(text)
                    if self.hour < 7:
                        self.hour += 12
                        
                self.minute = 0

    def read(self, text):
        split_date = text.split(" at ", 1)
        dateStr = split_date[0]
        split_time = split_date[-1].split(" - ")
        timeStr = split_time[0]
        self.info = split_time[-1]
        self.read_date(dateStr)
        self.read_time(timeStr)
        self.refresh()


def task_key(task):
    if task.freq != ONCE:
        return task.hour * 3600 + task.minute * 60
    else:
        string = " ".join([repr(task.year), repr(task.month), repr(task.day), repr(task.hour), repr(task.minute)])
        return mktime(strptime(string, "%Y %m %d %H %M"))

class Event:
    def __init__(self, task, info, year, month, day, hour, minute):
        
        self.task = task
        self.info = info
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

        self.reminder = False
        self.done = False
        self.snooze = 0

    def __repr__(self):
        return self.write()

    def write_date(self):
        wday = weekday(self.year, self.month, self.day)
        wdayStr = DAYS_DISPLAY[wday]
        monthStr = MONTHS_DISPLAY[self.month-1]

        return wdayStr + ", " + monthStr + " " + repr(self.day) + ", " + repr(self.year)

    def write_time(self):
        if self.hour == 0:
            hourStr = "12"
            ampm = "AM"
        elif self.hour < 12:
            hourStr = repr(self.hour)
            ampm = "AM"
        elif self.hour == 12:
            hourStr = "12"
            ampm = "PM"
        else:
            hourStr = repr(self.hour - 12)
            ampm = "PM"
        minuteStr = repr(self.minute).zfill(2)
        
        return hourStr + ":" + minuteStr + " " + ampm

    def write(self):
        return self.write_time() + " - " + self.info

class CalApp(Tk):
    def __init__(self, cal_file=None, log_file=None):
        Tk.__init__(self)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.cal_file = cal_file
        self.log_file = log_file

        self.cal = Cal()

        if cal_file:
            f_open = open(cal_file, "r")
            strTasks = f_open.read()
            f_open.close()
            
            for line in strTasks.split("\n"):
                self.cal.add_task(line)

        self.frame = Frame(self)

        self.frame.grid(sticky = "news")
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.l_routines = Label(self.frame, text = "Routines")
        self.sb_routines_horizontal = Scrollbar(self.frame, orient = "horizontal")
        self.sb_routines_vertical = Scrollbar(self.frame, orient = "vertical")

        self.lb_routines = Listbox(self.frame, xscrollcommand = self.sb_routines_horizontal.set, yscrollcommand = self.sb_routines_vertical.set, selectmode = "single")

        self.sb_routines_horizontal.config(command = self.lb_routines.xview) 
        self.sb_routines_vertical.config(command = self.lb_routines.yview)

        self.l_events = Label(self.frame, text = "Events")
        self.sb_events_horizontal = Scrollbar(self.frame, orient = "horizontal")
        self.sb_events_vertical = Scrollbar(self.frame, orient = "vertical")

        self.lb_events = Listbox(self.frame, xscrollcommand = self.sb_events_horizontal.set, yscrollcommand = self.sb_events_vertical.set, selectmode = "single")

        self.sb_events_horizontal.config(command = self.lb_events.xview)
        self.sb_events_vertical.config(command = self.lb_events.yview)

        self.f_buttons = Frame(self.frame)
        self.b_new = Button(self.f_buttons, text = "New", command = self.b_new_pressed)
        self.b_edit = Button(self.f_buttons, text = "Edit", command = self.b_edit_pressed)
        self.b_done = Button(self.f_buttons, text = "Done", command = self.b_done_pressed)
        self.b_delete = Button(self.f_buttons, text = "Delete", command = self.b_delete_pressed)
        self.b_save = Button(self.f_buttons, text = "Save", command = self.b_save_pressed)
        self.b_load = Button(self.f_buttons, text = "Load", command = self.b_load_pressed)
        
        self.l_routines.grid(row = 0, column = 0, columnspan = 2)
        self.lb_routines.grid(row = 1, column = 0, sticky = "news")
        self.sb_routines_horizontal.grid(row = 2, column = 0, columnspan = 2, sticky = "ew")
        self.sb_routines_vertical.grid(row = 1, column = 1, sticky = "ns")

        self.l_events.grid(row = 0, column = 2, columnspan = 2)
        self.lb_events.grid(row = 1, column = 2, sticky = "news")
        self.sb_events_horizontal.grid(row = 2, column = 2, columnspan = 2, sticky = "ew")
        self.sb_events_vertical.grid(row = 1, column = 3, sticky = "ns")

        self.f_buttons.grid(row = 3, column = 0, columnspan = 4)
        self.b_new.grid(row = 4, column = 0, sticky = "news")
        self.b_edit.grid(row = 4, column = 1, sticky = "news")
        self.b_done.grid(row = 4, column = 2, sticky = "news")
        self.b_delete.grid(row = 4, column = 3, sticky = "news")
        self.b_load.grid(row = 5, column = 1, sticky = "news")
        self.b_save.grid(row = 5, column = 2, sticky = "news")

        self.focus_force()
        self.refresh()

    def refresh(self):
        if self.cal_file:
            self.title("Cal - " + self.cal_file.split("/")[-1])
        else:
            self.title("Cal - New")

        self.lb_routines.delete(0, "end")
        self.lb_events.delete(0, "end")

        for task in self.cal.get_events():
            self.lb_events.insert("end", task.write())
        for task in self.cal.get_routines():
            self.lb_routines.insert("end", task.write())

    def update(self):
        now = localtime()
        for task in self.cal.tasks:
            for event in task.events:
                if (event.year, event.month, event.day, event.hour, event.minute + event.snooze) == (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min):
                    if not event.done and not event.reminder:
                        Reminder(self, event)
                        event.reminder = True

    def get_selected(self):
        task = None
        if len(self.lb_routines.curselection()) > 0:
            routineIndex = self.lb_routines.curselection()[0]
            task = self.cal.get_routines()[routineIndex]
            
        elif len(self.lb_events.curselection()) > 0:
            eventIndex = self.lb_events.curselection()[0]
            task = self.cal.get_events()[eventIndex]

        return task

    def b_new_pressed(self):
        TaskEditor(self)

    def b_edit_pressed(self):
        if self.get_selected():
            TaskEditor(self, self.get_selected())

    def b_done_pressed(self):
        if len(self.lb_events.curselection()) > 0:
            eventIndex = self.lb_events.curselection()[0]
            task = self.cal.get_events()[eventIndex]
            event = task.events[0]
            event.done = True
            event.snooze = 0
            self.cal.tasks.remove(task)
            self.refresh()

    def b_delete_pressed(self):
        if self.get_selected():
            TaskDelete(self, self.get_selected())

    def b_save_pressed(self):
        if not self.cal_file:
            self.cal_file = asksaveasfilename()
        else:
            strTasks = ""
            for task in self.cal.tasks:
                strTasks += task.write() + "\n"
            strTasks = strTasks.rstrip("\n")
            f_save = open(self.cal_file, "w")
            f_save.write(strTasks)
            f_save.close()
            self.refresh()

    def b_load_pressed(self):
        filename = askopenfilename()
        if filename:
            self.cal_file = filename
            f_open = open(filename, "r")
            strTasks = f_open.read()
            f_open.close()
            self.cal = Cal()
            for line in strTasks.split("\n"):
                self.cal.add_task(line)
            self.refresh()

    def log(self, event):
        if not self.log_file:
            self.log_file = askopenfilename()
        if self.log_file:
            f_open = open(self.log_file, "r")
            string = f_open.read()
            f_open.close()
            if string.split("\n")[0] == event.write_date():
                string = string[string.index("\n") + 1:]
            else:
                string = "\n\n" + string
            string = event.write_date() + "\n\n" + event.write() + string
            f_open = open(self.log_file, "w")
            f_open.write(string)
            f_open.close()

class TaskEditor(Toplevel):

    def __init__(self, app, task = None):
        Toplevel.__init__(self)
        self.app = app
        self.task = task
        
        if task:
            self.title("Edit Task")
        else:
            self.title("New Task")
        self.columnconfigure(0, weight = 1)
        
        self.frame = Frame(self)

        if task:
            self.lHeader = Label(self.frame, text = "Edit task:")
        else:
            self.lHeader = Label(self.frame, text = "Create new task:")
        
        self.lInfo = Label(self.frame, text = "Info:")
        self.eInfo = Entry(self.frame)
        self.eInfo.insert(0, task.info if task else "")

        self.lTime = Label(self.frame, text = "Time:")
        self.eTime = Entry(self.frame)
        self.eTime.insert(0, task.write_time() if task else "")

        self.lDate = Label(self.frame, text = "Date:")
        self.eDate = Entry(self.frame)
        self.eDate.insert(0, task.write_date() if task else "")

        self.bOK = Button(self.frame, text = "OK", command = self.bOKPressed)

        self.frame.grid(sticky = "news")
        self.frame.columnconfigure(1, weight = 1)
        self.lHeader.grid(row = 0, column = 0, columnspan = 2)
        self.lInfo.grid(row = 1, column = 0)
        self.lTime.grid(row = 2, column = 0)
        self.lDate.grid(row = 3, column = 0)
        self.eInfo.grid(row = 1, column = 1, sticky = "ew")
        self.eTime.grid(row = 2, column = 1, sticky = "ew")
        self.eDate.grid(row = 3, column = 1, sticky = "ew")
        self.bOK.grid(row = 4, column = 0, columnspan = 2)
        
        self.focus_force()
        self.eInfo.focus_force()

    def bOKPressed(self):
        if self.task == None:
            self.app.cal.add_task(self.eDate.get() + " at " + self.eTime.get() + " - " + self.eInfo.get())
        else:
            self.task.read(self.eDate.get() + " at " + self.eTime.get() + " - " + self.eInfo.get())
        self.app.refresh()
        self.destroy()

class TaskDelete(Toplevel):

    def __init__(self, app, task):
        Toplevel.__init__(self)
        self.app = app
        self.task = task
        
        self.title("Confirm")
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        
        self.frame = Frame(self)
        self.label = Label(self.frame, text = "Delete this task?")
        self.bYes = Button(self.frame, text = "Yes", command = self.bYesPressed)
        self.bCancel = Button(self.frame, text = "Cancel", command = self.bCancelPressed)

        self.frame.grid(sticky = "news")
        self.frame.columnconfigure(0, weight = 1)
        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(0, weight = 1)
        self.label.grid(row = 0, column = 0, columnspan = 2)
        self.bYes.grid(row = 1, column = 0)
        self.bCancel.grid(row = 1, column = 1)
        
        self.focus_force()
        self.attributes("-topmost",1)

    def bYesPressed(self):
        self.app.cal.tasks.remove(self.task)
        del self.task
        self.app.refresh()
        self.destroy()

    def bCancelPressed(self):
        self.app.refresh()
        self.destroy()

class Reminder(Toplevel):

    def __init__(self, app, event):
        Toplevel.__init__(self)
        self.app = app
        self.event = event
        
        self.title("Reminder")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.frame = Frame(self)
        self.label = Label(self.frame, text = self.event.info)
        self.b_done = Button(self.frame, text = "Done", command = self.b_done_pressed)
        self.b_later = Button(self.frame, text = "Later", command = self.b_later_pressed)

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.grid(sticky = "news")
        self.label.grid(row = 0, column = 0, columnspan = 2, sticky = "news")
        self.b_done.grid(row = 1, column = 0, sticky = "e")
        self.b_later.grid(row = 1, column = 1, sticky = "w")
        
        self.focus_force()
        self.attributes("-topmost",1)
        self.after(100, self.playReminderSound)

    def b_done_pressed(self):
        self.app.log(self.event)
        if self.event.task.freq == ONCE:
            self.app.cal.tasks.remove(self.event.task)
        self.app.refresh()
        self.destroy()

    def b_later_pressed(self):
        self.event.reminder = False
        self.event.snooze += 5
        self.destroy()

    def playReminderSound(self):
        from sys import platform
        if platform == "darwin":
            from subprocess import call
            from os import path
            call(["afplay", path.dirname(path.realpath(__file__)) + "/reminder.wav"])
        else:
            from winsound import MessageBeep, MB_ICONASTERISK
            MessageBeep(MB_ICONASTERISK)
        
app = CalApp("cal.txt","log.txt")
app.focus_force()
while True:
    app.frame.update()
    app.update()
