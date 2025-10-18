
# 🖐️ Gestura

**Gestura** is a real-time **AI-powered hand detection and visual effects system** built with **Python, OpenCV, and MediaPipe**.  
It detects your palm in front of the camera and generates cinematic visual effects — such as **fire**, **ice**, **lightning**, **energy**, **portal**, and **nebula** — that react dynamically to your movements.

---

## 🌟 Features

- 🔥 **6 dynamic visual effects** — fire, ice, lightning, energy, portal, nebula  
- ✋ **Real-time palm and finger tracking** using MediaPipe  
- 💫 **Particle system with physics-based movement and trails**  
- ⚙️ **Custom color palettes and glow effects**  
- 🎨 **Cinematic visuals with soft blur and intensity control**  
- ⌨️ **Keyboard shortcuts to switch effects instantly**  

---

## 🧠 How It Works

Gestura uses **MediaPipe Hands** to detect hand landmarks and compute the palm center.  
It then spawns a collection of **particles** around the palm and fingertips, simulating fire, lightning, or energy bursts using color gradients, velocity, and lifetimes.

Each frame:
1. The webcam captures an image.  
2. MediaPipe detects palm and landmarks.  
3. A particle system generates, updates, and decays visual particles.  
4. Effects are rendered with blur and glow layers for realism.  

---

## ⚙️ Technologies Used

- **Python 3.9+**
- **OpenCV** – for image processing and visualization  
- **MediaPipe** – for accurate hand tracking  
- **NumPy** – for efficient matrix operations  
- **Math / Random** – for particle behavior simulation  

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/navin-oss/Gestura.git
cd Gestura
````

### 2. Install dependencies

```bash
pip install opencv-python mediapipe numpy
```

### 3. Run the project

```bash
python main.py
```

---

## 🎮 Controls

| Key | Effect      | Description                           |
| --- | ----------- | ------------------------------------- |
| `1` | 🔥 Fire     | Classic flame particles rising upward |
| `2` | ❄️ Ice      | Soft blue-white drifting frost        |
| `3` | ⚡ Lightning | Rapid white-yellow electrical sparks  |
| `4` | 🧿 Energy   | Vibrant magenta pulsating aura        |
| `5` | 🌀 Portal   | Rotating swirl around palm center     |
| `6` | 🌌 Nebula   | Expanding cosmic particle field       |
| `Q` | ❌ Quit      | Exit the program                      |

---

## 📸 Preview

| Effect    | Example                                                                                    |
| --------- | ------------------------------------------------------------------------------------------ |
| Fire      | ![fire-demo](https://user-images.githubusercontent.com/your-demo-image-fire.gif)           |
| Lightning | ![lightning-demo](https://user-images.githubusercontent.com/your-demo-image-lightning.gif) |

*(You can add your demo GIFs or screenshots here)*

---

## 🧩 Project Structure

```
Gestura/
├── main.py            # Core hand detection and particle effect logic
├── README.md          # Project documentation
└── requirements.txt   # Dependencies (optional)
```

---

## 🧠 Behind the Scenes

Gestura builds a **custom particle class** that:

* Manages position, velocity, and color
* Decays over time to simulate lifelike movement
* Uses `cv2.circle()` layers and Gaussian blur for glowing visuals
* Responds to palm location updates for dynamic animation

Each particle effect defines:

* Unique **color palette**
* **Velocity** pattern
* **Life span**
* **Radius decay rate**

This modular design makes it easy to add new effects by editing the `col_pal` and `behaviors` dictionaries.

---

## 💡 Future Improvements

* Add gesture-based switching (e.g., swipe to change effects)
* Integrate with AR or camera filters
* Support multi-hand interactions
* Add sound or haptic feedback

---

## 👨‍💻 Author

**Navin Oss**
🔗 [GitHub](https://github.com/navin-oss)


> “Detect hands. Add effects. Make it cinematic — all in Python.”


---

Would you like me to include a **`requirements.txt`** file for easy installation (so users can just run `pip install -r requirements.txt`)?
```
