import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
import os
from django.conf import settings

class ImpactCalculator:
    def __init__(self):
        self.model_carbon = RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_split=15, random_state=42)
        self.model_energy = RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_split=15, random_state=42)
        self.model_water = RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_split=15, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder_location = LabelEncoder()
        self.label_encoder_technology = LabelEncoder()
        self.model_file_carbon = os.path.join(settings.BASE_DIR, 'investments/models/carbon_model.pkl')
        self.model_file_energy = os.path.join(settings.BASE_DIR, 'investments/models/energy_model.pkl')
        self.model_file_water = os.path.join(settings.BASE_DIR, 'investments/models/water_model.pkl')
        self.scaler_file = os.path.join(settings.BASE_DIR, 'investments/models/scaler.pkl')  # New scaler file
        self.categories = [
            'Renewable Energy', 'Recycling', 'Emission Control', 'Water Conservation',
            'Reforestation', 'Sustainable Agriculture', 'Clean Transportation',
            'Waste Management', 'Green Technology', 'Ocean Conservation'
        ]
        self.load_or_train_model()

    def train_model(self):
        X = np.array([
            # Original large-scale (unchanged)
            [125000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 10, 0, 0],  # Renewable Energy
            [4150000000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 5, 0, 8],    # Water Conservation
            
            # Original small-scale (tripled entries kept)
            [15000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 5, 1, 0],  # Renewable Energy
            [15000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 5, 1, 0],
            [15000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 5, 1, 0],
            [50000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 7, 0, 1],
            [15000, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 12, 4, 0, 9],  # Waste Management/Recycling
            [15000, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 12, 4, 0, 9],
            [15000, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 12, 4, 0, 9],
            [15000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 3, 0, 8],  # Water Conservation
            [15000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 3, 0, 8],
            [15000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 3, 0, 8],
            [20000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 18, 5, 1, 8],
            [15000, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 12, 3, 0, 3],  # Sustainable Agriculture
            [15000, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 12, 3, 0, 3],
            [15000, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 12, 4, 0, 7],  # Clean Transportation
            [15000, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 12, 4, 0, 7],
            [15000, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 12, 3, 0, 4],  # Waste Management
            [15000, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 12, 3, 0, 4],
            [15000, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 12, 3, 0, 5],  # Emission Control
            [15000, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 12, 3, 0, 9],  # Green Technology
            [15000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 12, 3, 0, 8],  # Ocean Conservation
            [10000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 3, 0, 8],
            [25000, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 12, 4, 1, 4],
            [30000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 6, 0, 0],
            [8000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 6, 2, 1, 8],

            # New small-scale initiatives
            [500, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0],    # Micro solar lantern
            [1000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 2, 1, 0],  # Small solar panel
            [5000, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 12, 3, 2, 4],  # Community recycling bin
            [2000, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 12, 2, 0, 5],  # Small emission scrubber
            [1000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 6, 1, 1, 8],   # Rainwater harvesting kit
            [500, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 6, 1, 0, 3],    # Compost pile
            [2500, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 12, 3, 2, 7],  # Electric bike subsidy
            [3000, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 12, 2, 1, 4],  # Waste sorting unit
            [4000, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 12, 3, 0, 9],  # AI waste monitor
            [2000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 12, 2, 3, 8],  # Beach cleanup kit
            [10000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 4, 0, 1], # Wind turbine prototype
            [7500, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 12, 3, 1, 3],  # Organic farm plot
            [8000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 12, 3, 2, 8],  # Coral restoration
            [500, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 6, 1, 0, 8],    # Tree planting micro-fund
            [20000, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 18, 5, 1, 7], # EV charging station
        ])

        y_carbon = np.array([
            # Original large-scale
            25000000, 500000,
            # Original small-scale
            1575, 1575, 1575, 3000, 750, 750, 750, 300, 300, 300, 400,
            750, 750, 500, 500, 300, 300, 750, 800, 600, 500, 800, 2000, 300,
            # New small-scale
            50,    # Micro solar lantern
            100,   # Small solar panel
            250,   # Community recycling bin
            150,   # Small emission scrubber
            50,    # Rainwater harvesting kit
            25,    # Compost pile
            200,   # Electric bike subsidy
            300,   # Waste sorting unit
            400,   # AI waste monitor
            150,   # Beach cleanup kit
            800,   # Wind turbine prototype
            300,   # Organic farm plot
            500,   # Coral restoration
            50,    # Tree planting micro-fund
            1000,  # EV charging station
        ])

        y_energy = np.array([
            # Original large-scale
            15000000, 0,
            # Original small-scale
            3375, 3375, 3375, 4800, 1500, 1500, 1500, 150, 150, 150, 200,
            0, 0, 1500, 1500, 0, 0, 500, 1000, 0, 0, 0, 4000, 0,
            # New small-scale
            100,   # Micro solar lantern
            200,   # Small solar panel
            500,   # Community recycling bin
            100,   # Small emission scrubber
            20,    # Rainwater harvesting kit
            0,     # Compost pile
            600,   # Electric bike subsidy
            400,   # Waste sorting unit
            600,   # AI waste monitor
            0,     # Beach cleanup kit
            1200,  # Wind turbine prototype
            0,     # Organic farm plot
            0,     # Coral restoration
            0,     # Tree planting micro-fund
            2000,  # EV charging station
        ])

        y_water = np.array([
            # Original large-scale
            0, 10000000,
            # Original small-scale
            0, 0, 0, 0, 0, 0, 0, 400000, 400000, 400000, 600000,
            0, 0, 0, 0, 7500, 7500, 0, 0, 0, 2000, 1000, 0, 800,
            # New small-scale
            0,      # Micro solar lantern
            0,      # Small solar panel
            0,      # Community recycling bin
            0,      # Small emission scrubber
            5000,   # Rainwater harvesting kit
            200,    # Compost pile
            0,      # Electric bike subsidy
            0,      # Waste sorting unit
            0,      # AI waste monitor
            0,      # Beach cleanup kit
            0,      # Wind turbine prototype
            1000,   # Organic farm plot
            2000,   # Coral restoration
            0,      # Tree planting micro-fund
            0,      # EV charging station
        ])

        X_transformed = X.copy()
        X_transformed[:, 0] = np.log1p(X[:, 0])
        self.scaler.fit(X_transformed)
        X_transformed = self.scaler.transform(X_transformed)

        self.model_carbon.fit(X_transformed, y_carbon)
        self.model_energy.fit(X_transformed, y_energy)
        self.model_water.fit(X_transformed, y_water)

        os.makedirs(os.path.dirname(self.model_file_carbon), exist_ok=True)
        with open(self.model_file_carbon, 'wb') as f:
            pickle.dump(self.model_carbon, f)
        with open(self.model_file_energy, 'wb') as f:
            pickle.dump(self.model_energy, f)
        with open(self.model_file_water, 'wb') as f:
            pickle.dump(self.model_water, f)
        with open(self.scaler_file, 'wb') as f:
            pickle.dump(self.scaler, f)

    def load_or_train_model(self):
        if (os.path.exists(self.model_file_carbon) and
            os.path.exists(self.model_file_energy) and
            os.path.exists(self.model_file_water) and
            os.path.exists(self.scaler_file)):  # Check scaler file too
            with open(self.model_file_carbon, 'rb') as f:
                self.model_carbon = pickle.load(f)
            with open(self.model_file_energy, 'rb') as f:
                self.model_energy = pickle.load(f)
            with open(self.model_file_water, 'rb') as f:
                self.model_water = pickle.load(f)
            with open(self.scaler_file, 'rb') as f:  # Load scaler
                self.scaler = pickle.load(f)
        else:
            self.train_model()

    def predict_impact(self, investment_amount, category_names, project_duration_months=12, project_scale=1, location='North India', technology_type=None):
        investment_amount = float(investment_amount)
        locations = ['North India', 'South India', 'East India', 'West India']
        technologies = ['Solar', 'Wind', 'Hydro', 'Organic', 'Mechanical', 'Chemical', 'Biofuel', 'EV', 'Manual', 'AI']

        self.label_encoder_location.fit(locations)
        self.label_encoder_technology.fit(technologies)

        location_map = {'India': 'North India', 'North America': 'West India'}
        mapped_location = location_map.get(location, location if location in locations else 'North India')
        location_encoded = self.label_encoder_location.transform([mapped_location])[0]

        tech_map = {'Filtration': 'Manual', 'Recycling Tech': 'Mechanical'}
        mapped_tech = tech_map.get(technology_type, technology_type if technology_type in technologies else 'Manual')
        technology_encoded = self.label_encoder_technology.transform([mapped_tech])[0]

        if not category_names:
            category_names = ['Green Technology']
        category_vector = [1 if cat in category_names else 0 for cat in self.categories]

        X = np.array([[investment_amount] + category_vector + [project_duration_months, project_scale, location_encoded, technology_encoded]])
        X_transformed = X.copy()
        X_transformed[:, 0] = np.log1p(X[:, 0])
        X_transformed = self.scaler.transform(X_transformed)

        carbon_reduced = max(0, self.model_carbon.predict(X_transformed)[0])
        energy_saved = max(0, self.model_energy.predict(X_transformed)[0])
        water_conserved = max(0, self.model_water.predict(X_transformed)[0])

        base_investment = 15000
        scaling_factor = investment_amount / base_investment

        if 'Water Conservation' in category_names:
            carbon_reduced = min(carbon_reduced * scaling_factor, 500 * scaling_factor)
            energy_saved = min(energy_saved * scaling_factor, 300 * scaling_factor)
            water_conserved = min(water_conserved * scaling_factor, 600000 * scaling_factor)
        elif 'Waste Management' in category_names or 'Recycling' in category_names:
            carbon_reduced = min(carbon_reduced * scaling_factor, 1000 * scaling_factor)
            energy_saved = min(energy_saved * scaling_factor, 2000 * scaling_factor)
            water_conserved = 0
        elif 'Reforestation' in category_names:
            carbon_reduced = min(carbon_reduced * scaling_factor, 1000 * scaling_factor)
            energy_saved = 0
            water_conserved = 0
        elif 'Clean Transportation' in category_names:
            carbon_reduced = min(carbon_reduced * scaling_factor, 750 * scaling_factor)
            energy_saved = min(energy_saved * scaling_factor, 2000 * scaling_factor)
            water_conserved = 0
        elif 'Sustainable Agriculture' in category_names:
            carbon_reduced = min(carbon_reduced * scaling_factor, 500 * scaling_factor)
            energy_saved = 0
            water_conserved = min(water_conserved * scaling_factor, 10000 * scaling_factor)
        elif 'Emission Control' in category_names:
            carbon_reduced = min(carbon_reduced * scaling_factor, 1000 * scaling_factor)
            energy_saved = min(energy_saved * scaling_factor, 750 * scaling_factor)
            water_conserved = 0
        elif 'Green Technology' in category_names:
            carbon_reduced = min(carbon_reduced * scaling_factor, 1000 * scaling_factor)
            energy_saved = min(energy_saved * scaling_factor, 1500 * scaling_factor)
            water_conserved = 0
        elif 'Ocean Conservation' in category_names:
            carbon_reduced = min(carbon_reduced * scaling_factor, 750 * scaling_factor)
            energy_saved = 0
            water_conserved = 0
        else:  # Default (Renewable Energy)
            carbon_reduced = min(carbon_reduced * scaling_factor, 2000 * scaling_factor)
            energy_saved = min(energy_saved * scaling_factor, 4000 * scaling_factor)
            water_conserved = 0

        return carbon_reduced, energy_saved, water_conserved