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
        self.label_encoder_location = LabelEncoder()
        self.label_encoder_technology = LabelEncoder()
        self.model_file_carbon = os.path.join(settings.BASE_DIR, 'investments/models/carbon_model.pkl')
        self.model_file_energy = os.path.join(settings.BASE_DIR, 'investments/models/energy_model.pkl')
        self.model_file_water = os.path.join(settings.BASE_DIR, 'investments/models/water_model.pkl')
        self.categories = [
            'Renewable Energy', 'Recycling', 'Emission Control', 'Water Conservation',
            'Reforestation', 'Sustainable Agriculture', 'Clean Transportation',
            'Waste Management', 'Green Technology', 'Ocean Conservation'
        ]
        self.load_or_train_model()

    def train_model(self):
        # Dataset: [investment_amount (INR), cat0-cat9 (binary), duration_months, project_scale, location_encoded, technology_encoded]
        X = np.array([
            [125000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 10, 0, 0],  # Adani Green Energy
            [166000000000, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 48, 12, 1, 0],  # Tesla Gigafactory
            [41000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 8, 0, 2],   # NTPC Renewable
            [24900000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 7, 1, 1],   # Vestas Wind Systems
            [4150000000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 5, 0, 8],    # Coca-Cola Water Project (Filtration -> Manual)
            [66400000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30, 9, 1, 0],   # First Solar
            [16000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 6, 0, 0],   # Tata Power Solar
            [8300000000, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 36, 4, 1, 4],    # Nestlé Recycling Initiative
            [12000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 7, 0, 1],   # Suzlon Energy
            [49800000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 8, 1, 0],   # BP Solar Expansion
            [83000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 48, 11, 0, 0],  # Reliance Green Energy (Solar + Hydro -> Solar)
            [6225000000, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 24, 6, 1, 8],    # PepsiCo Sustainability
            [33200000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30, 9, 1, 1],   # Enel Green Power
            [29000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 8, 0, 0],   # ReNew Power
            [16600000000, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 36, 7, 1, 0],  # IKEA Sustainability
            [20000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 6, 0, 0],   # Azure Power
            [58100000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 40, 10, 1, 2],  # GE Renewable Energy
            [8000000000, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 24, 5, 0, 4],    # Hindustan Zinc
            [99600000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 11, 1, 1],  # Ørsted Offshore Wind
            [25000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30, 8, 0, 0],   # JSW Energy
            [12450000000, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 24, 6, 1, 8],  # Unilever Green Projects
            [41500000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 9, 1, 0],   # Canadian Solar
            [16000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 7, 0, 1],   # Hero Future Energies
            [24900000000, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 36, 8, 1, 0],  # Walmart Sustainability
            [66000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 48, 10, 0, 0],  # Greenko Group (Solar + Hydro -> Solar)
            [49800000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30, 9, 1, 1],   # Duke Energy Renewables
            [4000000000, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 18, 4, 0, 8],    # ITC Green Initiative
            [37350000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 8, 1, 0],   # SunPower
            [12000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 6, 0, 0],   # Mahindra Susten
            [6640000000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 24, 5, 1, 8],    # Proctor & Gamble Water
            [58100000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 10, 1, 1],  # EDF Renewables
            [16000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 7, 0, 0],   # Sterlite Power
            [20750000000, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 30, 8, 1, 0],  # Ford Sustainability
            [25000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 8, 0, 0],   # Acme Solar
            [83000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 48, 12, 1, 1],  # NextEra Energy
            [8000000000, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 24, 5, 0, 4],    # Ambuja Cement Green
            [66400000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 10, 1, 2],  # Iberdrola Renewables
            [20000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 7, 0, 1],   # Ostro Energy
            [16600000000, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 30, 8, 1, 0],  # GM Green Projects
            [12000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 6, 0, 0],   # Vikram Solar
            [49800000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 9, 1, 1],   # Southern Company Renewables
            [6000000000, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 24, 5, 0, 8],    # Godrej Green
            [33200000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 8, 1, 0],   # Trina Solar
            [25000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30, 9, 0, 0],   # Sembcorp India (Solar + Wind -> Solar)
            [41500000000, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 48, 10, 1, 0], # Amazon Sustainability
            [16000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 7, 0, 0],   # Welspun Renewables
            [58100000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 10, 1, 1],  # Dominion Energy
            [5000000000, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 18, 4, 0, 8],    # Dabur Green Initiative
            [37350000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 8, 1, 0],   # Jinko Solar
            [41000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 9, 0, 0],   # NTPC Green Energy (Solar + Hydro -> Solar)
        ])

        y_carbon = np.array([
            25000000, 40000000, 15000000, 12000000, 500000, 18000000, 8000000, 2000000, 10000000, 14000000,
            30000000, 1000000, 16000000, 12000000, 5000000, 9000000, 20000000, 1500000, 28000000, 11000000,
            800000, 15000000, 8500000, 6000000, 22000000, 14500000, 400000, 13000000, 7000000, 600000,
            18000000, 9500000, 4500000, 11500000, 25000000, 1200000, 20500000, 10000000, 5500000, 7500000,
            15500000, 700000, 12500000, 14000000, 10000000, 8000000, 18500000, 500000, 13500000, 16000000
        ])

        y_energy = np.array([
            15000000, 20000000, 10000000, 8000000, 0, 12000000, 5000000, 0, 7000000, 9000000,
            18000000, 0, 11000000, 8000000, 3000000, 6000000, 14000000, 0, 17000000, 7500000,
            0, 10000000, 5500000, 4000000, 13000000, 9500000, 0, 8500000, 4500000, 0,
            12000000, 6000000, 3000000, 7800000, 15000000, 0, 13500000, 6500000, 3500000, 4800000,
            10500000, 0, 8200000, 9000000, 6000000, 5200000, 12500000, 0, 8800000, 10500000
        ])

        y_water = np.array([
            0, 500000, 1000000, 0, 10000000, 0, 0, 5000000, 0, 0,
            2000000, 8000000, 0, 0, 1000000, 0, 3000000, 6000000, 0, 0,
            7000000, 0, 0, 2000000, 1500000, 0, 4000000, 0, 0, 9000000,
            0, 0, 1200000, 0, 0, 5500000, 2500000, 0, 1000000, 0,
            0, 6500000, 0, 0, 2000000, 0, 0, 4500000, 0, 1800000
        ])

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

    def predict_impact(self, investment_amount, category_names, project_duration_months=12, project_scale=1, location='North India', technology_type=None):
        # Encode location and technology
        locations = ['North India', 'South India', 'East India', 'West India']
        technologies = ['Solar', 'Wind', 'Hydro', 'Organic', 'Mechanical', 'Chemical', 'Biofuel', 'EV', 'Manual', 'AI']

        self.label_encoder_location.fit(locations)
        self.label_encoder_technology.fit(technologies)

        # Map broader locations to your model's regions
        location_map = {'India': 'North India', 'North America': 'West India'}  # Simplified mapping
        mapped_location = location_map.get(location, 'North India')
        location_encoded = self.label_encoder_location.transform([mapped_location])[0]

        # Map dataset tech types to your model's tech types
        tech_map = {'Filtration': 'Manual', 'Recycling Tech': 'Mechanical'}
        mapped_tech = tech_map.get(technology_type, technology_type) if technology_type else 'Manual'
        technology_encoded = self.label_encoder_technology.transform([mapped_tech])[0]

        # Create binary category vector
        if not category_names:
            category_names = ['Green Technology']
        category_vector = [1 if cat in category_names else 0 for cat in self.categories]

        # Prepare input
        X = np.array([[investment_amount] + category_vector + [project_duration_months, project_scale, location_encoded, technology_encoded]])

        # Predict impacts
        carbon_reduced = max(0, self.model_carbon.predict(X)[0])
        energy_saved = max(0, self.model_energy.predict(X)[0])
        water_conserved = max(0, self.model_water.predict(X)[0])

        return carbon_reduced, energy_saved, water_conserved