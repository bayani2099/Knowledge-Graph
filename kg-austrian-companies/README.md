# Austrian Company Ownership and Control Knowledge Graph

## Project Overview

This project is a small Knowledge Graph prototype for Austrian company ownership and control analysis.

The goal is to model ownership relations between companies and investors, infer direct and indirect control, train a Knowledge Graph embedding model, and display the results in a simple Angular web interface.

The project uses:

- CSV as raw input data
- Python for data cleaning, Knowledge Graph generation, reasoning, embedding training, evaluation, and validation
- JSON as the data format between pipeline stages and for the frontend
- Angular for the web interface
- vis-network for browser-based graph visualization
- PyTorch for the TransE Knowledge Graph embedding implementation

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
│   ├── Raw_Companies_Data.csv
│   └── cleaned_data.json
│
├── scripts/
│   ├── clean_data.py
│   ├── build_kg.py
│   ├── reason_control.py
│   ├── export_frontend_data.py
│   ├── train_embeddings.py
│   ├── evaluate_embeddings.py
│   ├── test_reasoning.py
│   └── validate_pipeline.py
│
├── kg/
│   ├── graph.json
│   ├── graph_metadata.json
│   ├── control_relations.json
│   ├── embeddings.json
│   └── data_quality_report.json
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

### Nodes

Each company or other ownership entity is represented as a node.

Example:

```json
{
  "id": "Österreichische Post AG",
  "label": "Österreichische Post AG",
  "type": "company"
}
```

The prototype currently uses two broad node types:

- `company`
- `entity`

Companies are identified using common legal-form suffixes such as `AG`, `GmbH`, `SE`, and `KG`. Other ownership entities, such as the Republic of Austria, are classified as `entity`.

### Edges

Ownership relations are represented as directed `OWNS` edges.

Example:

```json
{
  "from": "Österreichische Beteiligungs AG",
  "to": "Österreichische Post AG",
  "label": "52.85%",
  "type": "OWNS",
  "percentage": 52.85
}
```

Meaning:

```text
Österreichische Beteiligungs AG owns 52.85% of Österreichische Post AG.
```

Direct and indirect control are not treated as original ownership facts. They are derived later by the reasoning stage.

---

## Control Rules

### Direct Control

For this prototype, an owner is considered to directly control a target company when ownership is at least 50%.

Rule:

```text
owner controls target if ownership >= 50%
```

Example:

```text
Österreichische Beteiligungs AG
        │ 52.85%
        ▼
Österreichische Post AG
```

Result:

```text
Österreichische Beteiligungs AG → DIRECT_CONTROL → Österreichische Post AG
```

### Indirect Control

Indirect control is inferred by traversing chains of direct control.

Example:

```text
Republic of Austria
        │ 100%
        ▼
Österreichische Beteiligungs AG
        │ 52.85%
        ▼
Österreichische Post AG
        │ 90%
        ▼
bank99 AG
```

Result:

```text
Republic of Austria → INDIRECT_CONTROL → bank99 AG
```

The reasoning stage also records the path and depth used to derive an indirect relation. A maximum reasoning depth of 10 and cycle protection are used to prevent unbounded traversal.

---

## Knowledge Graph Embeddings

The project also implements TransE using PyTorch.

TransE represents entities and relations as vectors and trains them so that valid triples approximately satisfy:

```text
h + r ≈ t
```

The current configuration is:

| Parameter | Value |
|---|---:|
| Embedding dimension | 32 |
| Epochs | 1,000 |
| Learning rate | 0.01 |
| Margin | 1.0 |
| Random seed | 42 |
| Relation | OWNS |

Negative samples are generated by replacing either the head or tail entity of an existing ownership triple.

The trained entity and relation vectors are stored in:

```text
kg/embeddings.json
```

### Embedding Evaluation

The project includes a leave-one-out link-prediction evaluation. Each ownership triple is held out in turn, the model is trained on the remaining triples, and the correct target entity is ranked against the other candidate entities.

Current evaluation results:

| Metric | Result |
|---|---:|
| MRR | 0.2059 |
| Hits@1 | 0.0000 |
| Hits@3 | 0.2222 |
| Hits@10 | 1.0000 |

Because the graph contains only 10 entities and 9 ownership relations, these metrics are mainly used as evidence of the implemented training and evaluation procedure rather than as evidence of strong generalization.

---

## Pipeline

The complete data-processing pipeline is:

```text
Raw_Companies_Data.csv
        │
        ▼
clean_data.py
        │
        ▼
cleaned_data.json
        │
        ▼
build_kg.py
        │
        ├── graph.json
        └── graph_metadata.json
        │
        ▼
reason_control.py
        │
        ▼
control_relations.json
        │
        ▼
train_embeddings.py
        │
        ▼
embeddings.json
        │
        ▼
validate_pipeline.py
        │
        ▼
export_frontend_data.py
        │
        ▼
frontend/kg-frontend/public/assets/kg-data.json
```

The project also includes:

```text
evaluate_embeddings.py
```

for leave-one-out embedding evaluation and:

```text
test_reasoning.py
```

for automated tests of the reasoning implementation.

---

## Running the Project

Run the Python scripts from the **project root**, not from inside the `scripts` directory.

### Generate the Knowledge Graph Data

```bash
python scripts/clean_data.py
python scripts/build_kg.py
python scripts/reason_control.py
python scripts/train_embeddings.py
python scripts/validate_pipeline.py
python scripts/export_frontend_data.py
```

### Evaluate the Embeddings

Run after `train_embeddings.py`:

```bash
python scripts/evaluate_embeddings.py
```

### Test the Reasoning Component

```bash
python scripts/test_reasoning.py
```

### Generated Files

The pipeline generates:

```text
data/cleaned_data.json
kg/data_quality_report.json
kg/graph.json
kg/graph_metadata.json
kg/control_relations.json
kg/embeddings.json
frontend/kg-frontend/public/assets/kg-data.json
```
---

## Run the Frontend

From the project root:

```bash
cd frontend/kg-frontend
npm install
ng serve
```

Then open:

```text
http://localhost:4200
```

The Angular frontend uses the exported `kg-data.json` file from:

```text
frontend/kg-frontend/public/assets/kg-data.json
```
---

## Frontend Features

### Company List

- Lists the companies and other ownership entities in the dataset
- Provides search functionality
- Provides navigation to company details

### Company Detail

Shows:

- Ownership relations
- Incoming ownership
- Direct control relations
- Indirect control relations
- Controllers derived by the reasoning stage

---

### Graph View

Uses vis-network to display:

- Companies and ownership entities as nodes
- Ownership relationships as directed edges
- Ownership percentages
- Interactive graph navigation

The graph view is intended to make multi-level ownership structures easier to inspect visually.

---

## Data Validation and Consistency Checks

The cleaning stage validates the raw ownership data by checking:

- Required fields
- Empty entity names
- Ownership percentages between 0 and 100
- Self-ownership
- Duplicate ownership records
- Whitespace normalization

The final pipeline validation checks that:

- All cleaned relations exist in the graph
- All graph edges reference valid nodes
- Graph metadata is consistent
- All control relations reference valid nodes
- Every KG entity has an embedding
- Every entity embedding has 32 dimensions

The current pipeline contains:

- 10 entities
- 9 ownership relations
- 5 direct-control relations
- 3 indirect-control relations
- 32-dimensional entity embeddings

All implemented pipeline validation checks currently pass.

---

## Encoding

The project uses UTF-8 throughout the data pipeline and frontend export. The frontend export script explicitly reads the graph and control data as UTF-8 and writes `kg-data.json` using UTF-8 with `ensure_ascii=False`.


## Limitations

The prototype intentionally has several limitations:

- Small curated dataset
- Static JSON frontend data
- Simplified 50% control threshold
- No shareholder agreement analysis
- No combined ownership calculations
- No live connection to Austrian company registers
- Simple entity classification based on legal-form suffixes
- Embedding evaluation is limited by the very small graph

Future work could include:

- Larger ownership datasets
- More detailed company and ownership metadata
- Beneficial ownership analysis
- More advanced control rules
- Neo4j integration for larger graphs
- SPARQL-based querying
- More extensive embedding experiments

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