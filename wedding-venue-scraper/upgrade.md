# Project Upgrade Roadmap: Integrating NRI Legal & Safety Intelligence

Based on the **"Marriages to Overseas Indians"** booklet by the Ministry of External Affairs (MEA), this roadmap outlines how to evolve the **Indian Wedding Venue Intelligence Platform** into a high-utility tool for the NRI marriage segment.

---

## 1. Feature: The "NRI-Ready" Venue Index
Currently, the scraper collects price and capacity. An upgrade would include **Legal & Logistics Readiness**.

*   **Scraping Addition:** Identify if venues offer "NRI Wedding Packages" which often include legal assistance for registration, proximity to Foreigners Regional Registration Offices (FRRO), or specialized verification services.
*   **Data Field:** `nri_certified` (boolean) — Flag venues that have experience hosting international weddings and provide "Marriage Registration Support."
*   **Proximity Logic:** Use Geocoding to calculate the distance from each venue to the nearest **Indian Embassy** or **Passport Seva Kendra**.

## 2. Feature: Automated Legal Compliance Pipeline
The current pipeline cleans price strings. The upgrade will clean and validate **Legal Documents**.

*   **The "Apostille" Validator:** A sub-module in `validator.py` that checks if a user's documentation (like the Single Status Affidavit) meets the MEA requirements for the specific host country (e.g., USA, UK, Canada).
*   **Checklist Generator:** A tool that takes the `host_country` as input and generates a dynamic markdown checklist of mandatory documents (Tax returns, SSN, Visa, etc.) as per the MEA booklet.

## 3. Feature: The "Trust & Safety" Score
Integrate a safety layer into the existing analytics.

*   **Risk Heatmap:** Overlay the venue density with "Matrimonial Dispute Frequency" data from NCW (if available via scraping or open data portals).
*   **Verification Scraper:** A new scraper in `src/scrapers/` for the **MEA Madad Portal** or **NCW NRI Cell** (where public advisories are posted) to flag "Blacklisted Marriage Bureaus" or high-risk regions.

## 4. Technical Architecture Enhancements
To support these features, the architecture needs to evolve:

### A. New Scraper Tier: Government Portals
*   **Source:** [MEA India](https://www.mea.gov.in) and [NCW NRI Cell](https://ncw.nic.in/nri-cell).
*   **Purpose:** To fetch real-time updates on legal requirements and emergency contact directories.

### B. NLP-Based Contract Analysis
*   **Tool:** Use a Large Language Model (LLM) or Regex to analyze venue "Terms & Conditions" for clauses related to international cancellations, visa-related refunds, or legal dispute jurisdictions (Indian vs. Foreign courts).

## 5. UI/UX: The NRI Safety Dashboard
Add a new tab to the Plotly dashboard (`dashboard.py`):
*   **Legal Readiness Gauge:** Visual representation of how "prepared" a couple is based on a checklist.
*   **Embassy Locator Map:** Interactive map showing venue locations relative to legal aid and consular services.

---

## Why this Upgrade?
1.  **Market Need:** The NRI wedding industry is worth billions, but "Information Asymmetry" (as mentioned in your research paper) leads to significant legal risks.
2.  **Academic Value:** Elevates the project from a "scraper" to a "SaaS-ready legal-tech platform," which is highly impressive for a 6th-semester project defense.
3.  **Social Impact:** Directly addresses the MEA's concern about "abandoned brides" by providing tools for verification and legal awareness at the planning stage.
