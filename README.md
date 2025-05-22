# 🚨 adv2-urgence – Real-Time Accident Detection via Video Stream

**adv2-urgence** is a real-time video processing system designed to detect accidents or abnormal events using a connected camera. It compares live frames against a background reference to identify anomalies and can trigger further analysis or API responses.

---

## 🚀 Features

-   🎥 **Real-Time Video Processing** via OpenCV
-   🧠 **Background Subtraction & Comparison** for motion detection
-   🔄 **Daily Reset Mechanism** for update checks
-   ⚙️ **Dynamic Configuration** via `settings.py`
-   🌐 **Web API Integration** for sending alerts (via `webservice.py`)
-   🧪 **Support for TensorFlow Model** (custom-trained)

---

## 🛠️ Tech Stack

| Component       | Technology                   |
| --------------- | ---------------------------- |
| Video Stream    | OpenCV, Python               |
| ML Inference    | TensorFlow Lite (custom)     |
| Backend         | Python Scripts               |
| Communication   | HTTP API (via webservice.py) |
| Config/Settings | JSON, Python                 |

---

## 📁 Folder Structure

```
adv2-urgence/
├── camera.py              # Camera stream utilities
├── main.py                # Main loop and detection logic
├── video.py               # Frame comparison and background modeling
├── person.py              # Person detection logic
├── webservice.py          # API integration
├── settings.py            # System configuration
├── tensorflow-for-poets-2/  # TensorFlow Lite model
└── images/                # Sample images and readme
```

---

## ▶️ How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Main Detection Loop

```bash
python main.py
```

> Make sure your camera is connected and accessible at index 0 (`Video(0)`)

---

## ⚙️ Configuration

You can modify detection sensitivity, background refresh interval, and alert settings in `settings.py`.

---

## 📄 License

This project is for educational and research purposes only. For inquiries, please contact [anirut.puangkingkaew@gmail.com](mailto:anirut.puangkingkaew@gmail.com)
