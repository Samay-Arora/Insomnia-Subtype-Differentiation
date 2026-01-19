import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

try:
    df = pd.read_csv('clustered_patients.csv')
except:
    print("Error: Run your clustering script first to generate the CSV.")
    exit()

def is_insomniac(sid):
    return str(sid).startswith('ins') or str(sid).startswith('ST')

df = df[df['Subject_ID'].apply(is_insomniac)].copy()

features = ['Rel_Delta', 'Rel_Theta', 'Rel_Alpha', 'Rel_Beta', 'Rel_Gamma', 
            'Perm_Entropy', 'Fractal_Dim', 'Hjorth_Complexity']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
kmeans.fit(X_scaled)

joblib.dump(scaler, 'insomnia_scaler.pkl')
joblib.dump(kmeans, 'insomnia_model.pkl')
print("Saved: 'insomnia_model.pkl' and 'insomnia_scaler.pkl' are ready.")