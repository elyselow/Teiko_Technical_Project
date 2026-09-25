#!/usr/bin/env python
# coding: utf-8

# In[8]:


import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import subprocess
from pathlib import Path
from scipy.stats import mannwhitneyu

st.title("Immune Cell Population Analysis Interactive Dashboard")

# In[9]:

# Generate cell_counts.db if not already in directory
DB_FILE = Path("cell_counts.db")

if not DB_FILE.exists():
    subprocess.run(["python", "load_data.py"], check=True)

# Connect to database
conn = sqlite3.connect("cell_counts.db")
cursor = conn.cursor()


# Read data from database
samples = pd.read_sql_query("""
    SELECT *
    FROM samples
""", conn)

subjects = pd.read_sql_query("""
    SELECT *
    FROM subjects
""", conn)


# In[ ]:



# Part 2: Cell Type Relative Frequency

st.header("Part 2: Cell Population Relative Frequencies")


cell_types = [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte"
]


# Calculate total cell count for each sample
samples["total_count"] = samples[cell_types].sum(axis=1)


# Create cell frequency summary table
cell_freq = samples.melt(
    id_vars=["sample", "total_count"],
    value_vars=cell_types,
    var_name="population",
    value_name="count"
)


# Calculate cell relative frequency percentages
cell_freq["percentage"] = (
    cell_freq["count"] / cell_freq["total_count"]
) * 100

# Order table by all cell populations listed for a sample first
cell_freq["population"] = pd.Categorical(
    cell_freq["population"],
    categories=cell_types,
    ordered=True
)

cell_freq = cell_freq.sort_values(["sample", "population"]).reset_index(drop=True)


# Interactive filters
selected_sample = st.selectbox(
    "Select a sample:",
    ["All"] + list(cell_freq["sample"].unique())
)

selected_population = st.selectbox(
    "Select a cell population:",
    ["All"] + cell_types
)


# Apply filters
filtered_data = cell_freq.copy()

if selected_sample != "All":
    filtered_data = filtered_data[
        filtered_data["sample"] == selected_sample
    ]

if selected_population != "All":
    filtered_data = filtered_data[
        filtered_data["population"] == selected_population
    ]


# Display cell frequency summary table
st.subheader("Cell Relative Frequency Summary Table")

st.dataframe(
    filtered_data,
    width="stretch"
)


# In[ ]:



# Part 3: Responders vs Non-responders

st.header("Part 3: Cell Frequencies of Responders vs Non-responders")


# Combine cell frequency data with sample and subject information
analysis_data = cell_freq.merge(
    samples[["sample", "subject", "sample_type"]],
    on="sample"
).merge(
    subjects[["subject", "condition", "treatment", "response"]],
    on="subject"
)


# Filter to melanoma PBMC samples treated with miraclib
analysis_data = analysis_data[
    (analysis_data["condition"] == "melanoma") &
    (analysis_data["treatment"] == "miraclib") &
    (analysis_data["sample_type"] == "PBMC") &
    (analysis_data["response"].isin(["yes", "no"]))
]

population_names = {
    "b_cell": "B Cell",
    "cd8_t_cell": "CD8 T Cell",
    "cd4_t_cell": "CD4 T Cell",
    "nk_cell": "NK Cell",
    "monocyte": "Monocyte"
}

# Select cell population
selected_part3_population = st.selectbox(
    "Select a cell population:",
    cell_types,
    key="part3_population"
)

population_name = population_names[selected_part3_population]

# Get responder and non-responder percentages
responder_data = analysis_data[
    (analysis_data["response"] == "yes") &
    (analysis_data["population"] == selected_part3_population)
]["percentage"]

non_responder_data = analysis_data[
    (analysis_data["response"] == "no") &
    (analysis_data["population"] == selected_part3_population)
]["percentage"]


# Create boxplot
fig, ax = plt.subplots(figsize=(6, 5))

ax.boxplot(
    [responder_data, non_responder_data],
    tick_labels=["Yes", "No"]
)

ax.set_title(
    f"{population_name} Relative Frequencies "
    "for Responders vs. Non-Responders"
)

ax.set_xlabel("Response")
ax.set_ylabel("Percentage (%)")

st.pyplot(fig)


# Mann-Whitney U test

statistic, p_value = mannwhitneyu(
    responder_data,
    non_responder_data,
    alternative="two-sided"
)

st.subheader(
    f"Mann-Whitney U Test for Statistically Significant Difference in {population_name} "
    "Relative Frequencies Between Responders vs. Non-responders"
)

st.write(f"Mann-Whitney U statistic: {statistic:.2f}")
st.write(f"p-value: {p_value:.4f}")

# Report results
if p_value < 0.05:
    st.write("The difference is statistically significant (p < 0.05).")
else:
    st.write("The difference is not statistically significant (p ≥ 0.05).")


# In[ ]:



# Part 4: Baseline Melanoma PBMC Samples

st.header("Part 4: Early Treatment Effects")

# Select what information to view
selected_category = st.selectbox(
    "Select a category:",
    ["Project", "Response", "Sex"],
    key="part4_category"
)


# Filter data accordingly using database and get number of samples for each project
if selected_category == "Project":

    cursor.execute("""
        SELECT subjects.project, COUNT(*)
        FROM samples
        JOIN subjects
            ON samples.subject = subjects.subject
        WHERE subjects.condition = 'melanoma'
          AND samples.sample_type = 'PBMC'
          AND subjects.treatment = 'miraclib'
          AND samples.time_from_treatment_start = 0
        GROUP BY subjects.project
    """)

    project_counts = cursor.fetchall()

    project_data = pd.DataFrame(
        project_counts,
        columns=["Project", "Number of Samples"]
    )

    selected_project = st.selectbox(
        "Select a project:",
        project_data["Project"],
        key="part4_project"
    )

    selected_data = project_data[
        project_data["Project"] == selected_project
    ]

    st.subheader("Number of Samples by Project")

    st.dataframe(
        selected_data,
        width="stretch",
        hide_index = True
    )


# Filter data accordingly using database and get number of subjects who are responders/non-responders
elif selected_category == "Response":

    cursor.execute("""
        SELECT subjects.response, COUNT(*)
        FROM samples
        JOIN subjects
            ON samples.subject = subjects.subject
        WHERE subjects.condition = 'melanoma'
          AND samples.sample_type = 'PBMC'
          AND subjects.treatment = 'miraclib'
          AND samples.time_from_treatment_start = 0
        GROUP BY subjects.response
        ORDER BY subjects.response DESC
    """)

    response_counts = cursor.fetchall()

    response_data = []

    for response, count in response_counts:
        if response == "yes":
            label = "Responders"
        elif response == "no":
            label = "Non-responders"

        response_data.append({
            "Response": label,
            "Number of Subjects": count
        })

    response_data = pd.DataFrame(response_data)

    selected_response = st.selectbox(
        "Select response:",
        response_data["Response"],
        key="part4_response"
    )

    selected_data = response_data[
        response_data["Response"] == selected_response
    ]

    st.subheader("Number of Subjects by Response")

    st.dataframe(
        selected_data,
        width="stretch",
        hide_index = True
    )


# Filter data accordingly using database and get number of subjects who are males/females
elif selected_category == "Sex":

    cursor.execute("""
        SELECT subjects.sex, COUNT(*)
        FROM samples
        JOIN subjects
            ON samples.subject = subjects.subject
        WHERE subjects.condition = 'melanoma'
          AND samples.sample_type = 'PBMC'
          AND subjects.treatment = 'miraclib'
          AND samples.time_from_treatment_start = 0
        GROUP BY subjects.sex
        ORDER BY subjects.sex DESC
    """)

    sex_counts = cursor.fetchall()

    sex_data = []

    for sex, count in sex_counts:
        if sex == "M":
            label = "Males"
        elif sex == "F":
            label = "Females"

        sex_data.append({
            "Sex": label,
            "Number of Subjects": count
        })

    sex_data = pd.DataFrame(sex_data)

    selected_sex = st.selectbox(
        "Select sex:",
        sex_data["Sex"],
        key="part4_sex"
    )

    selected_data = sex_data[
        sex_data["Sex"] == selected_sex
    ]

    st.subheader("Number of Subjects by Sex")

    st.dataframe(
        selected_data,
        width="stretch",
        hide_index = True
    )

conn.close()



