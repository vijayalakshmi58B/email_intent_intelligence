<img width="1400" height="856" alt="dashboard" src="https://github.com/user-attachments/assets/50c265cb-10a2-4308-ae0c-0aed3e9dc7ae" />**Email Intent Classifier – Rule-Based System**
This project is a simple and transparent rule-based email intent classifier built using Python + Flask.
It classifies any given email into categories using keyword-based rules—no machine learning required.
The project contains two versions:
1.app_simple.py → Beginner-friendly, minimal version
2.app_full.py → Advanced UI, structured rules, deployment-ready

**Files in This Project**
1. app_simple.py
Minimal Flask interface
Basic keyword rules
Easy to read and modify
Suitable for academic/demo submissions
2. app_full.py
Advanced version with improved UI
Clean layout using inline HTML + CSS
More structured email intent rules
Recommended for GitHub and deployment

**Features**
Classifies email text into intents such as:
Job Application
Complaint
Request
Query
Appreciation
General/Other
Transparent keyword-based rules (easy to customize)
Runs locally with no external dependencies except Flask
Clean web interface for classification

**Installation**
Install Flask:
1.pip install flask
2.Run the Simple Version:
3.python app_simple.py
4.Run the Full Version:
5.python app_full.py
6.Open in browser:
http://127.0.0.1:5000/

**Usage**
Enter or paste email text
Click the Classify button
The system analyzes keywords
Outputs the predicted intent category

**Output**
The entered email text
The predicted category
clean UI with formatted output
![home page](screenshots/home.png)
![result](screenshots/result.png)
![dashboard](screenshots/dashboard.png)

**Requirements**
Create a requirements.txt file:
flask==3.0.0
