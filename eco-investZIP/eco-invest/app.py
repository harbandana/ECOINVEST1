from flask import Flask, render_template, jsonify, request
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

app = Flask(__name__)

# Sample ESG data and ESI data
esg_data = {
    "State": ["Manipur", "Sikkim", "Tripura", "Nagaland", "Mizoram", "Arunachal Pradesh",
              "Chhattisgarh", "Orissa", "Uttaranchal", "Assam", "Meghalaya", "Jharkhand",
              "Kerala", "Bihar", "Jammu & Kashmir", "Goa", "Madhya Pradesh", "Maharashtra",
              "West Bengal", "Tamil Nadu", "Himachal Pradesh", "Karnataka", "Andhra Pradesh",
              "Rajasthan", "Haryana", "Uttar Pradesh", "Gujarat", "Punjab"],
    "Environmental Score": [80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 50, 60, 70, 80, 30, 25, 20, 15, 10, 5, 45, 40],
    "Social Score": [85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 55, 65, 75, 85, 35, 30, 25, 20, 15, 10, 50, 45],
    "Governance Score": [90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 60, 70, 80, 90, 40, 35, 30, 25, 20, 15, 55, 50]
}

esi_data = {
    "State": ["Manipur", "Sikkim", "Tripura", "Nagaland", "Mizoram", "Arunachal Pradesh",
              "Chhattisgarh", "Orissa", "Uttaranchal", "Assam", "Meghalaya", "Jharkhand",
              "Kerala", "Bihar", "Jammu & Kashmir", "Goa", "Madhya Pradesh", "Maharashtra",
              "West Bengal", "Tamil Nadu", "Himachal Pradesh", "Karnataka", "Andhra Pradesh",
              "Rajasthan", "Haryana", "Uttar Pradesh", "Gujarat", "Punjab"],
    "Normalized ESI Score": [1.0000, 0.9099, 0.8581, 0.8208, 0.8158, 0.7545, 0.7409, 0.7188, 0.7118, 0.7015, 0.6679, 0.6433,
                             0.6126, 0.5579, 0.5371, 0.5198, 0.4873, 0.4516, 0.4301, 0.3728, 0.3572, 0.3375, 0.3255, 0.2652,
                             0.2559, 0.2140, 0.1046, 0.0000]
}

esg_df = pd.DataFrame(esg_data)
esi_df = pd.DataFrame(esi_data)

# Merge the dataframes on the State column
combined_df = pd.merge(esi_df, esg_df, on='State')

# Calculate Combined ESI
def calculate_combined_esi(row):
    return (row['Normalized ESI Score'] + row['Environmental Score'] + row['Social Score'] + row['Governance Score']) / 4

combined_df['Combined ESI'] = combined_df.apply(calculate_combined_esi, axis=1)

# Add real sustainable initiatives for each state
sustainable_initiatives = {
    "Manipur": ["solar energy", "eco-tourism"],
    "Sikkim": ["organic farming", "eco-tourism"],
    "Tripura": ["biofuel", "solar energy"],
    "Nagaland": ["eco-tourism", "forest conservation"],
    "Mizoram": ["wind energy", "sustainable agriculture"],
    "Arunachal Pradesh": ["hydropower", "forest conservation"],
    "Chhattisgarh": ["biofuel", "sustainable agriculture"],
    "Orissa": ["solar energy", "wind energy"],
    "Uttaranchal": ["eco-tourism", "solar energy"],
    "Assam": ["biofuel", "forest conservation"],
    "Meghalaya": ["hydropower", "eco-tourism"],
    "Jharkhand": ["biofuel", "solar energy"],
    "Kerala": ["solar energy", "eco-tourism"],
    "Bihar": ["biofuel", "sustainable agriculture"],
    "Jammu & Kashmir": ["hydropower", "eco-tourism"],
    "Goa": ["solar energy", "eco-tourism"],
    "Madhya Pradesh": ["solar energy", "wind energy"],
    "Maharashtra": ["solar energy", "biofuel"],
    "West Bengal": ["solar energy", "eco-tourism"],
    "Tamil Nadu": ["wind energy", "solar energy"],
    "Himachal Pradesh": ["hydropower", "eco-tourism"],
    "Karnataka": ["solar energy", "wind energy"],
    "Andhra Pradesh": ["wind energy", "solar energy"],
    "Rajasthan": ["solar energy", "wind energy"],
    "Haryana": ["solar energy", "sustainable agriculture"],
    "Uttar Pradesh": ["biofuel", "sustainable agriculture"],
    "Gujarat": ["solar energy", "wind energy"],
    "Punjab": ["biofuel", "sustainable agriculture"]
}

combined_df['Sustainable Initiatives'] = combined_df['State'].map(sustainable_initiatives)

# Prepare data for machine learning
X = combined_df[['Normalized ESI Score', 'Environmental Score', 'Social Score', 'Governance Score']]
y = combined_df['Combined ESI']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict the Combined ESI for the entire dataset
combined_df['Predicted Combined ESI'] = model.predict(X)

# Rank the regions based on the predicted Combined ESI
combined_df['Rank'] = combined_df['Predicted Combined ESI'].rank(ascending=False)

# Sort the dataframe by rank
sorted_df = combined_df.sort_values(by='Rank')

# Identify Top Regions based on the highest Predicted Combined ESI
top_regions = sorted_df.head(10)  # Top 10 regions

@app.route('/')
def index():
    combined_data = combined_df.to_dict(orient='records')
    top_regions_data = top_regions.to_dict(orient='records')
    return render_template('index.html', combined_df=combined_data, top_regions=top_regions_data)

@app.route('/recommendations_by_sector', methods=['POST'])
def recommendations_by_sector():
    sector = request.form.get('sector')
    
    # Filter states based on the chosen sector
    filtered_df = combined_df[combined_df['Sustainable Initiatives'].apply(lambda x: sector in x)]
    
    if filtered_df.empty:
        return jsonify({"error": f"No regions found for the sector: {sector}"})
    
    # Rank the filtered regions by their Combined ESI
    top_states = filtered_df[['State', 'Combined ESI']].sort_values(by='Combined ESI', ascending=False)
    
    return jsonify(top_states.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
