# Austrian Company Ownership and Control Knowledge Graph

## Project Overview

This project is a small knowledge graph prototype for Austrian company ownership and control analysis.

The goal is to model ownership relations between companies and investors, infer direct and indirect control, and display the result in a simple Angular web interface.

The project uses:

- CSV as raw input data
- Python for data cleaning, KG generation, and reasoning
- JSON as the frontend data format
- Angular for the web interface
- vis-network for browser-based graph visualization

---

## Data Sources

The project uses a small manually curated dataset derived from publicly available Austrian company ownership and company register information. The dataset was created for educational and demonstration purposes and is not a complete representation of Austrian company ownership structures.

Note:

The dataset is intentionally small and curated. Real ownership structures are often significantly more complex and may involve indirect ownership, shareholder agreements, trusts, and beneficial ownership arrangements that are not represented in this prototype.

The following sources were used to identify companies, ownership relationships, and company metadata:

### Austrian Business Register (Open Data Context)

https://www.data.gv.at/datasets/e91bd464-be86-453c-b693-2ab818e11df2

Provides information about the Austrian Business Register and publicly available company data resources.

### Austrian Business Register Search (Firmenbuch)

https://justizonline.gv.at/jop/web/firmenbuchabfrage

Official Austrian company register search portal used for company verification and company information lookup.

### FinAPU Firmenbuch

https://www.finapu.com/en/blog/finapu-firmenbuch-free-company-data-available

Provides structured Austrian company register information including company names, legal forms, company identifiers, and management information.

### Public Ownership Information

Ownership examples used in this project were based on publicly available information published by companies and public investment organizations such as:

- Österreichische Beteiligungs AG (ÖBAG)
- Österreichische Post AG
- OMV AG
- VERBUND AG
- Telekom Austria AG

The final dataset was manually transformed into a simplified ownership graph format:

owner,target,percentage

to support knowledge graph construction and control reasoning.

---

## Project Structure

```txt
kg-austrian-companies/
│
├── data/
│   ├── raw_companies.csv
│   └── cleaned_data.json
│
├── scripts/
│   ├── clean_data.py
│   ├── build_kg.py
│   ├── reason_control.py
│   └── export_frontend_data.py
│
├── kg/
│   ├── graph.json
│   └── control_relations.json
│
├── frontend/
│   └── kg-frontend/
│       ├── public/
│       │   └── assets/
│       │       └── kg-data.json
│       └── src/
│           └── app/
│
└── README.md
```

---

## Knowledge Graph Schema

### Node

Each company or investor is represented as a node.

Example:

{
  "id": "Österreichische Post AG",
  "label": "Österreichische Post AG",
  "type": "company"
}

### Edge

Ownership relations are represented as directed edges.

Example:

{
  "from": "Österreichische Beteiligungs AG",
  "to": "Österreichische Post AG",
  "percentage": 52.85
}

Meaning:

Österreichische Beteiligungs AG owns 52.85% of Österreichische Post AG.

---

## Control Rules

### Direct Control

A company is considered directly controlled when ownership is at least 50%.

Rule:

owner controls target if ownership >= 50%

Example:

Österreichische Beteiligungs AG owns 52.85% of Österreichische Post AG

Result:

Österreichische Beteiligungs AG directly controls Österreichische Post AG

### Indirect Control

Indirect control is inferred through ownership chains.

Example:

Republic of Austria
→ Österreichische Beteiligungs AG
→ Österreichische Post AG
→ bank99 AG

Result:

Republic of Austria indirectly controls bank99 AG.

---

## Running the Project

### Generate Knowledge Graph Data

From the project root:

```bash
cd scripts

python clean_data.py
python build_kg.py
python reason_control.py
python export_frontend_data.py

```

Generated files:

- cleaned_data.json
- graph.json
- control_relations.json
- kg-data.json

### Run the Frontend

```bash
cd frontend/kg-frontend
npm install
ng serve
```
Open:

http://localhost:4200

---

## Frontend Features

### Company List

- Lists all companies and investors
- Search functionality
- Navigation to company details

### Company Detail

Shows:

- Ownership relations
- Incoming ownership
- Direct control
- Indirect control
- Controllers

### Graph View

Shows:

- Companies and investors as nodes
- Ownership relationships as edges
- Ownership percentages
- Interactive graph navigation

---

## Limitations

Limitations:

- Small curated dataset
- Static JSON frontend data
- Simple control threshold of 50%
- No shareholder agreement analysis
- No combined ownership calculations
- No live connection to Austrian company registers

Future work could include:

- Neo4j integration
- SPARQL querying
- Larger ownership datasets
- Beneficial ownership analysis

---

## References

1. Austrian Open Government Data Portal (data.gv.at)

   https://www.data.gv.at

2. Austrian Business Register Search (JustizOnline Firmenbuch)

   https://justizonline.gv.at

3. FinAPU Firmenbuch

   https://www.finapu.com

4. Österreichische Beteiligungs AG (ÖBAG)

   https://www.oebag.gv.at

5. Österreichische Post AG

   https://www.post.at

6. OMV AG

   https://www.omv.com

7. VERBUND AG

   https://www.verbund.com

8. Telekom Austria AG

   https://www.a1.group