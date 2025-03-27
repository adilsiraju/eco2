import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
import os
from django.conf import settings

class ImpactCalculator:
    def __init__(self):
        self.model_carbon = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_split=5, random_state=42)
        self.model_energy = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_split=5, random_state=42)
        self.model_water = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_split=5, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder_location = LabelEncoder()
        self.label_encoder_technology = LabelEncoder()

        self.model_file_carbon = os.path.join(settings.BASE_DIR, 'investments/models/carbon_model.pkl')
        self.model_file_energy = os.path.join(settings.BASE_DIR, 'investments/models/energy_model.pkl')
        self.model_file_water = os.path.join(settings.BASE_DIR, 'investments/models/water_model.pkl')
        self.scaler_file = os.path.join(settings.BASE_DIR, 'investments/models/scaler.pkl')

        self.categories = [
            'Renewable Energy', 'Recycling', 'Emission Control', 'Water Conservation',
            'Reforestation', 'Sustainable Agriculture', 'Clean Transportation',
            'Waste Management', 'Green Technology', 'Ocean Conservation'
        ]

        self.label_encoder_location.fit([
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
            'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
            'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
            'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
        ])
        self.label_encoder_technology.fit(['Solar', 'Wind', 'Hydro', 'Organic', 'Mechanical', 'Chemical', 'Biofuel', 'EV', 'Manual', 'AI'])

        self.load_or_train_model()

    def load_or_train_model(self):
        try:
            # Check if all necessary files exist
            if all(os.path.exists(f) for f in [self.model_file_carbon, self.model_file_energy, self.model_file_water, self.scaler_file]):
                print("Loading pre-trained models and scaler...")
                with open(self.model_file_carbon, 'rb') as f:
                    self.model_carbon = pickle.load(f)
                with open(self.model_file_energy, 'rb') as f:
                    self.model_energy = pickle.load(f)
                with open(self.model_file_water, 'rb') as f:
                    self.model_water = pickle.load(f)
                with open(self.scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)
                print("Models and scaler loaded successfully.")
            else:
                print("One or more model/scaler files missing. Training new models...")
                self.train_model()
        except Exception as e:
            print(f"Failed to load models or scaler: {e}. Training new models...")
            self.train_model()

    def train_model(self):
        # Create a more diverse training dataset with varied locations, categories, scales and technologies
        X = np.array([
            # Renewable Energy - Solar (high energy savings, moderate carbon reduction, minimal water impact)
            [500000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 5, 0, 0],    # Solar large-scale in Rajasthan
            [100000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 3, 0, 0],    # Solar medium-scale in Rajasthan  
            [10000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0],      # Solar small-scale in Rajasthan
            
            # Renewable Energy - Wind (high energy savings, good carbon reduction, zero water impact)
            [750000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 7, 1, 1],    # Wind large-scale in Gujarat
            [70000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 4, 1, 1],     # Wind medium-scale in Gujarat
            [5000, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 2, 1, 1],       # Wind small-scale in Gujarat
            
            # Recycling - Mechanical (moderate carbon reduction, low energy savings, moderate water savings)
            [200000, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 12, 4, 13, 4],   # Recycling large-scale in Maharashtra
            [50000, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 12, 3, 13, 4],    # Recycling medium-scale in Maharashtra
            [5000, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 6, 2, 13, 4],      # Recycling small-scale in Maharashtra
            
            # Emission Control - Chemical (very high carbon reduction, low energy impact, low water impact)
            [300000, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 12, 5, 25, 5],   # Emission control large-scale in UP
            [75000, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 12, 3, 25, 5],    # Emission control medium-scale in UP
            [3000, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 6, 2, 25, 5],      # Emission control small-scale in UP
            
            # Water Conservation (low carbon, minimal energy, extremely high water savings)
            [250000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 4, 16, 2],   # Water conservation large-scale in Rajasthan
            [25000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 12, 2, 16, 2],    # Water conservation medium-scale in Rajasthan
            [4000, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 6, 1, 16, 2],      # Water conservation small-scale in Rajasthan
            
            # Reforestation (highest carbon reduction, zero energy impact, good water conservation)
            [150000, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 24, 5, 3, 3],    # Reforestation large-scale in Assam
            [75000, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 18, 4, 3, 3],     # Reforestation medium-scale in Assam
            [15000, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 12, 3, 3, 3],     # Reforestation small-scale in Assam
            
            # Clean Transportation - EV (high carbon reduction, high energy savings, minimal water impact)
            [800000, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 18, 7, 13, 7],   # Clean transport large-scale in Maharashtra
            [80000, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 12, 5, 13, 7],    # Clean transport medium-scale in Maharashtra
            [8000, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 6, 2, 13, 7],      # Clean transport small-scale in Maharashtra
            
            # Waste Management (good carbon, moderate energy recovery, low water impact)
            [600000, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 12, 6, 25, 4],   # Waste management large-scale in UP
            [60000, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 12, 4, 25, 4],    # Waste management medium-scale in UP
            [6000, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 6, 2, 25, 4],      # Waste management small-scale in UP
            
            # Green Technology (moderate across all metrics)
            [700000, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 18, 7, 10, 9],   # Green tech large-scale in Karnataka
            [70000, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 12, 5, 10, 9],    # Green tech medium-scale in Karnataka
            [7000, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 6, 3, 10, 9],      # Green tech small-scale in Karnataka
            
            # Ocean Conservation (moderate carbon, low energy, extremely high water impact)
            [350000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 24, 6, 9, 2],    # Ocean conservation large-scale in Kerala
            [35000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 18, 4, 9, 2],     # Ocean conservation medium-scale in Kerala
            [3500, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 12, 2, 9, 2],      # Ocean conservation small-scale in Kerala
        ])

        # Create impact values with category-specific focus
        # Format: carbon (kg), energy (kWh), water (L) - per ₹1,000 investment
        y_carbon = np.array([
            750, 500, 150,      # Solar (by scale)
            700, 450, 120,      # Wind (by scale)
            300, 200, 80,       # Recycling (by scale)
            900, 650, 250,      # Emission Control (by scale) - highest carbon reduction
            100, 50, 20,        # Water Conservation (by scale)
            950, 600, 300,      # Reforestation (by scale) - highest carbon reduction
            800, 500, 150,      # Clean Transportation (by scale)
            500, 300, 100,      # Waste Management (by scale)
            400, 250, 80,       # Green Technology (by scale)
            250, 150, 50,       # Ocean Conservation (by scale)
        ])
        
        y_energy = np.array([
            1000, 600, 200,     # Solar (by scale) - highest energy savings
            900, 500, 150,      # Wind (by scale) - high energy savings
            100, 70, 30,        # Recycling (by scale)
            150, 90, 30,        # Emission Control (by scale)
            30, 20, 0,          # Water Conservation (by scale) - can be zero
            0, 0, 0,            # Reforestation (by scale) - zero energy impact
            750, 450, 120,      # Clean Transportation (by scale) - high energy savings
            400, 250, 80,       # Waste Management (by scale)
            350, 200, 60,       # Green Technology (by scale)
            50, 30, 0,          # Ocean Conservation (by scale) - can be zero
        ])
        
        y_water = np.array([
            50, 30, 0,          # Solar (by scale) - can be zero water impact
            0, 0, 0,            # Wind (by scale) - zero water impact
            200, 150, 50,       # Recycling (by scale)
            300, 150, 50,       # Emission Control (by scale) - REDUCED water impact
            3000, 2000, 1000,   # Water Conservation (by scale) - GREATLY INCREASED water savings
            500, 350, 200,      # Reforestation (by scale) - good water savings
            20, 15, 0,          # Clean Transportation (by scale) - can be zero
            150, 100, 30,       # Waste Management (by scale)
            250, 150, 50,       # Green Technology (by scale)
            2500, 1800, 800,    # Ocean Conservation (by scale) - highest water savings
        ])

        # Add interaction term to the training data
        interaction_term = X[:, 0] * X[:, 11]  # investment_amount * project_duration_months
        X = np.hstack((X, interaction_term.reshape(-1, 1)))  # Add interaction term as a new feature

        # Normalize the investment amounts and interaction term in the training data
        X[:, 0] = np.log1p(X[:, 0])  # Apply log transformation to scale down large values
        X[:, -1] = np.log1p(X[:, -1])  # Apply log transformation to the interaction term

        # Fit the scaler on the normalized training data
        self.scaler.fit(X)
        X_transformed = self.scaler.transform(X)

        self.model_carbon.fit(X_transformed, y_carbon)
        self.model_energy.fit(X_transformed, y_energy)
        self.model_water.fit(X_transformed, y_water)

        print("Feature importance (carbon model):", self.model_carbon.feature_importances_)
        print("Feature importance (energy model):", self.model_energy.feature_importances_)
        print("Feature importance (water model):", self.model_water.feature_importances_)

        os.makedirs(os.path.dirname(self.model_file_carbon), exist_ok=True)
        with open(self.model_file_carbon, 'wb') as f:
            pickle.dump(self.model_carbon, f)
        with open(self.model_file_energy, 'wb') as f:
            pickle.dump(self.model_energy, f)
        with open(self.model_file_water, 'wb') as f:
            pickle.dump(self.model_water, f)
        with open(self.scaler_file, 'wb') as f:
            pickle.dump(self.scaler, f)

    def predict_impact(self, investment_amount, category_names, project_duration_months=12, project_scale=1, location='North India', technology_type='Manual'):
        investment_amount = float(investment_amount)
        mapped_location = location if location in self.label_encoder_location.classes_ else 'Uttar Pradesh'
        location_encoded = self.label_encoder_location.transform([mapped_location])[0]
        mapped_tech = technology_type if technology_type in self.label_encoder_technology.classes_ else 'Manual'
        technology_encoded = self.label_encoder_technology.transform([mapped_tech])[0]

        category_vector = [1 if cat in category_names else 0 for cat in self.categories]
        
        # Correctly find the primary category index by matching with category_names
        primary_category_index = -1
        for i, cat in enumerate(self.categories):
            if cat in category_names:
                primary_category_index = i
                break
                
        print(f"Category names: {category_names}")
        print(f"Category vector: {category_vector}")
        print(f"Selected primary category: {self.categories[primary_category_index] if primary_category_index >= 0 else 'None'}")
        print(f"Primary index: {primary_category_index}")

        # Duration scaling factor - normalized to 12-month baseline
        if project_duration_months <= 12:
            duration_factor = project_duration_months / 12.0
        else:
            duration_factor = 1.0 + (np.sqrt(project_duration_months / 12.0) - 1.0) * 0.5
        
        # Scale factor based on project scale (1-10) with diminishing returns for larger scales
        scale_factor = 0.3 + 0.7 * (project_scale ** 0.4)  # Using power of 0.4 for less aggressive scaling
        
        # Calculate realistic base metrics by category - ADJUSTED TO MORE CONSERVATIVE ANNUAL VALUES
        # These are reference values per ₹1,000 for a 12-month, scale=1 project
        renewable_energy_base = {
            'carbon': 45,   # kg CO₂ 
            'energy': 50,   # kWh
            'water': 0,     # L
        }
        
        emission_control_base = {
            'carbon': 350,   # kg CO₂
            'energy': 80,    # kWh
            'water': 100,    # L
        }
        
        water_conservation_base = {
            'carbon': 80,    # kg CO₂
            'energy': 30,    # kWh
            'water': 1500,   # L
        }
        
        recycling_base = {
            'carbon': 200,   # kg CO₂
            'energy': 120,   # kWh
            'water': 200,    # L
        }
        
        reforestation_base = {
            'carbon': 500,   # kg CO₂
            'energy': 0,     # kWh
            'water': 1000,   # L
        }
        
        clean_transportation_base = {
            'carbon': 300,   # kg CO₂
            'energy': 250,   # kWh
            'water': 0,      # L
        }
        
        ocean_conservation_base = {
            'carbon': 150,   # kg CO₂
            'energy': 0,     # kWh
            'water': 1200,   # L
        }
        
        waste_management_base = {
            'carbon': 220,   # kg CO₂
            'energy': 180,   # kWh
            'water': 100,    # L
        }
        
        green_technology_base = {
            'carbon': 150,   # kg CO₂
            'energy': 220,   # kWh
            'water': 50,     # L
        }

        # Prepare model input data for fallback case
        interaction_term = investment_amount * project_duration_months
        X = np.array([[investment_amount, interaction_term] + category_vector + [project_duration_months, project_scale, location_encoded, technology_encoded]])
        
        X_transformed = X.copy()
        X_transformed[:, 0] = np.log1p(X[:, 0])
        X_transformed[:, 1] = np.log1p(X[:, 1])
        X_transformed = self.scaler.transform(X_transformed)

        # Category-specific logic takes priority over model predictions
        if primary_category_index == 4:  # Reforestation (corrected from 5)
            carbon_reduced = reforestation_base['carbon'] * scale_factor * duration_factor
            energy_saved = 0  # Enforce zero energy impact for reforestation
            water_conserved = 1000 * scale_factor * duration_factor  # Hardcode base 1000 L
            
            # Apply location-based water boost directly for more control
            if mapped_location in ["Assam", "Kerala", "Meghalaya", "West Bengal", "Nagaland"]:  # Added Nagaland
                water_conserved *= 1.2  # High rainfall regions boost
                
        elif primary_category_index == 0:  # Renewable Energy
            tech_multiplier = 1.15 if "Solar" in mapped_tech else (0.9 if "Wind" in mapped_tech else 0.8)
            carbon_reduced = renewable_energy_base['carbon'] * scale_factor * duration_factor * tech_multiplier
            energy_saved = renewable_energy_base['energy'] * scale_factor * duration_factor * tech_multiplier
            water_conserved = 0  # Zero water impact for renewable energy
            
            # For larger renewable projects, apply more modest boost
            if project_scale >= 5:
                energy_saved *= 1.2
                
        elif primary_category_index == 2:  # Emission Control
            carbon_reduced = emission_control_base['carbon'] * scale_factor * duration_factor
            energy_saved = emission_control_base['energy'] * scale_factor * duration_factor
            water_conserved = emission_control_base['water'] * scale_factor * duration_factor
            
            # For large emission control projects, use fixed value as recommended
            if project_scale >= 4:
                carbon_reduced = 1500  # Fixed value as recommended
            
        elif primary_category_index == 3:  # Water Conservation
            carbon_reduced = water_conservation_base['carbon'] * scale_factor * duration_factor
            energy_saved = water_conservation_base['energy'] * scale_factor * duration_factor
            water_conserved = water_conservation_base['water'] * scale_factor * duration_factor
            
            # Location-based boost for high-rainfall regions
            if mapped_location in ["Assam", "Kerala", "Meghalaya"]:
                water_conserved *= 1.15
            
        elif primary_category_index == 1:  # Recycling
            carbon_reduced = recycling_base['carbon'] * scale_factor * duration_factor
            energy_saved = recycling_base['energy'] * scale_factor * duration_factor
            water_conserved = recycling_base['water'] * scale_factor * duration_factor
            
        elif primary_category_index == 6:  # Clean Transportation
            carbon_reduced = clean_transportation_base['carbon'] * scale_factor * duration_factor
            energy_saved = clean_transportation_base['energy'] * scale_factor * duration_factor
            water_conserved = 0  # Zero water impact for clean transportation
            
        elif primary_category_index == 9:  # Ocean Conservation
            carbon_reduced = ocean_conservation_base['carbon'] * scale_factor * duration_factor
            energy_saved = 0  # Zero energy impact for ocean conservation
            water_conserved = ocean_conservation_base['water'] * scale_factor * duration_factor
            
        elif primary_category_index == 7:  # Waste Management
            carbon_reduced = waste_management_base['carbon'] * scale_factor * duration_factor
            energy_saved = waste_management_base['energy'] * scale_factor * duration_factor
            water_conserved = waste_management_base['water'] * scale_factor * duration_factor
            
        elif primary_category_index == 8:  # Green Technology
            carbon_reduced = green_technology_base['carbon'] * scale_factor * duration_factor
            energy_saved = green_technology_base['energy'] * scale_factor * duration_factor
            water_conserved = green_technology_base['water'] * scale_factor * duration_factor
            
            if "AI" in technology_type:
                water_conserved = 0  # Zero water impact for AI-based green tech
        else:
            # Fallback to model predictions only if no category is matched
            carbon_reduced = max(0, self.model_carbon.predict(X_transformed)[0])
            energy_saved = max(0, self.model_energy.predict(X_transformed)[0])
            water_conserved = max(0, self.model_water.predict(X_transformed)[0])
            print("Using model fallback for predictions")

        # Location-specific adjustments
        if mapped_location in ["Rajasthan", "Gujarat"] and primary_category_index == 0:
            # Higher solar efficiency in these regions
            energy_saved *= 1.1
            
        # Add small random variation (±5%) to avoid identical values for similar projects
        variation_factor = 1.0 + (np.random.random() - 0.5) * 0.1
        carbon_reduced *= variation_factor
        energy_saved *= 1.0 + (np.random.random() - 0.5) * 0.1
        water_conserved *= 1.0 + (np.random.random() - 0.5) * 0.1
        
        # Final guarantee that energy is zero for specific categories
        if primary_category_index in [5, 9]:  # Reforestation or Ocean Conservation
            energy_saved = 0
            
        # Ensure values can't go below zero after variation
        carbon_reduced = max(0, carbon_reduced)
        energy_saved = max(0, energy_saved)
        water_conserved = max(0, water_conserved)
        
        # Log impact calculation details
        print(f"Category: {category_names}, Primary Index: {primary_category_index}")
        print(f"Scale Factor: {scale_factor}, Duration Factor: {duration_factor}")
        print(f"Final Impact - Carbon: {carbon_reduced}, Energy: {energy_saved}, Water: {water_conserved}")
        
        # Return the final impact metrics
        return {
            "carbon": round(carbon_reduced, 2),
            "energy": round(energy_saved, 2),
            "water": round(water_conserved, 2)
        }