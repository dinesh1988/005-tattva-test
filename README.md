# VedAstro Python Engine

**Version:** 0.6.0 (January 25, 2026)  
**Status:** 18 modules, 21 yogas operational (22% complete)

This is a Python port of the core calculation engine of VedAstro.

## 🆕 What's New in v0.6.0

**Wealth Yogas Expansion:**
- ✨ 4 new yogas: Sakata, Chatussagara, Vasumathi, Parvata
- 🏆 Vasumathi Yoga: 75% frequency (highest in dataset!)
- ✅ Total: 21 yogas validated with real famous people data
- 📊 100% test success rate (20/20 people, 0 errors)

See [ROADMAP.md](ROADMAP.md) for complete feature list and [YOGA_PREDICTION_WORKFLOW.md](../YOGA_PREDICTION_WORKFLOW.md) for yoga documentation.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Download Ephemeris Files**:
    *   The Swiss Ephemeris library requires data files (`.se1`) to calculate planetary positions accurately.
    *   Download the files from [astro.com FTP](https://www.astro.com/ftp/swisseph/ephe/).
    *   At minimum, you need the main planetary files (e.g., `sepl_18.se1` for 1800-2400 AD).
    *   Place these files in the `ephe/` folder.

## Usage

Run the `main.py` script to see a demo calculation:

```bash
python main.py
```
