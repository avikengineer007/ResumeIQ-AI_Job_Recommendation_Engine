# Model Card & Registry

## Purpose
Track all embedding and reranking checkpoints, their exact Git revisions, input dimensions, sequence length limits, and text templates.

## Principles
1. Reproducibility: Every stored embedding array and benchmark result records the exact model name and git revision hash.
2. No Data Leakage: Models are evaluated strictly on validation and test splits with frozen seeds.
