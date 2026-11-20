# EDA Automation Assistant

A chat-based app that automates exploratory data analysis (EDA). Upload a CSV file and get a dataset summary, automatically generated charts and an LLM-written summary of the insights.

## Demo
<img width="627" height="209" alt="image" src="https://github.com/user-attachments/assets/1f16e36b-e05f-4939-b26b-294f0e113b53" />
<img width="510" height="308" alt="image" src="https://github.com/user-attachments/assets/bbf3214a-7856-4606-995f-1577911768e6" />
<img width="463" height="365" alt="image" src="https://github.com/user-attachments/assets/de53e774-481c-47be-90cf-889b2fd46346" />
<img width="183" height="334" alt="image" src="https://github.com/user-attachments/assets/d68b6962-71e7-434a-8be0-e6daf8ae1f5a" />
<img width="306" height="282" alt="image" src="https://github.com/user-attachments/assets/1c185acc-bb60-4cb6-9362-69ff9aeaed22" />
<img width="312" height="388" alt="image" src="https://github.com/user-attachments/assets/cf23d2ed-3a7b-42e0-b09d-50cd6337e2f2" />






## Features
- Upload any CSV in a Chainlit chat interface
- Dataset overview: shape, data types, missing values, unique values, most frequent values and summary statistics
- Charts chosen automatically by column type:
  - Numeric columns: correlation heatmap, pairplot, histograms, boxplots and violin plots
  - Categorical columns (10 or fewer unique values): pie charts and count plots
  - Date columns: time-series plots
- AI summary of the dataset using the Cohere Chat API

## Tech Stack
Python, Pandas, NumPy, Matplotlib, Seaborn, Chainlit, Cohere API

## How It Works
1. The user uploads a CSV file in the chat.
2. The file is loaded with Pandas and a summary table is shown.
3. Plotting functions check the column types and generate the matching charts.
4. The first 15 rows of the data are sent to the Cohere API, and the written summary is shown in the chat.

## Setup
1. Clone the repo and open the folder in a terminal.
2. Install dependencies: `pip install -r requirements.txt`
3. Get an API key from Cohere (dashboard.cohere.com).
4. Create a file named `.env` in the project folder with one line: `COHERE_API_KEY=your_key_here`
5. Run the app: `chainlit run app.py`
6. Open `http://localhost:8000` and upload a CSV. A small `sample.csv` is included for testing.

The `.env` file is ignored by Git, so your key is never uploaded.

## Notes
- A free Cohere trial key has rate limits, so the AI summary can fail if you upload files in quick succession.
- The AI summary is based on a small sample of the data (the first 15 rows), so treat it as a quick overview and not a full analysis.

## Author
Dhruv Panchal - [LinkedIn](https://linkedin.com/in/dhruv-panchal-a14865258)
