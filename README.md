# Exercise 3 - Atari Breakout Reinforcement Learning

## Overview 👾

This project implements a minimalistic clone of the classic Atari game "Breakout" and explores the application of Reinforcement Learning (RL) techniques to train an agent to play it. The primary goal is to use a Monte Carlo control method to compute an optimal policy for the paddle's movement, aiming to clear all bricks as quickly as possible.

The project comprises both a backend using Flask and handling game logic as well as the RL agent, and a JavaScript frontend providing a simple web-based visualization of the game in action.

## Project Goals (from Exercise 3.3)

* Implement a minimalistic Breakout game clone based on specified element sizes and grid dimensions.😃

* Apply a Monte Carlo control method to compute an optimal policy for the paddle.

* Experiment with various brick layouts (rectangle, other forms) and amounts (5-10 bricks).

* Analyze and report on how different brick layouts affect learning runtime.

* Generate figures to visualize found trajectories and learning progress.

## Technologies Used

* **Python 3.9:** For all backend logic, game simulation, and Reinforcement Learning agent.

* **HTML, CSS, JavaScript:** For the frontend web-based visualization.

## Setup Instructions

Follow these steps to set up and run the project locally. 🙌

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/TUWMLGW/Exercise_3.git](https://github.com/TUWMLGW/Exercise_3.git)
    cd Exercise_3
    ```

2.  **Create and Activate a Python Virtual Environment:**
    We recommend to use a virtual environment to manage dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run the Application 👀

Once the setup is complete, you can run the application.

1.  **Ensure your virtual environment is active.** (You should see `(venv)` in your terminal prompt).

2.  **Navigate to the project's root directory**

3.  **Run the Flask development server:**
    ```bash
    python3 -m backend.app
    ```

4.  **Access the GUI:**
    Open your web browser and navigate to:
    `http://127.0.0.1:5000/`

    If everything worked out smoothly, you should see the web page with the game. Have fun!🥳