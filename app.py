import chainlit as cl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile, io, os
from pathlib import Path
from dotenv import load_dotenv
import cohere

# --- Config ---
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("Set2")
load_dotenv(Path(__file__).parent / ".env")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY not found in .env file")
co = cohere.Client(COHERE_API_KEY)

# --- Utils ---
def save_and_send(fig, title, name):
    """Save a Matplotlib figure and send it as a Chainlit image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        fig.savefig(tmp.name, bbox_inches="tight")
        cl.run_sync(cl.Message(title, elements=[cl.Image(name=name, path=tmp.name)]).send())
    plt.close(fig)

def eda_summary(df):
    """Return a Markdown EDA summary."""
    return (
        f"**Shape:** Rows: {df.shape[0]}, Columns: {df.shape[1]}\n\n"
        f"**Data Types:**\n```text\n{df.dtypes}\n```\n\n"
        f"**Missing Values:**\n```text\n{df.isnull().sum()}\n```\n\n"
        f"**Unique Values per Column:**\n```text\n{df.nunique()}\n```\n\n"
        f"**Most Frequent Values:**\n```text\n{df.mode().head(1)}\n```\n\n"
        f"**Summary Stats:**\n{df.describe().to_markdown()}"
    )

def plot_numeric(df):
    """Generate numeric column plots."""
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return

    # Correlation heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(numeric.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("Correlation Heatmap")
    save_and_send(fig, "📌 Correlation Heatmap", "heatmap")

    # Pairplot (if manageable size)
    if len(numeric.columns) <= 5:
        sns_plot = sns.pairplot(df[numeric.columns].dropna(), corner=True)
        save_and_send(sns_plot.fig, "🔗 Pairplot", "pairplot")

    # Hist/Box/Violin
    for col in numeric.columns:
        for kind, func in {
            "Histogram": sns.histplot,
            "Boxplot": sns.boxplot,
            "Violinplot": sns.violinplot
        }.items():
            fig, ax = plt.subplots(figsize=(8, 5))
            func(df[col].dropna(), ax=ax)
            ax.set_title(f"{kind} for {col}")
            save_and_send(fig, f"{kind} for `{col}`", f"{kind}_{col}")

def plot_categorical(df):
    """Generate categorical column plots."""
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        if df[col].nunique() <= 10:
            # Pie chart
            fig, ax = plt.subplots(figsize=(6, 6))
            df[col].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
            ax.set_ylabel('')
            ax.set_title(f"Pie Chart of {col}")
            save_and_send(fig, f"🥧 Pie Chart for `{col}`", f"pie_{col}")

            # Countplot
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.countplot(data=df, x=col, ax=ax)
            ax.set_title(f"Countplot of {col}")
            plt.xticks(rotation=45)
            save_and_send(fig, f"📊 Countplot for `{col}`", f"count_{col}")

def plot_timeseries(df):
    """Generate simple time-series plots."""
    datetime_cols = list(df.select_dtypes(include="datetime64").columns)

    if not datetime_cols:  # ✅ Correct check for empty list
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]) or "date" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce")
                datetime_cols = [col]
                break

    if datetime_cols:  # ✅ Correct check again
        date_col = datetime_cols[0]
        numeric = df.select_dtypes(include="number")
        df_sorted = df.dropna(subset=[date_col]).sort_values(date_col)
        for num_col in numeric.columns:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df_sorted[date_col], df_sorted[num_col], marker="o")
            ax.set_title(f"{num_col} over time ({date_col})")
            plt.xticks(rotation=45)
            save_and_send(fig, f"⏳ Time Series Plot: `{num_col}` vs `{date_col}`", f"ts_{num_col}")

def ai_summary(df):
    """Generate AI summary using Cohere."""
    sample = df.head(15).to_string(index=False)
    prompt = f"You are a data analyst. Analyze this dataset and summarize insights:\n\n{sample}"
    res = co.generate(prompt=prompt, model="command-r-plus", max_tokens=300)
    return res.generations[0].text

# --- Chainlit Events ---
@cl.on_chat_start
async def main():
    await cl.Message("📂 Please upload a CSV file for analysis.").send()
    uploaded_files = await cl.AskFileMessage("🔺 Upload your CSV file", accept=["text/csv"]).send()
    if not uploaded_files:
        return await cl.Message("❌ No file uploaded.").send()

    try:
        with open(uploaded_files[0].path, encoding="utf-8", errors="replace") as f:
            df = pd.read_csv(io.StringIO(f.read()))
    except Exception as e:
        return await cl.Message(f"❌ Failed to read CSV: {e}").send()

    await cl.Message(f"✅ CSV Loaded:\n\n{df.head().to_markdown(index=False)}").send()
    await cl.Message(eda_summary(df)).send()

    plot_numeric(df)
    plot_categorical(df)
    plot_timeseries(df)

    try:
        summary = ai_summary(df)
        await cl.Message(f"🧠 **AI Summary**:\n\n{summary}").send()
    except Exception as e:
        await cl.Message(f"❌ Cohere Summary Error: {e}").send()
