"""Taxonomy management module for skills, aliases, and hierarchical/related relationships."""

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class SkillItem:
    skill_id: str
    canonical_name: str
    category: str
    skill_type: str  # technical, tool, domain, soft
    parent_skill_id: str | None = None
    description: str = ""
    taxonomy_version: str = "1.0.0"


@dataclass
class SkillRelation:
    source_skill_id: str
    target_skill_id: str
    relation_type: str  # parent_of, child_of, related_to
    discount_weight: float = 0.50


def normalize_lookup_key(text: str) -> str:
    """Normalize string key for exact dictionary lookup."""
    t = text.lower().strip()
    # Strip versions like '3.11' or 'v2'
    t = re.sub(r"\b(?:v|version)?\s*\d+(?:\.\d+)*\b", "", t).strip()
    # Normalize punctuation and dashes to spaces
    t = re.sub(r"[-_./]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


class SkillTaxonomy:
    """In-memory indexing for canonical skills, aliases, and relations."""

    def __init__(self) -> None:
        self.skills: dict[str, SkillItem] = {}
        self.alias_to_id: dict[str, str] = {}
        self.raw_aliases: list[str] = []
        self.relations_by_source: dict[str, list[SkillRelation]] = defaultdict(list)
        self.parents_by_child: dict[str, list[str]] = defaultdict(list)
        self.children_by_parent: dict[str, list[str]] = defaultdict(list)

    @classmethod
    def load_from_dir(cls, processed_dir: str | Path) -> "SkillTaxonomy":
        """Load taxonomy, aliases, and relations from standard CSV files."""
        p = Path(processed_dir)
        tax = cls()

        tax_file = p / "skills_taxonomy.csv"
        alias_file = p / "skill_aliases.csv"
        rel_file = p / "skill_relations.csv"

        if tax_file.exists():
            df_tax = pd.read_csv(tax_file)
            for _, row in df_tax.iterrows():
                parent = (
                    str(row["parent_skill_id"])
                    if pd.notnull(row.get("parent_skill_id"))
                    else None
                )
                item = SkillItem(
                    skill_id=str(row["skill_id"]),
                    canonical_name=str(row["canonical_name"]),
                    category=str(row.get("category", "General")),
                    skill_type=str(row.get("skill_type", "technical")),
                    parent_skill_id=parent,
                    description=str(row.get("description", "")),
                    taxonomy_version=str(row.get("taxonomy_version", "1.0.0")),
                )
                tax.skills[item.skill_id] = item
                # Map canonical name itself as an alias
                norm_name = normalize_lookup_key(item.canonical_name)
                tax.alias_to_id[norm_name] = item.skill_id
                tax.raw_aliases.append(norm_name)

                if parent:
                    tax.parents_by_child[item.skill_id].append(parent)
                    tax.children_by_parent[parent].append(item.skill_id)

        if alias_file.exists():
            df_alias = pd.read_csv(alias_file)
            for _, row in df_alias.iterrows():
                alias = str(row["alias"])
                c_id = str(row["canonical_skill_id"])
                norm_alias = normalize_lookup_key(alias)
                tax.alias_to_id[norm_alias] = c_id
                tax.raw_aliases.append(norm_alias)

        if rel_file.exists():
            df_rel = pd.read_csv(rel_file)
            for _, row in df_rel.iterrows():
                rel = SkillRelation(
                    source_skill_id=str(row["source_skill_id"]),
                    target_skill_id=str(row["target_skill_id"]),
                    relation_type=str(row["relation_type"]),
                    discount_weight=float(row.get("discount_weight", 0.50)),
                )
                tax.relations_by_source[rel.source_skill_id].append(rel)
                if rel.relation_type == "child_of":
                    tax.parents_by_child[rel.source_skill_id].append(
                        rel.target_skill_id
                    )
                elif rel.relation_type == "parent_of":
                    tax.children_by_parent[rel.source_skill_id].append(
                        rel.target_skill_id
                    )

        tax.raw_aliases = list(set(tax.raw_aliases))
        return tax

    def get_skill(self, skill_id: str) -> SkillItem | None:
        """Lookup SkillItem by canonical ID."""
        return self.skills.get(skill_id)

    def get_skill_by_name(self, name: str) -> SkillItem | None:
        """Lookup canonical SkillItem by raw or canonical name."""
        norm = normalize_lookup_key(name)
        sid = self.alias_to_id.get(norm)
        return self.skills.get(sid) if sid else None

    def get_all_parents(self, skill_id: str) -> list[str]:
        """Recursively retrieve all hierarchical parent skill IDs."""
        visited: set[str] = set()
        queue = list(self.parents_by_child.get(skill_id, []))
        while queue:
            curr = queue.pop(0)
            if curr not in visited:
                visited.add(curr)
                queue.extend(self.parents_by_child.get(curr, []))
        return list(visited)

    def get_related_skills(self, skill_id: str) -> list[tuple[str, float]]:
        """Retrieve direct non-hierarchical related skills with discount credit."""
        results: list[tuple[str, float]] = []
        for rel in self.relations_by_source.get(skill_id, []):
            if rel.relation_type == "related_to":
                results.append((rel.target_skill_id, rel.discount_weight))
        return results
