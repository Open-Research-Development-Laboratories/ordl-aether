"""
AETHER Anomaly Detection Module
NASA-Inspired Time-Series Analysis

Inspired by:
- NASA's Livingstone 2 (fault detection)
- ExoMiner (anomaly detection in space data)
- Deep Learning Anomaly Detection in Mars Rover Data
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from core.base_module import BaseModule
from core.event_bus import EventBus

logger = logging.getLogger(__name__)


class AnomalyDetectionModule(BaseModule):
    """
    Multi-algorithm anomaly detection for time-series data
    Uses statistical and ML-based approaches.
    """

    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus, "anomaly_detection")
        self.models = {}
        self.scalers = {}

    async def initialize(self):
        """Initialize detection models."""
        logger.info("Initializing Anomaly Detection Module...")

        self.models["default"] = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100,
            n_jobs=-1,
        )
        self.scalers["default"] = StandardScaler()

        self.initialized = True
        logger.info("Anomaly Detection Module ready")

    async def process(
        self,
        data: Any,
        context: Dict = None
    ) -> Dict:
        """
        Detect anomalies in time-series data.

        Args:
            data: List of values or pandas DataFrame
            context: Detection parameters

        Returns:
            Anomaly detection results
        """
        context = context or {}
        method = context.get("method", "ensemble")
        sensitivity = context.get("sensitivity", "medium")

        try:
            results = await asyncio.to_thread(
                self._run_detection_sync,
                data,
                method,
                sensitivity,
            )

            if results["anomaly_count"] > 0:
                await self.emit_event(
                    "anomaly.detected",
                    {
                        "count": results["anomaly_count"],
                        "severity": self._calculate_severity(results),
                        "method": method,
                    },
                    priority=3 if results["anomaly_count"] > 5 else 5,
                )

            self._update_stats(success=True)
            return results

        except Exception as exc:
            logger.error("Anomaly detection error: %s", exc)
            self._update_stats(success=False)
            return {"success": False, "error": str(exc)}

    def _run_detection_sync(self, data: Any, method: str, sensitivity: str) -> Dict:
        series = self._prepare_data(data)
        if len(series) < 3:
            raise ValueError("At least 3 data points are required for anomaly detection")

        results = {
            "success": True,
            "data_points": len(series),
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if method in {"statistical", "ensemble"}:
            results["statistical"] = self._statistical_detection(series, sensitivity)

        if method in {"isolation_forest", "ensemble"}:
            results["isolation_forest"] = self._isolation_forest_detection(series)

        if method in {"trend", "ensemble"}:
            results["trend"] = self._trend_detection(series)

        if method == "ensemble":
            combined = self._combine_detections(results)
            results["combined"] = combined
            results["anomalies"] = combined["anomalies"]
            results["anomaly_count"] = len(combined["anomalies"])
        else:
            if method not in results:
                raise ValueError(f"Unknown detection method: {method}")
            results["anomalies"] = results[method]["anomalies"]
            results["anomaly_count"] = len(results["anomalies"])

        anomaly_rate = results["anomaly_count"] / len(series)
        results["statistics"] = {
            "mean": float(series.mean()),
            "std": float(series.std(ddof=0)),
            "min": float(series.min()),
            "max": float(series.max()),
            "anomaly_rate": anomaly_rate,
        }
        results["severity"] = self._calculate_severity(results)
        return results

    def _prepare_data(self, data: Any) -> pd.Series:
        """Convert various formats to pandas Series."""
        if isinstance(data, pd.Series):
            return data.astype(float)
        if isinstance(data, pd.DataFrame):
            return data.iloc[:, 0].astype(float)
        if isinstance(data, (list, np.ndarray)):
            return pd.Series(data, dtype="float64")
        raise ValueError(f"Unsupported data type: {type(data)}")

    def _statistical_detection(self, series: pd.Series, sensitivity: str) -> Dict:
        """Statistical outlier detection using Z-score and IQR."""
        z_threshold = {"low": 3.0, "medium": 2.5, "high": 2.0}[sensitivity]

        raw_z = stats.zscore(series, nan_policy="omit")
        z_scores = np.nan_to_num(np.abs(raw_z), nan=0.0, posinf=0.0, neginf=0.0)
        z_anomalies = np.where(z_scores > z_threshold)[0].tolist()

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        iqr_anomalies = series[
            (series < (q1 - 1.5 * iqr)) | (series > (q3 + 1.5 * iqr))
        ].index.tolist()

        all_anomalies = sorted(set(z_anomalies + iqr_anomalies))

        return {
            "method": "statistical",
            "anomalies": [
                {
                    "index": int(idx),
                    "value": float(series.iloc[idx]),
                    "z_score": float(z_scores[idx]) if idx < len(z_scores) else None,
                }
                for idx in all_anomalies
            ],
            "z_threshold": z_threshold,
        }

    def _isolation_forest_detection(self, series: pd.Series) -> Dict:
        """ML-based anomaly detection."""
        features = pd.DataFrame(
            {
                "value": series,
                "rolling_mean": series.rolling(window=5, min_periods=1).mean(),
                "rolling_std": series.rolling(window=5, min_periods=1).std().fillna(0.0),
                "diff": series.diff().fillna(0.0),
            }
        )

        model = self.models["default"]
        scaler = self.scalers["default"]
        scaled = scaler.fit_transform(features)

        predictions = model.fit_predict(scaled)
        scores = model.score_samples(scaled)
        anomaly_indices = np.where(predictions == -1)[0].tolist()

        return {
            "method": "isolation_forest",
            "anomalies": [
                {
                    "index": int(idx),
                    "value": float(series.iloc[idx]),
                    "anomaly_score": float(scores[idx]),
                }
                for idx in anomaly_indices
            ],
        }

    def _trend_detection(self, series: pd.Series) -> Dict:
        """Detect trend breaks and sudden changes."""
        diff = series.diff().abs().fillna(0.0)
        threshold = diff.mean() + 2 * diff.std(ddof=0)
        trend_anomalies = diff[diff > threshold].index.tolist()

        return {
            "method": "trend",
            "anomalies": [
                {
                    "index": int(idx),
                    "value": float(series.iloc[idx]),
                    "change": float(diff.iloc[idx]),
                    "threshold": float(threshold),
                }
                for idx in trend_anomalies
            ],
            "threshold": float(threshold),
        }

    def _combine_detections(self, results: Dict) -> Dict:
        """Combine multiple detection methods."""
        anomaly_details = {}

        for method in ["statistical", "isolation_forest", "trend"]:
            if method not in results:
                continue
            for anomaly in results[method]["anomalies"]:
                idx = anomaly["index"]
                if idx not in anomaly_details:
                    anomaly_details[idx] = {
                        "index": idx,
                        "value": anomaly["value"],
                        "methods": [],
                        "confidence": 0,
                    }
                anomaly_details[idx]["methods"].append(method)
                anomaly_details[idx]["confidence"] += 1

        combined = sorted(
            anomaly_details.values(),
            key=lambda item: item["confidence"],
            reverse=True,
        )

        return {
            "method": "ensemble",
            "anomalies": combined,
            "total_unique": len(anomaly_details),
        }

    def _calculate_severity(self, results: Dict) -> str:
        """Calculate overall severity from anomaly rate and count."""
        stats_payload = results.get("statistics", {})
        rate = stats_payload.get("anomaly_rate", 0.0)
        count = results.get("anomaly_count", 0)

        if rate > 0.2 or count > 20:
            return "high"
        if rate > 0.1 or count > 10:
            return "medium"
        return "low"

    async def shutdown(self):
        """Cleanup."""
        logger.info("Shutting down Anomaly Detection Module")
        self.models.clear()
        self.scalers.clear()
        self.initialized = False
