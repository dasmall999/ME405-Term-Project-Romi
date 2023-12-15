'''!@file                       user_input_data_transfer.py
    @brief                      A UI implementation for testing the Romi
    @details                    The user is prompted to enter commands from a given menu along with requested values, if needed
    @author                     Andrew Whitacre
                                Drake Small
    @date                       October 22, 2023
'''

from pyb import UART, repl_uart
import pyb
from task_share import Queue, Share
import cotask

'''!@package              Import pyb, shares, queues, and cotask
'''

class user_input_data_transfer: #template developed by instructor
    
    def __init__(self, let: Share, oc: Share, dc: Share, gn: Share, sp: Share): #idk what we need to write too/UART, this modulae only sends out
        '''!@brief              Constructs a UI object
            @details            Initializes the serial comminication and data inputs
            @param              let Share for the letter command
            @param              oc Share for the open/closed loop command
            @param              dc Share for the duty cycle value
            @param              gn Share for the closed loop gain
            @param              sp Share for the velocity setpoint
        '''
        
        ## A UART obejct to write data to
        self._ser = pyb.USB_VCP() # Keep a reference to the UART for data comms
        
        self._let = let # for chars
        self._dc = dc #for floats
        self._gn = gn #for floats
        self._sp = sp #for floats
        self._oc = oc #open loop to start
        
        self.num = 0
        
        ## The present state of the task
        self._state = 0
        
            
        
    def run(self):
        '''!@brief          UI Task implementation as a generator function
            @details        Displays menu, prompts user, checks for validity, and sets the letter and/or values
        '''
        
        while True:
            
            yield self._state
            
            if self._state == 0:
                # Run state 0 - print menu
                
                str1 = "" #reinitialize
                str2 = ""
                cnt = 0
                self.num = 0.0
                
                self._ser.write("Here is your menu of commands:\n\r")
                self._ser.write("Lowercase = Motor 1, Uppercase = Motor 2\n\r")
                self._ser.write("Ex. 'z' will zero out motor 1, 'Z' will zero motor 2\n\n\r")
                
                self._ser.write("For Open-loop mode\n\r")
                self._ser.write("Z - Zero encoder position\n\r")
                self._ser.write("P - Print encoder position\n\r")
                self._ser.write("D - Print encoder delta\n\r")
                self._ser.write("V - Print encoder velocity\n\r")
                self._ser.write("M - Change duty cycle\n\r")
                self._ser.write("G - Plot 30 sec speed and position (OL)\n\r")
                self._ser.write("C - Switch to close-loop mode\n\r")
                
                self._ser.write("A - Display Euler Angles\n\r")
                self._ser.write("B - Display Angular Velocity\n\r")
                self._ser.write("N - Pivot North")
                
                
                self._ser.write("For Close-loop mode\n\r")
                self._ser.write("K - Change close-loop gain\n\r")
                self._ser.write("S - Choose velocity setpoint\n\r")
                self._ser.write("R - Plot step response\n\r")
                self._ser.write("O - Switch to open-loop mode\n\r")
                
                self._ser.write("E - Display Euler Angles\n\r")
                self._ser.write("F - Display Angular Velocity\n\r")
                
                self._state = 1
                             
                print("letter: ")
                print(self._let.get())
                print("\n\r")
                print("dc: ")
                print(self._dc.get())
                print("\n\r")
                print("gn: ")
                print(self._gn.get())
                print("\n\r")
                print("sp: ")
                print(self._sp.get())
                print("\n\r")
                print("OC_FLG: ")
                print(self._oc.get())
                print("\n\r")
               
                self._ser.write("Enter your command here: ")
                
            elif self._state == 1:
                # Run state 1 - prompt user for response, if invalid repeat again
                if(self._ser.any()):

                    char = self._ser.read(1).decode() #read in 1 byte response, aka 1 letter
                    cnt = cnt + 1
                    if (char.isdigit() == True): #no digits allowed
                        self._state = 0
                    elif (char.isalpha() == True):
                        if (self._oc.get() == 0): #valid open loop cmds
                            if (char.lower() in {"z", "p", "d", "v", "m", "g", "c", "a", "b", "n"}):
                                str1 = str1 + char
                                self._ser.write(char) #echo
                                self._state = 1
                            else:
                                self._state = 0 # print menu and prompt again 
                        elif (self._oc.get() == 1): #valid close loop cmds
                            if (char.lower() in {"k", "s", "r", "o", "e", "f"}):
                                str1 = str1 + char
                                self._ser.write(char) #echo
                                self._state = 1
                            else:
                                self._state = 0 # print menu and prompt again 
                    elif (char == '.'):
                        self._state = 0
                    elif (char == '-'):
                        self._state = 0
                    elif (char == '\x7F'): #backspace check
                        if (cnt == 1): # mistake
                            self._state = 0 # print menu and prompt again
                        else: #can fully delete entry only
                            if (cnt > 0): 
                                self._ser.write(char) #delete
                                str1 = str1[:-1] # remove last character appended, no echo
                                cnt = cnt - 2 #account for the backspace and removed char
                                self._state = 1
                            else:
                                self._state = 0
                    elif (char == '\r'): #enter check
                        cnt = cnt - 1 #dont count the enter character
                        if (cnt == 0): # mistake, enter is first entry
                            self._state = 0 # print menu and prompt again
                        elif ((str1.isalpha() == True) & (cnt > 1)): #too many letters
                            self._state = 0
                        elif (str1.isalpha() == False): #its digit and bad
                            self._state = 0
                        else: #its a single letter

                            self.num = ord(str1)
                                
                            self._let.put(self.num) #modify the output                 
                            
                            if((self._let.get() == ord('O')) | (self._let.get() == ord('o'))): # may have to deal with a switch?
                                self._oc.put(0) #0 means open loop
                                self._state = 0 # print menu and prompt again
                            elif((self._let.get() == ord('C')) | (self._let.get() == ord('c'))):
                                self._oc.put(1) #1 means close loop
                                self._state = 0 # print menu and prompt again                 
                            elif((self._let.get() == ord('M')) | (self._let.get() == ord('m'))): #check for m
                                self._ser.write("\n\rEnter your value here: ")
                                cnt = 0 #reset for new entry
                                str1 = ""
                                str2 = ""
                                self._state = 2
                            elif((self._let.get() == ord('K')) | (self._let.get() == ord('k'))): #check for k
                                self._ser.write("\n\rEnter your value here: ")
                                cnt = 0 #reset for new entry
                                str1 = ""
                                str2 = ""
                                self._state = 3
                            elif((self._let.get() == ord('S')) | (self._let.get() == ord('s'))): #check for s
                                self._ser.write("\n\rEnter your value here: ")
                                cnt = 0 #reset for new entry
                                str1 = ""
                                str2 = ""
                                self._state = 4
                            else:
                                self._state = 0 # print menu and prompt again
                        
            
            elif (self._state == 2):# for m
 
                if(self._ser.any()):
                    char = self._ser.read(1).decode() #read in 1 byte response, aka 1 letter
                    cnt = cnt + 1
                    if (char.isdigit() == True):
                        str1 = str1 + char
                        self._ser.write(char) #echo
                        self._state = 2 
                    elif (char == '.'):
                        str1 = str1 + char
                        self._ser.write(char) #echo
                        self._state = 2
                    elif (char == '-'):
                         if (cnt == 1):
                             str1 = str1 + char
                             self._ser.write(char) #echo
                             self._state = 2
                         else: # mistake
                             self._state = 0 # print menu and prompt again
                    elif (char == '\x7F'): #backspace check
                        if (cnt == 1): # mistake
                            self._state = 0 # print menu and prompt again
                        else: #can fully delete entry only
                            if (cnt > 0):
                                self._ser.write(char) #delete
                                str1 = str1[:-1] # remove last character appended, no echo
                                cnt = cnt - 2 #account for the backspace and removed char
                                self._state = 2
                            else:
                                self._state = 0
                    elif (char == '\r'): #enter check
                        cnt = cnt - 1 #dont count the enter character
                        str2 = str1 #make a copy for replace check
                        str2 = str2.replace("-", "", 1) #replace for check
                        if (cnt == 0): # mistake, enter is first entry
                            
                            self._state = 0 # print menu and prompt again
                        elif (str2.replace(".", "", 1).isdigit() == False): #too many dp
                                
                                self._state = 0
                        elif (str1 == "-"): #enter after single minus, mistake
                            
                            self._state = 0 # print menu and prompt again
                        elif (str1[len(str1) - 1] == "."): #mistake, dot at end of num
                            
                            self._state = 0 # print menu and prompt again
                                    
                        else: #valid digit/float
                            self.num = int(str1) 
                            if self.num > 100: #limit
                                self.num = 100
                            elif self.num < -100:
                                self.num = -100
                                    
                            self._dc.put(self.num) #modify the output
                            self._state = 0
                    else: # no letters allowed
                        self._state = 0
            elif (self._state == 3):# for k
 
                if(self._ser.any()):
                    char = self._ser.read(1).decode() #read in 1 byte response, aka 1 letter
                    cnt = cnt + 1
                    if (char.isdigit() == True):
                        str1 = str1 + char
                        self._ser.write(char) #echo
                        self._state = 3 
                    elif (char == '.'):
                        str1 = str1 + char
                        self._ser.write(char) #echo
                        self._state = 3
                    elif (char == '-'):
                         if (cnt == 1):
                             str1 = str1 + char
                             self._ser.write(char) #echo
                             self._state = 3
                         else: # mistake
                             self._state = 0 # print menu and prompt again
                    elif (char == '\x7F'): #backspace check
                        if (cnt == 1): # mistake
                            self._state = 0 # print menu and prompt again
                        else: #can fully delete entry only
                            if (cnt > 0):
                                self._ser.write(char) #delete
                                str1 = str1[:-1] # remove last character appended, no echo
                                cnt = cnt - 2 #account for the backspace and removed char
                                self._state = 3
                            else:
                                self._state = 0
                    elif (char == '\r'): #enter check
                        cnt = cnt - 1 #dont count the enter character
                        str2 = str1 #make a copy for replace check
                        str2 = str2.replace("-", "", 1) #replace for check
                        if (cnt == 0): # mistake, enter is first entry
                            
                            self._state = 0 # print menu and prompt again
                        elif (str2.replace(".", "", 1).isdigit() == False): #too many dp
                                
                                self._state = 0
                        elif (str1 == "-"): #enter after single minus, mistake
                            
                            self._state = 0 # print menu and prompt again
                        elif (str1[len(str1) - 1] == "."): #mistake, dot at end of num
                            
                            self._state = 0 # print menu and prompt again
                                    
                        else: #valid digit/float
                            self.num = float(str1) 
                            self._gn.put(self.num) #modify the output
                            self._state = 0
                    else: # no letters allowed
                        self._state = 0
            elif (self._state == 4):# for s
 
                if(self._ser.any()):
                    char = self._ser.read(1).decode() #read in 1 byte response, aka 1 letter
                    cnt = cnt + 1
                    if (char.isdigit() == True):
                        str1 = str1 + char
                        self._ser.write(char) #echo
                        self._state = 4 
                    elif (char == '.'):
                        str1 = str1 + char
                        self._ser.write(char) #echo
                        self._state = 4
                    elif (char == '-'):
                         if (cnt == 1):
                             str1 = str1 + char
                             self._ser.write(char) #echo
                             self._state = 4
                         else: # mistake
                             self._state = 0 # print menu and prompt again
                    elif (char == '\x7F'): #backspace check
                        if (cnt == 1): # mistake
                            self._state = 0 # print menu and prompt again
                        else: #can fully delete entry only
                            if (cnt > 0):
                                self._ser.write(char) #delete
                                str1 = str1[:-1] # remove last character appended, no echo
                                cnt = cnt - 2 #account for the backspace and removed char
                                self._state = 4
                            else:
                                self._state = 0
                    elif (char == '\r'): #enter check
                        cnt = cnt - 1 #dont count the enter character
                        str2 = str1 #make a copy for replace check
                        str2 = str2.replace("-", "", 1) #replace for check
                        if (cnt == 0): # mistake, enter is first entry
                            
                            self._state = 0 # print menu and prompt again
                        elif (str2.replace(".", "", 1).isdigit() == False): #too many dp
                                
                                self._state = 0
                        elif (str1 == "-"): #enter after single minus, mistake
                            
                            self._state = 0 # print menu and prompt again
                        elif (str1[len(str1) - 1] == "."): #mistake, dot at end of num
                            
                            self._state = 0 # print menu and prompt again
                                    
                        else: #valid digit/float
                            self.num = int(str1) 
                            if self.num > 250: #limit
                                self.num = 250
                            elif self.num < -250:
                                self.num = -250
                                    
                            self._sp.put(self.num) #modify the output
                            self._state = 0
                    else: # no letters allowed
                        self._state = 0
            else:
                # Invalid state
                raise ValueError(f"Invalid State: {self._state}")