import tkinter as tk
from tkinter import ttk
from tkinter import *
from queue import Queue
import os
import pickle
import multiprocessing
import threading
import multiprocessing
from multiprocessing import Process, Manager
import subprocess
import requests
import json
import time
import re

cwdVar = os.getcwd()

class Application(tk.Tk):
    def __init__(self, donationQueue, sharedDict, processor):
        super().__init__()

        self.InitializeUI()

        self.donationQueue = donationQueue
        self.sharedDict = sharedDict
        self.processor = processor

        self.ReadAPIKey()
        self.ReadMinimumDonationValue()

        self.processedDonations = set()

        self.FetchDonations()
        
        self.PollQueue()

    def InitializeUI(self):
        self.tabControl = ttk.Notebook(self)
        self.title("CelebrityTTS")

        # Tab 1
        self.tab_1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_1, text='Text To Speech')
        self.tabControl.pack(expand=1, fill="both")

        self.comboBox = ttk.Combobox(self.tab_1, values=["Default", "Elon Musk", "Trainwrecks"], state="readonly")
        self.comboBox.grid(row=0, column=0, sticky=W, pady=10)
        self.comboBox.bind("<<ComboboxSelected>>", self.ComboboxSelected)
        self.comboBox.current(0)

        self.label_entertext_1 = Label(self.tab_1, text="Enter text")
        self.label_entertext_1.grid(row=1, column=0, sticky=W)

        self.text_input_1 = Text(self.tab_1, height=22, width=70, font="Arial")
        self.text_input_1.grid(row=2,column=0, sticky=W)

        self.button_start_1 = Button(self.tab_1, text="Start", command=self.StartButton)
        self.button_start_1.grid(sticky=SW, pady=(5,3))

        self.button_stop_1 = Button(self.tab_1, text="Stop", command=self.StopButton)
        self.button_stop_1.grid(sticky=SW, pady=(5,3))

        self.button_clearqueue_1 = Button(self.tab_1, text="Clear Queue", command=self.ClearQueueButton)
        self.button_clearqueue_1.grid(sticky=SW, pady=(5,3))

        # Tab 2
        self.tab_2 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_2, text='Streamlabs')
        self.tabControl.pack(expand=1, fill="both")

        self.label_accesstoken_2 = Label(self.tab_2, text="Streamlabs Access Token")
        self.label_accesstoken_2.grid(row=0, column=0, sticky=W, pady=(3,3))

        self.entry_accesstoken_2 = ttk.Entry(self.tab_2, show="•")
        self.entry_accesstoken_2.grid(row=1, column=0, sticky=W)

        self.button_saveacesstoken_2 = Button(self.tab_2, text="Save Streamlabs Access Token", command=self.WriteAccessToken)
        self.button_saveacesstoken_2.grid(row=2,column=0, sticky=W, pady=(3,10))

        self.label_minimumdonation_2 = Label(self.tab_2, text="Minimum donation for TTS")
        self.label_minimumdonation_2.grid(row=6, column=0, sticky=W, pady=(0,3))

        self.entry_minimumdonation_2 = ttk.Entry(self.tab_2)
        self.entry_minimumdonation_2.grid(row=7, column=0, sticky=W)

        self.button_saveminimumdonation_2 = Button(self.tab_2, text="Save Minimum Donation Value", command=self.WriteMinimumDonationValue)
        self.button_saveminimumdonation_2.grid(row=9, sticky=W, pady=(3,10))

        self.label_streamlabslog_2 = Label(self.tab_2, text="Streamlabs Logs")
        self.label_streamlabslog_2.grid(row=10, column=0, sticky=W)

        self.text_streamlabslob_2 = Text(self.tab_2, height=22, width=70, font="Arial")
        self.text_streamlabslob_2.grid(row=11, column=0, sticky=W)
        self.text_streamlabslob_2.config(state="disabled")

    def ComboboxSelected(self, event=None):
        self.sharedDict['donationVoice'] = self.comboBox.get()
        
    # Inserts the text from the input box into the queue
    def StartButton(self):
        message = self.text_input_1.get("1.0", END)
        if message == "": return
        self.text_input_1.delete('1.0', END)
        self.donationQueue.put(message)

    def StopButton(self):
        self.processor.StopWorker()

    # Pops off all the current donations
    # Sets the flags for clearing the donations, and not inserting the donation into the input box
    # Also sets the flag for stopping the subprocess
    def ClearQueueButton(self):
        while not self.donationQueue.empty():
            self.donationQueue.get()
        self.sharedDict['clearInputBox'] = True
        self.sharedDict['insertDonation'] = False
        self.sharedDict['subprocessRunning'] = False

    def ReadMinimumDonationValue(self):
        try:
            pickle_in = open("minvalue.pickle", "rb")
            firstminvalue = pickle.load(pickle_in)
            self.entry_minimumdonation_2.insert(tk.END, firstminvalue)
        except Exception as e:
            print(f"An error occurred: {e}")

    def ReadAPIKey(self):
        try:
            pickle_in = open("accesstoken.pickle","rb")
            apiKey = pickle.load(pickle_in)
            self.entry_accesstoken_2.insert(tk.END, apiKey)
        except Exception as e:
            print(f"An error occurred: {e}")

    def WriteAccessToken(self):
        apiKey = self.entry_accesstoken_2.get()
        if apiKey == "": 
            self.label_accesstoken_2.config(text="Streamlabs Access Token (Please Enter a Valid Value)", fg="red")
            self.label_accesstoken_2.after(3000, lambda: self.label_accesstoken_2.config(text="Streamlabs Access Token", fg="black"))
            return
        pickle_out = open("accesstoken.pickle", "wb")
        pickle.dump(apiKey, pickle_out)
        pickle_out.close()

    def WriteMinimumDonationValue(self):
        minimumDonationValue = self.entry_minimumdonation_2.get()
        if minimumDonationValue == "":
            self.label_minimumdonation_2.config(text="Minimum donation for TTS (Please Enter a Valid Value)", fg="red")
            self.label_minimumdonation_2.after(3000, lambda: self.label_minimumdonation_2.config(text="Minimum donation for TTS", fg="black"))
            return
        else:
            try:
                minimumDonationValue = re.sub(r"[^0-9.]", "", minimumDonationValue)
                minimumDonationValue = float(self.entry_minimumdonation_2.get())
            except ValueError:
                self.label_minimumdonation_2.config(text="Minimum donation for TTS (Please Enter a Valid Value)", fg="red")
                self.label_minimumdonation_2.after(3000, lambda: self.label_minimumdonation_2.config(text="Minimum donation for TTS", fg="black"))
                self.entry_minimumdonation_2.delete(0, END)
                return
        twodec = ("{:.2f}".format(minimumDonationValue))
        pickle_out = open("minvalue.pickle", "wb")
        pickle.dump(twodec, pickle_out)
        pickle_out.close()
    
    # Unfortunately tkinter does not support direct updates from another process
    # so in order to have the GUI update I use a shared dictionary
    # this function polls the queue every 100ms and adds the current donation being processed to the text box 
    # it also disables the start button if there is a a donation being processed
    def PollQueue(self):
        if self.sharedDict['clearInputBox']:
            self.text_input_1.config(state="normal")
            self.button_start_1.config(state="normal")
            self.text_input_1.delete('1.0', END)
            sharedDict['clearInputBox'] = False
        if self.sharedDict['insertDonation']:
            self.text_input_1.insert(tk.INSERT, self.sharedDict['donationMessage'])
            sharedDict['insertDonation'] = False
            self.text_input_1.config(state="disabled")
            self.button_start_1.config(state="disabled")

        self.after(100, self.PollQueue)

    def FetchDonations(self):
        print("\nRunning FetchDonations\n")
        def APICall():
            try:
                if self.entry_accesstoken_2.get() == "": return

                # Get the minimum donation value, and error check to see if its a valid value
                minimumDonationValue = self.entry_minimumdonation_2.get()
                if minimumDonationValue == "":
                    minimumDonationValue = 0
                else:
                    try:
                        minimumDonationValue = re.sub(r"[^0-9.]", "", minimumDonationValue)
                        minimumDonationValue = float(self.entry_minimumdonation_2.get())
                    except ValueError:
                        self.label_minimumdonation_2.config(text="Minimum donation for TTS (Please Enter a Valid Value)", fg="red")
                        self.label_minimumdonation_2.after(3000, lambda: self.label_minimumdonation_2.config(text="Minimum donation for TTS", fg="black"))
                        self.entry_minimumdonation_2.delete(0, END)
                        return
                
                # Fetch donations from Streamlabs API, and parses using JSON
                url = "https://streamlabs.com/api/donations"
                querystring = {"access_token": {self.entry_accesstoken_2.get()}}
                response = requests.request("GET", url, params=querystring)
                data = json.loads(response.content)
                donationList = data.get('donations', [])


                # Iterates through each donation from the API call, and looks at its unique ID
                # then processes it and adds it to the processedDonations set
                for donation in donationList:
                    donationID = donation['id']

                    # If the donation has not been processed, and is greater than or equal to the minimum donation value
                    if donationID not in self.processedDonations and float(donation['amount']) >= minimumDonationValue:
                        donationAmount = float(donation['amount'])
                        donationMessage = donation['message']
                        donationName = donation['donator']['name']

                        # Clean up the donation message
                        donationMessage = re.sub(r'[<>:"\'/\\|?*]', ' ', donationMessage)
                        # Remove trailing spaces or periods
                        donationMessage = donationMessage.rstrip('. ')

                        # Add the donation to the logs
                        self.text_streamlabslob_2.config(state="normal")
                        self.text_streamlabslob_2.insert(tk.INSERT, f"Message:\n{donationMessage}\n")
                        self.text_streamlabslob_2.insert(tk.INSERT, f"Donation Amount:\n${donationAmount:.2f}\n")
                        self.text_streamlabslob_2.insert(tk.INSERT, f"Name:\n{donationName}\n")
                        self.text_streamlabslob_2.insert(tk.INSERT, "―――――――――――――――――――――――――――――――――――――――\n")
                        self.text_streamlabslob_2.see("end")
                        self.text_streamlabslob_2.config(state="disabled")

                        self.processedDonations.add(donationID)

                        # Add the donation to the worker queue for the separate process
                        self.donationQueue.put(donationMessage)
            # Handle errors from API
            except Exception as e:
                self.label_accesstoken_2.config(text="Streamlabs Access Token (There was an error, received. Please check your key to make sure it is correct)", fg="red")
                self.label_accesstoken_2.after(5500, lambda: self.label_accesstoken_2.config(text="Streamlabs Access Token", fg="black"))
                return

        # This is for the initial call to the API
        thread = threading.Thread(target=APICall)
        thread.start()

        # Everything after the initial call is done using a timer
        threading.Timer(30, self.FetchDonations).start()

    
# This class is used to process donations in a separate process
class Multiprocessor():
    def __init__(self, donationQueue, sharedDict):
        self.donationQueue = donationQueue
        self.sharedDict = sharedDict
        self.workerProcess = multiprocessing.Process(target=self.Worker)
        self.workerProcess.start()
        self.subprocess = None

    def ProcessDonation(self, donation):
        # Uses the shared dictionary to determine which TTS model to use
        self.sharedDict['insertDonation'] = True
        mode = self.sharedDict['donationVoice']

        # Swaps between the directories rather than just using the full path because of the way the .py files access the models
        # Since it's in a separate process its functionally the same
        if mode == "Default":
            os.chdir(cwdVar + "/RealTTS")
            self.subprocess = subprocess.Popen(['python', 'default.py', '--input_text', donation])
        elif mode == "Elon Musk":
            self.subprocess = subprocess.Popen(['python', 'elon.py', '--input_text', donation])
        elif mode == "Trainwrecks":
            os.chdir(cwdVar + "/trainTTS")
            self.subprocess = subprocess.Popen(['python', 'trainTTS.py', '--input_text', donation])

        # Starts an infinite loop that checks if the subprocess has finished or if the shared dictionary flag has been set to false
        self.sharedDict['subprocessRunning'] = True
        while True:
            # If the program is finished, break
            if self.subprocess.poll() is not None:
                break
            # If the flag is set to false, kill the subprocess and break
            if not self.sharedDict['subprocessRunning']:
                print("\nTERMINATING SUBPROCESS\n")
                self.subprocess.kill()
                break
            time.sleep(0.1)

        # Change the directory back to root
        os.chdir(cwdVar)

        # Sets the flags for clearing the donations, and not inserting the donation into the input box
        self.sharedDict['insertDonation'] = False
        self.sharedDict['clearInputBox'] = True

    # Worker process separate from tkinter process since it is very CPU intensive
    def Worker(self):
        while True:
            donation = self.donationQueue.get()
            self.sharedDict['donationMessage'] = donation

            self.ProcessDonation(donation)

    # Sets the shared dictionary flag to stop the worker process
    # This breaks the loop in the worker process and terminates it
    def StopWorker(self):
        self.sharedDict['subprocessRunning'] = False

    def OnExit(self):
        self.StopWorker()

if __name__ == "__main__":
    # A shared dictionary and donation queue are created for the worker process and tkinter process
    manager = Manager()
    sharedDict = manager.dict()
    sharedDict['donationMessage'] = ""
    sharedDict['donationVoice'] = "Default"
    sharedDict['clearInputBox'] = False
    sharedDict['insertDonation'] = False
    sharedDict['subprocessRunning'] = False
    donationQueue = multiprocessing.Queue()

    # Create and start separate worker process
    processor = Multiprocessor(donationQueue=donationQueue, sharedDict=sharedDict)

    # Run tkinter application
    app = Application(donationQueue=donationQueue, sharedDict=sharedDict, processor=processor)

    app.mainloop()

    processor.OnExit()