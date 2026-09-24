setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python Teiko_Technical_Assessment.py

dashboard:
	streamlit run Teiko_Technical_Interactive_Dashboard.py
