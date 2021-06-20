# -*- coding: utf-8 -*-

import tkinter as tk
import pyaes
import time
from tkinter import *
from tkinter import filedialog


class Application(tk.Tk):
    '''
    文件夹选择程序
        界面与逻辑分离
    '''
    def __init__(self):
        '''初始化    '''
        super().__init__()  # 有点相当于tk.Tk()
        self.geometry("800x500")  #整个界面大小
        self.createWidgets()

    def createWidgets(self):
        '''界面    '''
        self.title('AES-CRYPT')
        self.columnconfigure(0, minsize=50)
        # 定义一些变量
        self.cbcentryfilevar = tk.StringVar()
        self.cbcentrykeyvar = tk.StringVar()
        self.cfbentryfilevar = tk.StringVar()
        self.cfbentrykeyvar = tk.StringVar()
        self.cbc_entime = tk.StringVar()
        self.cbc_detime = tk.StringVar()
        self.cfb_entime = tk.StringVar()
        self.cfb_detime = tk.StringVar()
        # 先定义顶两个Frame，用来放置里面的部件
        cbcframe = tk.Frame(self, height=80)
        cbcframe.pack(side=tk.TOP, anchor=W, pady=10)
        cfbframe = tk.Frame(self, height=80)
        cfbframe.pack(side=tk.TOP, anchor=W)
        # cbc区域
        cbclabel = tk.Label(cbcframe, text='aes-cbc')
        cbcflabel = tk.Label(cbcframe, text='当前文件:')
        cbcentry = tk.Entry(cbcframe, textvariable=self.cbcentryfilevar)
        cbcbutton = tk.Button(cbcframe, command=self.__cbcopendir, text='选择')
        cbcklabel = tk.Label(cbcframe, text='请输入密钥:')
        cbckeyentry = tk.Entry(cbcframe, textvariable=self.cbcentrykeyvar)
        cbcencryptbutton = tk.Button(cbcframe,
                                     command=self.__cbcencrypt,
                                     text='加密')
        cbcdecryptbutton = tk.Button(cbcframe,
                                     command=self.__cbcdecrypt,
                                     text='解密')
        cbc_entimelabel = tk.Label(cbcframe, text='加密所花时间(s):')
        cbc_entimeshow = tk.Label(cbcframe, textvariable=self.cbc_entime)
        cbc_detimelabel = tk.Label(cbcframe, text='解密所花时间(s):')
        cbc_detimeshow = tk.Label(cbcframe, textvariable=self.cbc_detime)
        # cbc放置位置
        cbclabel.grid(row=0, column=0)
        cbcflabel.grid(row=1, column=0)
        cbcentry.grid(row=1, column=1)
        cbcbutton.grid(row=1, column=2)
        cbcklabel.grid(row=2, column=0)
        cbckeyentry.grid(row=2, column=1)
        cbcencryptbutton.grid(row=2, column=2, padx=5)
        cbcdecryptbutton.grid(row=2, column=3)
        cbc_entimelabel.grid(row=3, column=0)
        cbc_entimeshow.grid(row=3, column=1)
        cbc_detimelabel.grid(row=4, column=0)
        cbc_detimeshow.grid(row=4, column=1)
        # cfb区域
        cfblabel = tk.Label(cfbframe, text='aes-cfb')
        cfbflabel = tk.Label(cfbframe, text='当前文件:')
        cfbentry = tk.Entry(cfbframe, textvariable=self.cfbentryfilevar)
        cfbbutton = tk.Button(cfbframe, command=self.__cfbopendir, text='选择')
        cfbklabel = tk.Label(cfbframe, text='请输入密钥:')
        cfbkeyentry = tk.Entry(cfbframe, textvariable=self.cfbentrykeyvar)
        cfbencryptbutton = tk.Button(cfbframe,
                                     command=self.__cfbencrypt,
                                     text='加密')
        cfbdecryptbutton = tk.Button(cfbframe,
                                     command=self.__cfbdecrypt,
                                     text='解密')
        cfb_entimelabel = tk.Label(cfbframe, text='加密所花时间(s):')
        cfb_entimeshow = tk.Label(cfbframe, textvariable=self.cfb_entime)
        cfb_detimelabel = tk.Label(cfbframe, text='解密所花时间(s):')
        cfb_detimeshow = tk.Label(cfbframe, textvariable=self.cfb_detime)
        # cfb放置位置
        cfblabel.grid(row=0, column=0)
        cfbflabel.grid(row=1, column=0)
        cfbentry.grid(row=1, column=1)
        cfbbutton.grid(row=1, column=2)
        cfbklabel.grid(row=2, column=0)
        cfbkeyentry.grid(row=2, column=1)
        cfbencryptbutton.grid(row=2, column=2, padx=5)
        cfbdecryptbutton.grid(row=2, column=3)
        cfb_entimelabel.grid(row=3, column=0)
        cfb_entimeshow.grid(row=3, column=1)
        cfb_detimelabel.grid(row=4, column=0)
        cfb_detimeshow.grid(row=4, column=1)

    def __cbcopendir(self):
        '''打开文件夹的逻辑'''
        self.basename = filedialog.askopenfilename()  # 打开文件夹对话框
        self.cbcentryfilevar.set(
            self.basename)  # 设置变量...entryfilevar，等同于设置部件...fileEntry
        print(self.cbcentryfilevar.get())

    def __cbcencrypt(self):
        startime = time.perf_counter()
        cbcbytekey = self.cbcentrykeyvar.get().encode(
            'utf-8')  #通过get()将stringvar类型变成string再编码
        cbcmode = pyaes.AESModeOfOperationCBC(cbcbytekey)
        file_in = open(self.cbcentryfilevar.get(), 'rb')
        file_out = open('./passwdency_cbc.txt', 'wb')
        pyaes.encrypt_stream(cbcmode, file_in, file_out)
        file_in.close()
        file_out.close()
        endtime = time.perf_counter()
        self.cbc_entime.set(endtime - startime)

    def __cbcdecrypt(self):
        startime = time.perf_counter()
        cbcbytekey = self.cbcentrykeyvar.get().encode('utf-8')
        cbcmode = pyaes.AESModeOfOperationCBC(cbcbytekey)
        file_in = open('./passwdency_cbc.txt', 'rb')
        file_out = open('./passwddecy_cbc.txt', 'wb')
        pyaes.decrypt_stream(cbcmode, file_in, file_out)
        file_in.close()
        file_out.close()
        endtime = time.perf_counter()
        self.cbc_detime.set(endtime - startime)

    def __cfbopendir(self):
        '''打开文件夹的逻辑'''
        self.basename = filedialog.askopenfilename()  # 打开文件夹对话框
        self.cfbentryfilevar.set(self.basename)  # 设置变量entryvar，等同于设置部件Entry
        print(self.cfbentryfilevar.get())

    def __cfbencrypt(self):
        startime = time.perf_counter()
        cfbbytekey = self.cfbentrykeyvar.get().encode('utf-8')
        cfbmode = pyaes.AESModeOfOperationCFB(cfbbytekey,
                                              iv=None,
                                              segment_size=8)
        file_in = open(self.cfbentryfilevar.get(), 'rb')
        file_out = open('./passwdency_cfb.txt', 'wb')
        pyaes.encrypt_stream(cfbmode, file_in, file_out)
        file_in.close()
        file_out.close()
        endtime = time.perf_counter()
        self.cfb_entime.set(endtime - startime)

    def __cfbdecrypt(self):
        startime = time.perf_counter()
        cfbbytekey = self.cfbentrykeyvar.get().encode('utf-8')
        cfbmode = pyaes.AESModeOfOperationCFB(cfbbytekey,
                                              iv=None,
                                              segment_size=8)
        file_in = open('./passwdency_cfb.txt', 'rb')
        file_out = open('./passwddecy_cfb.txt', 'wb')
        pyaes.decrypt_stream(cfbmode, file_in, file_out)
        file_in.close()
        file_out.close()
        endtime = time.perf_counter()
        self.cfb_detime.set(endtime - startime)


if __name__ == '__main__':
    # 实例化Application
    app = Application()
    # 主消息循环:
    app.mainloop()