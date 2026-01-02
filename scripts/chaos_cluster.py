import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

INPUT_FILE = "features_with_chaos.csv"
OUTPUT_IMG = "chaos_subtypes.png"
OUTPUT_DATA = "chaos_subtypes.csv"

CHAOS_FEATURES = ['Perm_Entropy', 'Fractal_Dim', 'Hjorth_Complexity']

def run_chaos_analysis():
    print("Starting Chaos-Only Analysis...")
    
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        try:
            df = pd.read_csv("clustered_patients.csv")
        except:
            print("Error: Data file not found.")
            return

    def is_insomniac(sid):
        sid = str(sid)
        return sid.startswith('ins') or sid.startswith('ST')

    df_sick = df[df['Subject_ID'].apply(is_insomniac)].copy()
    print(f"   Analyzed Cohort: {len(df_sick)} Insomnia Patients")

    print("   Applying Site Correction to Chaos features...")
    df_corrected = df_sick.copy()
    
    for d in df_sick['Dataset'].unique():
        mask = df_sick['Dataset'] == d
        scaler = StandardScaler()
        df_corrected.loc[mask, CHAOS_FEATURES] = scaler.fit_transform(df_sick.loc[mask, CHAOS_FEATURES])

    X_chaos = df_corrected[CHAOS_FEATURES].values
    
    print("\n📊 Finding the strongest Chaos Subtypes...")
    best_k = 2
    best_score = -1
    
    for k in range(2, 6):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_chaos)
        score = silhouette_score(X_chaos, labels)
        print(f"   k={k}: Silhouette Score = {score:.3f}")
        
        if score > best_score:
            best_score = score
            best_k = k
            
    print(f"👉 Optimal Clusters: {best_k} (Highest stability)")
    
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df_sick['Chaos_Cluster'] = kmeans.fit_predict(X_chaos)
    
    print("\nCHAOS PHENOTYPES (Z-Score Standardized):")
    print("   (Positive = More Chaotic than Average, Negative = More Rigid)")
    print("-" * 60)
    
    df_corrected['Chaos_Cluster'] = df_sick['Chaos_Cluster']
    profile = df_corrected.groupby('Chaos_Cluster')[CHAOS_FEATURES].mean()
    print(profile.T)
    print("-" * 60)
    
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_chaos)
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x=X_pca[:,0], y=X_pca[:,1], 
        hue=df_sick['Chaos_Cluster'], 
        palette='magma', s=150, edgecolor='black', alpha=0.9
    )
    plt.title('Insomnia Phenotypes based on Signal Complexity ONLY', fontsize=14)
    plt.xlabel('PC1 (Complexity Axis)')
    plt.ylabel('PC2 (Signal Shape Axis)')
    plt.legend(title='Chaos Subtype', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG)
    print(f"\nSaved visualization to '{OUTPUT_IMG}'")
    
    df_sick.to_csv(OUTPUT_DATA, index=False)
    print(f"Results saved to '{OUTPUT_DATA}'")

if __name__ == "__main__":
    run_chaos_analysis()