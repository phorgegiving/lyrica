POLL_INTERVAL = 0.1 # how often does the program check what media is playing, lower values improve syching accuracy
WIN_DEBUG_ACTIVE = False # toggles debug in windows.py
PIPELINE_DEBUG_ACTIVE = True #toggles debug in data_cacher.py

SERVER_MODE = True # toggles pytorch and other AI, only uses already proceeded audio.
                   # if media wasnt proceeded, it is skipped

# SETTINGS BELOW ARE ONLY APPLIED IF SERVER_MODE = TRUE

WHISPER_MODEL = "small" # model choice for WhisperX 
