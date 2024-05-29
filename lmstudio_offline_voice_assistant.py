print("-------------------------------------LMstudio Offline Voice Assistant-v1-----------------------------------------------")
print("------------------------------------------Created by MushieKings-------------------------------------------------------")
import customtkinter # GUI
import pyttsx3 #Bassic TTS
import pyaudio #play and record audio
import winsound #notification
import random #randomize the ai voice response
import time
import threading
import sys as sys
import pyautogui
import win32gui
import librosa
import os
from AppOpener import open as appstart, close as appclose
from pygame import mixer
from openai import OpenAI
from vosk import Model, KaldiRecognizer
from datetime import datetime
#------------------------------to be continued---------------------------------
#gradio_client>=0.16.4
#from gradio_client import Client

#def applio_client():
#    client = Client("http://127.0.0.1:6969/")
#    result = client.predict(
#		api_name="/"
#)

# Instantiate configuration
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Global variables(settings)
keyword = ""
voiceid = 0
voskdir = ""
voskmodel = ""
input_text = ""
system_message = ""
voice_speed = 200
voice_vol = 0
radiovar = int
radio2var = int
model_response = ""
appliovm = ""
applioif = ""
appliottsv = ""
applio_of = ""
appliobw = ""
ttsrvc = "RVC"
stopvar = 0
# Basictts init
basictts = pyttsx3.init('sapi5')
voices = basictts.getProperty('voices')
basictts.setProperty('voice',voices[voiceid].id)
aitemp = 0.7 #creativity level
maxtokens = -1  #limit response size. -1 is unlimited
freq_p_val = 0.0  #frequency_penalty -2.0-2.0
presence_p_val = 0.0   #presence_penalty -2.0-2.0
username = "Boss"

def get_settings():
    global radiovar, radio2var, keyword, window, username, freq_p_val, presence_p_val, windowtitle, ttsfilesize, rvcfilesize, voiceid, voskdir, voskmodel, model_response, system_message, basictts, up_sound, down_sound, appliovm, applioif, appliottsv, applio_of, appliobw, stopvar, aitemp, maxtokens
    print("get settings")
    print(ttsrvc)
    radiovar = app.radio_var.get()
    radio2var = app.radio_var.get()
    username = app.entryun.get()
    # BasicTTS voice setting---
    voiceid = app.entrybttsv.get()
    voice_speed = app.entrybttsrate.get()
    voice_speed = int(voice_speed)
    voice_vol = app.entrybttsvol.get()
    voice_vol = float(voice_vol)
    try:
        voiceid = int(voiceid)
    except ValueError as ve: 
        print(ve)
        app.button_stop()
        return
    try:
        basictts.setProperty('voice',voices[voiceid].id)
        basictts.setProperty('rate', voice_speed)
        basictts.setProperty('volume', voice_vol)
    except:
        print("Failed to initalize basic TTS properties(Voice setting or other setting out of bounds)")
        app.button_stop()
        return
    basictts.say("Initializing")
    basictts.runAndWait()
    #pygame init for notification sound
    mixer.init()
    try:
        up_sound = mixer.Sound('up.wav')
        down_sound = mixer.Sound('down.wav')
    except:
        print('Failed to initialize sound files')
        basictts.say("Failed to initialize sound files")
        basictts.runAndWait()
        app.button_stop()
        return
    # Read system message from file
    system_message = read_file_content("system_message.txt")
    if system_message is None:
        basictts.say("System message file not found")
        basictts.runAndWait()
        print("System message file not found")
        app.button_stop()
        return
    #applio varriables
    appliovm = app.entry_applio_vm.get()
    applioif = app.entry_applio_if.get()
    if radiovar == 1 and ttsrvc == "RVC" and appliovm == "" and applioif == "":
        print("Applio voice model and or Index file input field empty")
        basictts.say("Applio voice model or Index file input field empty")
        basictts.runAndWait()
        app.button_stop()
        return
    appliottsv = app.entry_applio_ttsv.get()
    applio_of = app.entry_applio_of.get()
    applio_of = applio_of.replace( "\\", "/")
    appliobw = app.entrybw.get()
    #LMstudio settings
    try:
        aitemp = app.entrytemp.get()
        aitemp = float(aitemp)
        maxtokens = app.entrymt.get()
        maxtokens = int(maxtokens)
        freq_p_val = app.entryfp.get()
        freq_p_val = float(freq_p_val)
        presence_p_val = app.entrypp.get()
        presence_p_val = float(presence_p_val)
    except:
        basictts.say("Error loading LM studio settings")
        basictts.runAndWait()
        app.button_stop()
        return
    #keyword setting----------
    keyword = app.entrykw.get()
    keyword = keyword.lower()
    #Voice recognition init----
    voskdir = app.entryvosk.get()
    try:
        voskmodel=Model(voskdir)
    except Exception as ve:
        print(ve)
        basictts.say("Invalid Vosk Model Directory")
        basictts.runAndWait()
        app.button_stop()
        return
    try:
        voiceid = int(voiceid)
    except ValueError as ve: 
        print(ve)
        app.button_stop()
        return
    if radiovar == 1:
        try:
            ttsfilesize = os.path.getsize((applio_of + '/tts_output.wav'))#has to get file size sooner or else error...
            rvcfilesize = os.path.getsize((applio_of + '/tts_rvc_output.wav'))
        except:
            basictts.say("one or more output files not found or unreachable check Applio audios folder")
            basictts.runAndWait()
            print("one or more tts files not found or unreachable Applio\\assets\\audios (tts_output.wav) or (tts_rvc_output.wav)")
            app.button_stop()
            return
    if radiovar == 1:
        try:
            window = pyautogui.getWindowsWithTitle(appliobw)
            windowtitle = window[0].title
            print("windowtitle=", windowtitle)
        except:
            print('Window not found with the specified title')
            basictts.say("Window not found with the specified title")
            basictts.runAndWait()
            app.button_stop()
            return
    winsound.Beep(400, 100)
    return
    

def read_file_content(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

def wakeword():
    wake_text = str
    while startstop == 1:
        print("listening for wakeword...")
        if wake_text != keyword:
            wake_text = listen()
            if wake_text == keyword:
                print("Keyword Detected")
                basictts.say(("hi, " + username))
                basictts.runAndWait()
                return "input"
    else:
        print("Stopping wakeword")

def listen():
    print("listening...")
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    print("Start mic stream")
    stream.start_stream()
    listencounter = 0
    while startstop == 1 and stopvar == 0 and listencounter <= 41:
        listencounter += 1
        data = stream.read(4096) #4096 or 8192
        print("stream read...", listencounter, " of 42")
        if rec.AcceptWaveform(data) and stopvar == 0:
            listencounter -= 13
            print("Getting data... listencounter -13 ", listencounter, " of 42")
            audio2text = rec.Result()
            audio2text = audio2text[14:-3]
            if audio2text != "":
                print(audio2text)
            if audio2text.lower() in ['helfrich', 'how fetched', 'of fridge', 'how fred', 'how it', 'how for it', 'how fair', 'how forward', 'how ford']: #misheard alfred
                print("misheard alfred, correcting")
                audio2text = "alfred"
            if audio2text.lower() in ['huh', 'scripts', 'ha', 'soups', 'about', 'each', 'ps', 'hook', 'hush', 'teach', 'stitched', 'this', 'huge', 'twitch', "it's such", 'she says', 'shh shh', 'shh shh shh', 'she', 'search', 'sheesh', 'where', 'whoa', 'oh', 'of', 'it', 'to', 'hersh', "i've", 'uh', 'he', 'health', 'she touched', 'shh', 'hatched', 'he sucks', 'barking', "who'd", 'she says', "it's", 'so', 'huh well', 'well', 'spring', 'usps', 'hopes', 'we', 'all', 'which', 'while', 'his', 'him', 'match', 'the', 'here', 'there', "he's", 'here', 'and', 'hips', 'just', "who's", 'that', 'new', 'her', 'in', 'then', 'too', 'next', 'last', 'more', 'first', 'long']: #vosk misinterpret noise[single words only]
                print('noise words detected, deleting')
                audio2text = ""
            if audio2text != "": #if text is detected return text
                print("Input Text: ", audio2text)
                return audio2text
            if audio2text == None: #if None detected return ""
                print("audio2text None detected changing to '""'")
                audio2text = ""
                return audio2text
    else:
        print("Stopping listen. listentimer = ", listencounter, " of 42")

def input():
    global input_text, startstop, stopvar
    stopvar = 0
    mixer.stop()
    mixer.Sound.play(up_sound)
    mixer.stop()
    winsound.Beep(900, 100)
    while startstop == 1:
        rand1 = random.randrange(1, 101)
        input_text = listen()
        if input_text == None:
            input_text = ""
        if input_text != "":
            winsound.Beep(400, 100)
            mixer.Sound.play(down_sound)
            mixer.stop()
            return "inputdetected"
        if rand1 <=50 and startstop == 1:
            basictts.say("i'm listening")
            basictts.runAndWait()
    else:
        print("Stopping Input")

def confirm_input():
    print("confirming input")
    if startstop == 1:
        basictts.say("did you say ")
        basictts.runAndWait()
        print("Confirm Text: ", input_text)
        basictts.say(input_text)
        basictts.runAndWait()
    while startstop == 1:
        conf_text = listen()
        if conf_text == None:
            conf_text = ""
        if conf_text != "":
            conf_list = conf_text.split(" ")
            for s in conf_list:
                if s.lower() in ['no', 'nope', 'nah', 'negative', 'oh', 'note', 'now', 'know']:
                    basictts.say("ok, say again")
                    basictts.runAndWait()
                    return "input"
                elif s.lower() in ['yes', 'ya', 'yep', 'yah', 'yet', 'yeah', 'affirmative', 'correct', 'yes sir', 'right', 'this', 'ok', 'okay', 'sure', 'yup']:
                    mixer.Sound.play(down_sound)
                    mixer.stop()
                    print("confirmed")
                    return "inputconfirmed"
        if startstop == 1:
            rand1 = random.randrange(1, 101)
            if rand1 <=17:
                basictts.say(("awaiting confirmation, " + username))
                basictts.runAndWait()
            elif rand1 >=82:
                basictts.say(("yes or no, " + username))
                basictts.runAndWait()
            rand2 = random.randrange(1, 101)
            if rand2 <= 17:
                basictts.say("did you say ")
                basictts.runAndWait()
                print("Confirm Text: ", input_text)
                basictts.say(input_text)
                basictts.runAndWait()

def initiate_conversation():
    global model_response, stopvar
    model_response = "GeneratingLMstudioResponse"
    mixer.Sound.play(up_sound)
    mixer.stop()
    winsound.Beep(900, 100)
    #LMstudio settings
    aitemp = app.entrytemp.get()
    aitemp = float(aitemp)
    maxtokens = app.entrymt.get()
    maxtokens = int(maxtokens)
    freq_p_val = app.entryfp.get()
    freq_p_val = float(freq_p_val)
    presence_p_val = app.entrypp.get()
    presence_p_val = float(presence_p_val)    
    if startstop == 1:
        try:
            response = client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": input_text}
                ],
                temperature=aitemp,
                max_tokens=maxtokens,
                frequency_penalty=freq_p_val,
                presence_penalty=presence_p_val,
            )
            print("Model Response: ", response.choices[0].message.content.strip())
            model_response = response.choices[0].message.content.strip()
            return response.choices[0].message.content.strip()
        except Exception as ce:
            print(ce)
            print("Failed to connect to lm studio")
            stopvar = 1
            basictts.say("Failed to connect to lm studio")
            basictts.runAndWait()
    else:
        print("Stopping initiate conversation")

def model_thread():
    model_response_thread = threading.Thread(target=initiate_conversation)
    model_response_thread.start()
    return

#--------------------------------------------------------------------CHECK INPUT-------------------------------------------------------------------------------
def input_check():
    global model_response
    if startstop == 1:
        if input_text.lower() in ['listen wake word', 'listen', 'wakeword', 'wake word', 'wait', 'listen wakeword', 'sleep']:
            basictts.say(("ok i will listen for your command, " + username))
            basictts.runAndWait()
            return "listenwake"
        if input_text.lower() in ['exit', 'bye', 'end']:
            basictts.say(("Talk again soon, " + username))
            basictts.runAndWait()
            print("Exiting the conversation.")
            app.destroy()
            sys.exit()
        if input_text.lower() in ['shutdown system', 'shutdown the system', 'system shutdown', 'shutdown computer', 'shutdown the computer', 'computer shutdown', 'shut down system', 'shut down the system', 'system shut down', 'shut down computer', 'shut down the computer', 'computer shut down']:
            basictts.say("Initiating shutdown.")
            basictts.runAndWait()
            print("Shuting down computer.")
            os.system("shutdown /s /t 1")
            sys.exit()
        if input_text.lower() in ['clock', 'time', 'date', 'date time', 'time and date', 'date and time', 'time date', 'current time', 'current date', 'what is the time', 'what is the date', "today's date"]:
            return "timedate"
        if input_text.lower() in ['take note', 'save note', 'take notes', 'save notes', 'some notes', 'record some notes', 'save some notes', 'write some notes', "captain's log", 'captains log', 'star date', 'record log', 'write log', 'append log', 'save log']:
            basictts.say(("Ready to take your notes, " + username))
            basictts.runAndWait()
            return "takenotes"
        if input_text.lower() in ['open program', 'open a program', 'open an program', 'start program', 'start a program', 'start an program', 'launch program', 'launch a program', 'launch an program', 'open the program', 'start the program', 'launch the program', 'open application', 'open a application', 'open an application', 'launch application', 'launch a application', 'launch an application', 'start application', 'start a application', 'start an application', 'open the application', 'start the application', 'launch the application']:
            basictts.say("What program would you like to open?")
            basictts.runAndWait()
            return "openapp"
        if input_text.lower() in ['close program', 'stop program', 'exit program', 'close the program', 'stop the prorgram', 'exit the program', 'close application', 'stop application', 'exit application', 'close a program', 'stop a program', 'exit a program', 'close a application', 'stop a application', 'exit a application', 'close an program', 'stop an program', 'exit an program', 'close an application', 'stop an application', 'exit an application','exit the application','close the application', 'stop the application']:
            basictts.say("What program would you like to close?")
            basictts.runAndWait()
            return "closeapp"
        else:
            return "ttsthread" #---------------------------------------------------------Begin TTS-------------------------------------------------------

def tts_thread():
    print("Starting TTS")
    global stopvar, radiovar
    stopvar = 0
    radiovar = app.radio_var.get()#-----------------------------------check radio button setting------------------------------------------------------
    if radiovar == 0:#-----------------------------------------------------Basic TTS response------------------------------------------------------------
        for r in range(60): #timeout in 20 seconds. Adjust if computer is slower
            if startstop == 0 or stopvar == 1:
                break
            print("timeout in ", r, " of 60")
            if model_response == "GeneratingLMstudioResponse" and startstop == 1 and stopvar == 0: #Detect LM studio response
                print("Generating Response")
                time.sleep(1)
            else:
                print("New response detected")
                time.sleep(0.1)
                break
        else:
            stopvar = 1
            print("Waiting for Generate loop stopped ", r, "of 60. LM studio not running or Generating too slow. Adjust settings")
            basictts.say("Generating response loop timed out")
            basictts.runAndWait()

        if startstop == 1 and stopvar == 0:
            print("Starting BasicTTS Multithread Response")
            tts_threadvar = threading.Thread(target=basictts_response)
            tts_threadvar.start()
        while startstop == 1 and stopvar == 0:
            if stopvar == 0:
                time.sleep(1)
                print("listening for stop...")
                stop_text = listen()#----------------------listen for stop command-----------------
                if stop_text == None:
                    stop_text = ""
                stop_list = stop_text.split(" ")
                for s in stop_list:
                    if s.lower() in ['stop', 'stopped', 'stops', 'stuff', 'shut up', 'silence', 'quiet', 'top', 'dot']:
                        print("stop detected, killing thread")
                        stopvar = 1
                        break
            else:
                print("Stop detected. Exiting stop detection loop")
                break
    else:#-----------------------------------------------------------------Applio TTS response----------------------------------------------------------
        print("Starting Applio Multithread Response")
        tts_threadvar = threading.Thread(target=applio_response)
        tts_threadvar.start()
        while startstop == 1 and stopvar == 0:
            if stopvar == 0:
                time.sleep(1)
                print("listening for stop...")
                stop_text = listen()#-------------------------listen for stop command-----------------
                if stop_text == None:
                    stop_text = ""
                stop_list = stop_text.split(" ")
                for s in stop_list:
                    if s.lower() in ['stop', 'stopped', 'stops', 'stuff', 'shut up', 'silence', 'quiet', 'top', 'dot']:
                        print("stop detected, killing thread")
                        stopvar = 1
                        break
            else:
                print("Stop detected. Exiting stop detection loop")
                break
    mixer.stop()
    return "input"

def applio_response():
    global stopvar
#-----------------------------------------------Get initial File Sizes for Comparision Detection or Stop if file not detected-----------------------------------------------------------------------
    appliovm = app.entry_applio_vm.get()#Regrab input field just incase user changed settings while running
    applioif = app.entry_applio_if.get()
    if startstop == 1:
        if ttsrvc == "TTS":
            print("Checking if tts output file exists...")
            try:
                ttsfilesize = os.path.getsize((applio_of + '/tts_output.wav'))#has to get file size sooner or else error...
            except:
                basictts.say("tts_output.wav unreachable")
                basictts.runAndWait()
                print("tts_output.wav not found or unreachable")
                return "input"
        if ttsrvc == "RVC":
            print("Checking if RVC output file exists...")
            if appliovm == "" or applioif == "":
                print("Applio voice model and or Index file input field empty")
                basictts.say("Applio voice model or Index file input field empty")
                basictts.runAndWait()
                app.button_stop()
                return "input"
            try:
                rvcfilesize = os.path.getsize((applio_of + '/tts_rvc_output.wav'))
            except:
                basictts.say("tts_rvc_output.wav unreachable")
                basictts.runAndWait()
                print("tts_rvc_output.wav not found or unreachable")
                return "input"
#-----------------------------------------------------------------Get Applio Window---------------------------------------------------------------------
    print("Getting window")
    alttabcounter = 1
    while True and startstop == 1 and stopvar == 0:
        window = pyautogui.getWindowsWithTitle(appliobw) #Get window handle [Win32Window(hWnd=int)] from user input
        windowtitle = window[0].title #Get full title from window handle
        print("windowtitle: ", windowtitle)
        active_window_title = pyautogui.getActiveWindow().title #Get active window full title
        print("active window:", active_window_title)
        if active_window_title == windowtitle: #Compare full window titles
            print("correct window active")
            break
        else:
            print("active window doesn't match")
        try:
            window = pyautogui.getWindowsWithTitle(appliobw) #Get window handle information size/name from user input
            print("window data before set foreground:", window)
            rect = window[0]._rect #Get window dimensions for minimize check
            if rect.x == -32000 or rect.y == -32000: # minimized check
                window[0].restore()
                time.sleep(1)
            win32gui.SetForegroundWindow(window[0]._hWnd)
        except Exception as error:  #Alt tab and check 2 more times
            print(error)
            basictts.say("failed to get browser window, retrying")
            basictts.runAndWait()
            pyautogui.keyDown('alt')
            time.sleep(.1)
            pyautogui.press('tab')
            time.sleep(.1)
            pyautogui.keyUp('alt')
            if alttabcounter == 3:
                print("tab:", tabcounter)
                basictts.say("Applio broswer not detected, returning to input")
                basictts.runAndWait()
                stopvar = 1
                return "input"
            print("failed to get browser window, checking 2 more times")
            continue
    print("Getting TAB")
    tabcounter = 1
    while True and startstop == 1 and stopvar == 0: #check for applio tab
        window = pyautogui.getWindowsWithTitle(appliobw) #Get window handle [Win32Window(hWnd=int)] from user input
        windowtitle = window[0].title #Get full title from window handle
        print("window: ", windowtitle)
        titlesplit = windowtitle.split(" ")
        for x in titlesplit:
            print(x)
            if x == "Applio":
                print("Applio tab detected")
                break
        if x == "Applio":
            break
        else: #check through browser tabs 15 times if not detected
            print("Applio tab not detected, checking 15 tabs...")
            pyautogui.keyDown('ctrl')
            time.sleep(0.05)
            pyautogui.press('tab')
            pyautogui.keyUp('ctrl')
            if tabcounter == 15:
                print("tab:", tabcounter)
                basictts.say("Applio tab not detected, returning to input")
                basictts.runAndWait()
                stopvar = 1
                return "input"
            tabcounter += 1
            continue

#--------------------------------------------------------------------Start top of Page-----------------------------------------------------------
    print("Getting Top of page")
    if radio2var == 0: #--------------------------------------------img detection-------------------------------------------------------
        active_window_title = pyautogui.getActiveWindow().title
        while active_window_title != windowtitle and startstop == 1: #Make sure window active
            try:
                window = pyautogui.getWindowsWithTitle(appliobw)[0]
                win32gui.SetForegroundWindow(window._hWnd)
                time.sleep(0.1)
                break
            except:
                print("failed to get browser window, retrying...")
                time.sleep(0.1)
        pyautogui.press('home')
        while True and startstop == 1 and stopvar == 0:
            try:
                if pyautogui.locateOnScreen('logo.png', confidence=0.9):
                    time.sleep(0.1)
                    print("image located")
                    x, y = pyautogui.locateCenterOnScreen('logo.png', confidence=0.9)
                    print("x", x, "y", y)
                    pyautogui.click(x, y)
                    break
                else:
                    basictts.say("Applio logo not detected")
                    basictts.runAndWait()
                    print("Applio logo not detected, retrying")
            except Exception as error:
                active_window_title = pyautogui.getActiveWindow().title
                while active_window_title != windowtitle and startstop == 1: #Make sure window active
                    try:
                        window = pyautogui.getWindowsWithTitle(appliobw)[0]
                        win32gui.SetForegroundWindow(window._hWnd)
                        time.sleep(0.1)
                        break
                    except:
                        print("failed to get browser window, retrying...")
                time.sleep(0.1)
                print("exception error, can't find image")
                print(error)
                pyautogui.keyDown('shift')
                pyautogui.press('tab')
                pyautogui.keyUp('shift')
                pyautogui.press('home')
 #----------------------------------------------------------text detection----------------------------------------------------------------
    if radio2var == 1:
        active_window_title = pyautogui.getActiveWindow().title
        while active_window_title != windowtitle and startstop == 1: #Make sure window active
            try:
                window = pyautogui.getWindowsWithTitle(appliobw)[0]
                win32gui.SetForegroundWindow(window._hWnd)
                time.sleep(0.1)
                break
            except:
                print("failed to get browser window, retrying...")
                time.sleep(0.1)
        pyautogui.keyDown('ctrl')
        pyautogui.press('f')
        pyautogui.keyUp('ctrl')
        pyautogui.write("Applio")
        pyautogui.press('tab')
        pyautogui.press('enter')
    if startstop == 1:
        for t in range(6):
            pyautogui.press('tab')
        pyautogui.press('enter')

#------------------------------------------------------------------TAB to TTS tab---------------------------------------------------------------------------
    print("Getting TTS tab")
    active_window_title = pyautogui.getActiveWindow().title
    while active_window_title != windowtitle and startstop == 1: #Make sure window active
        try:
            window = pyautogui.getWindowsWithTitle(appliobw)[0]
            win32gui.SetForegroundWindow(window._hWnd)
            time.sleep(0.1)
            break
        except:
            print("failed to get browser window, retrying...")
            time.sleep(0.1) 
    if startstop == 1:
        for t in range(7): #Adjust number of tabs here if necessary
            print("Tab:", t)
            pyautogui.press('tab')
            time.sleep(0.1)
            active_window_title = pyautogui.getActiveWindow().title
            while active_window_title != windowtitle and startstop == 1: #Make sure window active
                try:
                    window = pyautogui.getWindowsWithTitle(appliobw)[0]
                    win32gui.SetForegroundWindow(window._hWnd)
                    time.sleep(0.1)
                    break
                except:
                    print("failed to get browser window, retrying...")
                    time.sleep(0.1)
        pyautogui.press('enter') #Select TTS Tab
#--------------------------------------------------------------TAB to unload voice models--------------------------------------------------------------------------
    print("TABBING to voice models")
    active_window_title = pyautogui.getActiveWindow().title
    while active_window_title != windowtitle and startstop == 1: #Make sure window active
        try:
            window = pyautogui.getWindowsWithTitle(appliobw)[0]
            win32gui.SetForegroundWindow(window._hWnd)
            time.sleep(0.1)
            break
        except:
            print("failed to get browser window, retrying...")
            time.sleep(0.1)
    pyautogui.keyDown('shift')
    pyautogui.press('tab')  #--------------------This tab back is necessary or else the next step can mess up
    pyautogui.keyUp('shift')
    if startstop == 1:
        for t in range(10): #Adjust number of tabs here if necessary
            print("Tab:", t)
            pyautogui.press('tab')
            time.sleep(0.1)
            active_window_title = pyautogui.getActiveWindow().title
            while active_window_title != windowtitle and startstop == 1: #Make sure window active
                try:
                    window = pyautogui.getWindowsWithTitle(appliobw)[0]
                    win32gui.SetForegroundWindow(window._hWnd)
                    time.sleep(0.1)
                    break
                except:
                    print("failed to get browser window, retrying...")
                    time.sleep(0.1)
        print("Unloading voice models...")
        pyautogui.press('enter') #Unload Voice Model
#--------------------------------------------------------------TAB to Input Voice Model---------------------------------------------------------------------------
    print("TAB to input voice model")
    active_window_title = pyautogui.getActiveWindow().title
    while active_window_title != windowtitle and startstop == 1: #Make sure window active
        try:
            window = pyautogui.getWindowsWithTitle(appliobw)[0]
            win32gui.SetForegroundWindow(window._hWnd)
            time.sleep(0.1)
            break
        except:
            print("failed to get browser window, retrying...")
            time.sleep(0.1)
    if startstop == 1:
        pyautogui.keyDown('shift')
        time.sleep(0.05)
        for t in range(3): #Adjust number of tabs here if necessary
            print("Tab:", t)
            pyautogui.press('tab')
            time.sleep(0.1)
            active_window_title = pyautogui.getActiveWindow().title
            while active_window_title != windowtitle and startstop == 1: #Make sure window active
                try:
                    window = pyautogui.getWindowsWithTitle(appliobw)[0]
                    win32gui.SetForegroundWindow(window._hWnd)
                    time.sleep(0.1)
                    break
                except:
                    print("failed to get browser window, retrying...")
                    time.sleep(0.1)
        pyautogui.keyUp('shift')
        time.sleep(0.05)
        pyautogui.press('backspace')
        time.sleep(0.05)
        if ttsrvc == "RVC":
            active_window_title = pyautogui.getActiveWindow().title
            while active_window_title != windowtitle and startstop == 1: #Make sure window active
                try:
                    window = pyautogui.getWindowsWithTitle(appliobw)[0]
                    win32gui.SetForegroundWindow(window._hWnd)
                    time.sleep(0.1)
                    break
                except:
                    print("failed to get browser window, retrying...")
                    time.sleep(0.1)
            pyautogui.write(appliovm) #Enter Voice Model
        else:
            active_window_title = pyautogui.getActiveWindow().title
            while active_window_title != windowtitle and startstop == 1: #Make sure window active
                try:
                    window = pyautogui.getWindowsWithTitle(appliobw)[0]
                    win32gui.SetForegroundWindow(window._hWnd)
                    time.sleep(0.1)
                    break
                except:
                    print("failed to get browser window, retrying...")
                    time.sleep(0.1)
            pyautogui.write("")
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.1)
#-------------------------------------------------------------TAB to Input Index Model---------------------------------------------------------------------------
    print("TAB to input Index model")
    active_window_title = pyautogui.getActiveWindow().title
    while active_window_title != windowtitle and startstop == 1: #Make sure window active
        try:
            window = pyautogui.getWindowsWithTitle(appliobw)[0]
            win32gui.SetForegroundWindow(window._hWnd)
            time.sleep(0.1)
            break
        except:
            print("failed to get browser window, retrying...")
            time.sleep(0.1)
    if startstop == 1:
        print("Entering index file")
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('backspace')
        time.sleep(0.1)
        if ttsrvc == "RVC":
            active_window_title = pyautogui.getActiveWindow().title
            while active_window_title != windowtitle and startstop == 1: #Make sure window active
                try:
                    window = pyautogui.getWindowsWithTitle(appliobw)[0]
                    win32gui.SetForegroundWindow(window._hWnd)
                    time.sleep(0.1)
                    break
                except:
                    print("failed to get browser window, retrying...")
                    time.sleep(0.1)
            pyautogui.write(applioif) #Enter Index Model
        else:
            active_window_title = pyautogui.getActiveWindow().title
            while active_window_title != windowtitle and startstop == 1: #Make sure window active
                try:
                    window = pyautogui.getWindowsWithTitle(appliobw)[0]
                    win32gui.SetForegroundWindow(window._hWnd)
                    time.sleep(0.1)
                    break
                except:
                    print("failed to get browser window, retrying...")
                    time.sleep(0.1)
            pyautogui.write("")
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.1)
#------------------------------------------------------------------TAB to TTS voices---------------------------------------------------------------------------
    print("TAB to input TTS voice model")
    if startstop == 1:
        print("Entering TTS voice model")
        for t in range(3): #Adjust number of tabs here if necessary
            print("Tab:", t)
            pyautogui.press('tab')
            time.sleep(0.1)
            active_window_title = pyautogui.getActiveWindow().title
            while active_window_title != windowtitle and startstop == 1: #Make sure window active
                try:
                    window = pyautogui.getWindowsWithTitle(appliobw)[0]
                    win32gui.SetForegroundWindow(window._hWnd)
                    time.sleep(0.1)
                    break
                except:
                    print("failed to get browser window, retrying...")
                    time.sleep(0.1)
        pyautogui.write(appliottsv) #Enter TTS Voice
        time.sleep(0.1)
        pyautogui.press('enter') #Convert audio
        time.sleep(0.1)
#------------------------------------------------------TAB to Input TEXT and then TAB to start---------------------------------------------------------------------------
    print("TAB to input TEXT")
    active_window_title = pyautogui.getActiveWindow().title
    while active_window_title != windowtitle and startstop == 1: #Make sure window active
        try:
            window = pyautogui.getWindowsWithTitle(appliobw)[0]
            win32gui.SetForegroundWindow(window._hWnd)
            time.sleep(0.1)
            break
        except:
            print("failed to get browser window, retrying...")
            time.sleep(0.1)
    if startstop == 1:
        print("Entering TEXT")
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.keyDown('ctrl')
        pyautogui.press('a')
        pyautogui.keyUp('ctrl')
        pyautogui.press('backspace')
        for r in range(60): #timeout in 20 seconds. Adjust if computer is slower
            if startstop == 0 or stopvar == 1:
                break
            print("timeout in ", r, " of 60")
            if model_response == "GeneratingLMstudioResponse" and startstop == 1 and stopvar == 0: #Detect LM studio response
                print("Generating Response")
                time.sleep(1)
            else:
                print("New response detected")
                time.sleep(0.1)
                break
        else:
            stopvar = 1
            print("Waiting for Generate loop stopped ", r, "of 60. LM studio not running or Generating too slow. Adjust settings")
            basictts.say("Generating response loop timed out")
            basictts.runAndWait()

        if startstop == 1 and stopvar == 0:
            replace_txt = model_response.replace('<|eot_id|>', '').replace('*', ' ').replace('\n', '.').replace('\t', ' ').replace('<|start_header_id|>', '').replace('<|end_header_id|>', '').replace('user', '')
            print(replace_txt)
            active_window_title = pyautogui.getActiveWindow().title
        while active_window_title != windowtitle and startstop == 1: #Make sure window active
            try:
                window = pyautogui.getWindowsWithTitle(appliobw)[0]
                win32gui.SetForegroundWindow(window._hWnd)
                time.sleep(0.1)
                break
            except:
                print("failed to get browser window, retrying...")
                time.sleep(0.1)
        pyautogui.write(replace_txt) #Enter response TEXT
        time.sleep(1)
    active_window_title = pyautogui.getActiveWindow().title
    while active_window_title != windowtitle and startstop == 1: #Make sure window active
        try:
            window = pyautogui.getWindowsWithTitle(appliobw)[0]
            win32gui.SetForegroundWindow(window._hWnd)
            time.sleep(0.1)
            break
        except:
            print("failed to get browser window, retrying...")
            time.sleep(0.1)
    if startstop == 1:
        for t in range(3): #Adjust number of tabs here if necessary
            print("Tab:", t)
            pyautogui.press('tab')
            time.sleep(0.05)
            active_window_title = pyautogui.getActiveWindow().title
            while active_window_title != windowtitle and startstop == 1: #Make sure window active
                try:
                    window = pyautogui.getWindowsWithTitle(appliobw)[0]
                    win32gui.SetForegroundWindow(window._hWnd)
                    time.sleep(0.1)
                    break
                except:
                    print("failed to get browser window, retrying...")
                    time.sleep(0.1)
        pyautogui.press('enter'), #Convert audio
        print("Convert audio...")
        time.sleep(0.1)
#-------------------------------------------------------------------------Save File Check------------------------------------------------------------------------
    if ttsrvc == "TTS" and startstop == 1:
        filecounter = 1
        while stopvar == 0 and startstop == 1 and True:
            print("Checking for TTS saved file...")
            print("old tts file size:", ttsfilesize)
            try:
                if ttsfilesize == os.path.getsize((applio_of + '/tts_output.wav')): #Compare file size to check for new file
                    print(ttsfilesize)
                    print("Files size the same, File still rendering")
                    print("sleep 1s")
                    time.sleep(1)
                    print(os.path.getsize((applio_of + '/tts_output.wav')))
                    filecounter += 1
                    print("remder timeout ", filecounter, " of 35")
                    if filecounter == 35:
                        break
                else:
                    print("else: File size not same", ttsfilesize)
                    ttsfilesize = os.path.getsize((applio_of + '/tts_output.wav'))
                    print("Grabbed new file size", ttsfilesize)
                    print("sleep 1s")
                    time.sleep(1)
                    break
            except:
                print("Exception File Unavailable Rendering")
                time.sleep(1)
        filecounter = 1
        while stopvar == 0 and startstop == 1:
            try:
                if ttsfilesize != os.path.getsize((applio_of + '/tts_output.wav')): #Compare file size to check for new file
                    print("new file size not equal to ", ttsfilesize)
                    print("File still saving")
                    print("sleep 2s")
                    time.sleep(2)
                    ttsfilesize = os.path.getsize((applio_of + '/tts_output.wav'))
                    print("Grabbed new file size", ttsfilesize)
                    time.sleep(1)
                    filecounter += 1
                    print("save timeout ", filecounter, " of 15")
                    if filecounter == 15:
                        break
                else:
                    print( "New file size is the same, ", ttsfilesize,)
                    break
            except:
                print("Exception File Unavailable Saving")
                time.sleep(1)

    if ttsrvc == "RVC" and startstop == 1:
        print("old rvc file size:", rvcfilesize)
        filecounter = 1
        while stopvar == 0 and startstop == 1 and True:
            print("Checking for RVC saved file...")
            try:
                if rvcfilesize == os.path.getsize((applio_of + '/tts_rvc_output.wav')): #Compare file size to check for new file
                    print(rvcfilesize)
                    print("Files size the same, File still rendering")
                    print("sleep 1s")
                    time.sleep(1)
                    print(os.path.getsize((applio_of + '/tts_rvc_output.wav')))
                    filecounter += 1
                    print("render timeout ", filecounter, " of 35")
                    if filecounter == 35:
                        break
                else:
                    print("else: File size not same", rvcfilesize)
                    rvcfilesize = os.path.getsize((applio_of + '/tts_rvc_output.wav'))
                    print("Grabbed new file size", rvcfilesize)
                    print("sleep 1s")
                    time.sleep(1)
                    break
            except:
                print("Exception File Unavailable Rendering")
                time.sleep(1)
        filecounter = 1
        while stopvar == 0 and startstop == 1:
            try:
                if rvcfilesize != os.path.getsize((applio_of + '/tts_rvc_output.wav')): #Compare file size to check for new file
                    print("new file size not equal to ", rvcfilesize)
                    print("File still saving")
                    print("sleep 2s")
                    time.sleep(2)
                    rvcfilesize = os.path.getsize((applio_of + '/tts_rvc_output.wav'))
                    print("Grabbed new file size", rvcfilesize)
                    time.sleep(1)
                    filecounter += 1
                    print("save timeout ", filecounter, " of 15")
                    if filecounter == 15:
                        break
                else:
                    print("New file size is the same, ", rvcfilesize)
                    break
            except:
                print("Exception File Unavailable Saving")
                time.sleep(1)
    print("Save Complete, Continuing to play audio")
    time.sleep(1)
    play_applio_tts()

def play_applio_tts():
    global stopvar
    while ttsrvc == "TTS" and startstop == 1 and stopvar == 0:
        try:
            rvcwav = mixer.Sound((applio_of + '/tts_output.wav')) #Initilize response playback
            audiolen = librosa.get_duration(filename=(applio_of + '/tts_output.wav')) #Get total duration in seconds
            audiolen = int(audiolen) + 1 #Round the audio duration and add 1 second
            print(audiolen)
            mixer.Sound.play(rvcwav)
            for i in range(audiolen):
                print(i, "s of ", audiolen)
                time.sleep(1)
                if stopvar == 1 or startstop == 0:
                    print("Playback timer loop stopped")
                    mixer.stop()
                    break
            else:
                print("else: Playback loop ended")
                mixer.stop()
                stopvar = 1
                break
        except Exception as error:
            print(error)
            print(("File not found, rechecking...", applio_of + '/tts_output.wav'))
            time.sleep(0.1)
    while ttsrvc == "RVC" and startstop == 1 and stopvar == 0:
        try:
            rvcwav = mixer.Sound((applio_of + '/tts_rvc_output.wav')) #Initilize response playback
            audiolen = librosa.get_duration(filename=(applio_of + '/tts_rvc_output.wav')) #Get total duration in seconds
            audiolen = int(audiolen) + 1 #Round the audio duration and add 1 second
            print(audiolen)
            mixer.Sound.play(rvcwav)
            for i in range(audiolen):
                print(i, "s of ", audiolen)
                time.sleep(1)
                if stopvar == 1 or startstop == 0:
                    print("Playback timer loop stopped")
                    mixer.stop()
                    break
            else:
                print("Playback loop ended")
                mixer.stop()
                stopvar = 1
                break
        except Exception as error:
            print(error)
            print(("File not found, rechecking...", applio_of + '/tts_rvc_output.wav'))
            time.sleep(0.1)

def basictts_response():
    global stopvar
    replace_txt = model_response.replace('Mr.', 'Mr').replace('Mrs.', 'Mrs').replace('<|eot_id|>', '').replace('*', ' ').replace('\n', '.').replace('\t', ' ').replace('<|start_header_id|>', '').replace('<|end_header_id|>', '').replace('user', '') #.replace(',', '.')
    split_txt = replace_txt.split('.')
    if startstop == 1 and stopvar == 0:
        for x in split_txt:
            basictts.say(x)
            print(x)
            basictts.runAndWait()
            if stopvar == 1:
                basictts.stop()
                print("Stopping basic TTS response")
                return
            if startstop == 0:
                break
        else:
            stopvar = 1
            print("Ending basic TTS response")
            return

def time_and_date():
    if startstop == 1:
        timestamp = time.time()
        timestamp = int(timestamp)
        date_time = datetime.fromtimestamp(timestamp)
        timevar = date_time.strftime("The time is %I %M %p")
        datevar = date_time.strftime("Today is %A, %B %d, %Y")
        print(timevar)
        basictts.say(timevar)
        basictts.runAndWait()
        print(datevar)
        basictts.say(datevar)
        basictts.runAndWait()
        basictts.say("returning to input")
        basictts.runAndWait()
        return "input"

def take_note():
    while True and startstop ==1:
        if input() == "inputdetected":
            if confirm_input() == "inputconfirmed":
                break
            else:
                continue
    filename = app.entrynote.get()
    timestamp = time.time()
    timestamp = int(timestamp)
    date_time = datetime.fromtimestamp(timestamp)
    timevar = date_time.strftime("The time is %I:%M %p")
    datevar = date_time.strftime("Today is %A, %B %d, %Y")
    txt_file = open((str(filename) + ".txt"), "a")
    txt_file.write((timevar + ", " + datevar + "\n" + "-" + input_text + "\n"))
    txt_file.close()
    print(input_text)
    print("Saved")
    basictts.say("Saved, returning to input")
    basictts.runAndWait()
    return "input"

def open_app():
    while True and startstop ==1:
        if input() == "inputdetected":
            if confirm_input() == "inputconfirmed":
                break
            else:
                continue
    try:
        appstart(input_text, match_closest=True)
    except:
        basictts.say("failed to open")
        basictts.runAndWait()
    basictts.say("returning to input")
    basictts.runAndWait()
    return "input"

def close_app():
    while True and startstop ==1:
        if input() == "inputdetected":
            if confirm_input() == "inputconfirmed":
                break
            else:
                continue
    try:
        appclose(input_text, match_closest=True, output=False)
    except:
        basictts.say("failed to close")
        basictts.runAndWait()
    basictts.say("returning to input")
    basictts.runAndWait()
    return "input"

# GUI-------------------------------------------------------------------------------------------------------------------
class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("505x515")
        self.title("LMstudio Offline Voice Assistant")
        self.frame = customtkinter.CTkFrame(master=self)
        self.frame.grid(padx=7, pady=10, row=20, column=3, rowspan=4, sticky="nsew")
#--------------------------------------middle----------------------------------------------------------------
        self.label3 = customtkinter.CTkLabel(master=self.frame, text="Basic TTS or Applio TTS", font=("Impact", 18), text_color="deep sky blue")
        self.label3.grid(row=1, column=2, pady=0, padx=6)
        self.radio_var = customtkinter.IntVar(value=0)
        self.radio_button1 = customtkinter.CTkRadioButton(master=self.frame, variable=self.radio_var, value=0, text="Basic TTS", font=("Impact", 14), text_color="teal")
        self.radio_button1.grid(row=1, column=1, pady=0, padx=6)
        self.radio_button2 = customtkinter.CTkRadioButton(master=self.frame, variable=self.radio_var, value=1, text="Applio TTS", font=("Impact", 14), text_color="teal")
        self.radio_button2.grid(row=1, column=3, pady=0, padx=6)

        self.labelkw = customtkinter.CTkLabel(master=self.frame, text="Keyword", font=("Impact", 18), text_color="deep sky blue")
        self.labelkw.grid(row=2, column=2, pady=3, padx=6)
        self.entrykw = customtkinter.CTkEntry(master=self.frame, placeholder_text="alfred")
        self.entrykw.insert(0, "alfred")
        self.entrykw.grid(row=3, column=2, pady=3, padx=6)

        self.labelun = customtkinter.CTkLabel(master=self.frame, text="User Name", font=("Impact", 18), text_color="deep sky blue")
        self.labelun.grid(row=4, column=2, pady=3, padx=6)
        self.entryun = customtkinter.CTkEntry(master=self.frame, placeholder_text="Boss")
        self.entryun.insert(0, "Boss")
        self.entryun.grid(row=5, column=2, pady=3, padx=6)

        self.start_button = customtkinter.CTkButton(master=self.frame, hover=False, fg_color="green", text="Start", font=("Impact", 28), text_color="white", command=self.button_start)
        self.start_button.grid(row=6, column=2, pady=6, padx=6)

        self.labeltemp = customtkinter.CTkLabel(master=self.frame, text="Temperature", font=("Impact", 18), text_color="light blue")
        self.labeltemp.grid(row=7, column=2, pady=3, padx=6)
        self.entrytemp = customtkinter.CTkEntry(master=self.frame, placeholder_text="0.7")
        self.entrytemp.insert(0, 0.7)
        self.entrytemp.grid(row=8, column=2, pady=3, padx=6)

        self.labelmt = customtkinter.CTkLabel(master=self.frame, text="Max Tokens", font=("Impact", 18), text_color="light blue")
        self.labelmt.grid(row=9, column=2, pady=3, padx=6)
        self.entrymt = customtkinter.CTkEntry(master=self.frame, placeholder_text="-1")
        self.entrymt.insert(0, -1)
        self.entrymt.grid(row=10, column=2, pady=3, padx=6)

        self.labelfp = customtkinter.CTkLabel(master=self.frame, text="Frequency Penalty", font=("Impact", 18), text_color="light blue")
        self.labelfp.grid(row=11, column=2, pady=3, padx=6)
        self.entryfp = customtkinter.CTkEntry(master=self.frame, placeholder_text="-2.0-2.0")
        self.entryfp.insert(0, 0.0)
        self.entryfp.grid(row=12, column=2, pady=3, padx=6)

        self.labelpp = customtkinter.CTkLabel(master=self.frame, text="Presence Penalty", font=("Impact", 18), text_color="light blue")
        self.labelpp.grid(row=13, column=2, pady=3, padx=6)
        self.entrypp = customtkinter.CTkEntry(master=self.frame, placeholder_text="-2.0-2.0")
        self.entrypp.insert(0, 0.0)
        self.entrypp.grid(row=14, column=2, pady=3, padx=6)

#-------------------------------------leftside btts------------------------------------------------------------
        self.labelvosk = customtkinter.CTkLabel(master=self.frame, text="Vosk Model Path", font=("Impact", 18), text_color="deep sky blue")
        self.labelvosk.grid(row=2, column=1, pady=3, padx=6)
        self.entryvosk = customtkinter.CTkEntry(master=self.frame, placeholder_text="vosk-model-small-en-us-0.15")
        self.entryvosk.insert(0, "vosk-model-small-en-us-0.15")
        self.entryvosk.grid(row=3, column=1, pady=3, padx=6)

        self.labelbttsv = customtkinter.CTkLabel(master=self.frame, text="Select Basic Voice", font=("Impact", 18), text_color="deep sky blue")
        self.labelbttsv.grid(row=4, column=1, pady=3, padx=6)
        self.entrybttsv = customtkinter.CTkEntry(master=self.frame, placeholder_text="0")
        self.entrybttsv.insert(0, 0)
        self.entrybttsv.grid(row=5, column=1, pady=3, padx=6)

        self.labelbttsrate = customtkinter.CTkLabel(master=self.frame, text="Basic tts Speed", font=("Impact", 18), text_color="deep sky blue")
        self.labelbttsrate.grid(row=6, column=1, pady=3, padx=6)
        self.entrybttsrate = customtkinter.CTkEntry(master=self.frame, placeholder_text="0")
        self.entrybttsrate.insert(0, 223)
        self.entrybttsrate.grid(row=7, column=1, pady=3, padx=6)

        self.labelbttsvol = customtkinter.CTkLabel(master=self.frame, text="Btts vol(0.0-1.0)", font=("Impact", 18), text_color="deep sky blue")
        self.labelbttsvol.grid(row=8, column=1, pady=3, padx=6)
        self.entrybttsvol = customtkinter.CTkEntry(master=self.frame, placeholder_text="1.0")
        self.entrybttsvol.insert(0, 1.0)
        self.entrybttsvol.grid(row=9, column=1, pady=3, padx=6)

        self.labelnote = customtkinter.CTkLabel(master=self.frame, text="Log file Name", font=("Impact", 18), text_color="deep sky blue")
        self.labelnote.grid(row=10, column=1, pady=3, padx=6)
        self.entrynote = customtkinter.CTkEntry(master=self.frame, placeholder_text="file name")
        self.entrynote.insert(0, "captains_log")
        self.entrynote.grid(row=11, column=1, pady=3, padx=6)

#--------------------------------------rightside applio--------------------------------------------------------

        self.labelbw = customtkinter.CTkLabel(master=self.frame, text="Browser Window", font=("Impact", 18), text_color="deep sky blue")
        self.labelbw.grid(row=2, column=3, pady=3, padx=6)
        self.entrybw = customtkinter.CTkEntry(master=self.frame, placeholder_text="Applio - Google Chrome")
        self.entrybw.insert(0, "Chrome")
        self.entrybw.grid(row=3, column=3, pady=3, padx=6)

        self.label_applio_vm = customtkinter.CTkLabel(master=self.frame, text="RVC:Voice Model", font=("Impact", 18), text_color="deep sky blue")
        self.label_applio_vm.grid(row=4, column=3, pady=3, padx=6)
        self.entry_applio_vm = customtkinter.CTkEntry(master=self.frame, placeholder_text="logs\model\model.pth")
        self.entry_applio_vm.insert(0, "")
        self.entry_applio_vm.grid(row=5, column=3, pady=3, padx=6)

        self.label_applio_if = customtkinter.CTkLabel(master=self.frame, text="RVC:Index File", font=("Impact", 18), text_color="deep sky blue")
        self.label_applio_if.grid(row=6, column=3, pady=3, padx=6)
        self.entry_applio_if = customtkinter.CTkEntry(master=self.frame, placeholder_text="logs\model\model.index")
        self.entry_applio_if.insert(0, "")
        self.entry_applio_if.grid(row=7, column=3, pady=3, padx=6)

        self.label_applio_ttsv = customtkinter.CTkLabel(master=self.frame, text="TTS Voice", font=("Impact", 18), text_color="deep sky blue")
        self.label_applio_ttsv.grid(row=8, column=3, pady=3, padx=6)
        self.entry_applio_ttsv = customtkinter.CTkEntry(master=self.frame, placeholder_text="en-US-AndrewNeural")
        self.entry_applio_ttsv.insert(0, "en-US-AndrewNeural")
        self.entry_applio_ttsv.grid(row=9, column=3, pady=3, padx=6)

        self.label_applio_of = customtkinter.CTkLabel(master=self.frame, text="Applio Output Folder", font=("Impact", 18), text_color="deep sky blue")
        self.label_applio_of.grid(row=10, column=3, pady=3, padx=6)
        self.entry_applio_of = customtkinter.CTkEntry(master=self.frame, placeholder_text="C:\AI\Applio\\assets\\audios")
        self.entry_applio_of.insert(0, "C:\\AI\\Applio\\assets\\audios")
        self.entry_applio_of.grid(row=11, column=3, pady=3, padx=6)

        self.ttsrvc_button = customtkinter.CTkButton(master=self.frame, hover=False, fg_color="blue", text="Applio RVC", font=("Impact", 18), text_color="white", command=self.play_tts)
        self.ttsrvc_button.grid(row=12, column=3, pady=3, padx=6)

        self.radio2_var = customtkinter.IntVar(value=0)
        self.radio2_button1 = customtkinter.CTkRadioButton(master=self.frame, variable=self.radio2_var, value=0, text="Image Detection", font=("Impact", 14), text_color="teal")
        self.radio2_button1.grid(row=13, column=3, pady=0, padx=6)
        self.radio2_button2 = customtkinter.CTkRadioButton(master=self.frame, variable=self.radio2_var, value=1, text="Text Detection", font=("Impact", 14), text_color="teal")
        self.radio2_button2.grid(row=14, column=3, pady=0, padx=6)

    def button_start(self):
        global startstop
        self.start_button.configure(fg_color="red", text="Stop", command=self.button_stop)
        startstop = 1
        print("Start Button Activated")
        thread_main = threading.Thread(target=main_thread)
        thread_main.start()
        return
    
    def button_stop(self):
        global startstop
        print("Stop Button Activated")
        startstop = 0
        self.start_button.configure(fg_color="green",text="Start", command=self.button_start)     
        return

    def play_rvc(self):
        global ttsrvc
        self.ttsrvc_button.configure(fg_color="blue", text="Applio RVC", command=self.play_tts)
        ttsrvc = "RVC"
        print("RVC button selected")
        return
    
    def play_tts(self):
        global ttsrvc
        self.ttsrvc_button.configure(fg_color="deep sky blue",text="Applio TTS", command=self.play_rvc)
        ttsrvc = "TTS"
        print("TTS button selected")
        return

def main_thread():
    global stopvar, rec, mic
    stopvar = 0
    get_settings()
    print("Init audio")
    if startstop == 1:
        rec = KaldiRecognizer(voskmodel, 16000)
        mic = pyaudio.PyAudio()
        main = "listenwake"
    while startstop == 1:
        if main == "listenwake":
            main = wakeword()
        if main == "input":
            main = input()
        if main == "inputdetected":
            main = confirm_input()
        if main == "inputconfirmed":
            main = input_check()
        if main == "timedate":
            main = time_and_date()
        if main == "takenotes":
            main = take_note()
        if main == "openapp":
            main = open_app()
        if main == "closeapp":
            main = close_app()
        if main == "ttsthread":
            model_thread()
            main = tts_thread()
            stopvar = 0
    else:
        basictts.say("Stopping")
        basictts.runAndWait() 

if __name__ == "__main__":
    app = App()
    app.mainloop()