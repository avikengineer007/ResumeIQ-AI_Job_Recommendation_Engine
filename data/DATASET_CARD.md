# Dataset Card: ResumeIQ Skill & Benchmark Data

## Dataset Summary
This dataset repository powers the ResumeIQ hybrid job recommendation engine and controlled evaluation platform. It includes:
- Synthetic & anonymized resumes and job postings with source-span tracking
- Canonical skills taxonomy with aliases and hierarchical/related graph edges
- Train / Validation / Test evaluation splits (60% / 20% / 20%) split at the **resume level** with zero cross-split leakage.

## Known Coverage Limits & Evaluation Caveats
> [!WARNING]
> **Taxonomy Coverage Limitation (38 Canonical Skills)**:
> The initial taxonomy currently indexes 38 canonical skills across core engineering, machine learning, databases, cloud, and soft skills.
> While sufficient for testing extraction cascades, disambiguation, and ranking mechanics, **38 skills is an explicit coverage constraint for a production setting**.
> 
> **Metric Impact**: A small taxonomy may artificially inflate apparent `Recall@K` in retrieval evaluation by making "missing" skills rarer than they would be in open-domain job market postings. Open-domain evaluations should expand the taxonomy before drawing final recall conclusions.

## Taxonomy Specifications
- **Canonical Skills**: 38 skills (`data/processed/skills_taxonomy.csv`)
- **Skill Aliases**: 48 aliases with normalization rules (`data/processed/skill_aliases.csv`)
- **Relations**: 14 hierarchical and sibling relations with discount penalties (`data/processed/skill_relations.csv`)

## Split Protocol
- **Resume Split**: 60% Train, 20% Validation, 20% Test (`data/processed/splits.json`)
- **Random Seed**: Fixed at `42`
- **Leakage Prevention**: Grouped strictly by resume ID; job interactions from validation/test resumes never appear in training.
