import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

INPUT_FILE = "features_with_chaos.csv" 
OUTPUT_IMG = "insomnia_clusters.png"
OUTPUT_DATA = "final_clusters.csv"

def run_correction_and_clustering():
    print("Data Loading...")
    
    try:
        df = pd.read_csv(INPUT_FILE)
    except:
        print("Missing Featured CSV...")
            
    feature_cols = [c for c in df.columns if c not in ['Subject_ID', 'Dataset']]
    df_corrected = df.copy()
    datasets = df['Dataset'].unique()
    print(f"   Found datasets: {datasets}")
    for d in datasets:
        mask = df['Dataset'] == d
        subset = df.loc[mask, feature_cols]
        scaler = StandardScaler()
        subset_scaled = scaler.fit_transform(subset)
        df_corrected.loc[mask, feature_cols] = subset_scaled
        
    print("Aligned Original Issues")

    X_scaled = df_corrected[feature_cols].values
    print("\nOptimizing cluster count...")
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
            
    print(f"👉 Optimal Clusters: {best_k}")
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df_corrected['Cluster'] = kmeans.fit_predict(X_scaled)
    df['Cluster'] = df_corrected['Cluster']
    df.to_csv(OUTPUT_DATA, index=False)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x=X_pca[:,0], y=X_pca[:,1], 
        hue=df['Cluster'], 
        style=df['Dataset'],
        palette='viridis', s=100, alpha=0.8
    )
    plt.title(f'Insomnia Phenotypes (Site-Corrected) - k={best_k}')
    plt.xlabel('PC1 (Complexity)')
    plt.ylabel('PC2 (Power)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG)
    print(f"\nSaved plot to {OUTPUT_IMG}")
    
    print("\nQuality Control...")
    print(pd.crosstab(df['Dataset'], df['Cluster']))
    
    print("\nCluster Profiles:")
    print(df.groupby('Cluster')[feature_cols].mean().T)

if __name__ == "__main__":
    run_correction_and_clustering()