# Research Paper Guide: Predictive Analytics in the Indian Wedding Industry

This document acts as a blueprint to write your research paper. The transition from a "scraping project" to a "research paper" requires focusing on the **insight** and **methodology**, rather than just the code. 

---

## 1. Proposed Paper Titles
Choose a title that sounds highly academic and captures the essence of data science:
1. *Spatial and Predictive Cost Analytics of Indian Wedding Tourism using Web-Scraped Data and Machine Learning*
2. *Bridging the Information Gap in the Indian Wedding Industry: A Data Engineering and NLP Perspective*
3. *AI-Augmented Intelligence for Unstructured Markets: A Case Study on Venue Pricing Dynamics in India*

---

## 2. Research Gaps (The "Why")
To justify your research, you must highlight the **Literature Gaps**. State clearly in your introduction what issues currently exist:

* **Information Asymmetry & Opaque Pricing:** Price discovery in the Indian wedding industry is hidden behind inquiries. There is no central, verified dataset that consumers can use to gauge market standards.
* **Fragmented Data Ecosystems:** Venue details, ratings, and real capacities are scattered across multiple aggregators with high duplicated rates and conflicting information.
* **Lack of Spatial Market Analysis:** There is minimal academic literature that maps out "luxury corridors" or analyzes how geographic micro-locations influence venue cost within India.
* **AI Underutilization:** While generic AI tools exist, vertical-specific models (predicting custom event costs, context-aware chatbots for venue selection) are absent in academic studies focusing on South Asian markets.

---

## 3. Recommended Abstract Outline
**[Context]** The Indian wedding industry is a multi-billion dollar market characterized by high operational fragmentation and information asymmetry. 
**[Problem]** Consumers and event planners face significant hurdles in price discovery and venue comparability due to unstructured, duplicated, and opaque online data. 
**[Methodology]** In this study, we propose an automated pipeline that aggregates, normalizes, and dynamically deduplicates event venue data across top-tier Indian domains. Using a dataset of over 2,000 validated venues, we apply Machine Learning regression models to predict venue pricing, and natural language processing to enable semantic searches. 
**[Results]** Our analysis identifies critical "luxury corridors" in tourism hotspots and demonstrates that predictive models can ascertain fair-market value with [X]% accuracy. 
**[Contribution]** This paper contributes to the fields of spatial economics and applied data science by providing a framework for bringing transparency to unstructured, culturally-heavy service industries.

---

## 4. Methodology Section (What You Did)
This is where your codebase shines in the paper. Break down your method into these formal steps:

1. **Automated Discovery & Scraping Layer:** Discuss how you extracted data from `__INITIAL_STATE__` JSON and JSON-LD formats, mitigating rate-limiting with exponential backoff.
2. **Data Normalization Engine:** Explain how you used regex to standardize mixed string forms (e.g., converting "₹5 Lakhs" and "₹2L – ₹10L" into a unified integer base).
3. **Cross-Source Entity Resolution (Deduplication):** This is a great academic topic. Discuss the use of the `fuzzywuzzy` algorithm (Levenshtein Distance) to merge identical properties from different sites without exact ID matches.
4. **Predictive Modeling / AI Layer:** Detail the ML algorithm (e.g., Random Forest) chosen to correlate features (`capacity`, `rating`, `venue_type`) with `min_price`.

---

## 5. Easy Experiments to Run for Your "Results" Section
To make the paper legitimate, include empirical findings:
* **Feature Importance Plot:** Run your data through a Random Forest tree and plot which factor drives price the most. Is it the *City*, the *Rating*, or the *Capacity*?
* **Heatmaps & Density Maps:** Include your `cost_location_matrix.png` and `city_heatmap.png`.
* **Deduplication Metrics:** Present a table showing how many duplicates your algorithm successfully caught. This proves the "Engineering" effectiveness.

---

## 6. How to Write it efficiently without Hallucinating
* **Don't fake results:** Your `pipeline.log` and CSVs hold real metadata. Report the actual number of venues scraped, exact execution times, and actual failure ratios. 
* **Use LaTeX or Overleaf:** Write the paper in standard IEEE double-column format. It instantly makes the project look twice as professional.
* **Cite Libraries:** Reference pandas, scikit-learn, fuzzywuzzy, and Selenium. Look up academic papers that cite these tools and include them in your bibliography.
