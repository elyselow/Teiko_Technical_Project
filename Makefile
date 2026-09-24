setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python Teiko_Technical_Assessment.py

dashboard:
	python -m streamlit run Teiko_Technical_Interactive_Dashboard.py
