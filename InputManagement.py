# will grow as input management needs change, but working well so far.

from tkinter import *
import tkinter.ttk as ttk

class InputManagement:
    who_called_number_frame = None
    callers_type = ''
    text_box = None
    num_stack = []
    numpad_frame = None
    neg_button = None
    min_val = None
    
    who_called_pan_frame = None #reference to widget that will be called on close
    name_called_pan_frame = ''
    pan_frame = None
    RA_button = None
    DEC_button = None
    b_back = None
    b_center = None
    
    current_RA = ''
    current_DEC = ''
    
    def __init__(self):
        pass
    
    def set_text_box(self, text_box):
        self.text_box = text_box
        
    def set_neg_button(self, neg_button):
        self.neg_button = neg_button
    
    def is_number(self, to_check):
        try:
            float(to_check)
            return True
        except ValueError:
            return False
    
    def call_number_frame(self, new_caller, return_type, min_val = None):
        self.who_called_number_frame = new_caller
        self.callers_type = return_type
        init_text = str(new_caller['text'])
        first_char = init_text[0]
        self.min_val = min_val
        
        if(first_char.isalpha()):
            self.num_stack = []
            init_text = ''
        
        if(self.callers_type == 'RA_Degrees' or self.callers_type == 'DEC_Degrees'):
            self.num_stack = list(init_text)
            self.text_box.insert(0, init_text)

        elif(init_text != '' and self.is_number(init_text)):
            if(float(int(float(init_text))) == float(init_text)):
                self.num_stack = list(str(int(float(init_text))))
            else:
                self.num_stack = list(init_text)
            init_text = ''.join(self.num_stack[:])
            self.text_box.insert(0, init_text)
       
        if(self.callers_type == 'RA_Degrees'):
            self.neg_button.config(state=ACTIVE)
        
        if(self.callers_type == 'FloatNoNeg'):
            self.neg_button.config(state=DISABLED)

        if(self.callers_type == 'FloatWithNeg'):
            self.neg_button.config(state=ACTIVE)

        self.numpad_frame.tkraise()
        
    def close_number_frame(self):
        num_input = self.text_box.get()
        if(num_input == ''):
            self.num_stack = []
            self.numpad_frame.lower()
            return
        
        self.text_box.delete(0, len(self.text_box.get()))
        
        if(self.callers_type == 'Int'):
            num_input = int(float(num_input))

        elif('Float' in self.callers_type):
            num_input = float(num_input)
        
        if(self.min_val != None):
            if(num_input < self.min_val):
                num_input = self.min_val

        self.who_called_number_frame['text'] = num_input
        self.num_stack = []
        self.neg_button.config(state=DISABLED)
        self.numpad_frame.lower()
        
    def enter_number(self, entered):
        if(entered == '.'):
            if(self.callers_type == 'Int' or 'Float' in self.callers_type):
                if(self.num_stack.count('.') == 1):
                    return
                    
            if(self.callers_type == 'DEC_Degrees'):
                if(self.num_stack.count('.') < 3 and self.num_stack[-1] != '.'):
                    pass
                else:
                    return

            if(self.callers_type == 'RA_Degrees'):
                if(self.num_stack.count('.') < 2 and self.num_stack[-1] != '.'):
                    pass
                else:
                    return

        if(entered == '-'):
            if(self.num_stack[0] == '-'):
                del(self.num_stack[0])
            else:
                self.num_stack.insert(0, '-')
        else:
            self.num_stack.append(entered)
        self.text_box.delete(0, END)
        self.text_box.insert(0, ''.join(self.num_stack))
    
    def delete_digit(self):
        if(self.num_stack != []):
            self.num_stack.pop()
            self.text_box.delete(0, len(self.num_stack) + 1)
            self.text_box.insert(0, ''.join(self.num_stack))
    
    def set_pan_frame_buttons(self, RA_button=None, DEC_button=None, 
        b_back=None, b_center=None):
        if(RA_button != None):
            self.RA_button = RA_button
        if(DEC_button != None):
            self.DEC_button = DEC_button
        if(b_back != None):
            self.b_back = b_back
        if(b_center != None):
            self.b_center = b_center
    
    def call_pan_frame(self, new_caller, named_caller=''):
        self.who_called_pan_frame = new_caller
        self.name_called_pan_frame = named_caller
        if(self.name_called_pan_frame == 'dia_2'):
            self.b_center['text'] = 'Set'
            self.b_back['text'] = 'Next step'
        self.pan_frame.tkraise()
        
    
    def close_pan_frame(self):
        if(self.name_called_pan_frame == 'dia_2'):
            self.b_back['text'] = '<-'
            self.b_center['text'] = 'Track!'
        self.who_called_pan_frame.tkraise()
        
