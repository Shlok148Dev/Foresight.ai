"""
Foresight — NLP Detection Service (Signal Clustering Pipeline)
===============================================================
Implements the core signal detection engine:
  1. Text preprocessing (cleaning, normalization)
  2. TF-IDF vectorization for signal similarity
  3. DBSCAN clustering to group related signals into detections
  4. Keyword extraction via TF-IDF scoring
  5. Velocity calculation (signals per hour)
  6. Spread stage classification based on signal count + velocity

This is the brain of Foresight — turns raw signals into actionable trend detections.
Follows Technical Bible §3.1 — NLP Pipeline specification.
"""

import re
import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Signal, Detection, SpreadStage, PlatformType

logger = logging.getLogger("foresight.detection")


# ── Text Preprocessing ───────────────────────────────────────────

# Common stop words to filter out during keyword extraction
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "but", "and", "or", "if", "this", "that", "these", "those",
    "it", "its", "i", "me", "my", "we", "our", "you", "your", "he", "him",
    "she", "her", "they", "them", "their", "what", "which", "who", "whom",
    "up", "about", "get", "like", "think", "know", "see", "come", "make",
    "also", "amp", "https", "http", "www", "com", "rt", "via",
}


def clean_text(text: str) -> str:
    """
    Clean and normalize text for NLP processing.
    Removes URLs, mentions, hashtag symbols, and extra whitespace.
    """
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove @mentions (keep the name for context)
    text = re.sub(r"@(\w+)", r"\1", text)
    # Remove hashtag symbol but keep the word
    text = re.sub(r"#(\w+)", r"\1", text)
    # Remove special characters except basic punctuation
    text = re.sub(r"[^\w\s.,!?'-]", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def tokenize(text: str) -> list[str]:
    """Split cleaned text into tokens, filtering stop words and short words."""
    words = re.findall(r"\b[a-z]{3,}\b", text)
    return [w for w in words if w not in STOP_WORDS]


# ── TF-IDF Vectorization (Pure Python — no sklearn dependency for speed) ─────

def compute_tfidf(documents: list[list[str]]) -> tuple[list[dict[str, float]], dict[str, float]]:
    """
    Compute TF-IDF vectors for a list of tokenized documents.

    Returns:
        - List of TF-IDF vectors (one dict per document)
        - IDF dictionary (term → IDF score)
    """
    n_docs = len(documents)
    if n_docs == 0:
        return [], {}

    # Document frequency (how many docs contain each term)
    df = {}
    for doc in documents:
        unique_terms = set(doc)
        for term in unique_terms:
            df[term] = df.get(term, 0) + 1

    # IDF = log(N / df)
    idf = {term: math.log(n_docs / count) for term, count in df.items()}

    # TF-IDF for each document
    tfidf_vectors = []
    for doc in documents:
        tf = {}
        for term in doc:
            tf[term] = tf.get(term, 0) + 1
        # Normalize TF by document length
        doc_len = len(doc) if doc else 1
        vector = {term: (count / doc_len) * idf.get(term, 0) for term, count in tf.items()}
        tfidf_vectors.append(vector)

    return tfidf_vectors, idf


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse TF-IDF vectors."""
    common_terms = set(vec_a.keys()) & set(vec_b.keys())
    if not common_terms:
        return 0.0

    dot_product = sum(vec_a[t] * vec_b[t] for t in common_terms)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


# ── DBSCAN Clustering (Pure Python) ──────────────────────────────

def dbscan_cluster(
    vectors: list[dict[str, float]],
    eps: float = 0.35,
    min_samples: int = 2,
) -> list[int]:
    """
    DBSCAN clustering on sparse TF-IDF vectors.
    Returns cluster labels (-1 = noise/outlier).

    Args:
        vectors: List of TF-IDF dicts
        eps: Maximum distance between two samples (1 - cosine_similarity)
        min_samples: Minimum points to form a cluster
    """
    n = len(vectors)
    labels = [-1] * n
    visited = [False] * n
    cluster_id = 0

    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True

        # Find neighbors within eps distance
        neighbors = _region_query(vectors, i, eps)

        if len(neighbors) < min_samples:
            # Mark as noise (label stays -1)
            continue

        # Start a new cluster
        labels[i] = cluster_id
        seed_set = list(neighbors)
        j = 0

        while j < len(seed_set):
            q = seed_set[j]
            if not visited[q]:
                visited[q] = True
                q_neighbors = _region_query(vectors, q, eps)
                if len(q_neighbors) >= min_samples:
                    seed_set.extend(q_neighbors)
            if labels[q] == -1:
                labels[q] = cluster_id
            j += 1

        cluster_id += 1

    return labels


def _region_query(vectors: list[dict], point_idx: int, eps: float) -> list[int]:
    """Find all points within eps distance of point_idx."""
    neighbors = []
    for j in range(len(vectors)):
        if j == point_idx:
            continue
        sim = cosine_similarity(vectors[point_idx], vectors[j])
        distance = 1.0 - sim
        if distance <= eps:
            neighbors.append(j)
    return neighbors


# ── Keyword Extraction ───────────────────────────────────────────

def extract_keywords(
    documents: list[list[str]], idf: dict[str, float], top_k: int = 10
) -> list[str]:
    """
    Extract top-K keywords from a cluster of documents using TF-IDF scores.
    Merges all documents and ranks terms by aggregate TF-IDF.
    """
    # Aggregate term frequencies across all documents
    aggregate_tf = {}
    total_terms = 0
    for doc in documents:
        for term in doc:
            aggregate_tf[term] = aggregate_tf.get(term, 0) + 1
            total_terms += 1

    if total_terms == 0:
        return []

    # Score each term: tf * idf
    scores = {
        term: (count / total_terms) * idf.get(term, 0)
        for term, count in aggregate_tf.items()
    }

    # Sort by score and return top K
    sorted_terms = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [term for term, _ in sorted_terms[:top_k]]


# ── Spread Stage Classification ──────────────────────────────────

def classify_stage(signal_count: int, velocity: float) -> SpreadStage:
    """
    Classify a detection's spread stage based on signal count and velocity.

    Stages (from Technical Bible §3.2):
        embryonic:    < 5 signals, low velocity
        emerging:     5-20 signals, moderate velocity
        accelerating: 20-100 signals, high velocity
        peaking:      100+ signals, velocity plateau/decline
        declining:    any count, negative velocity trend
    """
    if velocity < 0:
        return SpreadStage.DECLINING
    if signal_count < 5:
        return SpreadStage.EMBRYONIC
    if signal_count < 20:
        return SpreadStage.EMERGING
    if signal_count < 100:
        return SpreadStage.ACCELERATING
    return SpreadStage.PEAKING


def compute_confidence(signal_count: int, velocity: float, platform_count: int) -> float:
    """
    Compute confidence score (0.0 – 1.0) for a detection.
    Higher signal count + velocity + platform diversity = higher confidence.
    """
    # Signal count component (log scale, max 0.4)
    count_score = min(math.log(signal_count + 1) / math.log(100), 1.0) * 0.4
    # Velocity component (max 0.3)
    velocity_score = min(velocity / 50.0, 1.0) * 0.3
    # Platform diversity (max 0.3)
    diversity_score = min(platform_count / 5.0, 1.0) * 0.3

    return round(min(count_score + velocity_score + diversity_score, 1.0), 3)


# ── Main Detection Pipeline ─────────────────────────────────────

async def run_detection_pipeline(
    db: AsyncSession,
    window_hours: int = 24,
    eps: float = 0.35,
    min_samples: int = 2,
) -> list[Detection]:
    """
    Run the full NLP detection pipeline:
      1. Fetch recent unprocessed signals (last window_hours)
      2. Clean and tokenize text
      3. Compute TF-IDF vectors
      4. Cluster with DBSCAN
      5. Create/update Detection records

    Args:
        db: Database session
        window_hours: Time window to analyze (default 24h)
        eps: DBSCAN distance threshold
        min_samples: Minimum signals per cluster

    Returns:
        List of new/updated Detection objects
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)

    # 1. Fetch recent unprocessed signals
    result = await db.execute(
        select(Signal)
        .where(
            and_(
                Signal.created_at >= cutoff,
                Signal.detection_id.is_(None),  # Not yet assigned to a detection
            )
        )
        .order_by(Signal.created_at.desc())
    )
    signals = result.scalars().all()

    if len(signals) < min_samples:
        logger.info(f"Not enough unprocessed signals ({len(signals)}) for clustering")
        return []

    logger.info(f"Running detection pipeline on {len(signals)} signals (window={window_hours}h)")

    # 2. Clean and tokenize
    cleaned_texts = [clean_text(s.text) for s in signals]
    tokenized = [tokenize(t) for t in cleaned_texts]

    # 3. Compute TF-IDF
    tfidf_vectors, idf = compute_tfidf(tokenized)

    # 4. Cluster
    labels = dbscan_cluster(tfidf_vectors, eps=eps, min_samples=min_samples)

    # 5. Create detections from clusters
    unique_labels = set(l for l in labels if l >= 0)
    new_detections = []

    for cluster_id in unique_labels:
        # Get signals in this cluster
        cluster_indices = [i for i, l in enumerate(labels) if l == cluster_id]
        cluster_signals = [signals[i] for i in cluster_indices]
        cluster_tokens = [tokenized[i] for i in cluster_indices]

        # Extract keywords for topic
        keywords = extract_keywords(cluster_tokens, idf, top_k=10)
        topic = ", ".join(keywords[:5]) if keywords else "Unknown Topic"

        # Compute metrics
        platforms = list(set(s.platform.value for s in cluster_signals))
        signal_count = len(cluster_signals)

        # Velocity: signals per hour over the window
        if signal_count > 1:
            time_span = (
                max(s.created_at for s in cluster_signals)
                - min(s.created_at for s in cluster_signals)
            ).total_seconds() / 3600
            velocity = signal_count / max(time_span, 0.1)
        else:
            velocity = 0.0

        stage = classify_stage(signal_count, velocity)
        confidence = compute_confidence(signal_count, velocity, len(platforms))
        action_prompt = _generate_action_prompt(topic, stage, velocity)
        
        # --- PHASE 2 AI/ML ENHANCEMENTS ---
        try:
            from app.services.llm_orchestration import trend_analyzer
            from app.services.mirofish_integration import mirofish_simulator
            from app.api.websocket import manager
            
            signal_dict = {
                "text": cluster_signals[0].text if cluster_signals else "",
                "entities": keywords,
                "keywords": keywords,
                "confidence": int(confidence * 100)
            }
            
            # Trend analysis via LLM 
            llm_analysis = await trend_analyzer.analyze_trend(signal_dict)
            if llm_analysis and llm_analysis.get("trend_name"):
                topic = llm_analysis.get("trend_name", topic)
                action_prompt = llm_analysis.get("forecast", action_prompt)
                
            # MiroFish Simulation
            simulation = mirofish_simulator.simulate_trend_spread(signal_dict)
            if simulation and simulation.get("virality_coefficient"):
                velocity = velocity + simulation["virality_coefficient"] * 10
        except Exception as e:
            logger.warning(f"Phase 2 AI Integration failed: {e}")
        # ----------------------------------

        # Create detection
        detection = Detection(
            topic=topic,
            description=f"Auto-detected cluster of {signal_count} signals across {', '.join(platforms)}",
            stage=stage,
            confidence=confidence,
            signal_count=signal_count,
            velocity=round(velocity, 2),
            platforms=platforms,
            keywords=keywords,
            action_prompt=action_prompt,
            metadata_={"cluster_id": cluster_id, "window_hours": window_hours, "eps": eps},
        )
        db.add(detection)
        await db.flush()
        
        # Broadcast via WebSocket
        try:
            from app.api.websocket import manager
            await manager.broadcast({
                "type": "new_trend",
                "data": {
                    "id": str(detection.id),
                    "topic": topic,
                    "stage": stage.value,
                    "confidence": confidence
                }
            })
        except Exception:
            pass

        # Link signals to this detection
        for signal in cluster_signals:
            signal.detection_id = detection.id

        new_detections.append(detection)
        logger.info(
            f"Detection created: '{topic}' | stage={stage.value} "
            f"| signals={signal_count} | velocity={velocity:.1f}/h | conf={confidence:.2f}"
        )

    logger.info(f"Pipeline complete: {len(new_detections)} detections created, "
                f"{sum(1 for l in labels if l == -1)} signals classified as noise")

    # --- PHASE 3A ENSEMBLE FORECASTING ---
    if new_detections:
        try:
            from app.services.forecasting_ensemble import EnsembleForecaster
            from app.models.database import Forecast
            from datetime import datetime, timezone, timedelta
            
            forecaster = EnsembleForecaster()
            
            for detection in new_detections:
                # Generate synthetic history for new detection to enable forecasting demo
                history = []
                base_count = max(10, detection.signal_count)
                now = datetime.now(timezone.utc)
                for i in range(7, 0, -1):
                    history.append({
                        "timestamp": (now - timedelta(days=i)).isoformat(),
                        "count": max(1, int(base_count * (0.8 ** i)))
                    })
                
                forecast_data = forecaster.forecast_trend(history, periods=21)
                
                # Save forecast
                for i in range(21):
                    f = Forecast(
                        detection_id=detection.id,
                        forecast_date=now + timedelta(days=i),
                        predicted_mentions=int(forecast_data["forecast"][i]),
                        confidence_lower=float(forecast_data["confidence_lower"][i]),
                        confidence_upper=float(forecast_data["confidence_upper"][i]),
                        model_version="ensemble-v1"
                    )
                    db.add(f)
                
                # Broadcast to frontend
                try:
                    from app.api.websocket import manager
                    await manager.broadcast({
                        "type": "new_forecast",
                        "data": {
                            "id": str(detection.id),
                            "forecast": forecast_data["forecast"],
                            "virality_score": forecast_data["virality_score"],
                            "peak_day": forecast_data["peak_day"]
                        }
                    })
                except Exception:
                    pass
                
                # --- PHASE 3B GNN PROPAGATION ---
                try:
                    from app.services.graph_neural_networks import TrendNetworkAnalyzer
                    from app.models.database import Simulation
                    gnn_analyzer = TrendNetworkAnalyzer()
                    propagation = gnn_analyzer.predict_propagation({"initial_adoption": 0.1}, time_steps=21)
                    
                    sim = Simulation(
                        detection_id=detection.id,
                        simulation_data=propagation,
                        virality_coefficient=float(propagation.get("mainstream_probability", 0.0))
                    )
                    db.add(sim)
                    
                    try:
                        await manager.broadcast({
                            "type": "new_propagation",
                            "data": {
                                "id": str(detection.id),
                                "peak_community": propagation["peak_community"],
                                "mainstream_probability": propagation["mainstream_probability"]
                            }
                        })
                    except Exception:
                        pass
                except Exception as e:
                    logger.warning(f"Phase 3B GNN failed: {e}")
                # --------------------------------
                
                # --- PHASE 3C ANOMALY DETECTION ---
                try:
                    from app.services.anomaly_detection import AnomalyDetector
                    detector = AnomalyDetector()
                    anomaly = detector.detect_anomalies(history)
                    
                    if anomaly["is_anomaly"]:
                        # Store in detection metadata
                        detection.metadata_["anomaly"] = anomaly
                        db.add(detection)
                        
                        try:
                            await manager.broadcast({
                                "type": "anomaly_alert",
                                "data": {
                                    "id": str(detection.id),
                                    "anomaly_type": anomaly["anomaly_type"],
                                    "confidence": anomaly["confidence"]
                                }
                            })
                        except Exception:
                            pass
                except Exception as e:
                    logger.warning(f"Phase 3C Anomaly Detection failed: {e}")
                # ----------------------------------
                
            await db.flush()
        except Exception as e:
            logger.warning(f"Phase 3 AI Pipeline failed: {e}")
    # -------------------------------------

    return new_detections


def _generate_action_prompt(topic: str, stage: SpreadStage, velocity: float) -> str:
    """Generate an actionable recommendation based on detection stage."""
    prompts = {
        SpreadStage.EMBRYONIC: f"Monitor '{topic}' closely — early signal detected. Set up alerts for keyword mentions.",
        SpreadStage.EMERGING: f"'{topic}' is gaining traction. Research the community and prepare a position.",
        SpreadStage.ACCELERATING: f"'{topic}' is accelerating fast ({velocity:.0f} signals/hr). Act NOW — write content, build tooling, or invest.",
        SpreadStage.PEAKING: f"'{topic}' is at peak. Maximize visibility — this is the moment. Be ready for the decline.",
        SpreadStage.DECLINING: f"'{topic}' is declining. Pivot to the next wave. Capture learnings and archive.",
    }
    return prompts.get(stage, f"Track '{topic}' and assess opportunities.")


# ── Single Signal Processing ────────────────────────────────────

async def process_single_signal(signal_id: str, db: AsyncSession) -> Optional[Detection]:
    """
    Process a single signal — attempt to match it to existing detections.
    If no match found, the signal remains unassigned until the batch pipeline runs.

    Used for real-time processing on signal ingestion.
    """
    result = await db.execute(select(Signal).where(Signal.id == UUID(signal_id)))
    signal = result.scalar_one_or_none()

    if not signal:
        logger.warning(f"Signal {signal_id} not found for processing")
        return None

    if signal.detection_id is not None:
        logger.debug(f"Signal {signal_id} already assigned to detection {signal.detection_id}")
        return None

    # Clean and tokenize the new signal
    cleaned = clean_text(signal.text)
    tokens = tokenize(cleaned)

    if not tokens:
        return None

    # Try to match against recent detections
    recent_detections = await db.execute(
        select(Detection)
        .where(Detection.first_seen >= datetime.now(timezone.utc) - timedelta(hours=48))
        .order_by(Detection.confidence.desc())
    )
    detections = recent_detections.scalars().all()

    for detection in detections:
        if not detection.keywords:
            continue
        # Simple keyword overlap matching
        overlap = len(set(tokens) & set(detection.keywords))
        overlap_ratio = overlap / max(len(tokens), 1)

        if overlap_ratio > 0.3:
            # Match found — assign signal to this detection
            signal.detection_id = detection.id
            detection.signal_count = (detection.signal_count or 0) + 1
            detection.last_updated = datetime.now(timezone.utc)
            logger.info(f"Signal {signal_id} matched to detection '{detection.topic}' (overlap={overlap_ratio:.2f})")
            return detection

    logger.debug(f"Signal {signal_id} — no matching detection found, awaiting batch pipeline")
    return None
