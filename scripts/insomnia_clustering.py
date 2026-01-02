import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

INPUT_FILE = "features_with_chaos.csv"
OUTPUT_IMG = "insomnia_subtypes_only.png"
OUTPUT_DATA = "insomnia_subtypes.csv"

def run_subtyping():
    print("🧪 Loading Data...")
    df = pd.read_csv(INPUT_FILE)
    def is_insomniac(sid):
        sid = str(sid)
        return sid.startswith('ins') or sid.startswith('ST')

    df_sick = df[df['Subject_ID'].apply(is_insomniac)].copy()
    print(f"Filtered Dataset: {len(df_sick)} Insomnia Patients (Healthy controls removed)")
    
    feature_cols = [c for c in df.columns if c not in ['Subject_ID', 'Dataset']]
    df_corrected = df_sick.copy()
    
    print("   Applying Site Correction...")
    for d in df_sick['Dataset'].unique():
        mask = df_sick['Dataset'] == d
        subset = df_sick.loc[mask, feature_cols]
        
        scaler = StandardScaler()
        df_corrected.loc[mask, feature_cols] = scaler.fit_transform(subset)

    X_scaled = df_corrected[feature_cols].values
    
    print("\nOptimizing Clusters...")
    best_k = 2
    best_score = -1
    for k in range(2, 6):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        print(f"   k={k}: Silhouette Score = {score:.3f}")
        if score > best_score:
            best_score = score
            best_k = k
            
    print(f"Optimal Subtypes: {best_k}")
    
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    df_sick['Subtype'] = clusters
    
    print("\nINSOMNIA SUBTYPE PROFILES:")
    print("-" * 60)
    profile = df_sick.groupby('Subtype')[feature_cols].mean()
    print(profile.T)
    print("-" * 60)
    
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x=X_pca[:,0], y=X_pca[:,1], 
        hue=df_sick['Subtype'], 
        style=df_sick['Dataset'],
        palette='magma', s=120, alpha=0.9
    )
    plt.title(f'Insomnia Subtypes (Excluded Healthy Controls)', fontsize=14)
    plt.xlabel('PC1 (Hyperarousal Axis)')
    plt.ylabel('PC2 (Sleep Depth Axis)')
    plt.legend(title='Subtype', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG)
    print(f"\nSaved plot to {OUTPUT_IMG}")
    
    df_sick.to_csv(OUTPUT_DATA, index=False)
    print(f"Saved patient list to {OUTPUT_DATA}")

if __name__ == "__main__":
    run_subtyping()