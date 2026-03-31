# 🪑 Smart Posture Detection System (Advanced)

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose%20Detection-orange)
![Status](https://img.shields.io/badge/Project-Completed-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## 📌 Project Overview

Maintaining proper posture during long study or work sessions is essential to prevent health issues such as back pain and fatigue.

This project presents an **Advanced Smart Posture Detection System** that uses computer vision and pose estimation to monitor posture in real time.

Unlike basic systems, this project uses **multi-metric analysis** for improved accuracy.

---

## 🎯 Objectives

- Detect and classify posture in real time  
- Provide intelligent feedback  
- Track posture quality over time  
- Build a practical AI-based solution  

---

## ⚙️ Technologies Used

- **Python**
- **OpenCV**
- **MediaPipe**

---

## 🧠 Working Principle

1. Capture video using webcam  
2. Detect body landmarks using MediaPipe  
3. Compute posture metrics:
   - Shoulder Tilt  
   - Side Lean  
   - Slouch Detection (calibrated)  
   - Head Tilt  

4. Classify posture:
- ✅ Good  
- 😐 Okay  
- ❌ Bad  

---

## 🚀 Features

- 📷 Real-time posture detection  
- 🧍 Skeleton tracking  
- 📏 Multi-metric analysis  
- ⚙️ Automatic calibration  
- 📊 Session posture score  
- ⏱️ Bad posture duration tracking  
- 🔔 Smart alert system  
- 📁 CSV logging for analysis  

---
## 💡 Novelty of the Project

Unlike traditional posture detection systems that rely on a single angle or basic landmark comparison, this project introduces a **multi-metric posture analysis approach** for improved accuracy and real-world usability.

### 🔹 Key Novel Contributions

- **Multi-Parameter Posture Analysis**  
  Instead of using a single angle, the system evaluates posture using multiple metrics such as:
  - Shoulder tilt  
  - Side lean  
  - Head tilt  
  - Slouch detection  

- **Personalized Calibration System**  
  The system dynamically calibrates the user’s natural upright posture during initial frames, allowing for **adaptive and user-specific posture evaluation**.

- **Heuristic-Based Intelligent Classification**  
  Posture is classified into Good, Okay, and Bad categories using a combination of multiple conditions rather than a single threshold.

- **Real-Time Posture Quality Tracking**  
  The system tracks session-level posture quality and calculates the percentage of time the user maintains a good posture.

- **Smart Alert Mechanism with Cooldown**  
  Alerts are generated intelligently with a cooldown mechanism to prevent repetitive notifications and improve user experience.

- **Data Logging for Future Analysis**  
  Posture data is stored in CSV format, enabling further analysis and potential integration with machine learning models.

### 🔹 Overall Innovation

This project demonstrates how **lightweight computer vision techniques combined with intelligent heuristics** can create an effective and practical posture monitoring system without requiring heavy machine learning training.

## 📊 Output

- Posture status (Good / Okay / Bad)  
- Real-time metrics  
- Session quality (%)  
- Detected posture issues  

---

## ⚠️ Limitations

- Approximate posture detection (not medical-grade)  
- Accuracy depends on camera angle and lighting  
- Slight posture issues may still be classified as "Good"  

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python app.py

##  Author: Anushka Singh