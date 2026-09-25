Steps to Run Code:
1. To run load_data.py by itself, use this command: python load_data.py

1a. This will create a relational database schema using SQLite called cell_counts.db

1b. Make sure that cell-count.csv is in the same directory when running this

2. To run Teiko_Technical_Assessment.py (Python program/analysis script) by itself, use this command: python Teiko_Technical_Assessment.py

2a. This will produce the required outputs for parts 2-4 of the project instructions

3. As stated in the project instructions, to run the whole project from start to finish, use this worklow: make setup --> make pipeline --> make dashboard

4. Installed packages from requirements.txt should work, but if not, use these package versions:

4a. pandas: 3.0.6

4b. matplotlib: 3.11.2

4c. scipy: 1.18.1

4d. streamlit: 1.64.0

Note 1: Teiko_Technical_Assessment.ipynb is included in the GitHub repository for visual/debugging purposes and to show outputs more clearly (especially boxplots, which will not be shown just by running the Teiko_Technical_Assessment.py file due to the nature of the Codespace terminal but can be viewed in the Teiko_Technical_Assessment.ipynb file or the interactive dashboard).

Note 2: If make dashboard is ever run before make pipeline, cell_counts.db will already be created in the repository environment since its creation is required in the dashboard code to make the dashboard URL. Thus, cell_counts.db must be removed from the Codespaces environment before make pipeline is run to prevent "table already exists" error. Dashboard URL can be clicked at any time without creation or required removal of cell_counts.db.

Link to Dashboard: https://elyselow-teiko-tec-teiko-technical-interactive-dashboard-2wxzyg.streamlit.app/
