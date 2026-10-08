# **Minutes of Meeting: Project Setup and Modeling Roadmap**

**Date:** 5 October 2026

**Purpose:** Review progress on the literature review and data search, discuss the modeling approach, and agree how to organize the repository and working environment.

## **Literature review and paper**

* **Work completed or underway:** Ishika reported reading Nishant’s air protection paper and a paper by Priya. She had emailed 5–6 government organizations, including West Bengal Transportation and M. Parivahan, to seek data. None had responded yet.  
* **Plan:** Continue the literature review, discuss the findings, and begin writing the paper. The team was also asked to seek live data through college authorities where possible and keep those authorities informed about access.

## **Dataset search and modeling**

* **Priya’s findings:** She could not find the GitHub repository used by a reference paper. That paper used GPS and AVL data from Macau and Brazil, but its original dataset was not publicly available. **Her suggestion** was to use publicly available datasets instead; no dataset was selected in the meeting.  
* Priya also reviewed Nishant’s flight-delay prediction paper. It used historical flight data and Random Forest, XGBoost, and Lasso Regression. She suggested its preprocessing and prediction workflow could inform this project, with Lasso worth testing if the GPS dataset has many features. These were ideas for experimentation, **not chosen models**.  
* **Current status:** Modeling had not started. The team was still learning relevant methods: Vishal and Priya had some familiarity with ANN, while Transformer and other deep-learning models were still being studied. Around two deep-learning theory classes had taken place; an MLB module was expected to start the next day.  
* **Proposed plan:** Choose one algorithm class and focus on it. The specific class and start date were not specified.

## **Repository and data handling**

* **Issue-tracking plan:** Remove duplicate GitHub issues and keep three active issues. Add status updates and development progress to the relevant issue as work proceeds.  
* **Data-handling direction:** Put dataset links or paths in the source folder, **not the data itself**. A Google Drive link or separate data drive was discussed. A Python data loader was proposed so teammates could download data to the correct local path and run the models without sharing data through the repository.

## **Shared environment and security**

* **Decision:** Vishal will document the Python environment so everyone uses the same Python version and avoids package conflicts. Conda/Miniconda and virtual environments were discussed as options; neither was selected. Keep `requirements.txt` updated, or use a YAML environment file. A more robust Linux-based YAML setup was discussed as an option, **not an agreed requirement**.  
* **Security direction:** Do not put API keys in GitHub. Placeholders may be committed, but actual keys should be shared privately. Vishal asked whether GitHub secrets and variables could be used; the response focused instead on keeping local secret files out of the repository with `.gitignore` and sharing keys through a separate private channel. An earlier incident involving exposed and misused keys was cited as the reason for caution.

## **Action items**

| Task | Owner | Deadline |
| ----- | ----- | ----- |
| Continue the literature review, discuss findings, and begin drafting the paper | Ishika and Priya | Not specified |
| Continue seeking live data and coordinate with college authorities where possible | Jasveer and Ishika | Not specified |
| Find a publicly available dataset suitable for the project | Not specified | Not specified |
| Choose an algorithm class to focus on before modeling | Not specified | Not specified |
| Remove duplicate issues and maintain three active GitHub issues | Not specified | Not specified |
| Record development updates in the relevant GitHub issues | Team | As work progresses |
| Document the shared Python version and environment; maintain dependencies in `requirements.txt` or a YAML file | Vishal | Not specified |
| Keep API keys out of the repository and arrange private sharing where needed | Vishal | Not specified |

