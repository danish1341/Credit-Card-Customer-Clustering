# -*- coding: utf-8 -*-
"""Credit Card Customer Clustering.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Vq7lpx-zeaX0Grx7aIGIEyQwsz1JRfTr
"""

# Importing the required libraries
import warnings
import pandas as pd
import plotly.express as px
from scipy.stats.mstats import trimmed_var
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.simplefilter(action="ignore", category=FutureWarning)

# Reading data into Dataframe `df`
df = pd.read_csv("/content/CC GENERAL.csv")
print(df.info())
df.head()



"""# EDA"""

df.drop(columns={"CUST_ID"}, inplace=True)

# Dataframe statistics
df.describe()

# Checking Missing Values
df.isnull().sum() / len(df)

# Handling Missing Values
df.loc[(df['MINIMUM_PAYMENTS'].isnull()==True),'MINIMUM_PAYMENTS']=df['MINIMUM_PAYMENTS'].mean()
df.loc[(df['CREDIT_LIMIT'].isnull()==True),'CREDIT_LIMIT']=df['CREDIT_LIMIT'].mean()

# Check for duplicate Values
df.duplicated().sum()

# Calculating the variance, get 10 largest features
top_ten_var = df.var().sort_values().tail(10)
top_ten_var

# Creating horizontal bar chart of `top_ten_var`
fig = px.bar(
    x = top_ten_var,
    y = top_ten_var.index,
    title = "High Variance Features"
)

fig.update_layout(xaxis_title = "Variance", yaxis_title = "Feature")

fig.show()

# Create a boxplot of `NHNFIN`
fig = px.box(
    data_frame = df,
    x = "CREDIT_LIMIT",
    title = "Distribution of Credit Cards Limits"
    )
fig.update_layout(xaxis_title = "Value [$]")

fig.show()

# Calculate trimmed variance
top_ten_trim_var = df.apply(trimmed_var, limits=(0.1,0.1)).sort_values().tail(10)
top_ten_trim_var

# Create horizontal bar chart of `top_ten_trim_var`
fig = px.bar(
    x = top_ten_trim_var,
    y = top_ten_trim_var.index,
    title = "High Variance Features"
    )

fig.update_layout(xaxis_title ="Trimmed Variance", yaxis_title="Feature")

fig.show()

high_var_cols = top_ten_trim_var.tail(5).index.to_list()
high_var_cols

"""SPLITTING"""

X = df[high_var_cols]
print("X shape:", X.shape)
X.head()

"""Build model

Iterate
"""

X_summary = X.aggregate(["mean","std"]).astype(int)
X_summary

# Instantiate transformer
ss = StandardScaler()

# Transform `X`
X_scaled_data = ss.fit_transform(X)

# Put `X_scaled_data` into DataFrame
X_scaled = pd.DataFrame(X_scaled_data, columns=X.columns)

print("X_scaled shape:", X_scaled.shape)
X_scaled.head()

X_scaled_summary = X_scaled.aggregate(["mean","std"]).astype(int)
X_scaled_summary

n_clusters = range(2,13)
inertia_errors = []
silhouette_scores = []

# Add `for` loop to train model and calculate inertia, silhouette score.
for k in n_clusters:
    #Build model
    model = make_pipeline(
        StandardScaler(),
        KMeans(n_clusters=k, random_state=42)
        )
    #Train model
    model.fit(X)

    #Calculate inertia
    inertia_errors.append(model.named_steps['kmeans'].inertia_)

    #Calculate silhouette score
    silhouette_scores.append(
        silhouette_score(X, model.named_steps['kmeans'].labels_)
        )


print("Inertia:", inertia_errors[:3])
print()
print("Silhouette Scores:", silhouette_scores[:3])

# Create line plot of `inertia_errors` vs `n_clusters`
fig = px.line(
    x=n_clusters, y=inertia_errors, title="K-Mean Model: Inertia vs Number of Clusters"
    )

fig.update_layout(xaxis_title="Number of Clusters", yaxis_title="Inertia")

fig.show()

# Create a line plot of `silhouette_scores` vs `n_clusters`
fig = px.line(
    x=n_clusters, y=silhouette_scores, title="K-Means Model: Silhouette Score vs Number of Clusters"
    )
fig.update_layout(xaxis_title="Number of Clusters", yaxis_title="Silhouette score")
fig.show()

final_model = make_pipeline(
    StandardScaler(),
    KMeans(n_clusters=3, random_state=42)
)
final_model.fit(X)

"""Results"""

labels = final_model.named_steps["kmeans"].labels_
print(labels[:5])

xgb = X.groupby(labels).mean()
xgb

# Create side-by-side bar chart of `xgb`
fig = px.bar(
    xgb,
    barmode="group",
    title="Mean Household Finances by Cluster"
)
fig.update_layout(xaxis_title="Cluster", yaxis_title="Value [$]")
fig.show()

# Instantiate transformer
pca = PCA(n_components=2, random_state=42)

# Transform `X`
X_t = pca.fit_transform(X)

# Put `X_t` into DataFrame
X_pca = pd.DataFrame(X_t, columns= ["PC1","PC2"])

print("X_pca shape:", X_pca.shape)
X_pca.head()

# Create scatter plot of `PC2` vs `PC1`
fig = px.scatter(
    data_frame=X_pca,
    x= "PC1",
    y="PC2",
    color=labels.astype(str),
    title= "PCA Representation of Clusters"
)
fig.update_layout(xaxis_title="PC1", yaxis_title="PC2")

fig.show()

