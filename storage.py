import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from config import Config
import logging

class ActivityStorage:
    """Handles storage and retrieval of activity records"""

    def __init__(self):
        self.log_file = Config.ACTIVITY_LOG_FILE
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Create activity log file if it doesn't exist"""
        if not os.path.exists(self.log_file):
            initial_data = {
                "created_at": datetime.now().isoformat(),
                "activities": []
            }
            self._save_data(initial_data)

    def _load_data(self) -> Dict[str, Any]:
        """Load data from the activity log file"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load activity log: {str(e)}")
            return {"created_at": datetime.now().isoformat(), "activities": []}

    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save data to the activity log file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to save activity log: {str(e)}")
            raise

    def save_activity(self, activity_data: Dict[str, Any]) -> bool:
        """
        Save a new activity record

        Args:
            activity_data (Dict[str, Any]): Activity data to save

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            data = self._load_data()

            # Create activity record
            activity_record = {
                "timestamp": datetime.now().isoformat(),
                "screenshot_path": activity_data.get("screenshot_path"),
                "activity_description": activity_data.get("activity_description"),
                "analysis_result": activity_data.get("analysis_result", {}),
                "confidence": activity_data.get("confidence", "unknown"),
                "analysis_successful": activity_data.get("analysis_successful", False),
                "error": activity_data.get("error")
            }

            # Add to activities list
            data["activities"].append(activity_record)

            # Save updated data
            self._save_data(data)

            logging.info(f"Activity saved successfully at {activity_record['timestamp']}")
            return True

        except Exception as e:
            logging.error(f"Failed to save activity: {str(e)}")
            return False

    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent activity records

        Args:
            limit (int): Maximum number of activities to return

        Returns:
            List[Dict[str, Any]]: Recent activities ordered from newest to oldest
        """
        try:
            data = self._load_data()
            activities = data.get("activities", [])

            if not activities:
                return []

            # Normalize limit so we can safely slice and always return newest-first.
            if limit is None:
                normalized_limit = len(activities)
            else:
                try:
                    normalized_limit = int(limit)
                except (TypeError, ValueError):
                    normalized_limit = len(activities)

            if normalized_limit <= 0:
                return []

            recent_activities = activities[-normalized_limit:]

            # Return newest records first so UIs that slice the first page show recent data.
            return list(reversed(recent_activities))

        except Exception as e:
            logging.error(f"Failed to get recent activities: {str(e)}")
            return []

    def get_activities_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """
        Get activities for a specific date

        Args:
            date_str (str): Date string in YYYY-MM-DD format

        Returns:
            List[Dict[str, Any]]: List of activities for the specified date
        """
        try:
            data = self._load_data()
            activities = data.get("activities", [])

            # Filter activities by date
            filtered_activities = []
            for activity in activities:
                activity_date = activity["timestamp"][:10]  # Extract YYYY-MM-DD
                if activity_date == date_str:
                    filtered_activities.append(activity)

            return filtered_activities

        except Exception as e:
            logging.error(f"Failed to get activities by date: {str(e)}")
            return []

    def get_activity_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about recorded activities

        Returns:
            Dict[str, Any]: Activity statistics
        """
        try:
            data = self._load_data()
            activities = data.get("activities", [])

            if not activities:
                return {
                    "total_activities": 0,
                    "successful_analyses": 0,
                    "failed_analyses": 0,
                    "success_rate": 0.0,
                    "first_activity": None,
                    "last_activity": None
                }

            successful_analyses = sum(1 for activity in activities if activity.get("analysis_successful", False))
            failed_analyses = len(activities) - successful_analyses
            success_rate = (successful_analyses / len(activities)) * 100 if activities else 0

            return {
                "total_activities": len(activities),
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "success_rate": round(success_rate, 2),
                "first_activity": activities[0]["timestamp"] if activities else None,
                "last_activity": activities[-1]["timestamp"] if activities else None
            }

        except Exception as e:
            logging.error(f"Failed to get activity statistics: {str(e)}")
            return {"error": str(e)}

    def cleanup_old_activities(self, keep_days: int = 30) -> int:
        """
        Clean up activities older than specified days

        Args:
            keep_days (int): Number of days to keep activities

        Returns:
            int: Number of activities removed
        """
        try:
            data = self._load_data()
            activities = data.get("activities", [])

            if not activities:
                return 0

            # Calculate cutoff date
            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)

            # Filter activities
            original_count = len(activities)
            filtered_activities = []

            for activity in activities:
                activity_timestamp = datetime.fromisoformat(activity["timestamp"]).timestamp()
                if activity_timestamp >= cutoff_date:
                    filtered_activities.append(activity)

            # Update data
            data["activities"] = filtered_activities
            self._save_data(data)

            removed_count = original_count - len(filtered_activities)
            logging.info(f"Cleaned up {removed_count} old activities")

            return removed_count

        except Exception as e:
            logging.error(f"Failed to cleanup old activities: {str(e)}")
            return 0

    def export_activities(self, output_file: str, date_range: Optional[tuple] = None) -> bool:
        """
        Export activities to a separate file

        Args:
            output_file (str): Path to output file
            date_range (Optional[tuple]): Optional date range (start_date, end_date)

        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            data = self._load_data()
            activities = data.get("activities", [])

            if date_range:
                start_date, end_date = date_range
                filtered_activities = []
                for activity in activities:
                    activity_date = activity["timestamp"][:10]
                    if start_date <= activity_date <= end_date:
                        filtered_activities.append(activity)
                activities = filtered_activities

            export_data = {
                "exported_at": datetime.now().isoformat(),
                "total_activities": len(activities),
                "activities": activities
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            logging.info(f"Exported {len(activities)} activities to {output_file}")
            return True

        except Exception as e:
            logging.error(f"Failed to export activities: {str(e)}")
            return False
