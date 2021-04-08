'''
tracker tk interface
'''
import tkinter as tk
from tkinter import messagebox
import shelve
from datetime import datetime, timedelta
import dbm

SHELVE_NAME = 'tracker.dat'
BRANCH_SPACE = '    '
BRANCH_DOWN =  '│   '
BRANCH_SIDE = '─'
BRANCH_TO_SIDE = '└'
BRANCH_DOWN_SIDE = '├'
WIDTH = 400
HEIGHT = 600

class Tracker(tk.Frame):
    '''
    Class for tk interface
    '''
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.tree_layer = [True]*10
        self.tree_item_dict = dict()
        self.pack()
        self.master.wm_protocol('WM_DELETE_WINDOW', self.exit)

        try:
            self.sh = shelve.open(
                SHELVE_NAME,
                flag='w',
                writeback=True
                )
            self.nested_tree = self.sh['1']
        except dbm.error:
            self.sh = shelve.open(
                SHELVE_NAME,
                flag='n', writeback=True
                )
            self.tree_init()

        self.update_on_init()

        self.top = tk.Frame(master=self)
        self.top.pack()
        self.mid = tk.Frame(master=self)
        self.mid.pack()
        self.bot = tk.Frame(master=self)
        self.bot.pack()

        self.top_frame_functions()
        self.bottom_frame_functions()
        self.entry_box_functions()

    def exit(self):
        # self.sh['0']['time'] = datetime.strftime(datetime.now(), "%d/%m/%y %H:%M:%S")
        self.sh['0']['time'] = datetime.now()
        self.sh.sync()
        self.sh.close()
        self.master.destroy()

    def top_frame_functions(self):
        # top frame
        self.top_frame = tk.Frame(master = self.top)
        self.top_frame.pack(side='top', anchor='e')

        self.countdown_time_label = tk.Label(
            master = self.top_frame,
            font = ('Source Code Pro', 24),
            anchor = 'sw')
        self.countdown_time_label.pack(
            side=tk.LEFT,
            anchor='sw',
            padx=(0, 2), pady=(0, 0)
            )
        self.countdown_timer_daily()

        self.countdown_text_label = tk.Label(
            master = self.top_frame,
            font = ('Source Code Pro', 16),
            anchor = 'se',
            text = 'until reset' # locale
        )
        self.countdown_text_label.pack(
            side=tk.LEFT,
            anchor='se',
            padx=(0, 0), pady=(4, 3)
            )

        ## -------------------------------------------------------------
        self.top_frame_2 = tk.Frame(master = self.top)
        self.top_frame_2.pack(side='bottom')

        self.countdown_week_label = tk.Label(
            master = self.top_frame_2,
            font = ('Source Code Pro', 13),
            anchor = 's')
        self.countdown_week_label.pack(
            side=tk.LEFT,
            anchor='w',
            padx=(0, 2), pady=(0, 0)
            )
        self.countdown_timer_weekly()

    def countdown_timer_daily(self):
        # daily remaining time
        self.now = datetime.now()
        end = datetime(self.now.year, self.now.month, self.now.day,
                       hour=23, minute=59, second=59)
        remain = end - self.now
        remain_h = str(int(remain.total_seconds()//3600)).zfill(2)
        remain_m = str(int((remain.total_seconds()%3600)/60)).zfill(2)
        remain_s = str(int((remain.total_seconds()%3600)%60)).zfill(2)
        remain_str = remain_h+':'+remain_m+':'+remain_s

        remain_color = 'white'
        if remain.total_seconds() < 7200 and remain.total_seconds() >= 3600:
            remain_color = 'light goldenrod'
        elif remain.total_seconds() < 3600:
            remain_color = 'firebrick1'
        if remain.total_seconds() == 0:
            self.revert_status(self.nested_tree['Dailies'])

        self.countdown_time_label.config(text=remain_str, foreground=remain_color)
        self.countdown_time_label.after(1000, self.countdown_timer_daily)

    def countdown_timer_weekly(self):
        # weekly remining time
        week_end = datetime(self.now.year, self.now.month, self.now.day,
                       hour=23, minute=59, second=59)
        week_end -= timedelta(days=self.now.weekday())
        week_end += timedelta(days=6)
        remain = week_end - self.now
        remain_d = int(remain.total_seconds()//86400)
        if remain_d > 0:
            remain_str = str(remain_d) + ' days until'
        else:
            remain_str = 'Today is'
        if remain.total_seconds() == 0:
            self.revert_status(self.nested_tree['Weeklies'])
        self.countdown_week_label.config(text=remain_str+' weekly reset')
        self.countdown_week_label.after(1000, self.countdown_timer_daily)

    def bottom_frame_functions(self):
        # bottom frame
        self.bottom_frame = tk.Frame(master = self.mid)
        self.bottom_frame.pack()

        self.main_frame = tk.LabelFrame(
            master = self.bottom_frame,
            bd = 2,
            relief = 'ridge',
            text = 'Queued Task',
            width = 380, height = 480,
            font = ('Source Code Pro', 14)
            )
        self.main_frame.pack()
        self.main_frame.pack_propagate(0)

        self.tree_label_out(self.nested_tree)

    def tree_label_out(self, t_dict, layer=0):
        '''
        Recursion function to output tree
        '''

        dict_key_count = len(t_dict.keys())
        if dict_key_count == 0 or layer >= 3:
            return

        spacer =''
        for it in range(layer):
            if self.tree_layer[it]:
                spacer += BRANCH_SPACE
            else:
                spacer += BRANCH_DOWN

        for key in t_dict:
            if key == 'Stauts':
                break
            dict_key_count -= 1
            if dict_key_count != 0:
                self.tree_label_print(key, t_dict, spacer, BRANCH_DOWN_SIDE)
                self.tree_layer[layer] = False

            elif dict_key_count == 0:
                self.tree_label_print(key, t_dict, spacer, BRANCH_TO_SIDE)
                self.tree_layer[layer] = True

            else:
                print ('Something went wrong, line 131')
                return 0

            layer += 1
            self.tree_label_out(t_dict[key], layer)
            layer -= 1

        self.tree_layer = [True]*10

    def tree_label_print(self, key, curd, spacer, branch):
        # print (spacer + branch + ' ' +key)
        # print(len(spacer))
        if len(spacer) != 8:
            tk.Label(
                master = self.main_frame,
                text = spacer + branch + ' ' + key,
                font = ('Source Code Pro', 11),
                width = 40, anchor = 'w'
            ).pack(anchor='w', padx = (20, 0))
        else:
            # print(curd[key])
            foo = tk.Label(
                master = self.main_frame,
                text = spacer + branch + ' ',
                font = ('Source Code Pro', 11),
                anchor = 'w'
            )
            foo.pack(anchor='w', padx = (20, 0))

            if curd[key]['Status'] == 'Done':
                status_color = 'white'
                status_checkbutton = tk.IntVar(value=1)
                status_text = 'Completed'
            else:
                status_color = 'red'
                status_checkbutton = tk.IntVar()
                status_text = 'Waiting'


            self.tree_item_dict[key] = list()
            # tree_item_dict[key][]
            # 0: tkinter.Label
            # 1: tkinter.IntVar
            # 2: tkinter.Checkbutton
            self.tree_item_dict[key].append(tk.Label(
                master = foo,
                text = key,
                font = ('Source Code Pro', 11),
                width = 0, anchor = 'w',
                foreground = status_color
            ))

            self.tree_item_dict[key][0].pack(anchor='w', padx=(80,0))
            # self.tree_item_dict[key].pack(anchor='w')
            self.tree_item_dict[key].append(status_checkbutton)
            self.tree_item_dict[key].append(tk.Checkbutton(
                master=self.tree_item_dict[key][0],
                text = status_text,
                font = ('Source Code Pro', 11),
                anchor = 'e',
                variable = self.tree_item_dict[key][1],
                borderwidth = 0,
                pady = 0,
                highlightthickness = 0,
                command = lambda : self.checkbutton_update(key, curd)
                ))
            self.tree_item_dict[key][2].pack(anchor='e', padx=(150,0))

    def checkbutton_update(self, key, curd):
        print ('Hey i found this '+key)
        if self.tree_item_dict[key][1].get() == 1:
            self.tree_item_dict[key][0].configure(foreground='white')
            curd[key]['Status'] = 'Done'
            self.tree_item_dict[key][2].configure(text='Completed')
        else:
            self.tree_item_dict[key][0].configure(foreground='red')
            curd[key]['Status'] = 'Wait'
            self.tree_item_dict[key][2].configure(text='Waiting')

    def tree_refresh(self):
        self.sh.sync()
        self.tree_item_dict.clear()
        self.bottom_frame.destroy()
        self.bottom_frame_functions()

    def tree_init(self):
        '''
        Create default categories
        '''
        self.sh['0'] = {}
        self.sh['0']['time'] = 0
        self.sh['1'] = {}
        self.nested_tree = self.sh['1']

        # Main categories
        self.nested_tree['Weeklies'] = {}
        self.nested_tree['Dailies'] = {}

        # Sub categories
        self.nested_tree['Weeklies']['Bossing'] = {}

        self.nested_tree['Dailies']['Arcane_River'] = {}
        self.nested_tree['Dailies']['Bossing'] = {}

        print ('tree_init running...')
        self.sh.sync()

    def entry_box_functions(self):
        # entry box
        self.entry_frame = tk.Frame(self.bot)
        self.entry_frame.pack()
        entry_box_label = tk.Label(
            self.entry_frame,
            text = 'Input >>>',
            font = ('Source Code Pro', 12))
        entry_box_label.pack(side=tk.LEFT)
        self.entry_box = tk.Entry(
            master = self.entry_frame,
            width = 36,
            font = ('Source Code Pro', 14))
        self.entry_box.pack(side=tk.LEFT)
        self.entry_box.bind(
            '<Return>', self.entry_process)
        self.entry_box.focus()
        self.respond_frame = tk.Frame(self)
        self.respond_frame.pack(anchor='e')
        self.respond_box = tk.Label(
            master = self.respond_frame,
            font = ('Source Code Pro', 12),
            text = 'Welcome',
            foreground = 'white',
            )
        self.respond_box.pack()

    def respond_default(self):
        '''Display default message'''
        self.respond_box.configure(text = 'All seems normal?')

    def entry_process(self, result):
        # print(result.widget.get())
        command_raw = result.widget.get()
        result.widget.delete(0, 'end')
        command = command_raw.split(' ')

        try:
            if len(command) == 2:
                # add [location] [item]
                # rm [location] [item]
                if command[0] in ('add', 'remove', 'format', 'test'):
                    location = command[1].split('.')
                    # Title everything
                    location = [item.title() for item in location]
                    command = command[0]
                    print ('Received command :' + command)
                    print ('Received arguments :', location)

                    if command == 'add':
                        self.add_to_nest(location)
                        self.respond_box.configure(text='Added variable '+location[-1])
                        self.respond_box.after(10000, self.respond_default)

                    elif command == 'remove':
                        self.remove_from_nest(location)
                        self.respond_box.configure(text='Removed variable '+location[-1])
                        self.respond_box.after(10000, self.respond_default)

                    elif command == 'test':
                        if location[0] == 'Show_Dict':
                            self.show_dict()
                        elif location[0] == 'Func':
                            self.update_on_init()

                    elif command[0] == 'format' and command[1] == 'Tree':
                        if messagebox.askokcancel(
                            title = 'Format tree',
                            message = 'This is going to reformat your tree, \
                            Are you sure?',
                            icon = 'warning',
                            default = 'cancel'
                        ):
                            print ('true')
                        else:
                            print ('no')
                else:
                    raise ValueError(command_raw)
            elif len(command) == 1:
                if command[0] == 'quit':
                    if messagebox.askokcancel(
                        title = 'Exit',
                        message = 'Do you want to exit?',
                        icon = 'warning',
                    ):
                        self.exit()
                if command[0].lower() in ('hi', 'hello', 'hey', 'sup'):
                    self.respond_box.configure(text='Hello! Hows your day?')
                elif command[0] == 'help':
                    print ('help')
                elif command[0] == 'refresh':
                    self.tree_refresh()
                else:
                    pass
            else:
                raise ValueError(command_raw)
        except ValueError as err:
            self.respond_box.configure(
                text = 'Unknown Arguemnt: '+err.__str__())

    def check_main_category_route(self, route):
        if route[0] not in self.nested_tree.keys():
            raise ValueError('Error within main categories')

    def check_sub_category_route(self, route):
        if route[1] not in self.nested_tree[route[0]].keys():
            raise ValueError('Error within sub categories')

    def add_to_nest(self, route):
        self.check_main_category_route(route)
        if len(route) == 2:
            self.nested_tree[route[0]][route[1]] = {}
        else:
            self.check_sub_category_route(route)
            self.nested_tree[route[0]][route[1]][route[2]] = {'Status':'Wait'}
        self.tree_refresh()

    def remove_from_nest(self, route):
        self.check_main_category_route(route)
        if len(route) == 2:
            del self.nested_tree[route[0]][route[1]]
        else:
            self.check_sub_category_route(route)
            del self.nested_tree[route[0]][route[1]][route[2]]
        self.tree_refresh()

    def revert_status(self, t_dict):
        # pass in nested_tree['Weeklies']
        # switch all layer 3 to off
        for sub in t_dict:
            for item in sub:
                item['Status'] = 'Wait'

    def update_on_init(self):
        prev_t = self.sh['0']['time']
        now = datetime.now()

        if now.day-prev_t.day != 0:
            self.revert_status(self.sh['1']['Dailies'])
        if datetime.date(now).isocalendar()[1]-datetime.date(prev_t).isocalendar()[1] != 0:
            self.revert_status(self.sh['1']['Weeklies'])

    def show_dict(self):
        for item in self.tree_item_dict:
            print(item, self.tree_item_dict[item])

def main():
    root = tk.Tk()
    root.title('Queue_Tracker')
    root.geometry(str(WIDTH)+'x'+str(HEIGHT))
    root.minsize(width=WIDTH, height=HEIGHT)
    root.maxsize(width=WIDTH, height=HEIGHT)
    app = Tracker(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
