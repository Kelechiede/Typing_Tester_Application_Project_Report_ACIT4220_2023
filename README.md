# Typing Tester Application

A Python-based Typing Tester Application developed using Tkinter. This application helps users improve their typing speed and accuracy by providing timed typing tests. It also includes features like user authentication, progress tracking, and a leaderboard to compare performances.

## Description

The Typing Tester Application is designed to help users enhance their typing skills by offering a platform where they can practice typing and receive feedback on their speed (WPM) and accuracy. Users can log in or register, choose between practice mode or timed tests, and track their performance over time. The application also features a leaderboard to compare the best performances.

## Features

- **User Authentication**: Secure login and registration system.
- **Typing Test**: Users can take a timed typing test and receive feedback on their performance.
- **Practice Mode**: Users can practice typing without a time limit, with instant feedback on accuracy and WPM.
- **Progress Tracking**: The application records each session’s performance, allowing users to track their progress over time.
- **Leaderboard**: Displays the top performances based on typing speed (WPM) and accuracy.
- **Text-to-Speech**: Provides spoken feedback of typed characters or sentences using the `pyttsx3` library.
- **Customizable Interface**: Users can change the background color and theme of the application.
- **Visual Feedback**: The application highlights typing errors and provides instant feedback during practice sessions.
- **Graphical Analysis**: View your typing performance over time through graphs showing progress in accuracy and WPM.

## Installation Instructions
Ensure the installation and importation of relevant libraries as shown in the main application script. 

### Prerequisites

Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Clone the Repository

To get started, clone the repository to your local machine:

```bash
git clone https://github.com/Kelechiede/Typing_Tester_Application_Project_Report_ACIT4220_2023.git

### How to Use the Application
1. Launch the Application: Run the TypingTestApp.py file to launch the application.
2. Log In or Register: If you're a new user, you can register by entering a username and password. Existing users can log in with their credentials.
3. Choose Mode: After logging in, choose between "Practice Mode" or "Test Mode".
	.Practice Mode: Allows you to practice typing with instant feedback on accuracy and WPM. No time limit is imposed.
	.Test Mode: Start a timed test by setting the time limit and number of sentences to type. Your performance will be recorded for future reference.
4. Typing Test: Type the displayed text as accurately and quickly as possible. Errors will be highlighted, and you'll receive feedback on your typing speed and accuracy.
5. View Results: After completing the test, view your results including average accuracy, WPM, and performance remark.
6. Track Progress: View your typing history and progress over time using the “View History” and “Show Progress Graph” options.
7. View Leaderboard: Compare your performance with others on the leaderboard.

### License
This project is licensed under the MIT License. See the LICENSE file for more details.
