""" ============================================================ THE IMPORTATION OF USED PYTHON LIBRARIES =================================================================== """
import sys
print(sys.executable)

import csv
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import random
import matplotlib.pyplot as plt
import threading
import numpy as np
import pyttsx3  # Import the pyttsx3 library
import queue   
from queue import Queue
from tkinter import colorchooser  # Import the colorchooser module

""" ============================================================= THE IMPLEMENTATION OF GLOBAL FUNCTIONS STARTS HERE ========================================================== """

# Function or Method that loads User Credentials
# Returns a dictionary of username-password pairs
def load_user_credentials():
    users = {}
    try:
        # Open the CSV file and read each line
        with open('users.csv', 'r') as file:
            for line in file:
                # Split each line into username and password
                username, password = line.strip().split(',')
                users[username] = password
    except FileNotFoundError:
        pass  # File not found, will be created during registration
    return users

# Function to save performance data including user name
def save_performance_data(user_id, user_name, date, accuracy, wpm):
    try:
        score = calculate_score(accuracy, wpm)  # Calculate the score
        # Open the file in append mode
        with open('user_performance.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            # Write the data
            writer.writerow([user_id, user_name, date, accuracy, wpm, score])
    except IOError:
        print("Error in saving performance data")


# Function to load performance data
def load_performance_data(user_id):
    performance_data = []
    try:
        with open('user_performance.csv', 'r') as file:  # with open('user_performance.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == user_id:
                    performance_data.append(row)
    except IOError:
        print("Error in loading performance data")
    return performance_data

# Function to load leaderboard data
def load_leaderboard_data():
    leaderboard_data = []
    try:
        with open('user_performance.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 6:  # Ensure the row has at least 5 columns
                    leaderboard_data.append(row)
    except IOError as e:
        print(f"Error in loading leaderboard data: {e}")
    return sorted(leaderboard_data, key=lambda x: float(x[4]), reverse=True)[:65]  # Top 10 performances based on WPM

# Function to filter data by date
def filter_data_by_date(data, start_date, end_date):
    filtered_data = []
    for row in data:
        date = datetime.strptime(row[1], '%Y-%m-%d')
        if start_date <= date <= end_date:
            filtered_data.append(row)
    return filtered_data

# Function to load text examples from a file
def load_text_examples(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        sentences = [line.strip() for line in file if line.strip()]
    return sentences

# Function to calculate typing accuracy
def calculate_accuracy(original, typed):
    # Split the original text and the typed text into words
    original_words = original.split()
    typed_words = typed.split()

    # Initialize a variable to count the number of correct words
    correct_word_count = 0

    # Iterate over the pairs of original and typed words
    for o, t in zip(original_words, typed_words):
        # Increase the count if the words match
        if o == t:
            correct_word_count += 1

    # Calculate accuracy as the ratio of correct words to total words in the original text
    # Check if the original text is not empty to avoid division by zero
    accuracy = (correct_word_count / len(original_words)) * 100 if original_words else 0
    return accuracy  # This should be a value between 0 and 100

# Function to calculate score based on accuracy and WPM
def calculate_score(accuracy, wpm):
    # Example scoring logic: score is 10 times the product of accuracy and WPM
    return 10 * accuracy * wpm

# Function to determine performance remark based on accuracy
def get_performance_remark(accuracy):
    if accuracy >= 0.95:
        return "Excellent"
    elif accuracy >= 0.80:
        return "Very Good"
    elif accuracy >= 0.65:
        return "Good"
    elif accuracy >= 0.55:
        return "Fair"
    elif accuracy >= 0.45:
        return "Poor"
    else:
        return "Needs Improvement"

""" ============================================================= THE IMPLEMENTATION OF GLOBAL FUNCTIONS STARTS HERE ========================================================== """


""" ============================================================== THE IMPLEMENTATION OF THE MAIN CLASS STARTS HERE ============================================================ """
# Main class for the Typing Test Application
class TypingTestApp:
    """ ======================================= THE IMPLEMENTATION OF LOCAL FUNCTIONS (POPULARLY KNOWN AS METHODS) STARTS HERE ===================================== """
    def __init__(self, user_id, root, sentences):
        self.root = root
        self.original_sentences = sentences.copy()
        self.sentences = sentences
        self.current_example = None
        self.start_time = None
        self.typing_speeds = []
        self.total_accuracy = []  # Initialize as a list
        self.num_examples = len(sentences)
        self.practice_mode = False
        self.session_time_limit = 300  # 5 minutes in seconds
        self.session_end_time = None
        self.test_active = False
        
        # Attributes for user authentication
        self.is_authenticated = False
        
        # Create a label for displaying the time limit
        self.time_limit_label = tk.Label(root, text="Set Time Limit (in minutes):", bg='lightblue')
        self.time_limit_label.pack()

        self.time_limit_entry = tk.Entry(root, bg='lightblue')
        self.time_limit_entry.pack()
                
        self.user_id = user_id  # "user123" Example user ID, can be dynamically set
        self.points = 0
        self.level = 1
        
        self.last_speech_time = 0
        self.speech_delay = 1  # seconds

        
        self.session_data = []
        self.session_end_time = time.time() + self.session_time_limit

        # Setting up the GUI elements like labels, buttons, text entry, etc.
        self.root.title("Typing Test")
        self.root.configure(bg='lightblue')

        # Initialize the progress bar
        self.setup_progress_bar()
        
        # Display points and level
        self.points_label = tk.Label(root, text=f"Points: {self.points}", font=("Helvetica", 16), bg='lightblue')
        self.points_label.pack()

        self.level_label = tk.Label(root, text=f"Level: {self.level}", font=("Helvetica", 16), bg='lightblue')
        self.level_label.pack()

        # User input for number of examples
        self.num_examples_label = tk.Label(root, text="Enter number of text sentences to be typed:", bg='lightblue')
        self.num_examples_label.pack()

        self.num_examples_entry = tk.Entry(root, bg='lightblue')
        self.num_examples_entry.pack()

        # Start button
        self.start_button = tk.Button(root, text="Start Test", command=self.start_countdown, bg='orange')
        self.start_button.pack()

        # Countdown label
        self.countdown_label = tk.Label(root, text="", font=("Helvetica", 16), bg='lightblue')
        self.countdown_label.pack()
        
        # Text display and entry
        self.text_to_type = tk.Text(root, height=5, width=50, font=("Helvetica", 16), bg='lightblue')
        self.text_to_type.pack()
        self.text_to_type.tag_configure("error", background="white", foreground="red")  # Error highlighting style
        self.entry = tk.Entry(root, font=("Helvetica", 16), bg='lightblue')
        self.entry.pack()
        self.entry.bind("<KeyRelease>", self.on_key_release)  # Bind key release event
        self.text_to_type.bind("<KeyRelease>", self.on_key_release)
        self.entry.bind("<Return>", self.submit_text)

        # Results display
        self.results_label = tk.Label(root, text="", font=("Helvetica", 16), bg='yellow')
        self.results_label.pack()

        self.average_accuracy_label = tk.Label(root, text="", font=("Helvetica", 16), bg='yellow')
        self.average_accuracy_label.pack()

        self.average_wpm_label = tk.Label(root, text="", font=("Helvetica", 16), bg='lightblue')
        self.average_wpm_label.pack()

        self.performance_remark_label = tk.Label(root, text="", font=("Helvetica", 16), bg='lightblue')
        self.performance_remark_label.pack()

        # Exit button
        self.exit_button = tk.Button(root, text="Exit", command=root.destroy, bg='pink')
        self.exit_button.pack()

        # Practice Mode Toggle
        self.practice_mode_button = tk.Button(root, text="Toggle Practice Mode", command=self.toggle_practice_mode, bg='lightgreen')
        self.practice_mode_button.pack()
        self.practice_mode_label = tk.Label(root, text="Practice Mode: OFF", font=("Helvetica", 12), bg='lightblue')
        self.practice_mode_label.pack()

        # Animated Text Label
        self.animated_text_label = tk.Label(root, text="Welcome To OsloMet Typing Tests Competition School!", font=("Helvetica", 16), bg='lightblue')
        self.animated_text_label.pack()
        self.animate_text()
        
        # Initialize the text-to-speech engine
        self.speech_queue = queue.Queue()
        self.speech_engine = pyttsx3.init()
        self.speech_engine.setProperty('rate', 150)  # Set speech rate
        self.currently_speaking = None
        # Start the speech processing thread
        threading.Thread(target=self.process_speech_queue, daemon=True).start()

        # Add a label for the countdown
        self.session_time_label = tk.Label(root, text="", font=("Helvetica", 16), bg='lightblue')
        self.session_time_label.pack()

        # Add buttons for viewing history and progress graph
        self.view_history_button = tk.Button(self.root, text="View History", command=self.show_history)
        self.view_history_button.pack()

        self.show_graph_button = tk.Button(self.root, text="Show Progress Graph", command=self.show_progress_graph)
        self.show_graph_button.pack()
           
        # Create a label and entry for the user name
        self.user_name_label = tk.Label(self.root, text="Enter Your Name:", bg='lightblue')
        self.user_name_label.pack()

        self.user_name_entry = tk.Entry(self.root, bg='lightblue')
        self.user_name_entry.pack()

        # Add a button to view the leaderboard
        self.leaderboard_button = tk.Button(self.root, text="View Leaderboard", command=self.show_leaderboard)
        self.leaderboard_button.pack()
        
        # Add a button to change the background color
        self.color_button = tk.Button(root, text="Change Background Color", command=self.choose_background_color)
        self.color_button.pack()
        
        # Add a button to open the settings window
        self.settings_button = tk.Button(root, text="Settings", command=self.create_settings_window)
        self.settings_button.pack()
        
        # Add a label to display authorship and creation year
        self.authorship_label = tk.Label(root, text="Team-ACIT-Oslomet-TypingTester2023 | 3rd Semester 2023", font=("Helvetica", 10), bg='lightblue', fg='gray')
        self.authorship_label.pack(side=tk.BOTTOM, pady=10)

        # Prompt for user login
        self.login_window()
    
    
    def get_current_word_or_sentence(self):
        # Implement the logic to extract the current word or sentence
        # For now, let's just return a placeholder string
        return "current word or sentence"
      
    # Method for User's Registration Form
    def on_register(self):
        entered_username = self.username_entry.get().strip()
        entered_password = self.password_entry.get().strip()
        # Verify credentials (username and password)
        if entered_username and entered_password:
            # Load existing users
            users = load_user_credentials()

            if entered_username in users:
                tk.messagebox.showerror("Registration Failed", "Sorry!, username already exists.")
                return

            # Append new user to the file
            with open('users.csv', 'a') as file:
                file.write(f"{entered_username},{entered_password}\n")

            tk.messagebox.showinfo("Registration Successful", f"{entered_username}, has been successfully registered. You can now log in.")
        else:
            # Show error message for invalid credentials
            tk.messagebox.showerror("Registration Failed", "Username and password cannot be empty.")
 
    # Method to collect both username and userID
    def login_window(self):
        self.login_win = tk.Toplevel(self.root)
        self.login_win.title("Login")
        self.login_win.geometry("300x200")

        tk.Label(self.login_win, text="Welcome to Oslomet typing tester system").pack()
        tk.Label(self.login_win, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_win)
        self.username_entry.pack()

        tk.Label(self.login_win, text="Password:").pack()  # Changed from User ID to Password
        self.password_entry = tk.Entry(self.login_win, show="*")
        self.password_entry.pack()

        tk.Button(self.login_win, text="Login", command=self.on_login).pack()
        tk.Button(self.login_win, text="Register", command=self.on_register).pack()  # Registration button

    # This method is called when the user clicks the login button. It stores the username and user ID and then closes the login window. 
    def on_login(self):
        entered_username = self.username_entry.get().strip()
        entered_password = self.password_entry.get().strip()
        
        # Load existing users
        users = load_user_credentials()
        # Verify credentials (You need to implement this method)
        if entered_username in users and users[entered_username] == entered_password:
            self.user_name = entered_username
            self.user_id = entered_username  # Assuming username as user ID for simplicity
            self.is_authenticated = True
            # Close the login window and display a welcome message
            self.login_win.destroy()
            tk.messagebox.showinfo("Welcome", f"Welcome to the Oslomet typing tester system, {self.user_name}!")
        else:
            # Show error message for invalid credentials
            tk.messagebox.showerror("Login Failed", "Invalid username or password.")


    def verify_credentials(self, username, user_id):
        # Implement your credential verification logic here
        # For now, it just returns True for demonstration purposes
        return True

    # Method to speak the given text
    def speak_text(self, text):
        # Check if the text is already in the queue or being spoken
        if not self.is_text_in_queue(text) and self.currently_speaking != text:
            # Add text to the queue if it's not too full
            if self.speech_queue.qsize() < 5:  # Adjust the threshold as needed
                self.speech_queue.put(text)
     
    def is_text_in_queue(self, text):
        # Check if the text is already in the queue
        with self.speech_queue.mutex:
            return text in self.speech_queue.queue
              
    # Method to handle functionality for speaking out the text     
    def _speak(self, text):
        while True:
            text = self.speech_queue.get()
            self.speech_engine.say(text)
            self.speech_engine.runAndWait()
            self.speech_queue.task_done()
        
    # This method processes the speech queue continuously.     
    def process_speech_queue(self):
        while True:
            text = self.speech_queue.get()
            self.currently_speaking = text
            self.speech_engine.say(text)
            self.speech_engine.runAndWait()
            self.currently_speaking = None
            # Clear the queue to prioritize latest input
            with self.speech_queue.mutex:
                self.speech_queue.queue.clear()
            self.speech_queue.task_done()
    
    # Method to animate text in the GUI
    def animate_text(self):
        def rotate_text(text, i):
            display_text = text[i:] + text[:i]
            self.animated_text_label.config(text=display_text)
            self.root.after(300, lambda: rotate_text(text, (i + 1) % len(text)))
        rotate_text("Welcome To OsloMet Typing Tests Competition School!", 0)

    # Method to start the countdown before the test begins
    def start_countdown(self):
        self.countdown_label.config(text="Starting in 3 seconds...")
        self.root.after(1000, lambda: self.countdown_label.config(text="Starting in 2 seconds..."))
        self.root.after(2000, lambda: self.countdown_label.config(text="Starting in 1 second..."))
        self.root.after(3000, self.prepare_test)

    # Method called when a key is released in the text entry
    # It checks for typing errors and updates the display accordingly
    def on_key_release(self, event):
        typed_text = self.entry.get()
        self.highlight_errors(typed_text)
        
        # Speak the last character typed, if any
        if typed_text:
            last_char = typed_text[-1]
            self.speak_text(last_char)
            
        # Speak the last character typed, if any
        current_time = time.time()
        if current_time - self.last_speech_time > self.speech_delay:
            self.speak_text(event.char)
            self.last_speech_time = current_time

        # Example: Speak only the current word or sentence
        current_text = self.get_current_word_or_sentence()
        if current_text:
            self.speak_text(current_text)


    # Method to highlight errors in the typed text
    def highlight_errors(self, typed_text):
        self.text_to_type.tag_remove("error", "1.0", tk.END)
        min_length = min(len(self.current_example), len(typed_text))
        for i in range(min_length):
            if self.current_example[i] != typed_text[i]:
                self.text_to_type.tag_add("error", f"1.{i}", f"1.{i+1}")
        
        self.text_to_type.tag_remove("error", "1.0", tk.END)
        for i, (original_char, typed_char) in enumerate(zip(self.current_example, typed_text)):
            if original_char != typed_char:
                self.text_to_type.tag_add("error", f"1.{i}", f"1.{i+1}")
                self.text_to_type.tag_config("error", background="yellow", foreground="red")

    # Method to prepare the test by setting the number of examples
    def prepare_test(self):
        try:
            new_num_examples = int(self.num_examples_entry.get())
            new_time_limit = int(self.time_limit_entry.get()) * 60  # Convert minutes to seconds
            if new_num_examples <= 0 or new_time_limit <= 0:
                raise ValueError
        except ValueError:
            self.results_label.config(text="Please enter a valid number of examples and time limit.")
            return

        if not self.test_active:
            self.session_time_limit = new_time_limit
            self.session_end_time = time.time() + self.session_time_limit
            self.test_active = True
            self.start_test()
        else:
            self.num_examples += new_num_examples
            self.next_example()

    # Method to start the typing test
    def start_test(self):
        # Reset session data and other variables at the start of each test
        self.typing_speeds = []
        self.total_accuracy = []  # Initialize as an empty list
        self.session_data = []
        self.test_active = True
        self.session_end_time = time.time() + self.session_time_limit
        self.next_example()
        self.check_session_time()

    # Method to check if the session time limit has been reached
    def check_session_time(self):
        if not self.practice_mode:  # Only check time if not in practice mode
            remaining_time = max(int(self.session_end_time - time.time()), 0)
            self.session_time_label.config(text=f"Time remaining: {remaining_time} seconds")
            if remaining_time <= 0:
                if not self.practice_mode:
                    if self.sentences:
                        self.record_session_data()
                    self.end_test(time_up=True)
            else:
                self.root.after(1000, self.check_session_time)

    # Method record_session_data to handle the session data recording
    def record_session_data(self):
        average_wpm = sum(self.typing_speeds) / len(self.typing_speeds) if self.typing_speeds else 0
        average_accuracy = sum(self.total_accuracy) / len(self.total_accuracy) if self.total_accuracy else 0
        self.session_data.append({
            'session_number': len(self.session_data) + 1,
            'average_wpm': average_wpm,
            'average_accuracy': average_accuracy
        })
     
    # Method to display the next example for typing
    def next_example(self):
        if not self.sentences or time.time() >= self.session_end_time:
            self.end_test()
            return

        self.current_example = self.sentences.pop()
        self.text_to_type.delete("1.0", tk.END)
        self.text_to_type.insert("1.0", self.current_example)
        self.entry.focus_set()
        self.start_time = time.time()
        
        self.current_example = self.sentences.pop()
        self.text_to_type.delete("1.0", tk.END)
        self.text_to_type.insert("1.0", self.current_example)
        self.entry.focus_set()
        self.start_time = time.time()

        # Speak the text
        self.speak_text(self.current_example)
        
        completed_examples = self.num_examples - len(self.sentences)
        self.update_progress_bar(completed_examples, self.num_examples)

    # Method to submit the typed text and calculate performance
    def submit_text(self, event=None):
        if not self.test_active:
            return

        end_time = time.time()
        time_taken = end_time - self.start_time
        typed_text = self.entry.get()
        accuracy = calculate_accuracy(self.current_example, typed_text)  # Calculate accuracy for the current sentence
        wpm = len(typed_text.split()) / (time_taken / 60)  # Calculate WPM for the current sentence
        self.typing_speeds.append(wpm)
        self.total_accuracy.append(accuracy)  # Append accuracy for each sentence

        
        # wpm = len(self.current_example.split()) / (time_taken / 60)

        # Calculate points (example calculation, you can modify it)
        points_earned = int(wpm * accuracy * 10) # Example formula
        self.points += points_earned
        self.points_label.config(text=f"Points: {self.points}")
        # Update level based on points
        self.level = self.points // 100 + 1 # Example: level up every 100 points
        self.level_label.config(text=f"Level: {self.level}")

        if self.practice_mode:
            self.results_label.config(text=f"Instant Feedback - Accuracy: {accuracy:.2%}, WPM: {wpm:.2f}")

        #if not self.practice_mode:
           

        self.entry.delete(0, tk.END)

        if not self.sentences or (self.practice_mode and len(self.sentences) == 1):
            self.sentences = self.original_sentences.copy()  # Reset sentences for continuous practice

        self.next_example()

    # Method to set up the progress bar in the GUI
    def setup_progress_bar(self):
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()

    # Method to update the progress bar based on current progress
    def update_progress_bar(self, current_length, total_length):
        self.progress_bar['value'] = (current_length / total_length) * 100
        self.root.update_idletasks()

    # Method to end the test and display results
    def end_test(self, time_up=False):
        # Calculate and display average accuracy and WPM
        self.test_active = False
        average_accuracy = sum(self.total_accuracy) / len(self.total_accuracy) if self.total_accuracy else 0
        average_wpm = sum(self.typing_speeds) / len(self.typing_speeds) if self.typing_speeds else 0

        #average_accuracy = self.total_accuracy / len(self.typing_speeds) if self.typing_speeds else 0
        #average_accuracy = np.mean(self.total_accuracy) if self.total_accuracy else 0  # Calculate average accuracy
        #average_wpm = np.mean(self.typing_speeds) if self.typing_speeds else 0

        # Convert average accuracy to a decimal
        average_accuracy_decimal = average_accuracy / 100
        
        # Update the labels for accuracy, WPM, and performance remark
        self.average_accuracy_label.config(text=f"Average Accuracy: {average_accuracy:.2f}%")
        self.average_wpm_label.config(text=f"Average WPM: {average_wpm:.2f}")
        self.performance_remark_label.config(text=f"Performance: {get_performance_remark(average_accuracy_decimal)}")
        
        self.session_time_label.config(text="")
        self.display_bar_chart()

        # Save performance data
        date = datetime.now().strftime('%Y-%m-%d')
        user_name = self.user_name_entry.get()  # Get the name entered by the user
        if not user_name:  # Check if the user name is not empty
            # Use the username stored in self.user_name
            user_name = self.user_name if self.user_name else "Anonymous"  # Default name if no name is entered
        print(f"Debug: user_id={self.user_id}, user_name={user_name}, date={date}, average_accuracy={average_accuracy}, average_wpm={average_wpm}")
        save_performance_data(self.user_id, user_name, date, average_accuracy, average_wpm)

        # Record session data for the current session
        self.session_data.append({
            'session_number': len(self.session_data) + 1,
            'average_wpm': average_wpm,
            'average_accuracy': average_accuracy
        })
        
        # Record session data
        if not self.practice_mode:
            self.record_session_data()
        
        if time_up:
            self.results_label.config(text="Time's up! Test ended.")
            self.display_session_graphs()

              
    # Check if typing time duration and display graphs upon completion of the total time. 
    def check_time_and_display_graphs(self):
        if time.time() >= self.session_end_time:
            self.display_session_graphs()

    # Display separate bar graphs for each session
    def display_session_graphs(self):
        # Display graphs only for the current session
        if not self.session_data:
            print("No session data to display")
            return

        # Get data for the current session
        current_session = self.session_data[-1]
        plt.figure(figsize=(10, 6))

        # Typing Speed for the Current Session
        plt.subplot(2, 1, 1)
        plt.bar(1, current_session['average_wpm'], color='blue')
        plt.xlabel('Current Session')
        plt.ylabel('Average WPM')
        plt.title(f"{self.user_name}'s Typing Speed in Current Session")

        # Accuracy for the Current Session
        plt.subplot(2, 1, 2)
        plt.bar(1, current_session['average_accuracy'], color='green')
        plt.xlabel('Current Session')
        plt.ylabel('Average Accuracy')
        plt.title(f"{self.user_name}'s Accuracy in Current Session")

        plt.tight_layout()
        plt.show()

    # Method to toggle practice mode
    def toggle_practice_mode(self):
        self.practice_mode = not self.practice_mode
        mode_text = "ON" if self.practice_mode else "OFF"
        self.practice_mode_label.config(text=f"Practice Mode: {mode_text}")

    # Method to show user's typing history with improved scrollbar and listbox
    def show_history(self):
        if not self.is_authenticated:
            tk.messagebox.showerror("Access Denied", "Please log in to view history.")
            return
        performance_data = load_performance_data(self.user_id)
        print(performance_data)  # Add this line to inspect the performance data
        history_window = tk.Toplevel(self.root)
        history_window.title("Typing Test History")

        # Create a frame to hold the listbox and scrollbar
        frame = tk.Frame(history_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a scrollbar
        scrollbar_vertical = tk.Scrollbar(frame, orient="vertical")
        scrollbar_horizontal = tk.Scrollbar(frame, orient="horizontal")

        # Create a Listbox to display the history
        history_listbox = tk.Listbox(frame, yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set, width=50)

        for i, (user_id, user_name, date, accuracy, wpm, score) in enumerate(performance_data):
            history_listbox.insert(tk.END, f"{i+1}. Date: {date}, Accuracy: {accuracy}, WPM: {wpm}")

        # Pack the scrollbar and listbox
        scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)
        history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the scrollbars to control the listbox
        scrollbar_vertical.config(command=history_listbox.yview)
        scrollbar_horizontal.config(command=history_listbox.xview)
        
        
    # Method to show progress graph
    def show_progress_graph(self):
        if not self.is_authenticated:
            tk.messagebox.showerror("Access Denied", "Please log in to view progress graphs.")
            return
        performance_data = load_performance_data(self.user_id)
        print(performance_data)  # Add this line to inspect the performance data
        dates = []
        accuracies = []
        wpms = []

        for _, _, date, accuracy, wpm, _ in performance_data:
            dates.append(datetime.strptime(date, '%Y-%m-%d'))
            accuracies.append(float(accuracy))
            wpms.append(float(wpm))

        plt.figure(figsize=(10, 6))
        plt.plot(dates, accuracies, marker='o', label='Accuracy')
        plt.plot(dates, wpms, marker='s', label='WPM')
        plt.xlabel('Date')
        plt.ylabel('Performance')
        plt.title(f"{self.user_name}'s Typing Performance Over Time")
        plt.legend()

        # Adding session labels
        for i, date in enumerate(dates):
            plt.text(date, max(accuracies[i], wpms[i]), f"Session {i+1}", ha='right', va='bottom')

        plt.show()
        
    # Method to display bar chart for current session
    def display_bar_chart(self):
        if not self.typing_speeds:
            return

        plt.figure(figsize=(10, 6))
        # Create an array for the x-axis positions
        x_positions = np.arange(len(self.typing_speeds))
        # Plot a bar for each sentence's typing speed
        plt.bar(x_positions, self.typing_speeds, color=plt.cm.viridis(np.linspace(0, 1, len(self.typing_speeds))))

        plt.xlabel('Sentence Number')
        plt.ylabel('WPM')
        plt.title(f"{self.user_name}'s Typing Speed for Each Sentence in Current Session")
        plt.xticks(x_positions)  # Set the x-ticks to correspond to sentence numbers
        plt.show()

    # Function to display the leaderboard
    def show_leaderboard(self):
        if not self.is_authenticated:
            tk.messagebox.showerror("Access Denied", "Please log in to view the leaderboard.")
            return
        try:
            leaderboard_window = tk.Toplevel(self.root)
            leaderboard_window.title("Leaderboard")

            columns = ('User ID','User Name','Date', 'Accuracy', 'WPM', 'Score')
            leaderboard_tree = ttk.Treeview(leaderboard_window, columns=columns, show='headings')

            for col in columns:
                leaderboard_tree.heading(col, text=col)

            leaderboard_data = load_leaderboard_data()

            for row in leaderboard_data:
                # Ensure that each column gets the correct data
                leaderboard_tree.insert('', tk.END, values=row)  # Insert the entire row

            leaderboard_tree.pack(expand=True, fill='both')
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while loading the leaderboard: {e}")


    def choose_background_color(self):
        # Open the color chooser dialog
        color_code = colorchooser.askcolor(title="Choose background color")[1]
        if color_code:
            self.apply_background_color(color_code)

    def apply_background_color(self, color):
        # Apply the selected color to the background of the GUI elements
        self.root.configure(bg=color)
        self.time_limit_label.configure(bg=color)
        self.time_limit_entry.configure(bg=color)  
    
    def create_settings_window(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Customize Interface")

        # Theme Option
        tk.Label(settings_window, text="Select Theme:").pack()
        self.theme_var = tk.StringVar()
        themes = ["Light", "Dark"]
        for theme in themes:
            tk.Radiobutton(settings_window, text=theme, variable=self.theme_var, value=theme, command=self.apply_theme).pack()

        # Font Option
        tk.Label(settings_window, text="Select Font:").pack()
        self.font_var = tk.StringVar()
        fonts = ["Helvetica", "Arial", "Times New Roman"]
        for font in fonts:
            tk.Radiobutton(settings_window, text=font, variable=self.font_var, value=font, command=self.apply_font).pack()

        # Color Option
        tk.Label(settings_window, text="Select Text Color:").pack()
        self.color_var = tk.StringVar()
        colors = ["Black", "Blue", "Red"]
        for color in colors:
            tk.Radiobutton(settings_window, text=color, variable=self.color_var, value=color, command=self.apply_color).pack()

    def apply_theme(self):
        theme = self.theme_var.get()
        if theme == "Dark":
            self.root.configure(bg='gray')
            # Apply dark theme to other widgets...
        else:
            self.root.configure(bg='lightblue')
            # Apply light theme to other widgets...

    def apply_font(self):
        font = self.font_var.get()
        # Apply font to widgets...
        self.text_to_type.configure(font=(font, 16))
        self.entry.configure(font=(font, 16))

    def apply_color(self):
        color = self.color_var.get()
        # Apply color to widgets...
        self.text_to_type.configure(fg=color)
        self.entry.configure(fg=color)
        
    """ =======================================THE IMPLEMENTATION OF LOCAL FUNCTIONS (POPULARLY KNOWN AS METHODS) STOPS HERE ===================================== """
    
    
    
""" ============================================================== THE IMPLEMENTATION OF THE MAIN CLASS STOPS HERE ========================================================== """

""" ========================================================THE IMPLEMENTATION EXECUTION OF THIS MAIN CLASS STARTS HERE ====================================================== """
# Main function to run the application
def main():
    root = tk.Tk()
    sentences = load_text_examples("sentences.txt")
    app = TypingTestApp(None, root, sentences)  # Initialize with None or some placeholder
    root.mainloop()

if __name__ == "__main__":
    main()

