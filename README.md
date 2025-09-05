<div align="center">
  <h1 align="center">Django Weather Dashboard</h1>
  <p align="center">
    A well designed, responsive web application built with Django to provide real-time weather forecasts and stunning data visualizations.
    <br />
    
    
  </p>
</div>

<!-- Badges -->
<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/Django-4.x-green?style=for-the-badge&logo=django" alt="Django Version">
  <img src="https://img.shields.io/badge/Matplotlib-3.x-orange?style=for-the-badge&logo=matplotlib" alt="Matplotlib Version">
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="License">
</div>

---

## Key Features

This dashboard provides a comprehensive suite of features to keep you informed about the weather.

*   ** City & Day Selection:** Easily switch between pre-configured cities and select the forecast duration (1 to 5 days).
*   ** Current Weather at a Glance:** A beautifully designed card displays the most critical real-time data:
    *   Temperature, wind speed, and pressure
    *   Cloud coverage and UV index
    *   Sunrise and sunset times
    *   Modern, condition-based SVG weather icons.
*   ** Dynamic Data Charts:** Four interactive charts visualize the 24-hour forecast for:
    *   **Temperature:** Track the highs and lows throughout the day.
    *   **Precipitation:** View rain accumulation and probability.
    *   **Cloud Coverage:** See when the skies will be clear or overcast.
    *   **Wind Speed:** Monitor wind conditions.
*   ** Current Hour Marker:** Each chart features a distinct vertical line that marks the current hour, so you always know where you are in the forecast.
*   ** Dismissible Alerts:** Important weather alerts or application notifications are displayed in a clean, dismissible banner.
*   ** Detailed Hourly Forecast:** A clean, organized table breaks down the weather for every hour of the selected forecast period.
*   ** Fully Responsive Design:** The interface is optimized for a seamless experience on both desktop and mobile devices.

---

##  Technology Stack

This project is built with a modern and robust set of technologies:

*   **Backend:**
    *   ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
    *   ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
*   **Frontend:**
    *   ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
    *   ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
    *   ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
*   **Data Visualization:**
    *   ![Matplotlib](https://img.shields.io/badge/Matplotlib-872A20?style=flat&logo=matplotlib&logoColor=white) (for server-side chart generation)
*   **API:**
    *   External weather API (e.g., Open-Meteo) to fetch forecast data.

---

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Make sure you have Python (3.10+) and pip installed on your system.

*   **Python:** `python --version`

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/Czerw0/Django-Weather-App.git
    cd Django-Weather-App
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```sh
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    *   This project likely requires an API URL to fetch weather data. You should handle this securely. While not included in the repo, you would typically create a `.env` file in the project root.

5.  **Run the development server:**
    ```sh
    python manage.py runserver
    ```
    Open your browser and navigate to `http://127.0.0.1:8000/` to see the application in action!

---

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` file for more information.

---
