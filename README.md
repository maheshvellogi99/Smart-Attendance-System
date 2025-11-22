# Smart Attendance System

A computer-vision–based attendance system that uses **face recognition** with a **QR / barcode fallback** to mark student attendance. Attendance is stored both **locally in an Excel sheet** and **remotely in Firebase Realtime Database**, with **audio confirmations** via text‑to‑speech.

This project is intended for classroom / lab environments where each student has a unique ID (on an ID card as QR/barcode) and a registered face image.

---

## Features

- **Face recognition–based attendance**  
  Recognizes registered student faces from the webcam using the `face_recognition` library.

- **QR / barcode fallback**  
  If a face is not recognized, the system prompts the user to scan a QR code or barcode (e.g., on an ID card) to register and/or mark attendance.

- **Automatic student registration**  
  When a new code is scanned, the captured face image is associated with that ID and stored for future recognition.

- **Excel-based attendance log**  
  Attendance is recorded in `attendance.xlsx` with:
  - `Student ID`
  - `Year`
  - `Registration Date`
  - One column per date, with the **time** at which attendance was marked.

- **Cloud sync with Firebase Realtime Database**  
  Attendance records are also pushed to Firebase under structured paths for both **date-wise** and **student-wise** lookup.

- **Audio feedback (text‑to‑speech)**  
  Uses `pyttsx3` to announce events such as unrecognized faces and successful attendance marking.

- **Persistent face encodings**  
  Face encodings are stored in `face_encodings.pkl` and reference images in `registered_faces/` for reuse across runs.

- **Error logging**  
  Errors (e.g., issues updating Firebase or saving Excel) are appended to `error_log.txt` for debugging.

---

## Tech Stack

- **Language:** Python 3
- **Computer Vision:** OpenCV (`opencv-python`)
- **Face Recognition:** `face-recognition`, `dlib`, `face-recognition-models`
- **Data Storage:**
  - Local: Excel file via `openpyxl`
  - Cloud: Firebase Realtime Database via `firebase-admin`
- **Barcode / QR:** `pyzbar`, OpenCV QRCode detector
- **Text-to-Speech:** `pyttsx3`

All Python dependencies are listed in `requirements.txt`.

---

## Project Structure

```text
Smart attendence system/
├── code.py                  # Main entry point for the attendance system
├── face_utils.py            # Helper functions for face registration / recognition
├── firebase_config.py       # Firebase initialization and database helper
├── qr.py                    # Simple script to generate a test QR code image
├── attendance.xlsx          # Excel workbook used to store attendance locally
├── face_encodings.pkl       # Pickled face encodings (created at runtime)
├── registered_faces/        # Saved face images for each registered ID
├── firebase-credentials.json# Firebase service account credentials (DO NOT COMMIT)
├── requirements.txt         # Python dependencies
├── error_log.txt            # Error log file (appended at runtime)
├── .venv/                   # (Optional) Local virtual environment
└── __pycache__/             # Python bytecode cache (auto-generated)
```

> Note: Files like `.venv/`, `__pycache__/`, and `.DS_Store` are local / generated artifacts and generally **should not** be committed to Git.

---

## How It Works

### 1. Main Flow (`code.py`)

1. **Startup**
   - Registers a signal handler to exit cleanly on `Ctrl+C`.
   - Opens or creates `attendance.xlsx`.
   - Obtains (or creates) the `Attendance` sheet and initializes headers (`Student ID`, `Year`, `Registration Date`, etc.).

2. **Infinite loop: one attendance cycle per student**
   - Prompts the user to position their face and press `c` to capture.
   - Calls `capture_face_from_webcam()`:
     - Opens the webcam, displays a live feed.
     - Attempts to recognize faces periodically using `recognize_face()` from `face_utils.py`.
     - Shows **face recognized** / **face not recognized** messages on the video frame.
     - Plays audio prompts if the face is not recognized.
     - On `c`, returns the captured frame.

3. **Face recognition path**
   - If `recognize_face(face_frame)` returns a known `roll_no` (Student ID):
     - Logs `"Face recognized! Roll No: {roll_no}"`.
     - Calls `process_attendance(roll_no, wb, sheet)`:
       - Ensures the current date column exists (creates it if needed).
       - Finds or creates a row for that student.
       - Calculates/stores the year based on the ID format (configurable in code).
       - Fills the current date column cell with the **time** string.
       - Speaks an audio confirmation.
       - Calls `update_cloud_storage()` to push the record to Firebase.
       - Saves the `attendance.xlsx` workbook.

4. **New student (unrecognized face) path**
   - If the face is **not** recognized:
     - Prints a message instructing the user to scan their barcode/QR.
     - Calls `read_code_from_webcam()`:
       - Shows webcam feed with a green box and instructions.
       - Uses both:
         - OpenCV `QRCodeDetector` for QR codes.
         - `pyzbar` for barcodes.
       - Returns the scanned code data (treated as the student ID).
     - Calls `register_face(face_frame, code_data)` from `face_utils.py`:
       - Extracts a face encoding from the frame (requires exactly one face).
       - Stores the encoding in `face_encodings.pkl` keyed by the ID.
       - Saves a reference face image to `registered_faces/{ID}.jpg`.
     - On successful registration, calls `process_attendance(code_data, wb, sheet)` to mark attendance.

5. **Loop continues** with a short delay, ready for the next student.

### 2. Face Utilities (`face_utils.py`)

- **`register_face(image, roll_no)`**
  - Ensures `registered_faces/` exists.
  - Detects face(s) and computes an encoding.
  - Saves the encoding in `face_encodings.pkl` (a dict mapping `roll_no -> encoding`).
  - Saves the face image as `registered_faces/{roll_no}.jpg`.

- **`recognize_face(image)`**
  - Loads all known encodings.
  - Detects faces in the given frame and computes encodings.
  - Compares each detected face to known encodings using `face_recognition.compare_faces`.
  - Returns the first matching `roll_no` or `None` if no match.

- **`deregister_face(roll_no)`**
  - Optional helper to remove encodings and stored face images for a given ID.

### 3. Firebase Integration (`firebase_config.py`, `update_cloud_storage`)

- `firebase_config.py`:
  - Loads service account credentials from `firebase-credentials.json`.
  - Initializes a Firebase Admin app with `databaseURL` pointing to your Realtime Database.
  - Exposes `get_database()` which returns a root database reference.

- `update_cloud_storage(barcode, date_str, time_str)` in `code.py`:
  - Builds a small attendance record containing:
    - `time`
    - `status` (e.g., `"present"`)
    - `last_updated` timestamp
  - Writes data to paths such as:
    - `attendance/{date}/{studentId}`
    - `attendance/students/{studentId}/{date}`

> Ensure that your **student IDs are valid Firebase keys** (e.g., no `https://`, spaces, or special URL characters), otherwise writes will fail and be logged in `error_log.txt`.

### 4. QR Code Test Script (`qr.py`)

- Simple script that generates a QR code image (`test_barcode.png`) from a hardcoded string.
- Useful for testing scanning functionality or generating sample IDs.

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "Smart attendence system"
```

### 2. Create & activate a virtual environment (recommended)

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> Depending on your OS, installing `dlib` and `face-recognition` may require extra system packages (CMake, C++ build tools, etc.). Refer to their official installation guides if you face build errors.

### 4. Configure Firebase

1. Create a **Firebase project** and **Realtime Database**.
2. Generate a **service account** JSON key and download it.
3. Save it in the project root as:
   - `firebase-credentials.json`
4. Edit `firebase_config.py` if needed so that:
   - The path to the JSON file matches.
   - `databaseURL` points to your own database URL, e.g.:

   ```python
   firebase_admin.initialize_app(cred, {
       'databaseURL': 'https://<your-project-id>.firebaseio.com/'
   })
   ```

> **Security tip:** Do **not** commit `firebase-credentials.json` to public repositories. Add it to your `.gitignore`.

### 5. Webcam setup

- Ensure a working webcam is connected.
- If you have multiple cameras, adjust `WEBCAM_ID` in `code.py` (default is `0`).

---

## Running the Attendance System

From the project root (and with your virtual environment activated, if using one):

```bash
python code.py
```

You should see console output similar to:

- "Attendance system started. Scan face or QR codes/barcodes using webcam."
- Instructions about pressing `c`, `q`, `k`, or `ESC`.

### Typical Usage Flow

1. **First-time student (no registered face yet)**
   - Student stands in front of the camera.
   - When prompted, press `c` to capture.
   - If the face is not recognized, the system will ask to scan an ID.
   - Hold the **ID card (QR/barcode)** inside the green box of the scanner window.
   - Once the code is read:
     - The system registers the face with that ID.
     - Attendance is marked for that ID.

2. **Returning student**
   - Student stands in front of the camera.
   - When prompted, press `c` to capture.
   - If the face matches a registered encoding:
     - Attendance is marked automatically.
     - Audio announces success.

3. **Stopping the system**
   - Press `ESC`, `q`, or `k` on the scanner window to stop scanning.
   - Or press `Ctrl+C` in the terminal to exit gracefully (resources are cleaned up and the workbook is saved).

---

## Data Files & Directories

- **`attendance.xlsx`**
  - Main local attendance log.
  - If missing, it is created automatically.

- **`face_encodings.pkl`**
  - Binary file containing known face encodings.
  - Automatically created/updated by `register_face()`.

- **`registered_faces/`**
  - Contains image files like `{StudentID}.jpg` for human reference and debugging.

- **`error_log.txt`**
  - Logs errors such as Firebase write failures or Excel save errors.
  - Helpful for diagnosing issues (e.g., invalid student IDs as Firebase keys).

---

## Customization

- **Change sheet name or file name**
  - Edit `EXCEL_FILE` and `SHEET_NAME` constants in `code.py`.

- **Change camera source**
  - Modify `WEBCAM_ID` (0 = default webcam, 1 = external, etc.).

- **Adjust face recognition sensitivity**
  - In `face_utils.py`, tweak the `tolerance` parameter in:
    ```python
    face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.5)
    ```
  - Lower tolerance → stricter matching, higher tolerance → more lenient.

- **Adapt year calculation logic**
  - In `process_attendance()` in `code.py`, the year is derived from characters of the student ID.
  - Modify this logic to fit your institution’s ID format.

---

## Known Limitations / Notes

- **Student ID format:**
  - Must be a valid Firebase key (avoid URLs or strings with special characters like `/`, `?`, `#`, `[`, `]`).
  - Prefer simple alphanumeric IDs.

- **Lighting & camera quality:**
  - Face recognition accuracy depends heavily on lighting and camera resolution.

- **Performance:**
  - Face recognition and `dlib` can be CPU-intensive on low‑power machines.

---

## License

Specify your preferred license here (e.g., MIT, Apache 2.0) before publishing to GitHub.
