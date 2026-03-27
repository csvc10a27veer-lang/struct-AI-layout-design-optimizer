from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Advanced Mock data for location-based information including Boring/Well data
MOCK_LOCATION_DATA = {
    "Mumbai": {
        "fsi": 2.5, 
        "soil": "Black Cotton Soil", 
        "boring_depth": "150ft - 250ft",
        "water_quality": "Slightly Hard",
        "foundation_depth": "2.5m to 3.5m",
        "foundation_width": "1.5m",
        "foundation_fertility": "Deep Pile Foundation",
        "rules": [
            "Open space required: 3m on all sides", 
            "Maximum height limit: 70m",
            "Balcony area cannot exceed 10% of floor area",
            "Fire safety norms for 2+ floors apply"
        ]
    },
    "Delhi": {
        "fsi": 2.0, 
        "soil": "Alluvial Soil", 
        "boring_depth": "200ft - 300ft",
        "water_quality": "Good/Potable",
        "foundation_depth": "1.8m to 2.5m",
        "foundation_width": "1.2m",
        "foundation_fertility": "Raft Foundation",
        "rules": [
            "Rainwater harvesting mandatory", 
            "Ground coverage: Maximum 60%",
            "Setback: Front 3m, Sides 2m",
            "Parking: 1 ECS per 100 sq.m"
        ]
    },
    "Bangalore": {
        "fsi": 1.75, 
        "soil": "Red Loamy Soil", 
        "boring_depth": "800ft - 1200ft",
        "water_quality": "Hard",
        "foundation_depth": "1.5m to 2.0m",
        "foundation_width": "1.0m",
        "foundation_fertility": "Isolated Footing",
        "rules": [
            "Solar water heater mandatory", 
            "Setback: 2m all sides for 30x40 sites",
            "FAR: 1.75 for residential",
            "Minimum 10% green area required"
        ]
    },
    "Default": {
        "fsi": 1.5, 
        "soil": "Sandy Loam", 
        "boring_depth": "100ft - 200ft",
        "water_quality": "Moderate",
        "foundation_depth": "1.5m to 2.0m",
        "foundation_width": "1.0m to 1.2m",
        "foundation_fertility": "Spread Footing",
        "rules": [
            "Standard National Building Code (NBC) apply",
            "Minimum room height: 2.75m",
            "Kitchen ventilation: Minimum 10% of floor area"
        ]
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_design', methods=['POST'])
def generate_design():
    data = request.json
    city = data.get('city', 'Default')
    
    # Validation: Enforce Maximum Plot Dimensions
    MAX_WIDTH = 150.0
    MAX_LENGTH = 200.0
    
    plot_width = min(float(data.get('plotWidth', 30)), MAX_WIDTH)
    plot_length = min(float(data.get('plotLength', 40)), MAX_LENGTH)
    
    area_sqft = float(data.get('plotArea', plot_width * plot_length))
    if area_sqft > (MAX_WIDTH * MAX_LENGTH):
        area_sqft = MAX_WIDTH * MAX_LENGTH
        
    floors = int(data.get('floors', 1))
    rooms = int(data.get('rooms', 2))
    bathrooms = int(data.get('bathrooms', 1))
    pooja_room = data.get('poojaRoom', False)
    parking = data.get('parking', False)
    bath_type = data.get('bathType', 'common')

    loc_info = MOCK_LOCATION_DATA.get(city, MOCK_LOCATION_DATA['Default'])
    
    fsi = loc_info['fsi']
    ground_coverage_ratio = 0.65 
    ground_floor_built_up = area_sqft * ground_coverage_ratio
    
    total_built_up = ground_floor_built_up
    if floors > 1:
        total_built_up += (ground_floor_built_up * 0.85) * (floors - 1)
    
    max_fsi_area = area_sqft * fsi
    if total_built_up > max_fsi_area:
        total_built_up = max_fsi_area

    carpet_area = total_built_up * 0.82

    # Layout generation logic
    accuracy = random.randint(92, 99)
    safety_score = random.randint(88, 97)
    column_count = (rooms * 4) + 4
    
    layout = {
        "floors": [],
        "summary": {
            "plot_width": plot_width,
            "plot_length": plot_length,
            "total_carpet": round(carpet_area, 2),
            "total_built_up": round(total_built_up, 2),
            "fsi_applied": fsi,
            "soil_fertility": loc_info['soil'],
            "boring_depth": loc_info['boring_depth'],
            "water_quality": loc_info['water_quality'],
            "foundation_depth": loc_info['foundation_depth'],
            "foundation_width": loc_info['foundation_width'],
            "foundation_fertility": loc_info['foundation_fertility'],
            "gov_rules": loc_info['rules'],
            "safety_score": safety_score,
            "structural_accuracy": accuracy,
            "column_count": column_count,
            "orientation": data.get('orientation', 'N'),
            "city": city
        }
    }

    for f in range(floors):
        layout["floors"].append({
            "floor_no": f + 1,
            "rooms": rooms,
            "bathrooms": bathrooms,
            "bath_type": bath_type,
            "has_pooja": pooja_room and f == 0
        })

    return jsonify(layout)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
