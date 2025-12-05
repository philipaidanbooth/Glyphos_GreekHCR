## Glyphos OCR

### Overview

This repository contains code and minimal assets for a Greek OCR project whose **best-performing model is trained from scratch** on Greek text lines, using a custom character vocabulary and dataset-specific preprocessing.

The core workflow is:
- **Preprocessing**: prepare line-level images and text annotations from the GRPOLY dataset and related sources.
- **Vocabulary building**: construct a Greek character vocabulary compatible with the OCR model.
- **Pre-training / fine-tuning**: train the OCR model on the prepared data.
- **Demo / comparison**: run an OCR comparison demo notebook.

### Origin of the Notebooks (Kaggle)

The main notebooks for this project were originally developed and run on Kaggle:

- **Pre-training notebook** (original Kaggle version):  
  [Kaggle Pre-Train Notebook](https://www.kaggle.com/code/philipbooth26/pre-train)
- **Demo OCR comparison notebook** (original Kaggle version):  
  [Kaggle Demo OCR Comparison Notebook](https://www.kaggle.com/code/philipbooth26/demo-ocr-comparison)

Local copies of these notebooks are included under the `Kaggle/` directory:
- `Kaggle/Pre_Train.ipynb`
- `Kaggle/Demo OCR Comparison (1).ipynb`

You can open and run these locally as long as you have the required dependencies and data in place.

### Repository Contents 

- `preprocess.py` – scripts for preprocessing the GRPOLY (and related) datasets into line-level images and labels.
- `extract_printed_lines.py` – utilities for extracting printed lines and generating CSV annotations.
- `tcocr_vocab.py`, `update_vocab.py` – tools for building and updating the OCR vocabulary JSON files and character set used by the **from-scratch** model.
- `train.py`, `configs.py` – training loop and configuration for the from-scratch OCR model.
- `trocr_vocab.json`, `vocabulary.json` – vocabulary files used by the model and comparison baselines.
- `train_split.csv`, `val_split.csv`, `test_split.csv` – dataset split definitions.
- `Kaggle/` – local copies of the original Kaggle notebooks mentioned above.

### Setup

1. **Create and activate a virtual environment** (optional but recommended).
2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Place data files** (images and CSV/JSON annotations) in the expected locations described in the notebooks and scripts (e.g., GRPOLY dataset folders, `printed_lines_5k.csv`, and the split CSVs).

### Running

- To reproduce preprocessing steps, run `preprocess.py` and/or `extract_printed_lines.py` as described in the Kaggle notebooks.
- To explore or rerun experiments, open:
  - (https://www.kaggle.com/code/philipbooth26/pre-train) for data preparation and model training.
  - (https://www.kaggle.com/code/philipbooth26/demo-ocr-comparison) for the OCR comparison demo.


