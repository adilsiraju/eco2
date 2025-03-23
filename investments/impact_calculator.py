import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os
from django.conf import settings

class ImpactCalculator:
    def __init__(self):
        self.model_carbon = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42)
        self.model_energy = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42)
        self.model_water = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42)
        self.label_encoder_category = LabelEncoder()
        self.label_encoder_location = LabelEncoder()
        self.label_encoder_technology = LabelEncoder()
        self.model_file_carbon = os.path.join(settings.BASE_DIR, 'investments/models/carbon_model.pkl')
        self.model_file_energy = os.path.join(settings.BASE_DIR, 'investments/models/energy_model.pkl')
        self.model_file_water = os.path.join(settings.BASE_DIR, 'investments/models/water_model.pkl')
        self.load_or_train_model()

    def train_model(self):
        # Mock data: [investment_amount (INR), category_encoded, duration_months, project_scale, location_encoded, technology_encoded]
        # For companies, technology_encoded is set to a default (e.g., 8 for 'Manual') since it's not used
        X = np.array([
            # Renewable Energy (Solar in South India, Wind in West India - Initiatives; Manual for Companies)
            [10000, 0, 6, 1, 1, 0], [50000, 0, 18, 5, 3, 1], [100000, 0, 30, 10, 1, 8],
            # Recycling (Mechanical in North India, Chemical in East India - Initiatives; Manual for Companies)
            [15000, 1, 6, 2, 0, 4], [40000, 1, 18, 4, 2, 5], [80000, 1, 30, 8, 0, 8],
            # Emission Control (Chemical in West India, AI in North India - Initiatives; Manual for Companies)
            [20000, 2, 6, 1, 3, 5], [60000, 2, 18, 6, 0, 9], [90000, 2, 30, 9, 3, 8],
            # Water Conservation (Hydro in South India, Manual in East India - Initiatives; Manual for Companies)
            [12000, 3, 6, 2, 1, 2], [45000, 3, 18, 5, 2, 8], [85000, 3, 30, 10, 1, 8],
            # Reforestation (Manual in East India, Organic in South India - Initiatives; Manual for Companies)
            [25000, 4, 6, 3, 2, 8], [70000, 4, 18, 7, 1, 3], [120000, 4, 30, 12, 2, 8],
            # Sustainable Agriculture (Organic in East India, Biofuel in West India - Initiatives; Manual for Companies)
            [18000, 5, 6, 2, 2, 3], [55000, 5, 18, 6, 3, 6], [95000, 5, 30, 9, 2, 8],
            # Clean Transportation (EV in North India, Biofuel in South India - Initiatives; Manual for Companies)
            [30000, 6, 6, 3, 0, 7], [65000, 6, 18, 7, 1, 6], [110000, 6, 30, 11, 0, 8],
            # Waste Management (Mechanical in West India, Manual in North India - Initiatives; Manual for Companies)
            [14000, 7, 6, 1, 3, 4], [48000, 7, 18, 5, 0, 8], [87000, 7, 30, 8, 3, 8],
            # Green Technology (AI in South India, Solar in North India - Initiatives; Manual for Companies)
            [22000, 8, 6, 2, 1, 9], [60000, 8, 18, 6, 0, 0], [100000, 8, 30, 10, 1, 8],
            # Ocean Conservation (Manual in South India, Mechanical in East India - Initiatives; Manual for Companies)
            [16000, 9, 6, 2, 1, 8], [50000, 9, 18, 5, 2, 4], [90000, 9, 30, 9, 1, 8],
        ])

        # Realistic impact data (adjusted for location and technology where applicable)
        y_carbon = np.array([
            30, 150, 300,    # Renewable Energy
            50, 130, 260,    # Recycling
            45, 135, 200,    # Emission Control
            15, 50, 90,      # Water Conservation
            90, 240, 400,    # Reforestation
            30, 90, 160,     # Sustainable Agriculture
            80, 180, 320,    # Clean Transportation
            35, 100, 190,    # Waste Management
            70, 200, 330,    # Green Technology
            20, 60, 110      # Ocean Conservation
        ])  # kg CO2 reduced

        y_energy = np.array([
            60, 300, 600,    # Renewable Energy
            40, 110, 220,    # Recycling
            35, 100, 150,    # Emission Control
            15, 50, 90,      # Water Conservation
            10, 25, 40,      # Reforestation
            20, 60, 100,     # Sustainable Agriculture
            70, 160, 280,    # Clean Transportation
            30, 100, 180,    # Waste Management
            80, 230, 380,    # Green Technology
            10, 30, 50       # Ocean Conservation
        ])  # kWh saved

        y_water = np.array([
            300, 1500, 3000, # Renewable Energy
            70, 180, 350,    # Recycling
            25, 70, 100,     # Emission Control
            1500, 5000, 9000,# Water Conservation
            100, 280, 480,   # Reforestation
            100, 300, 520,   # Sustainable Agriculture
            35, 80, 140,     # Clean Transportation
            50, 160, 300,    # Waste Management
            100, 270, 450,   # Green Technology
            400, 1200, 2000  # Ocean Conservation
        ])  # L conserved

        # Train models
        self.model_carbon.fit(X, y_carbon)
        self.model_energy.fit(X, y_energy)
        self.model_water.fit(X, y_water)

        # Save models
        os.makedirs(os.path.dirname(self.model_file_carbon), exist_ok=True)
        with open(self.model_file_carbon, 'wb') as f:
            pickle.dump(self.model_carbon, f)
        with open(self.model_file_energy, 'wb') as f:
            pickle.dump(self.model_energy, f)
        with open(self.model_file_water, 'wb') as f:
            pickle.dump(self.model_water, f)

    def load_or_train_model(self):
        if (os.path.exists(self.model_file_carbon) and
            os.path.exists(self.model_file_energy) and
            os.path.exists(self.model_file_water)):
            with open(self.model_file_carbon, 'rb') as f:
                self.model_carbon = pickle.load(f)
            with open(self.model_file_energy, 'rb') as f:
                self.model_energy = pickle.load(f)
            with open(self.model_file_water, 'rb') as f:
                self.model_water = pickle.load(f)
        else:
            self.train_model()

    def predict_impact(self, investment_amount, category_name, project_duration_months=12, project_scale=1, location='North India', technology_type=None):
        # Encode inputs
        categories = [
            'Renewable Energy', 'Recycling', 'Emission Control', 'Water Conservation',
            'Reforestation', 'Sustainable Agriculture', 'Clean Transportation',
            'Waste Management', 'Green Technology', 'Ocean Conservation'
        ]
        locations = ['North India', 'South India', 'East India', 'West India']
        technologies = ['Solar', 'Wind', 'Hydro', 'Organic', 'Mechanical', 'Chemical', 'Biofuel', 'EV', 'Manual', 'AI']

        self.label_encoder_category.fit(categories)
        self.label_encoder_location.fit(locations)
        self.label_encoder_technology.fit(technologies)

        category_encoded = self.label_encoder_category.transform([category_name])[0]
        location_encoded = self.label_encoder_location.transform([location])[0]
        # Use 'Manual' (index 8) as default if technology_type is None (for companies)
        technology_encoded = self.label_encoder_technology.transform([technology_type])[0] if technology_type else 8

        # Prepare input
        X = np.array([[investment_amount, category_encoded, project_duration_months, project_scale, location_encoded, technology_encoded]])

        # Predict impacts
        carbon_reduced = max(0, self.model_carbon.predict(X)[0])
        energy_saved = max(0, self.model_energy.predict(X)[0])
        water_conserved = max(0, self.model_water.predict(X)[0])

        return carbon_reduced, energy_saved, water_conserved