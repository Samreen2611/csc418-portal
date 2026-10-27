# Assignment Submission Portal (CSC418 Lab Midterm)

Flask portal jahan students name, registration number, assignment title aur submission URL submit karte hain.
Har push par GitHub Actions tests chalata hai aur report local machine par `test-report.json` me save hoti hai.

## Setup
```
pip install -r requirements.txt
```

## Run the application
```
python app.py
```
Open http://localhost:5000

## Run the tests
```
python -m pytest
```

## Start the receiver
```
python receiver.py
```
Receiver http://localhost:8000/report par sunta hai aur report `test-report.json` me likhta hai.

## CI pipeline
`.github/workflows/ci.yml` har push par chalti hai (self-hosted runner):
1. dependencies install
2. pytest run (junit.xml banta hai; fail hua to step fail)
3. `ci/send_report.py` report ko receiver ko POST karta hai (pass aur fail dono me)