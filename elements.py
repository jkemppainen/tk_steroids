import copy 

import tkinter as tk
import tkinter.scrolledtext

class Listbox(tk.Frame):
    '''
    Essentially tkinter's Listbox rewrapped.
    
    At initialization, a list of selectable options are passed together with a callback
    function, which on selection is called using the current selection as the input
    argument.
    '''

    def __init__(self, parent, selections, callback):
        '''
        SELECTIONS
        A list of strings that make up the listbox. The selection is passed
        to the callback function.
        
        CALLBACK
        Set the callback function that is called when any change or selection
        in the listbox happens.

        The current selection is passed as the one and only argument to the callback function.
        '''
        
        tk.Frame.__init__(self, parent)
        self.parent = parent
        

        self.listbox = tk.Listbox(self)
        self.listbox.grid(sticky='NS')
       
        self.scrollbar= tk.Scrollbar(self, orient='vertical', command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky='NS')
        
        self.listbox.config(yscrollcommand=self.scrollbar.set)


        self.set_selections(selections)
        
        self.listbox.bind('<<ListboxSelect>>', lambda x: self._errorchecked(callback))
        
        # Make the listbox to stretch in North-South to take all the available space
        self.rowconfigure(0, weight=1)
        #parent.rowconfigure(2, weight=1)


    def _errorchecked(self, callback):
        '''
        
        '''
        try:
            sel = self.listbox.curselection()[0]
            argument = self.selections[sel]
        except:
            argument = None

        if not argument is None:
            callback(self.selections[sel])

    def set_selections(self, selections):
        
        # Empty current as it may have old entries
        self.listbox.delete(0, tk.END)
        
        self.selections = selections
        
        for item in self.selections:
            self.listbox.insert(tk.END, item)



class TickSelect(tk.Frame):
    '''
    User sets ticks to select items from selections group and
    presses ok -> callback_on_ok gets called as the made selections list
    as the only input argument.
    '''

    def __init__(self, parent, selections, callback_on_ok, close_on_ok=True):
        '''
        selections          List of strings
        callback_on_ok      Callable, whom a sublist of selections is passed
        close_on_ok         Call root.destroy() when pressing ok
        '''
        tk.Frame.__init__(self, parent)
        
        self.callback_on_ok = callback_on_ok
        self.selections = selections
        self.close_on_ok = close_on_ok

        # Add scrollbar - adds canvas and extra frame
        canvas = tk.Canvas(self)
        frame = tk.Frame(canvas)
        
        scrollbar = tk.Scrollbar(self, orient='vertical', command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='NS')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0,0), window=frame, anchor='nw')
        
        canvas.grid(row=0, column=0)
        
        # Create tickboxes and entries
        N_selections = len(self.selections)
        tk_variables = [tk.IntVar() for i in range(N_selections)]

        for i_row, selection in enumerate(self.selections):        
            tk.Checkbutton(frame, text=selection, variable=tk_variables[i_row]).grid(sticky='W')

        tk.Button(self, text='Ok', command=self.on_ok).grid(row=1, column=0)
        self.winfo_toplevel().after(50, self._update)
        
        self.frame = frame
        self.canvas = canvas
        self.tk_variables = tk_variables


    def _update(self):
        self.canvas.config(scrollregion=(0, 0, self.frame.winfo_reqwidth(), self.frame.winfo_reqheight()))
        self.winfo_toplevel().after(1000, self._update)


    def on_ok(self):
        '''
        Gets called when the OK button is pressed, and calls callback_on_ok with
        the made selections.
        '''
        made_selections = []

        for tk_variable, selection in zip(self.tk_variables, self.selections):
            if tk_variable.get() == 1:
                made_selections.append(selection)

        self.callback_on_ok(made_selections)
        
        if self.close_on_ok:
            self.winfo_toplevel().destroy()


class Tabs(tk.Frame):
    '''
    Tabs widget. Can contain any tkinter widgets.
    '''
    def __init__(self, parent, tab_names, elements):
        '''
        
        *sub_elements   Constructors of the elements that get to initialized,
                        only one argument allowed, the parent
        '''

        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.current = 0

        self.buttons = []
        self.initialized_elements = []

        # Initialize content/elements
        for i_button, (name, element) in enumerate(zip(tab_names, elements)):

            initialized_element = element(self)
            self.initialized_elements.append(initialized_element)
            

            button = tk.Button(self, text=name, command=lambda i_button=i_button: self.button_pressed(i_button))
            button.grid(row=0, column = i_button)
            self.buttons.append(button)
            

        self.initialized_elements[self.current].grid(row=1, columnspan=len(self.buttons))

    def button_pressed(self, i_button):
        print(i_button) 
        self.initialized_elements[self.current].grid_remove()
        self.current = i_button
        
        self.initialized_elements[self.current].grid(row=1, columnspan=len(self.buttons))

    def get_elements(self):
        '''
        Returns the initialized elements which have to the Tab as their master/parent.
        '''
        return self.initialized_elements


class ButtonsFrame(tk.Frame):
    '''
    If you just need a frame with simply buttons (with a callback) next to each other,
    use this widget.
    '''

    def __init__(self, parent, button_names, button_commands, title=''):
        '''
        '''
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        if title:
            target = tk.LabelFrame(self, text=title)
            target.grid()
        else:
            target = self

        self.buttons = []

        for i_button, (name, command) in enumerate(zip(button_names, button_commands)):
            button = tk.Button(target, text=name, command=command)
            button.grid(row=0, column=i_button)
            self.buttons.append(button)


    def get_buttons(self):
        '''
        Returns the initialized buttons in the order that the buttons_kwargs
        were delivered in the ButtonsFrame constructor.
        '''
        return self.buttons



class BufferShower(tk.Frame):
    '''
    Redirect any string buffer to be printed on this buffer reader.
    Bit like a non-interactive console window.
    '''
    def __init__(self, parent, string_buffer, max_entries=100):
        '''
        string_buffer       Like StringIO, or sys.stdout
        '''
        tk.Frame.__init__(self, parent)

        self.parent = parent    
        self.string_buffer = string_buffer
        self.max_entries = max_entries
        
        self.entries = 0
        self.offset = 0

        self.text = tkinter.scrolledtext.ScrolledText(self)
        self.text.grid()
        
        self.parent.after(20, self.callback)
        
    def callback(self):
        self.string_buffer.seek(self.offset)

        for line in self.string_buffer:

            if self.entries > self.max_entries:
                self.text.delete('1.0','2.0')

            self.text.insert(tk.END, line)
            self.text.yview(tk.END)
            self.entries += 1
        
        self.offset = self.string_buffer.tell()

        self.parent.after(20, self.callback)
    





def main():
    pass

if __name__ == "__main__":
    main()
