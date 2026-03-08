"""
AETHER Anomaly Detection Module
NASA-Inspired Time-Series Analysis

Inspired by:
- NASA's Livingstone 2 (fault detection)
- ExoMiner (anomaly detection in space data)
- Deep Learning Anomaly Detection in Mars Rover Data
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

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
    Uses statistical, ML, and deep learning approaches
    """
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus, "anomaly_detection")
        self.models = {}
        self.scalers = {}
        self.historical_data = {}
    
    async def initialize(self):
        """Initialize detection models"""
        logger.info("🔍 Initializing Anomaly Detection Module...")
        
        # Pre-configure models for common data types
        self.models["default"] = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scalers["default"] = StandardScaler()
        
        self.initialized = True
        logger.info("✅ Anomaly Detection Module ready")
    
    async def process(
        self,
        data: Any,
        context: Dict = None
    ) -> Dict:
        """
        Detect anomalies in time-series data
        
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
            # Convert to pandas Series
            series = self._prepare_data(data)
            
            results = {
                "success": True,
                "data_points": len(series),
                "method": method,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Run detection algorithms
            if method in ["statistical", "ensemble"]:
                stat_anomalies = self._statistical_detection(series, sensitivity)
                results["statistical"] = stat_anomalies
            
            if method in ["isolation_forest", "ensemble"]:
                if_anomalies = self._isolation_forest_detection(series)
                results["isolation_forest"] = if_anomalies
            
            if method in ["trend", "ensemble"]:
                trend_anomalies = self._trend_detection(series)
                results["trend"] = trend_anomalies
            
            # Combine results for ensemble method
            if method == "ensemble":
                combined = self._combine_detections(results)
                results["combined"] = combined
                results["anomalies"] = combined["anomalies"]
                results["anomaly_count"] = len(combined["anomalies"])
            else:
                # Use single method results
                key = method
                results["anomalies"] = results[key]["anomalies"]
                results["anomaly_count"] = len(results["anomalies"])
            
            # Calculate statistics
            results["statistics"] = {
                "mean": float(series.mean()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max()),
                "anomaly_rate": results["anomaly_count"] / len(series) if len(series) > 0 else 0
            }
            
            # Emit event if anomalies found
            if results["anomaly_count"] > 0:
                await self.emit_event(
                    "anomaly.detected",
                    {
                        "count": results["anomaly_count"],
                        "severity": self._calculate_severity(results),
                        "method": method
                    },
                    priority=3 if results["anomaly_count"] > 5 else 5
                )
            
            self._update_stats(success=True)
            return results
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection error: {e}")
            self._update_stats(success=False)
            return {"success": False, "error": str(e)}
    
    def _prepare_data(self, data: Any) -> pd.Series:
        """Convert various formats to pandas Series"""
        if isinstance(data, pd.Series):
            return data
        elif isinstance(data, pd.DataFrame):
            return data.iloc[:, 0]
        elif isinstance(data, (list, np.ndarray)):
            return pd.Series(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def _statistical_detection(
        self,
        series: pd.Series,
        sensitivity: str
    ) -> Dict:
        """Statistical outlier detection using Z-score and IQR"""
        # Z-score method
        z_threshold = {"low": 3, "medium": 2.5, "high": 2}[sensitivity]
        z_scores = np.abs(stats.zscore(series))
        z_anomalies = np.where(z_scores > z_threshold)[0].tolist()
        
        # IQR method
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        iqr_anomalies = series[
            (series < (Q1 - 1.5 * IQR)) | (series > (Q3 + 1.5 * IQR))
        ].index.tolist()
        
        # Combine
        all_anomalies = list(set(z_anomalies + iqr_anomalies))
        
        return {
            "method": "statistical",
            "anomalies": [
                {
                    "index": int(idx),
                    "value": float(series.iloc[idx]),
                    "z_score": float(z_scores[idx]) if idx < len(z_scores) else None
                }
                for idx in all_anomalies
            ],
            "z_threshold": z_threshold
        }
    
    def _isolation_forest_detection(self, series: pd.Series) -> Dict:
        """ML-based anomaly detection"""
        # Prepare features (value + rolling statistics)
        df = pd.DataFrame({
            'value': series,
            'rolling_mean': series.rolling(window=5, min_periods=1).mean(),
            'rolling_std': series.rolling(window=5, min_periods=1).std().fillna(0),
            'diff': series.diff().fillna(0)
        })
        
        # Fit and predict
        model = self.models["default"]
        scaler = self.scalers["default"]
        
        scaled = scaler.fit_transform(df)
        predictions = model.fit_predict(scaled)
        
        # -1 indicates anomaly
        anomaly_indices = np.where(predictions == -1)[0].tolist()
        
        return {
            "method": "isolation_forest",
            "anomalies": [
                {
                    "index": int(idx),
                    "value": float(series.iloc[idx]),
                    "anomaly_score": float(model.score_samples(scaled)[idx])
                }
                for idx in anomaly_indices
            ]
        }
    
    def _trend_detection(self, series: pd.Series) -> Dict:
        """Detect trend breaks and sudden changes"""
        # Calculate rate of change
        diff = series.diff().abs()
        threshold = diff.mean() + 2 * diff.std()
        
        trend_anomalies = diff[diff > threshold].index.tolist()
        
        return {
            "method": "trend",
            "anomalies": [
                {
                    "index": int(idx),
                    "value": float(series.iloc[idx]),
                    "change": float(diff.iloc[idx]),
                    "threshold": float(threshold)
                }
                for idx in trend_anomalies
            ],
            "threshold": float(threshold)
        }
    
    def _combine_detections(self, results: Dict) -> Dict:
        """Combine multiple detection methods"""
        all_indices = set()
        anomaly_details = {}
        
        for method in ["statistical", "isolation_forest", "trend"]:
            if method in results:
                for anomaly in results[method]["anomalies"]:
                    idx = anomaly["index"]
                    all_indices.add(idx)
                    if idx not in anomaly_details:
                        anomaly_details[idx] = {
                            "index": idx,
                            "value": anomaly["value"],
                            "methods": [],
                            "confidence": 0
                        }
                    anomaly_details[idx]["methods"].append(method)
                    anomaly_details[idx]["confidence"] += 1
        
        # Convert to list and sort by confidence
        combined = sorted(
            anomaly_details.values(),
            key=lambda x: x["confidence"],
            reverse=True
        )
        
        return {
            "method": "ensemble",
            "anomalies": combined,
            "total_unique": len(all_indices)
        }
    
    def _calculate_severity(self, results: Dict) -> str:
        """Calculate overall severity"""
        rate = results.get("anomaly_rate", 0)
        count = results.get("anomaly_count", 0)
        
        if rate > 0.2 or count > 20:
            return "high"
        elif rate > 0.1 or count > 10:
            return "medium"
        else:
            return "low"
    
    async def shutdown(self):
        """Cleanup"""
        logger.info("🛑 Shutting down Anomaly Detection Module")
        self.models.clear()
        self.scalers.clear()
        self.initialized = False