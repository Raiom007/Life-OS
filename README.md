<div align="center">
  <img src="https://raw.githubusercontent.com/Raiom007/Life-OS/main/assets/logo.png" alt="Life OS Logo" width="120" style="border-radius: 20%;" onerror="this.onerror=null; this.src='https://img.icons8.com/color/120/000000/dashboard-layout.png'"/>
  
  <h1>⚡ Life OS</h1>
  
  <p><strong>A Gamified Personal Command Center & Performance Dashboard built with Streamlit.</strong></p>

  <p>
    <a href="https://github.com/Raiom007/Life-OS/stargazers"><img src="https://img.shields.io/github/stars/Raiom007/Life-OS?style=for-the-badge&color=ffd700" alt="Stars" /></a>
    <a href="https://github.com/Raiom007/Life-OS/issues"><img src="https://img.shields.io/github/issues/Raiom007/Life-OS?style=for-the-badge&color=dc143c" alt="Issues" /></a>
    <a href="https://github.com/Raiom007/Life-OS/network/members"><img src="https://img.shields.io/github/forks/Raiom007/Life-OS?style=for-the-badge&color=00bfff" alt="Forks" /></a>
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/>
    <img src="https://img.shields.io/badge/Streamlit-Framework-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  </p>
</div>

<hr/>

## 🎯 What is Life OS?

Life OS is your ultimate productivity dashboard, transforming daily habits, learning routines, and fitness goals into an engaging, RPG-style experience. It tracks everything from your LeetCode/DSA grinds to gym sessions and AI studies, granting Experience Points (XP) and visualizing your discipline.

Stop tracking habits in boring spreadsheets. **Level up your life.**

---

## ✨ Features

- **🎮 RPG Integration:** Gain XP, maintain streaks, and level up as you complete tasks. Encounter weekly "bosses" (your weakest performance areas) to conquer.
- **🏋️‍♂️ Body & Gym Log:** Track workouts, energy levels, and weight with rolling weekly average visualizations.
- **💻 DSA Tracker:** Log coding problems, identify weakest topics based on completion time, and track difficulty across multiple platforms.
- **🧠 AI Learning Hub:** Log hours studied, code implementation milestones, and note-taking consistency.
- **📊 Advanced Analytics:** Beautiful, interactive Plotly charts, habit heatmaps, and a dynamic radar chart displaying your overall performance balance.
- **📓 Mistake Log:** A dedicated area to document, analyze, and resolve conceptual gaps and logic errors from your coding journey.
- **🌙 Cyber-Dark Theme:** A sleek, high-contrast aesthetics built directly into the UI components.

---

## 📸 Screenshots

<div align="center">
  <img src="https://raw.githubusercontent.com/Raiom007/Life-OS/main/assets/dashboard.png" alt="Command Center Dashboard" width="80%">
  <p><em>The Command Center displaying RPG stats, heatmaps, and progress gauges.</em></p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/Raiom007/Life-OS/main/assets/analytics.png" alt="Weekly Analytics" width="80%">
  <p><em>Weekly Analytics showcasing the Balance Radar and hard stats.</em></p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/Raiom007/Life-OS/main/assets/gym.png" alt="Body and Gym Tracker" width="80%">
  <p><em>Body & Gym tracker with rolling average weight visualizations.</em></p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/Raiom007/Life-OS/main/assets/dsa.png" alt="DSA Tracker" width="80%">
  <p><em>DSA Tracker showing topic distribution and difficulty breakdowns.</em></p>
</div>

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Raiom007/Life-OS.git
cd Life-OS
```

### 2. Install Dependencies
Ensure you have Python 3.8+ installed. Install the required libraries using pip:
```bash
pip install -r requirements.txt
```

### 3. Run the OS
Launch the Streamlit dashboard:
```bash
python -m streamlit run app.py
```
> The web app will instantly open in your default browser at `http://localhost:8501`.

---

## 🛠️ Tech Stack & Architecture

- **Frontend / UI:** [Streamlit](https://streamlit.io/) + Custom CSS
- **Visualizations:** [Plotly](https://plotly.com/python/) & Pandas
- **Database:** SQLite (Built-in via `database.py`)
- **Data Handling:** Pandas & Numpy

**Core Files Structure:**
- `app.py`: The main routing and UI definitions.
- `analytics.py`: Handles RPG XP logic, scoring systems, and data processing.
- `database.py`: Manages SQLite connections and table schema definitions.
- `components.py`: Reusable UI modules (KPI headers, progress bars, radar charts).
- `utils.py`: CSV backup handling and utility functions.
- `assets/style.css`: Core aesthetic rules and overrides.

---

## 🗺️ Roadmap / Future Updates

- [ ] Export/Import functionality for database backups.
- [ ] Customizable theme selections (Light, Synthwave, Minimal).
- [ ] GitHub/LeetCode API integrations for automated syncing.
- [ ] Mobile-optimized responsive layout tweaks.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check out the [issues page](https://github.com/Raiom007/Life-OS/issues).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <b>Built with ❤️ and Discipline</b>
</div>
