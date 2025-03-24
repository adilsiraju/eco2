import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
import os
from django.conf import settings

class ImpactCalculator:
    def __init__(self):
        self.model_carbon = RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_split=15, random_state=42)  # Further reduce overfitting
        self.model_energy = RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_split=15, random_state=42)
        self.model_water = RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_split=15, random_state=42)
        self.scaler = StandardScaler()
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
        X = np.array([
            # Large-scale (reduced influence)
            [125000000000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 10, 0, 0],
            [4150000000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 5, 0, 8],
            # Small-scale renewable energy (more weight)
            [15000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 5, 1, 0],
            [15000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 5, 1, 0],
            [15000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 5, 1, 0],  # Tripled
            [50000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 7, 0, 1],
            # Small-scale waste management
            [15000, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 12, 4, 0, 9],
            [15000, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 12, 4, 0, 9],
            [15000, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 12, 4, 0, 9],
            # Small-scale water conservation
            [15000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 3, 0, 8],
            [15000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 3, 0, 8],
            [15000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 3, 0, 8],  # Tripled
            [20000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 18, 5, 1, 8],
            # New small-scale initiatives
            [15000, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 12, 3, 0, 3],
            [15000, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 12, 3, 0, 3],  # Doubled
            [15000, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 12, 4, 0, 7],
            [15000, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 12, 4, 0, 7],  # Doubled
            [15000, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 12, 3, 0, 4],
            [15000, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 12, 3, 0, 4],  # Doubled
            [15000, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 12, 3, 0, 5],
            [15000, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 12, 3, 0, 9],
            [15000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 12, 3, 0, 8],
            # Other small-scale
            [10000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 3, 0, 8],
            [25000, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 12, 4, 1, 4],
            [30000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 6, 0, 0],
            [8000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 6, 2, 1, 8],
        ])

        y_carbon = np.array([
            25000000, 500000, 1575, 1575, 1575, 3000, 750, 750, 750, 300, 300, 300, 400,
            750, 750, 500, 500, 300, 300, 750, 800, 600, 500, 800, 2000, 300,
        ])

        y_energy = np.array([
            15000000, 0, 3375, 3375, 3375, 4800, 1500, 1500, 1500, 150, 150, 150, 200,
            0, 0, 1500, 1500, 0, 0, 500, 1000, 0, 0, 0, 4000, 0,
        ])

        y_water = np.array([
            0, 10000000, 0, 0, 0, 0, 0, 0, 0, 400000, 400000, 400000, 600000,
            0, 0, 0, 0, 7500, 7500, 0, 0, 0, 2000, 1000, 0, 800,
        ])

        X_transformed = X.copy()
        X_transformed[:, 0] = np.log1p(X[:, 0])
        X_transformed = self.scaler.fit_transform(X_transformed)

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

        # Apply scaling with dynamic caps
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