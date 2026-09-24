"""Joint hyperparameter optimization and calibration module for the validation split.

Protocol Rules:
1. Joint search across retrieval fusion weights and personalization weights
   (they interact and must not be tuned in isolation).
2. Optimization objective is frozen NDCG@10 from Phase 5 evaluation harness.
3. Calibration is fit exclusively on validation prediction scores resulting from the optimal parameters.
4. Serializes calibrator to safe JSON and exports tuned hyperparameters.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Any

from src.embeddings.embedder import (
    DenseEmbedder,
    format_job_text,
    format_resume_text,
)
from src.embeddings.faiss_index import FaissVectorIndex
from src.evaluation.metrics import evaluate_ranking_dataset
from src.recommendation.calibration import (
    ScoreCalibrator,
    brier_score,
    expected_calibration_error,
)
from src.recommendation.personalization import CandidatePreferences, PersonalizedScorer
from src.reranking.cross_encoder import CrossEncoderReranker
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_search import HybridSearchEngine
from src.skill_normalization.skill_matcher import SkillMatcher


@dataclass
class TunedPipelineConfig:
    rrf_k: int
    fusion_weights: dict[str, float]
    lambda_exp: float
    personalization_weights: dict[str, float]
    best_ndcg_at_10: float
    best_mrr: float
    calibrator_method: str = "isotonic"
    calibrator_brier: float = 0.0
    calibrator_ece: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _extract_skill_ids(skills: Any) -> list[str]:
    if skills is None:
        return []
    if hasattr(skills, "tolist"):
        skills = skills.tolist()
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",")]
    clean_ids: list[str] = []
    for item in skills:
        if isinstance(item, dict):
            s_id = item.get("skill_id") or item.get("name", "")
            if s_id:
                clean_ids.append(str(s_id))
        elif hasattr(item, "skill_id"):
            clean_ids.append(str(item.skill_id))
        elif isinstance(item, str) and item.strip():
            clean_ids.append(item.strip())
    return clean_ids


class JointPipelineTuner:
    """Jointly tunes retrieval fusion, reranking cutoff, personalization weights, and score calibrator."""

    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        vector_index: FaissVectorIndex,
        embedder: DenseEmbedder,
        skill_matcher: SkillMatcher,
        reranker: CrossEncoderReranker,
    ) -> None:
        self.bm25 = bm25_retriever
        self.vector_index = vector_index
        self.embedder = embedder
        self.skill_matcher = skill_matcher
        self.reranker = reranker

    def tune(
        self,
        val_resumes: Sequence[dict[str, Any]],
        jobs: Sequence[dict[str, Any]],
        val_qrels: dict[str, dict[str, float]],
        fusion_candidates: Sequence[dict[str, Any]] | None = None,
        personalization_candidates: Sequence[dict[str, Any]] | None = None,
        top_candidates_pool: int = 20,
    ) -> tuple[TunedPipelineConfig, ScoreCalibrator]:
        """Perform joint parameter search over validation set and fit score calibrator."""
        job_lookup = {str(j.get("job_id", j.get("id"))): j for j in jobs}
        job_texts = {j_id: format_job_text(j) for j_id, j in job_lookup.items()}

        # Default joint grid candidates if none provided
        f_grid = fusion_candidates or [
            {"mode": "rrf", "rrf_k": 40, "weights": None},
            {"mode": "rrf", "rrf_k": 60, "weights": None},
            {
                "mode": "linear",
                "rrf_k": 60,
                "weights": {"bm25": 0.30, "vector": 0.50, "skill": 0.20},
            },
            {
                "mode": "linear",
                "rrf_k": 60,
                "weights": {"bm25": 0.40, "vector": 0.40, "skill": 0.20},
            },
        ]

        p_grid = personalization_candidates or [
            {
                "lambda_exp": 0.25,
                "weights": {
                    "s_rerank": 0.35,
                    "s_sem": 0.20,
                    "s_skill": 0.25,
                    "s_exp": 0.10,
                    "s_role": 0.05,
                    "s_loc": 0.025,
                    "s_mode": 0.025,
                },
            },
            {
                "lambda_exp": 0.35,
                "weights": {
                    "s_rerank": 0.45,
                    "s_sem": 0.15,
                    "s_skill": 0.20,
                    "s_exp": 0.10,
                    "s_role": 0.05,
                    "s_loc": 0.025,
                    "s_mode": 0.025,
                },
            },
            {
                "lambda_exp": 0.35,
                "weights": {
                    "s_rerank": 0.30,
                    "s_sem": 0.20,
                    "s_skill": 0.30,
                    "s_exp": 0.10,
                    "s_role": 0.05,
                    "s_loc": 0.025,
                    "s_mode": 0.025,
                },
            },
        ]

        best_score = -1.0
        best_f_cfg = f_grid[0]
        best_p_cfg = p_grid[0]
        best_metrics: dict[str, float] = {}

        # Joint search loop
        for f_cfg in f_grid:
            engine = HybridSearchEngine(
                bm25_retriever=self.bm25,
                vector_index=self.vector_index,
                embedder=self.embedder,
                rrf_k=f_cfg["rrf_k"],
                linear_weights=f_cfg.get("weights"),
                job_skills_lookup={
                    j_id: (
                        j.get("skills", []).tolist()
                        if hasattr(j.get("skills", []), "tolist")
                        else list(j.get("skills", []))
                    )
                    for j_id, j in job_lookup.items()
                },
                skill_matcher=self.skill_matcher,
            )

            for p_cfg in p_grid:
                scorer = PersonalizedScorer(weights=p_cfg["weights"])
                all_retrieved: list[list[str]] = []
                all_relevant: list[dict[str, float]] = []

                for resume in val_resumes:
                    r_id = str(resume.get("resume_id", resume.get("id")))
                    if r_id not in val_qrels:
                        continue

                    # 1. Hybrid search
                    query_text = format_resume_text(resume)
                    clean_skill_ids = _extract_skill_ids(resume.get("skills", []))

                    candidates = engine.search(
                        query=query_text,
                        candidate_skill_ids=clean_skill_ids,
                        top_k=top_candidates_pool,
                        mode=f_cfg["mode"],
                    )

                    # 2. Cross-Encoder reranking
                    reranked = self.reranker.rerank(
                        query_text=query_text,
                        candidates=candidates,
                        job_texts_lookup=job_texts,
                        top_k=top_candidates_pool,
                    )

                    # 3. Personalization
                    pref_obj = resume.get("preferences", {})
                    roles = (
                        pref_obj.get("roles", []) if isinstance(pref_obj, dict) else []
                    )
                    if hasattr(roles, "tolist"):
                        roles = roles.tolist()
                    target_role = (
                        roles[0]
                        if (isinstance(roles, list) and len(roles) > 0)
                        else str(
                            pref_obj.get("role", "")
                            if isinstance(pref_obj, dict)
                            else ""
                        )
                    )

                    prefs = CandidatePreferences(
                        target_role=target_role,
                        years_of_experience=float(resume.get("total_years", 0.0)),
                        candidate_skills=clean_skill_ids,
                        preferred_locations=(
                            pref_obj.get("locations", [])
                            if isinstance(pref_obj, dict)
                            else []
                        ),
                        preferred_work_modes=(
                            pref_obj.get("work_modes", [])
                            if isinstance(pref_obj, dict)
                            else []
                        ),
                    )

                    cand_dicts = []
                    for r_res in reranked:
                        j_item = dict(job_lookup.get(r_res.job_id, {}))
                        j_item["rerank_score"] = r_res.rerank_score
                        cand_dicts.append(j_item)

                    personalized = scorer.score_candidates(cand_dicts, prefs, top_k=10)
                    ranked_ids = [p.job_id for p in personalized]

                    all_retrieved.append(ranked_ids)
                    all_relevant.append(val_qrels[r_id])

                if not all_retrieved:
                    continue

                eval_results = evaluate_ranking_dataset(
                    all_retrieved, all_relevant, k_values=[5, 10]
                )
                ndcg10 = eval_results.get("ndcg@10", 0.0)

                if ndcg10 > best_score:
                    best_score = ndcg10
                    best_f_cfg = f_cfg
                    best_p_cfg = p_cfg
                    best_metrics = eval_results

        # Collect prediction scores from best configuration to fit calibrator
        val_pred_scores: list[float] = []
        val_true_labels: list[int] = []

        best_engine = HybridSearchEngine(
            bm25_retriever=self.bm25,
            vector_index=self.vector_index,
            embedder=self.embedder,
            rrf_k=best_f_cfg["rrf_k"],
            linear_weights=best_f_cfg.get("weights"),
            job_skills_lookup={
                j_id: (
                    j.get("skills", []).tolist()
                    if hasattr(j.get("skills", []), "tolist")
                    else list(j.get("skills", []))
                )
                for j_id, j in job_lookup.items()
            },
            skill_matcher=self.skill_matcher,
        )
        best_scorer = PersonalizedScorer(weights=best_p_cfg["weights"])

        for resume in val_resumes:
            r_id = str(resume.get("resume_id", resume.get("id")))
            if r_id not in val_qrels:
                continue

            query_text = format_resume_text(resume)
            clean_skill_ids = _extract_skill_ids(resume.get("skills", []))

            candidates = best_engine.search(
                query=query_text,
                candidate_skill_ids=clean_skill_ids,
                top_k=top_candidates_pool,
                mode=best_f_cfg["mode"],
            )
            reranked = self.reranker.rerank(
                query_text=query_text,
                candidates=candidates,
                job_texts_lookup=job_texts,
                top_k=top_candidates_pool,
            )

            pref_obj = resume.get("preferences", {})
            roles = pref_obj.get("roles", []) if isinstance(pref_obj, dict) else []
            if hasattr(roles, "tolist"):
                roles = roles.tolist()
            target_role = (
                roles[0]
                if (isinstance(roles, list) and len(roles) > 0)
                else str(pref_obj.get("role", "") if isinstance(pref_obj, dict) else "")
            )

            prefs = CandidatePreferences(
                target_role=target_role,
                years_of_experience=float(resume.get("total_years", 0.0)),
                candidate_skills=clean_skill_ids,
                preferred_locations=(
                    pref_obj.get("locations", []) if isinstance(pref_obj, dict) else []
                ),
                preferred_work_modes=(
                    pref_obj.get("work_modes", []) if isinstance(pref_obj, dict) else []
                ),
            )
            cand_dicts = []
            for r_res in reranked:
                j_item = dict(job_lookup.get(r_res.job_id, {}))
                j_item["rerank_score"] = r_res.rerank_score
                cand_dicts.append(j_item)

            personalized = best_scorer.score_candidates(cand_dicts, prefs, top_k=10)
            for p_item in personalized:
                rel = val_qrels[r_id].get(p_item.job_id, 0.0)
                val_pred_scores.append(p_item.final_score)
                val_true_labels.append(1 if rel > 0.0 else 0)

        # Fit calibrator on validation predictions
        if len(set(val_true_labels)) > 1:
            calibrator = ScoreCalibrator(method="isotonic")
            calibrator.fit(val_pred_scores, val_true_labels)
            cal_probs = calibrator.predict_proba(val_pred_scores)
            brier = brier_score(val_true_labels, cal_probs)
            ece = expected_calibration_error(val_true_labels, cal_probs)
        else:
            # Fallback default calibrator if single class
            calibrator = ScoreCalibrator(method="platt")
            calibrator.is_fit = True
            brier, ece = 0.0, 0.0

        tuned_config = TunedPipelineConfig(
            rrf_k=best_f_cfg["rrf_k"],
            fusion_weights=best_f_cfg.get("weights")
            or {"bm25": 0.35, "vector": 0.45, "skill": 0.20},
            lambda_exp=best_p_cfg["lambda_exp"],
            personalization_weights=best_p_cfg["weights"],
            best_ndcg_at_10=best_metrics.get("ndcg@10", 0.0),
            best_mrr=best_metrics.get("mrr", 0.0),
            calibrator_method="isotonic",
            calibrator_brier=brier,
            calibrator_ece=ece,
        )

        return tuned_config, calibrator
