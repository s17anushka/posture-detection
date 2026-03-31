import cv2
import mediapipe as mp
import math
import time
import csv
import platform

if platform.system() == "Windows":
    import winsound

# ─────────────────────────────────────────────
# MediaPipe Setup
# ─────────────────────────────────────────────
mp_pose    = mp.solutions.pose
pose       = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# ─────────────────────────────────────────────
# State
# ─────────────────────────────────────────────
bad_start    = None
last_beep    = 0
total_frames = 0
good_frames  = 0
BEEP_COOLDOWN = 5

calib_samples             = []
calibrated_shoulder_width = None
CALIBRATION_FRAMES        = 40

# ─────────────────────────────────────────────
# CSV Log
# ─────────────────────────────────────────────
log_file   = open("posture_log.csv", "w", newline="")
log_writer = csv.writer(log_file)
log_writer.writerow(["Time", "Posture", "Issues", "ShoulderTilt(px)",
                     "SideLean(%)", "Slouch(%)", "HeadTilt(px)", "BadDuration(s)"])

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def px(lm, landmark, w, h):
    p = lm[landmark.value]
    return [p.x * w, p.y * h]

def dist(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def angle_from_vertical(top, bottom):
    """Angle a line makes with vertical. 0=upright, 90=horizontal."""
    dx = top[0] - bottom[0]
    dy = top[1] - bottom[1]
    return math.degrees(math.atan2(abs(dx), abs(dy) + 1e-6))

def beep_alert():
    global last_beep
    now = time.time()
    if platform.system() == "Windows" and (now - last_beep) >= BEEP_COOLDOWN:
        winsound.Beep(1000, 300)
        last_beep = now

def draw_panel(img, x1, y1, x2, y2, alpha=0.82):
    overlay = img.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (25, 25, 25), -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

def draw_metric(img, label, value, unit, y, good_thresh, warn_thresh, invert=False):
    """
    invert=False: lower value = better (shoulder tilt, head tilt, spine offset)
    invert=True : higher value = better (slouch %)
    """
    if invert:
        ok = value >= good_thresh
        warn = value >= warn_thresh
        dot_col = (0, 200, 0) if ok else ((0, 165, 255) if warn else (0, 0, 220))
    else:
        ok = value <= good_thresh
        warn = value <= warn_thresh
        dot_col = (0, 200, 0) if ok else ((0, 165, 255) if warn else (0, 0, 220))

    cv2.circle(img, (38, y - 6), 8, dot_col, -1)
    cv2.putText(img, f"{label}: {value:.1f}{unit}", (55, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 2)
    return dot_col

# ─────────────────────────────────────────────
# Thresholds
# ─────────────────────────────────────────────
# 1. Shoulder Tilt  — Y-difference between left & right shoulder (front lean)
SHOULDER_TILT_GOOD = 12   # px
SHOULDER_TILT_WARN = 22   # px  (tighter than before)

# 2. Side Lean      — shoulder midpoint X drift vs hip midpoint X (sideways bend)
SIDE_LEAN_GOOD     = 4    # % of frame width
SIDE_LEAN_WARN     = 8    # %

# 3. Slouch         — current shoulder width vs calibrated (forward hunch)
SLOUCH_WARN        = 88   # % of calibrated width
SLOUCH_BAD         = 74   # %

# 4. Head Tilt      — nose X vs shoulder midpoint X
HEAD_TILT_GOOD     = 18   # px
HEAD_TILT_WARN     = 35   # px

# ─────────────────────────────────────────────
# Webcam
# ─────────────────────────────────────────────
cap       = cv2.VideoCapture(0)
prev_time = time.time()

print("Sit straight for calibration (first 40 frames)...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w    = frame.shape[:2]
    rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    image   = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    curr_time = time.time()
    fps       = int(1 / max(curr_time - prev_time, 1e-6))
    prev_time = curr_time
    total_frames += 1

    # Side panel
    draw_panel(image, 0, 0, 380, h)
    cv2.putText(image, f"FPS: {fps}", (w - 110, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (160, 160, 160), 2)

    try:
        lm = results.pose_landmarks.landmark

        # ── Landmarks ──
        l_sh  = px(lm, mp_pose.PoseLandmark.LEFT_SHOULDER,  w, h)
        r_sh  = px(lm, mp_pose.PoseLandmark.RIGHT_SHOULDER, w, h)
        l_hip = px(lm, mp_pose.PoseLandmark.LEFT_HIP,       w, h)
        r_hip = px(lm, mp_pose.PoseLandmark.RIGHT_HIP,      w, h)
        nose  = px(lm, mp_pose.PoseLandmark.NOSE,           w, h)

        # Midpoints
        sh_mid  = [(l_sh[0]+r_sh[0])/2,   (l_sh[1]+r_sh[1])/2]
        hip_mid = [(l_hip[0]+r_hip[0])/2, (l_hip[1]+r_hip[1])/2]

        # ── METRIC 1: Shoulder Tilt (px) ──
        shoulder_tilt = abs(l_sh[1] - r_sh[1])

        # ── METRIC 2: Side Lean ──
        # How far shoulder midpoint drifts from hip midpoint horizontally
        side_lean_px  = abs(sh_mid[0] - hip_mid[0])
        side_lean_pct = (side_lean_px / w) * 100  # normalise to frame width

        # ── METRIC 3: Slouch (shoulder width vs calibrated) ──
        cur_sh_width = dist(l_sh, r_sh)

        if calibrated_shoulder_width is None:
            calib_samples.append(cur_sh_width)
            if len(calib_samples) >= CALIBRATION_FRAMES:
                calibrated_shoulder_width = sum(calib_samples) / len(calib_samples)
                print(f"Calibrated: {calibrated_shoulder_width:.1f}px")

            rem = CALIBRATION_FRAMES - len(calib_samples)
            cv2.putText(image, "Sit straight — calibrating...", (390, h//2 - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 210, 255), 2)
            cv2.putText(image, f"{rem} frames left", (390, h//2 + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (200, 200, 200), 2)
            slouch_pct = 100.0
        else:
            slouch_pct = (cur_sh_width / calibrated_shoulder_width) * 100

        # ── METRIC 4: Head Tilt (px) ──
        head_tilt = abs(nose[0] - sh_mid[0])

        # ─────────────────────────────────────────
        # Determine individual issues
        # ─────────────────────────────────────────
        issues = []

        if shoulder_tilt > SHOULDER_TILT_WARN:
            issues.append(("Uneven Shoulders", (0, 80, 255)))
        elif shoulder_tilt > SHOULDER_TILT_GOOD:
            issues.append(("Slight Shoulder Tilt", (0, 140, 255)))

        if side_lean_pct > SIDE_LEAN_WARN:
            issues.append(("Leaning Sideways!", (0, 0, 220)))      # <-- sideways catch
        elif side_lean_pct > SIDE_LEAN_GOOD:
            issues.append(("Slight Side Lean", (0, 140, 255)))

        if calibrated_shoulder_width:
            if slouch_pct < SLOUCH_BAD:
                issues.append(("Slouching Forward!", (0, 0, 220)))
            elif slouch_pct < SLOUCH_WARN:
                issues.append(("Slight Slouch", (0, 140, 255)))

        if head_tilt > HEAD_TILT_WARN:
            issues.append(("Head Tilted", (0, 80, 255)))
        elif head_tilt > HEAD_TILT_GOOD:
            issues.append(("Slight Head Tilt", (0, 140, 255)))

        # ─────────────────────────────────────────
        # Overall posture classification
        # ─────────────────────────────────────────
        bad_issues  = [i for i in issues if "Slight" not in i[0]]
        okay_issues = [i for i in issues if "Slight" in i[0]]

        if bad_issues:
            posture = "Bad Posture"
            p_color = (0, 0, 220)
            if bad_start is None:
                bad_start = time.time()
            duration = int(time.time() - bad_start)
            beep_alert()
        elif okay_issues:
            posture   = "Okay Posture"
            p_color   = (0, 140, 255)
            bad_start = None
            duration  = 0
        else:
            posture   = "Good Posture"
            p_color   = (0, 200, 0)
            bad_start = None
            duration  = 0
            good_frames += 1

        good_pct = int((good_frames / total_frames) * 100)

        # CSV log
        if total_frames % 30 == 0:
            log_writer.writerow([
                time.strftime("%H:%M:%S"), posture,
                " | ".join([i[0] for i in issues]),
                round(shoulder_tilt, 1), round(side_lean_pct, 1),
                round(slouch_pct, 1), round(head_tilt, 1), duration
            ])

        # ─────────────────────────────────────────
        # UI Panel
        # ─────────────────────────────────────────
        cv2.putText(image, "POSTURE MONITOR", (25, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.78, (255, 255, 255), 2)
        cv2.line(image, (15, 52), (365, 52), (80, 80, 80), 1)

        draw_metric(image, "Shoulder Tilt", shoulder_tilt, "px",
                    95,  SHOULDER_TILT_GOOD, SHOULDER_TILT_WARN, invert=False)
        draw_metric(image, "Side Lean    ", side_lean_pct, "%",
                    135, SIDE_LEAN_GOOD,     SIDE_LEAN_WARN,     invert=False)
        draw_metric(image, "Slouch       ", slouch_pct,    "%",
                    175, SLOUCH_WARN,        SLOUCH_BAD,         invert=True)
        draw_metric(image, "Head Tilt    ", head_tilt,     "px",
                    215, HEAD_TILT_GOOD,     HEAD_TILT_WARN,     invert=False)

        cv2.line(image, (15, 228), (365, 228), (80, 80, 80), 1)

        cv2.putText(image, posture, (25, 268),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, p_color, 3)
        cv2.putText(image, f"Bad Time : {duration}s", (25, 305),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.68, (150, 150, 255), 2)
        cv2.putText(image, f"Session  : {good_pct}% good", (25, 335),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.68, (100, 220, 100), 2)

        if issues:
            cv2.line(image, (15, 348), (365, 348), (80, 80, 80), 1)
            for i, (issue_text, issue_color) in enumerate(issues[:4]):
                cv2.putText(image, f"! {issue_text}", (25, 378 + i * 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.60, issue_color, 2)

        # ── Body overlay lines ──
        # Shoulder bar
        cv2.line(image, (int(l_sh[0]),  int(l_sh[1])),
                         (int(r_sh[0]),  int(r_sh[1])), (0, 255, 255), 2)
        # Hip bar
        cv2.line(image, (int(l_hip[0]), int(l_hip[1])),
                         (int(r_hip[0]), int(r_hip[1])), (0, 255, 255), 2)
        # Spine
        cv2.line(image, (int(sh_mid[0]),  int(sh_mid[1])),
                         (int(hip_mid[0]), int(hip_mid[1])), (255, 200, 0), 3)
        # Nose
        cv2.circle(image, (int(nose[0]), int(nose[1])), 8, (255, 0, 255), -1)
        # Vertical reference line from hip mid
        cv2.line(image, (int(hip_mid[0]), int(hip_mid[1])),
                         (int(hip_mid[0]), int(sh_mid[1])),  (80, 80, 80), 1)

    except AttributeError:
        cv2.putText(image, "No pose detected", (25, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (160, 160, 160), 2)
        cv2.putText(image, "Move camera back so", (25, 115),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (160, 160, 160), 2)
        cv2.putText(image, "head & hips are visible", (25, 148),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (160, 160, 160), 2)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(180, 180, 180), thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=(120, 120, 255), thickness=2)
        )

    cv2.imshow("Posture Detection", image)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
log_file.close()
print("Done. Log saved to posture_log.csv")