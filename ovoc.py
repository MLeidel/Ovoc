'''
code file: ovoc.py
date: March 2024
comments:
    converts text to audio file
    using openai's audio API
    Linux uses the 'play' (SoX) utility
    openai module is required
        as is ttkbootstrap

'''
import os, sys
import platform
import openai
import subprocess
from tkinter.font import Font
from ttkbootstrap import *
from ttkbootstrap.constants import *
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip

class Application(Frame):
    ''' main class docstring '''
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=True, padx=4, pady=4)
        self.create_widgets()

    def create_widgets(self):
        ''' creates GUI for app '''

        frm1 = Frame(self)
        frm1.grid(row=1, column=1, sticky='nsew')

        self.ent_file_data = StringVar()
        ent_file = Entry(frm1, textvariable=self.ent_file_data, width=12)
        ent_file.grid(row=1, column=1, padx=4, pady=4)
        lbl_file = Label(frm1, text='Audio File Name')
        lbl_file.grid(row=1, column=2, sticky='nsw', padx=4, pady=4)
        self.ent_file_data.set("test.mp3")

        ToolTip(ent_file,
                text="Saves to ovoc/files/ directory",
                bootstyle=(WARNING),
                wraplength=130)

        optionlist = ('mp3', 'mp3', 'opus', 'aac', 'flac', 'wav', 'pcm')
        self.opt_format_data = StringVar()
        self.opt_format_data.set(optionlist[0])
        opt_format = OptionMenu(frm1, self.opt_format_data, *optionlist)
        opt_format.grid(row=2, column=1, sticky='nse', padx=4, pady=4)

        lbl_opt = Label(frm1, text='File Format')
        lbl_opt.grid(row=2, column=2, sticky='nsw', padx=4, pady=4)

        optionlist = (
            'alloy',
            'ash',
            'ballad',
            'coral',
            'echo',
            'fable',
            'nova',
            'onyx',
            'sage',
            'shimmer'
        )
        self.opt_voice_data = StringVar()
        self.opt_voice_data.set(optionlist[0])
        opt_voice = OptionMenu(frm1, self.opt_voice_data, *optionlist)
        opt_voice.grid(row=3, column=1, sticky='nse', padx=4, pady=4)

        lbl_voice = Label(frm1, text='Voice')
        lbl_voice.grid(row=3, column=2, sticky='nsw', padx=4, pady=4)

        frm2 = Frame(self)
        frm2.grid(row=1, column=2, sticky='nsew')


        ## speed not supported with this model
        #
        # self.ent_speed_data = StringVar()
        # ent_speed = Entry(frm2, textvariable=self.ent_speed_data, width=5)
        # ent_speed.grid(row=1, column=1, padx=4, pady=4)
        # lbl_speed = Label(frm2, text='Speed')
        # lbl_speed.grid(row=1, column=2, sticky='nsw', padx=4, pady=4)
        # self.ent_speed_data.set("1.0")

        # ToolTip(ent_speed,
        #         text=" .25 to 4.0 ",
        #         bootstyle=(WARNING),
        #         wraplength=140)

        self.mod_var = StringVar() # USE ONE VAR PER GROUP OF BUTTONS
        rad_mod1 = Radiobutton(frm2, variable=self.mod_var, value='tts-1-hd', text='HD')
        rad_mod1.grid(row=2, column=1, sticky='nsw', padx=4, pady=4)
        rad_mod2 = Radiobutton(frm2, variable=self.mod_var, value='tts-1', text='Norm')
        rad_mod2.grid(row=3, column=1, sticky='nsw', padx=4, pady=4)
        self.mod_var.set("tts-1")

        lbl_text = Label(frm2, text='Text ↓')
        lbl_text.grid(row=4, column=1, sticky='nw', padx=4, pady=(40,0))


        frm3 = Frame(self)
        frm3.grid(row=2, column=1, columnspan=2, sticky='nsew')

        self.txt = Text(frm3)
        self.txt.grid(row=1, column=1)
        efont = Font(family="Sans", size=11)
        self.txt.configure(font=efont)
        self.txt.config(wrap="word", # wrap=NONE
                           undo=True, # Tk 8.4
                           width=45,
                           height=9,
                           padx=5, # inner margin
                           insertbackground='#FFF',   # cursor color
                           tabs=(efont.measure(' ' * 4),))
        self.txt.focus()

        self.scr_txt = Scrollbar(frm3, orient=VERTICAL, command=self.txt.yview)
        self.scr_txt.grid(row=1, column=2, sticky='nsw')
        self.txt['yscrollcommand'] = self.scr_txt.set

        frm4 = Frame(self)
        frm4.grid(row=3, column=1, columnspan=2, sticky='')

        btn_paste = Button(frm4, text="Paste",
                           command=self.paste_text, bootstyle="outline")
        btn_paste.grid(row=1, column=1, padx=20)

        btn_create = Button(frm4, text='Create',
                            command=self.create_file, bootstyle="outline")
        btn_create.grid(row=1, column=2, padx=20, pady=8)
        ToolTip(btn_create,
                text="Creates audio file from the above specifications",
                bootstyle=(WARNING),
                wraplength=130)

        btn_play = Button(frm4, text='Play', command=self.play_file, bootstyle="outline")
        btn_play.grid(row=1, column=3, padx=20, pady=8)

        btn_close = Button(frm4, text='Close', command=save_location, bootstyle="outline")
        btn_close.grid(row=1, column=4, padx=20, pady=8)

    def create_file(self):
        ''' create the audio file
            get parameters from GUI
            and get response from openai '''
        mod = self.mod_var.get()  # model to use
        voc = self.opt_voice_data.get()  # voice to use
#        spe = float(self.ent_speed_data.get())  # speed to use NOT SUPPORTED
        fmt = self.opt_format_data.get()  # audio file format to use
        inp = self.txt.get("1.0", END).strip()  # text to convert to speech
        fou = self.ent_file_data.get()  # file name to use
        # print()
        # print(mod,voc,spe,fmt,inp.strip(),fou)

        if not fou.endswith(fmt):
            messagebox.showwarning("Audio File", "Extension must agree with format")
            return

        try:
            speech_file_path = os.path.dirname(__file__) + "/files/" + fou

            with openai.audio.speech.with_streaming_response.create(
              model="gpt-4o-mini-tts",
              voice=voc,
              response_format=fmt,
              input=inp
            ) as response:
              response.stream_to_file(speech_file_path)
            messagebox.showinfo("Success", "saved " + fou)
        except Exception as e:
            messagebox.showerror("Problems", e)

    def play_file(self):
        ''' Play the audio file currently set
        different actions occur based on running OS '''
        playcmd = ""
        fou = self.ent_file_data.get()  # file name to use
        speech_file_path = os.path.dirname(__file__) + "/files/" + fou
        if platform.system() == "Windows":
            playcmd = [speech_file_path,]
        else:
            playcmd = ['play', speech_file_path]
        subprocess.Popen(playcmd)

    def paste_text(self):
        ''' Replaces the current text with text from the clipboard '''
        resp = messagebox.askokcancel('Paste Text', 'OK to paste over existing text?')
        if resp is not True:
            return
        self.txt.delete("1.0", END)
        self.txt.insert("1.0", root.clipboard_get())

############################################################
# change working directory to path for this file
p = os.path.realpath(__file__)
os.chdir(os.path.dirname(p))

try:
    # Load the API key from an environment variable or a .env file
    openai.api_key = os.getenv("GPTKEY")
except Exception as e:
  print("Could Not Read Key file\n", "Did you enter your Gpt Key?")
  sys.exit()


# THEMES
# 'cosmo', 'flatly', 'litera', 'minty', 'lumen',
# 'sandstone', 'yeti', 'pulse', 'united', 'morph',
# 'journal', 'darkly', 'superhero', 'solar', 'cyborg',
# 'vapor', 'simplex', 'cerculean'
root = Window("Ovoc V1.2", "superhero", "ovoc.png")

# TO SAVE GEOMETRY INFO
def save_location(e=None):
    ''' executes at WM_DELETE_WINDOW event - see below '''
    with open("winfo", "w") as fout:
        fout.write(root.geometry())
    root.destroy()

# SAVE GEOMETRY INFO
if os.path.isfile("winfo"):
    with open("winfo") as f:
        lcoor = f.read()
    root.geometry(lcoor.strip())
else:
    root.geometry("430x354") # WxH+left+top

root.protocol("WM_DELETE_WINDOW", save_location)  # UNCOMMENT TO SAVE GEOMETRY INFO
root.resizable(0, 0) # no resize & removes maximize button

Application(root)

root.mainloop()
