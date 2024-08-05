import tkinter as tk
from tkinter import messagebox, filedialog
import textwrap
import os

class SimpleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("INPUT BUILDER")
        self.configure(background="#C0C0C0")
        
        self.label = tk.Label(self, text="Select Input Builder:", font=("Georgia", 50 ), foreground="#1B1212",background="#C0C0C0")
        self.label.grid(row=0, column=1, columnspan=1, pady=100,padx=100,ipadx=100)
        
        self.option_var = tk.StringVar()
        self.option_var.set("GAMESS")
        
        self.option1_button = tk.Radiobutton(self, text="GAMESS", variable=self.option_var, value="GAMESS", font=("Tahoma", 30),height=5,width=5,background="#C0C0C0")
        self.option1_button.grid(row=10, column=0,padx=40,ipadx=50)
        
        self.option2_button = tk.Radiobutton(self, text="GAUSSIAN", variable=self.option_var, value="GAUSSIAN", font=("Tahoma", 30),background="#C0C0C0")
        self.option2_button.grid(row=10, column=1)

        self.submit_button = tk.Button(self, text="GO", command=self.submit_option, font=("Helvetica", 15))
        self.submit_button.grid(row=50, column=1, pady=100, padx=10)
       
    def submit_option(self):
        selected_option = self.option_var.get()
        if selected_option == "GAMESS":
            app = ComputationalChemistryInputBuilder()
            app.mainloop()
        elif selected_option == "GAUSSIAN":
            app = GaussianComputational()
            app.mainloop()
        else:
            messagebox.showinfo("Selected Option", f"You selected: {selected_option}")

class ComputationalChemistryInputBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GAMESS Input Builder")
        self.geometry_file = ""
        self.options = {
            'GUESS': ["HUCKEL", "HCore"],
            'RUNTYP': ["Energy", "Hessian", "Optimization"],
            'SCFMETH': ["RHF", "UHF", "ROHF", "GVB", "MCSCF"],
            'LVL': ["LEVL2", "DFT"],
            'CHARGE': list(map(str, range(6))),
            'SPIN': ["1", "2"],
            'MEMORY': ["10", "20", "30"],
            'MEMDDI': ["1", "2", "3"],
            'BASIS': ["cc-pVDZ", "cc-pVTZ", "cc-pVQZ"]
        }
        self.parameter_values = {key: self.options[key][0] for key in self.options}
        self.create_widgets()

    def create_widgets(self):
        row = 0
        for i, (key, values) in enumerate(self.options.items()):
            label = tk.Label(self, text=key + ":", padx=30, pady=10, font=("verdana 11 "))
            label.grid(row=row // 2, column=(row % 2) * 2, sticky=tk.W, padx=130, pady=5)
            variable = tk.StringVar(self)
            variable.set(values[0])
            self.parameter_values[key] = values[0]
            option_menu = tk.OptionMenu(self, variable, *values, command=lambda value, k=key: self.set_value(k, value))
            option_menu.grid(row=row // 2, column=(row % 2) * 2 + 1, sticky=tk.EW, padx=50, pady=5, ipadx=70)
            row += 1

        geom_button = tk.Button(self, text="Import Geometry File", command=self.import_geometry, background="#DCDCDC", relief="raised")
        geom_button.grid(row=(row + 1) // 2, column=0, columnspan=4, pady=20, padx=5, ipadx=30)

        generate_button = tk.Button(self, text="Generate Output", command=self.generate_input, background="#DCDCDC", relief="raised")
        generate_button.grid(row=(row + 3) // 2, column=0, columnspan=4, pady=0, padx=5, ipadx=0)

        save_button = tk.Button(self, text="Save Input File", command=self.save_input_file, background="#DCDCDC", relief="raised")
        save_button.grid(row=(row + 100) // 2, column=1, columnspan=1, pady=0, padx=5, ipadx=1)

        submit_button = tk.Button(self, text="Submit", command=self.submit_input, background="#DCDCDC", relief="raised")
        submit_button.grid(row=(row + 100) // 2, column=2, columnspan=1, pady=10, padx=0, ipadx=10)

        self.output_text = tk.Text(self, height=10, width=80)
        self.output_text.grid(row=(row + 50) // 2, column=0, columnspan=4, pady=20, ipady=96, ipadx=50, padx=5)

    def set_value(self, key, value):
        self.parameter_values[key] = value

    def import_geometry(self):
        filename = filedialog.askopenfilename(filetypes=[("XYZ files", "*.xyz"), ("All files", "*.*")])
        if filename:
            self.geometry_file = filename
            messagebox.showinfo("File Selected", f"Geometry file selected: {os.path.basename(filename)}")
        else:
            messagebox.showinfo("File Selection Cancelled", "No file was selected.")

    def generate_input(self):
        input_content = self.generate_input_content()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, input_content)
        messagebox.showinfo("Success", "Input file generated successfully!")

    def generate_input_content(self):
        parameters = {
            'scfmeth': self.parameter_values['SCFMETH'],
            'lvl': self.parameter_values['LVL'],
            'charge': self.parameter_values['CHARGE'],
            'spin': self.parameter_values['SPIN'],
            'memory': self.parameter_values['MEMORY'],
            'memddi': self.parameter_values['MEMDDI'],
            'basis': self.parameter_values['BASIS'],
            
        }

        geom_content = ""
        if self.geometry_file:
            with open(self.geometry_file, 'r') as file:
                geom_content = file.read()
                
            parameters_text = '''
            $CONTRL SCFTYP={scfmeth} {lvl} RUNTYP=OPTIMIZE ICHARG={charge}
            COORD=UNIQUE MULT={spin} MAXIT=200 ISPHER=1 $END
            $SYSTEM MWORDS={memory} MEMDDI ={memddi} $END
            $STATPT NSTEP=100 HSSEND=.T. $END
            $BASIS  GBASIS={basis} $END
            $GUESS  GUESS=HUCKEL $END
            $DATA
            optg and freq
            C1'''
            input_content = textwrap.dedent(parameters_text).format(**parameters)
            geom_content =""
        if self.geometry_file:
         with open(self.geometry_file, 'r') as file:
          geom_content = file.read().split('\n', 2)[2]  # Remove the first two lines
        input_template = f"""{input_content}
{geom_content}$END"""

        return input_template

    def save_input_file(self):
        input_content = self.generate_input_content()
        file_path = filedialog.asksaveasfilename(defaultextension=".inp", filetypes=[("Input files", "*.inp"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(input_content)
            messagebox.showinfo("File Saved", f"Input file saved as: {os.path.basename(file_path)}")
        else:
            messagebox.showinfo("Save Cancelled", "File save operation was cancelled.")
    
    def submit_input(self):
        # Functionality to be executed when the submit button is clicked
        messagebox.showinfo("SUBMIT", "File Submitted Successfully to GAMESS")

class GaussianComputational(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gaussian Calculation GUI")
        self.geometry_file = ""

        self.options = {
            #'GUESS': ["HUCKEL"],
            'RUNTYP': ["energy", "Hessian", "Optimization"],
            'SCFMETH': ["RHF", "UHF", "ROHF"],
            'PROC': ["1","2"],
            'CHARGE': list(map(str, range(6))),
            'SPIN': ["0","1","2"],
            'MEMORY': ["10", "20", "30"],
           # 'MEMDDI': ["1"],
            'BASIS': ["cc-pVDZ", "cc-pVTZ", "cc-pVQZ"],
        }
        
        self.parameter_values = {key: self.options[key][0] for key in self.options}
        self.create_widgets()

    def create_widgets(self):
        # Create the widgets dynamically
        row = 0
        for i, (key, values) in enumerate(self.options.items()):
            label = tk.Label(self, text=key + ":", padx=30, pady=10, font=("verdana 11 "))
            label.grid(row=row // 2, column=(row % 2) * 2, sticky=tk.W, padx=130, pady=5)
            variable = tk.StringVar(self)
            variable.set(values[0])  # default value
            self.parameter_values[key] = values[0]  # set default
            option_menu = tk.OptionMenu(self, variable, *values, command=lambda value, k=key: self.set_value(k, value))
            option_menu.grid(row=row // 2, column=(row % 2) * 2 + 1, sticky=tk.EW, padx=50, pady=5, ipadx=70)
            row += 1

        # Buttons for geometry, generation, submit and save
        geom_button = tk.Button(self, text="Import Geometry File", command=self.import_geometry, background="#DCDCDC", relief="raised")
        geom_button.grid(row=(row + 1) // 2, column=0, columnspan=4, pady=20, padx=5, ipadx=30)

        generate_button = tk.Button(self, text="Generate Intput File", command=self.generate_input, background="#DCDCDC", relief="raised")
        generate_button.grid(row=(row + 3) // 2, column=0, columnspan=4, pady=0, padx=5, ipadx=0)

        save_button = tk.Button(self, text="Save Output File", command=self.save_input_file, background="#DCDCDC", relief="raised")
        save_button.grid(row=(row + 100) // 2, column=1, columnspan=1, pady=0, padx=5, ipadx=1)

        # Submit button
        submit_button = tk.Button(self, text="Submit", command=self.submit_input, background="#DCDCDC", relief="raised")
        submit_button.grid(row=(row + 100) // 2, column=2, columnspan=1, pady=10, padx=0, ipadx=10)

        # Output Text Area
        self.output_text = tk.Text(self, height=10, width=80)
        self.output_text.grid(row=(row + 50) // 2, column=0, columnspan=4, pady=20, ipady=96, ipadx=50, padx=5)

    def set_value(self, key, value):
        self.parameter_values[key] = value

    def import_geometry(self):
        # Open a file dialog to choose the geometry file
        filename = filedialog.askopenfilename(filetypes=[("XYZ files", "*.xyz"), ("All files", "*.*")])
        if filename:
            self.geometry_file = filename
            messagebox.showinfo("File Selected", f"Geometry file selected: {os.path.basename(filename)}")
        else:
            messagebox.showinfo("File Selection Cancelled", "No file was selected.")

    def generate_input(self):
        # Generate the input file content
        input_content = self.generate_input_content()
        # Display the input file content in the output text area
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, input_content)
        messagebox.showinfo("Success", "Input file generated successfully!")
        if self.parameter_values['RUNTYP']=="energy":
                    self.parameter_values['RUNTYP']=="hf"
        else:
            self.parameter_values['RUNTYP']==self.parameter_values['RUNTYP']



    def generate_input_content(self):
        # Get the values of the parameters
        parameters = {
            'runtyp':self.parameter_values['RUNTYP'],
        

            'scfmeth': self.parameter_values['SCFMETH'],
            'proc': self.parameter_values['PROC'],
            'charge': self.parameter_values['CHARGE'],
           'spin': self.parameter_values['SPIN'],
            'memory': self.parameter_values['MEMORY'],
           # 'memddi': self.parameter_values['MEMDDI'],
            'basis': self.parameter_values['BASIS'],
           # 'geometry': self.parameter_values['GEOMETRY']
        
        }
        



    

        # Fill in the template with the parameter values
        parameters_text = '''
            Gaussian File 
            %mem={memory}              
            # {runtyp} wb97xd/cc-pvtz geom=connectivity'''
        input_content = textwrap.dedent(parameters_text).format(**parameters)
        geom_content = ""
        if self.geometry_file:
            with open(self.geometry_file, 'r') as file:
                geom_content = file.read().split('\n',2)[2]
        input_template = f"""{input_content}
{geom_content}"""

        return input_template

    def save_input_file(self):
        # Save the generated input content to a file
        input_content = self.generate_input_content()
        file_path = filedialog.asksaveasfilename(defaultextension=".chk", filetypes=[("Input files", "*.com"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(input_content)
            messagebox.showinfo("File Saved", f"Input file saved as: {os.path.basename(file_path)}")
        else:
            messagebox.showinfo("Save Cancelled", "File save operation was cancelled.")
    
    def submit_input(self):
        # Functionality to be executed when the submit button is clicked
        messagebox.showinfo("SUBMIT", "File Submitted Successfully to GUSSAIN")

if __name__ == "__main__":
    app = SimpleGUI()
    app.mainloop()