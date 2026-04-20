# Technical Presentation & Viva Defense Kit

This document is designed to help your team of 5 present this project as a **6th-semester high-grade submission**. In the "AI Era," a simple scraper isn't enough; you must demonstrate **System Architecture, Data Reliability, and Intelligent Analytics.**

---

## 1. How to "Show Off" in the AI Era
Professors often think scrapers are "too easy." To counter this, frame your project using these three pillars:

### A. Data Engineering Resilience (The "How")
*   **The Argument:** *"We didn't just scrape; we built a resilient pipeline that handles structured (JSON-LD), semi-structured (HTML), and dynamic (Selenium) data across 10 states with automated error handling and caching."*
*   **Show:** The `pipeline.log`, the SQLite caching system, and the `selectors.json` abstraction layer. Explain that your code is **Configuration-Driven**, meaning adding a new city takes 30 seconds, not a rewrite.

### B. Intelligent Normalization (The "Brain")
*   **The Argument:** *"Raw web data is filthy. We built a custom normalization engine that uses Probabilistic Deduplication and Regex-based extraction to turn '₹10L' and '₹10,00,000' into unified integers for ML modeling."*
*   **Show:** The `normalizer.py` test cases and the result of the `deduplicator.py` (how many duplicates were actually caught).

### C. Predictive/Generative Layer (The "Wow Factor")
*   **The Argument:** *"We used this clean dataset to train ML models that predict fair pricing and built an LLM-powered RAG agent for natural language venue discovery."*
*   **Show:** A live Streamlit dashboard where you type *"I want a royal wedding in Jaipur"* and it finds the venues.

---

## 2. Team Role Matrix (5 Members)
To ensure every member gets a high grade, assign these "Technical Labels" to their contributions:

| Member | Professional Title | Contribution for Viva |
| :--- | :--- | :--- |
| **Member 1** | **Backend & Architecture Lead** | Pipeline flow, Caching logic, CLI design, Multi-source orchestration. |
| **Member 2** | **Data Engineering Specialist** | Normalization logic, Regex engines, Schema validation, Database/Pandas optimization. |
| **Member 3** | **ML & Predictive Analytics** | Pricing Regression models, Anomaly detection (finding "fake" prices), Feature importance analysis. |
| **Member 4** | **AI Integration (NLP/LLM)** | Vector embeddings for venues, RAG Search integration, Sentiment analysis on scraped reviews. |
| **Member 5** | **Frontend & Data Visualization** | Full-stack Dashboard (Streamlit/FastAPI), Interactive maps (Folium), Automated Report generation. |

---

## 3. Top 5 "AI Addition" Features (Implementation Details)

### I. LLM-Query Agent (The "Agentic" Feature)
*   **Tech:** LangChain + Gemini-1.5-Flash (Free Tier).
*   **Why:** Instead of filters, the professor types: *"Which venue in Goa has the best price-to-rating ratio for 200 people?"*
*   **Implementation:** Convert your `venues_clean.csv` into a Vector Store (FAISS) or use the LLM to write Pandas queries on the fly.

### II. Automated Drift & Quality Monitoring
*   **Tech:** Pandera or Great Expectations.
*   **Why:** Shows you care about Data Quality. It automatically checks if `min_price` is missing for more than 20% of records and alerts the team.

### III. ML Venue Recommendation System
*   **Tech:** Scikit-learn (Content-based filtering).
*   **Why:** "Users who liked Palace X also liked Hotel Y." Simple to build using the `venue_type` and `city` features but sounds very advanced.

### IV. Dynamic Sentiment Insights
*   **Tech:** HuggingFace Transformers (`sentiment-analysis`).
*   **Why:** Don't just show a "4.5" rating. Show *"78% of people mentioned 'Poor Parking' in this area"*—this is "Deep Intelligence."

### V. Real-time Dashboard with Webhooks
*   **Tech:** Streamlit + Plotly.
*   **Why:** Seeing a static PNG is boring. Seeing an interactive map where you can click a venue and see its "Price vs Local Average" is a guaranteed A+.

---

## 4. Expected Viva Questions (Be Prepared!)

1.  **Q: "Why didn't you just use a single website?"**
    *   *A: Data fragmentation. Different sites have different price points and availability. Merging them gives us a 'Single Source of Truth' and exposes market outliers.*
2.  **Q: "How did you handle the legal/ethical aspect of scraping?"**
    *   *A: We implemented strict rate-limiting (1.5-3s delays), respected robots.txt, and used the data solely for academic aggregate analysis.*
3.  **Q: "What happened when a website changed its layout?"**
    *   *A: Our system is decoupled. We use `selectors.json`. We only update the JSON config, the logic in `main.py` remains untouched. This is industry-standard 'Clean Architecture'.*
4.  **Q: "How do you handle 'Fuzzy' duplicates?"**
    *   *A: We use the Levenshtein distance algorithm. If two venues are 90% similar in name and in the same city, we merge them and keep the data with higher density (more reviews).*

---

## 5. Live Demo Script
1.  **Start with the Log:** Show the terminal running. Say: *"Our pipeline is currently orchestrating parallel requests and caching responses to save bandwidth."*
2.  **The CSV Clean-up:** Show a "Raw" CSV vs a "Cleaned" CSV. Say: *"Look at how we handled the mixed currency and capacity strings."*
3.  **The AI Search:** Type a natural language query into your dashboard. Say: *"Our AI Advisor understands the intent, not just keywords."*
4.  **The Analytics:** Show the "Luxury Corridors" map. Say: *"This isn't just data; it's market intelligence for the $50 Billion Indian wedding industry."*
