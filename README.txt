https://github.com/MushieKings

-You need to download vosk-model-small-en-us-0.15 or better and extract in root folder
https://alphacephei.com/vosk/models

-Run setup.bat first
-Make sure LMstudio inferance server is running
(url="http://localhost:1234/v1", api_key="lm-studio)

-Image detect failed: If your desktop scale is set to 100% then the browser zoom should be set to 150% and vice versa. Also make sure the Applio theme is set to "Applio" Or you can update the logo.png if detecting the "Applio" text at the top of the webui isn't working. Else you can use the Text Detection which will use the browsers "find" function. Only tested with chrome and firefox!

-If computer generates the response longer than 60 seconds you will need to edit the timeout: "for r in range(60):" 60 is number of seconds

-Make sure "advanced settings" menu is minimized on the applio webui

-If you have any issues detecting the save file or your computer taking longer to save adjust the "filecounter" variable. Increase or decrease the timeout if in the rare occurance the saved file is not detected.

-You can change the system_message.txt to change how LM studio will respond to you.

Make sure Applio webui is loaded in browser if Applio TTS selected. The program will look for the the browser window with applio webui loaded and use pyautogui to fill out the settings.
Theres a possibility when the program tabs through the options it might mess up if there's a new version of applio or a different browser than chrome
Adjust the number of tabs necessary under "def applio_response():"

max_tokens: The maximum number of [tokens](/tokenizer) that can be generated in the chat
completion.

temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
make the output more random, while lower values like 0.2 will make it more
focused and deterministic.

frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
existing frequency in the text so far, decreasing the model's likelihood to
repeat the same line verbatim.

presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
whether they appear in the text so far, increasing the model's likelihood to
talk about new topics.

Commands

'no', 'nope', 'nah', 'negative', 'oh', 'note', 'now', 'know'
confirmation
'yes', 'ya', 'yep', 'yah', 'yet', 'yeah', 'affirmative', 'correct', 'yes sir', 'right', 'this', 'ok', 'okay', 'sure'
confirmation

'listen wake word', 'listen', 'wakeword', 'wake word', 'wait', 'listen wakeword', 'sleep'
Go back to listening for keyword

'exit', 'bye', 'end'
Exit the program

'shutdown system', 'shutdown the system', 'system shutdown', 'shutdown computer', 'shutdown the computer', 'computer shutdown', 'shut down system', 'shut down the system', 'system shut down', 'shut down computer', 'shut down the computer', 'computer shut down'
shutdown your computer

'clock', 'time', 'date', 'date time', 'time and date', 'date and time', 'time date', 'current time', 'current date', 'what is the time', 'what is the date', "today's date"
get time and date

'take note', 'save note', 'take notes', 'save notes', 'some notes', 'record some notes', 'save some notes', 'write some notes', "captain's log", 'captains log', 'star date', 'record log', 'write log', 'append log', 'save log'
save a note to text file

'open program', 'open a program', 'open an program', 'start program', 'start a program', 'start an program', 'launch program', 'launch a program', 'launch an program', 'open the program', 'start the program', 'launch the program', 'open application', 'open a application', 'open an application', 'launch application', 'launch a application', 'launch an application', 'start application', 'start a application', 'start an application', 'open the application', 'start the application', 'launch the application'
open a program

'close program', 'stop program', 'exit program', 'close the program', 'stop the prorgram', 'exit the program', 'close application', 'stop application', 'exit application', 'close a program', 'stop a program', 'exit a program', 'close a application', 'stop a application', 'exit a application', 'close an program', 'stop an program', 'exit an program', 'close an application', 'stop an application', 'exit an application','exit the application','close the application', 'stop the application'
close a program

'stop', 'stopped', 'stops', 'stuff' 'shut up', 'silence', 'quiet', 'top', 'dot' *sometimes stop is misinterperted as top or dot or the so this helps things function better*
interrupt a response(durring this process it checks all words in the string so regardless of what you say if it sees a stop command it will stop)