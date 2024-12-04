import Task
import dispatcher
import utils
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import plotly.graph_objects as go
import pandas as pd

class TaskSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler")
        self.final_schedule = None
        self.d = None

        # Create input fields for task attributes
        self.entries = []
        labels = ["Task name", "Period", "Deadline", "WCET", "m", "k"]
        for i, label_text in enumerate(labels):
            entry = tk.Entry(root)
            entry.insert(0, label_text)
            entry.bind("<FocusIn>", lambda e, entry=entry, label=label_text: self.clear_placeholder(entry, label))
            entry.bind("<FocusOut>", lambda e, entry=entry, label=label_text: self.add_placeholder(entry, label))
            entry.grid(row=0, column=i, padx=5, pady=5)
            self.entries.append(entry)

        # Add Task Button
        add_task_btn = tk.Button(root, text="Add Task", command=self.add_task)
        add_task_btn.grid(row=0, column=len(labels), padx=5)

        # Delete Task Button
        delete_task_btn = tk.Button(root, text="Delete Task", command=self.delete_task)
        delete_task_btn.grid(row=0, column=len(labels) + 1, padx=5)

        # Task Box (Listbox for displaying tasks)
        self.task_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=60, height=8)
        self.task_listbox.grid(row=1, column=0, columnspan=len(labels) + 2, padx=5, pady=5)

        # Load Tasks from File Button
        load_tasks_btn = tk.Button(root, text="Load Tasks from File", command=self.load_tasks_from_file)
        load_tasks_btn.grid(row=2, column=0, columnspan=len(labels) + 2, padx=5, pady=5)

        # Drop down for m-k pattern
        self.pattern_var = tk.StringVar()
        pattern_label = tk.Label(root, text="m-k Pattern:")
        pattern_label.grid(row=3, column=0)
        self.pattern_dropdown = ttk.Combobox(root, textvariable=self.pattern_var, values=["evenly", "deeply_red"]) # ---------
        self.pattern_dropdown.grid(row=3, column=1)

        # Drop down for Scheduling Algorithm
        self.algorithm_var = tk.StringVar()
        algorithm_label = tk.Label(root, text="Scheduling Algorithm:")
        algorithm_label.grid(row=3, column=2)
        self.algorithm_dropdown = ttk.Combobox(root, textvariable=self.algorithm_var, values=["EDF", "LLF", "RM_P", "RM_NP"]) # ----------
        self.algorithm_dropdown.grid(row=3, column=3)

        # Processor Count Entry
        processor_label = tk.Label(root, text="Number of Processors:")
        processor_label.grid(row=3, column=4)
        self.processor_count_entry = tk.Entry(root, width=5)
        self.processor_count_entry.insert(0, "1")  # Default value for processors
        self.processor_count_entry.grid(row=3, column=5)

        # Execute Button
        execute_btn = tk.Button(root, text="Execute", command=self.execute)
        execute_btn.grid(row=3, column=6)

        # Placeholder for the task list
        self.task_list = []

        # Frame for Gantt Chart
        self.chart_frame = tk.Frame(root)
        self.chart_frame.grid(row=4, column=0, columnspan=len(labels) + 2, padx=5, pady=5)
        
        self.chart_image_label = None
        
        
        stats_label = tk.Label(root, text="Scheduling Statistics:")
        stats_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=5)
        
        # Text widget for statistics display
        self.stats_text = tk.Text(root, height=10, width=80, wrap="word", state="disabled")
        self.stats_text.grid(row=6, column=0, columnspan=len(labels) + 2, padx=5, pady=5)

        # # Export Gantt Chart Button
        # export_image_btn = tk.Button(root, text="Export Gantt Chart as Image", command=self.export_gantt_image)
        # export_image_btn.grid(row=7, column=0, padx=5, pady=5)

        # Export Schedule Data Button
        export_excel_btn = tk.Button(root, text="Export Schedule as Excel", command=self.export_schedule_to_excel)
        export_excel_btn.grid(row=7, column=0, padx=5, pady=5)

    def clear_placeholder(self, entry, label):
        if entry.get() == label:
            entry.delete(0, tk.END)

    def add_placeholder(self, entry, label):
        if not entry.get():
            entry.insert(0, label)

    def add_task(self):
        task_data = [entry.get() for entry in self.entries]
        if any(data == "" or data in ["Task name", "Period", "Deadline", "WCET", "m", "k"] for data in task_data):
            messagebox.showwarning("Warning", "Please fill in all fields before adding a task.")
            return
        self.task_listbox.insert(tk.END, " ".join(task_data))
        self.task_list.append(task_data)

    def delete_task(self):
        selected_task_index = self.task_listbox.curselection()
        if not selected_task_index:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return
        self.task_listbox.delete(selected_task_index)
        del self.task_list[selected_task_index[0]]

    def load_tasks_from_file(self):
        file_path = filedialog.askopenfilename(title="Select Task File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        if file_path:
            with open(file_path, "r") as file:
                for line in file:
                    task_data = line.strip().split(" ")
                    self.task_listbox.insert(tk.END, " ".join(task_data))
                    self.task_list.append(task_data)

    def execute(self):
        selected_pattern = self.pattern_var.get()
        selected_algorithm = self.algorithm_var.get()
        processor_count = self.processor_count_entry.get()

        if not selected_pattern or not selected_algorithm:
            messagebox.showwarning("Warning", "Please select both m-k pattern and scheduling algorithm.")
            return

        if not processor_count.isdigit() or int(processor_count) < 1:
            messagebox.showwarning("Warning", "Please enter a valid number of processors.")
            return

        task_objects = [self.create_task_object(data) for data in self.task_list]
        
        d = dispatcher.Dispatcher(int(processor_count), task_objects)
        d.run(selected_algorithm, selected_pattern)
        d.print_all_schedules()
        #d.print_diagnostics()
        self.final_schedule = d.get_all_schedules()
        self.d = d
        #messagebox.showinfo("Info", f"Executed with {selected_algorithm} algorithm and {selected_pattern} pattern, using {processor_count} processors.")
        
        # Plot the Gantt chart
        self.plot_gantt_chart2()
        self.display_statistics()

    def display_statistics(self):
        # Gather statistics after execution
        stats_info = []
        
        # Add overall CPU utilization and other metrics
        if self.final_schedule:
            
            # Per processor statistics
            for processor in self.d.processor_list:
                proc_util = processor.utilization()
                stats_info.append(f"Processor {processor.name}: Utilization = {proc_util:.2f}%")
            
            for t in self.d.tasklist : 
                stats_info.append(f"Task : {t.name}, No. of Mandatory jobs missed : {t.Mandatory_jobsmissed}, No. of Optional jobs missed : {t.Optional_jobsmissed}")
                
            

        # Display statistics in the stats_text widget
        self.stats_text.config(state="normal")  # Enable editing
        self.stats_text.delete(1.0, tk.END)  # Clear previous statistics
        self.stats_text.insert(tk.END, "\n".join(stats_info))  # Insert new statistics
        self.stats_text.config(state="disabled")  # Disable editing

    def create_task_object(self, data):
        # Convert data from task list to a Task object
        task_name, period, deadline, wcet, m, k = data
        return Task.Task(task_name, int(period), int(deadline), int(wcet), int(m), int(k))
    
    
    def plot_gantt_chart2(self):

        # Sample hyperperiod for demonstration
        hyperperiod = self.d.hyperperiod

        # Sample schedule dictionary structure
        schedule = self.final_schedule

        # Transform the schedule dictionary into a DataFrame for Plotly
        data = []
        for processor, tasks in schedule.items():
            for time_int, task in tasks.items():
                start_time = time_int[0]
                end_time = time_int[1]
                data.append({
                    "Processor": processor,
                    "Start": start_time,
                    "Finish": end_time,
                    "Task": task
                })

        df = pd.DataFrame(data)

        # Initialize an empty Plotly figure
        fig = go.Figure()

        # Predefined list of unique tasks
        unique_tasks = [task.name for task in self.d.tasklist]
        num_tasks = len(unique_tasks)

        # Generate a color map for the tasks using Matplotlib
        colors = plt.cm.get_cmap("tab10", num_tasks)  # Using 'tab10' colormap for up to 10 colors
        task_colors = {task: colors(i) for i, task in enumerate(unique_tasks)}

        # Convert RGBA colors to hex for Plotly
        task_colors = {task: f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}" 
                    for task, (r, g, b, _) in task_colors.items()}

        # Add a trace for each task interval with labels and narrower bars
        for _, row in df.iterrows():
            fig.add_trace(go.Bar(
                x=[row["Finish"] - row["Start"]],
                y=[row["Processor"]],
                base=row["Start"],
                orientation='h',
                name=row["Task"],
                marker_color=task_colors.get(row["Task"], "gray"),
                text=row["Task"],  # Adding task name as text
                textposition="inside",  # Positioning text inside the rectangle
                insidetextanchor="middle",  # Centering text
                hovertemplate=f"Processor: {row['Processor']}<br>Task: {row['Task']}<br>Start: {row['Start']}<br>End: {row['Finish']}"
            ))

        # Customize layout
        fig.update_layout(
            title="Multiprocessor Task Scheduling Gantt Chart",
            xaxis=dict(
                title="Time (seconds)",
                rangeslider=dict(visible=True),
                range=[0, hyperperiod]
            ),
            yaxis=dict(
                title="Processor",
                categoryorder="category ascending",
                tickvals=df["Processor"].unique(),
                tickmode="array",
                dtick=1
            ),
            barmode='relative',  # Change from 'stack' to 'relative' for narrower bars
            showlegend=False
        )

        fig.show()
    
    def export_gantt_image(self):
        if self.final_schedule is None:
            messagebox.showerror("Error", "No schedule available to export.")
            return

        # Ask the user where to save the image
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")]
        )
        if not file_path:
            return  # User canceled the save dialog

        # Generate the Plotly figure again
        fig = self.create_gantt_chart()
        try:
            fig.write_image(file_path)  # Export the image
            messagebox.showinfo("Success", f"Gantt chart successfully exported to {file_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export image. Error: {e}")

    def export_schedule_to_excel(self):
        if self.final_schedule is None:
            messagebox.showerror("Error", "No schedule available to export.")
            return

        # Ask the user where to save the Excel file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if not file_path:
            return  # User canceled the save dialog

        # Transform the schedule dictionary into a DataFrame
        data = []
        for processor, tasks in self.final_schedule.items():
            for time_int, task in tasks.items():
                start_time = time_int[0]
                end_time = time_int[1]
                data.append({
                    "Processor": processor,
                    "Start": start_time,
                    "Finish": end_time,
                    "Task": task
                })

        df = pd.DataFrame(data)
        try:
            # Export the DataFrame to an Excel file
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Schedule successfully exported to {file_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel file. Error: {e}")

    def create_gantt_chart(self):
        # This method replicates your existing Gantt chart generation logic
        # Returns the Plotly figure object
        hyperperiod = self.d.hyperperiod
        schedule = self.final_schedule

        data = []
        for processor, tasks in schedule.items():
            for time_int, task in tasks.items():
                start_time = time_int[0]
                end_time = time_int[1]
                data.append({
                    "Processor": processor,
                    "Start": start_time,
                    "Finish": end_time,
                    "Task": task
                })

        df = pd.DataFrame(data)

        fig = go.Figure()
        unique_tasks = [task.name for task in self.d.tasklist]
        num_tasks = len(unique_tasks)

        colors = plt.cm.get_cmap("tab10", num_tasks)
        task_colors = {task: colors(i) for i, task in enumerate(unique_tasks)}
        task_colors = {task: f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}" 
                       for task, (r, g, b, _) in task_colors.items()}

        for _, row in df.iterrows():
            fig.add_trace(go.Bar(
                x=[row["Finish"] - row["Start"]],
                y=[row["Processor"]],
                base=row["Start"],
                orientation='h',
                name=row["Task"],
                marker_color=task_colors.get(row["Task"], "gray"),
                text=row["Task"],
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=f"Processor: {row['Processor']}<br>Task: {row['Task']}<br>Start: {row['Start']}<br>End: {row['Finish']}"
            ))

        fig.update_layout(
            title="Multiprocessor Task Scheduling Gantt Chart",
            xaxis=dict(
                title="Time (seconds)",
                rangeslider=dict(visible=True),
                range=[0, hyperperiod]
            ),
            yaxis=dict(
                title="Processor",
                categoryorder="category ascending",
                tickvals=df["Processor"].unique(),
                tickmode="array",
                dtick=1
            ),
            barmode='relative',
            showlegend=False
        )
        return fig

# Run the Tkinter application
root = tk.Tk()
app = TaskSchedulerApp(root)
root.mainloop()
