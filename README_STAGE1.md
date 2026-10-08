# Production Planning Optimisation — Stage 1

This stage creates the beginner-friendly Streamlit project structure and a minimal app that can be run before the database and ML model integration are added.

## Project structure

```text
production-planning-optimisation/
├── app/
│   ├── app.py                  # Streamlit entry point
│   ├── db/                     # SQLAlchemy models and database helpers
│   ├── models/                 # Saved ML model artifacts (not committed yet)
│   ├── pages/                  # Streamlit multi-page screens
│   └── services/               # Forecasting, planning, and order logic
├── data/
│   ├── raw/                    # Source CSV files from the repository
│   └── processed/              # Feature-engineered datasets and results
├── tests/                      # Automated tests added in later stages
├── .env.example                # Optional local configuration
├── requirements.txt            # Python dependencies
└── README_STAGE1.md            # Stage 1 instructions
```

## Run on Windows PowerShell

From the repository folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, run this once in a PowerShell window where you have permission:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## What you should see

A browser tab opens with the **Production Planning Optimisation** title and a Stage 1 information message.

## Common errors

- **`py` is not recognised:** install Python 3.11 and enable “Add Python to PATH”.
- **PowerShell script execution error:** run the `Set-ExecutionPolicy` command above.
- **`streamlit` is not recognised:** activate `.venv` and run `pip install -r requirements.txt` again.
- **A package fails to install:** confirm that Python 3.11 is active with `python --version`, then retry.

## Important model note

The repository includes the training notebooks and data, but the current Git checkout does **not** include a `.pkl`, `.joblib`, or other saved model artifact. Stage 3 will support the exact artifact once it is added to `models/`, or will provide a clearly labelled development fallback for testing the UI.
