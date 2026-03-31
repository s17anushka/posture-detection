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