# StructAI Layout Design Optimizer

StructAI is an Advanced Architectural Design AI that generates 2D blueprints and 3D models based on user-defined plot dimensions and location data.

## Features

- **2D Blueprint Generation**: Automatically creates floor plans with rooms, furniture, and walkway gaps.
- **3D Interior View**: Visualizes the layout in a 3D "dollhouse" view with realistic textures, furniture, and room labels.
- **3D Structural Grid**: Generates a structural model with columns and beams.
- **3D Foundation Analysis**: Analyzes and visualizes underground footings based on soil data.
- **Location-Based Rules**: Applies city-specific architectural rules (FSI, soil type, etc.) for Mumbai, Delhi, Bangalore, and more.
- **Real-Time Synchronization**: Manual 2D layout adjustments instantly reflect in the 3D interior model.

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Three.js for 3D rendering, GSAP for animations).
- **Backend**: Python (Flask).
- **Styling**: Google Fonts (DM Serif Display, DM Mono, Barlow).

## Getting Started

### Prerequisites

- Python 3.x
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/csvc10a27veer-lang/struct-AI-layout-design-optimizer.git
   cd struct-AI-layout-design-optimizer
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://127.0.0.1:5000`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
