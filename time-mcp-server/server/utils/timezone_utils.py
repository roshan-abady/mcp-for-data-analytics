"""
Timezone utilities for the Time MCP Server.
"""

import datetime
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
import pytz
from dateutil import parser

logger = logging.getLogger(__name__)

class TimezoneUtils:
    """Utility class for timezone operations."""
    
    def __init__(self, default_timezone: str = "Australia/Melbourne"):
        """
        Initialize with default timezone.
        
        Args:
            default_timezone: Default timezone to use (default: Australia/Melbourne)
        """
        self.default_timezone = default_timezone
        self._validate_timezone(default_timezone)
    
    def _validate_timezone(self, timezone: str) -> None:
        """
        Validate that the timezone is valid.
        
        Args:
            timezone: Timezone string to validate
            
        Raises:
            ValueError: If timezone is invalid
        """
        if timezone not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {timezone}")
    
    def get_current_time(self, timezone: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current time in the specified timezone or default timezone.
        
        Args:
            timezone: Timezone to use (optional, defaults to default_timezone)
            
        Returns:
            Dict with current time information
        """
        tz = timezone or self.default_timezone
        self._validate_timezone(tz)
        
        tz_obj = pytz.timezone(tz)
        now = datetime.datetime.now(tz_obj)
        
        # Check if in DST
        is_dst = now.dst() != datetime.timedelta(0)
        
        # Get UTC offset
        utc_offset = now.strftime('%z')
        utc_offset_hours = float(utc_offset[:-2]) + float(utc_offset[-2:]) / 60
        
        # Format for return
        return {
            "timezone": tz,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timestamp": now.timestamp(),
            "utc_offset": utc_offset,
            "utc_offset_hours": utc_offset_hours,
            "is_dst": is_dst,
            "day_of_week": now.strftime("%A"),
            "day_of_year": now.timetuple().tm_yday,
            "week_of_year": now.isocalendar()[1],
            "timezone_abbreviation": now.strftime("%Z"),
        }
    
    def convert_time(self, 
                    time_str: str, 
                    source_timezone: Optional[str] = None, 
                    target_timezone: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert time between timezones.
        
        Args:
            time_str: Time string to convert
            source_timezone: Source timezone (optional, defaults to default_timezone)
            target_timezone: Target timezone (optional, defaults to default_timezone)
            
        Returns:
            Dict with converted time information
        """
        src_tz = source_timezone or self.default_timezone
        dst_tz = target_timezone or self.default_timezone
        
        self._validate_timezone(src_tz)
        self._validate_timezone(dst_tz)
        
        # Parse the input time
        try:
            # Try to parse as a time only first (assuming today's date)
            if ":" in time_str and not any(c in time_str for c in "/-"):
                # This looks like just a time (HH:MM or HH:MM:SS)
                time_parts = time_str.split(":")
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                second = int(time_parts[2]) if len(time_parts) > 2 else 0
                
                # Create datetime with today's date
                src_tz_obj = pytz.timezone(src_tz)
                now = datetime.datetime.now(src_tz_obj)
                dt = src_tz_obj.localize(
                    datetime.datetime(now.year, now.month, now.day, hour, minute, second)
                )
            else:
                # Try to parse as a full datetime
                dt = parser.parse(time_str)
                if dt.tzinfo is None:
                    # If no timezone info was provided, assume source timezone
                    src_tz_obj = pytz.timezone(src_tz)
                    dt = src_tz_obj.localize(dt)
        except Exception as e:
            raise ValueError(f"Could not parse time string: {time_str}. Error: {e}")
        
        # Convert to target timezone
        dst_tz_obj = pytz.timezone(dst_tz)
        converted_dt = dt.astimezone(dst_tz_obj)
        
        # Check if either timezone is in DST
        source_is_dst = dt.dst() != datetime.timedelta(0)
        target_is_dst = converted_dt.dst() != datetime.timedelta(0)
        
        # Format for return
        return {
            "original": {
                "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": src_tz,
                "is_dst": source_is_dst,
                "timezone_abbreviation": dt.strftime("%Z"),
            },
            "converted": {
                "datetime": converted_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": dst_tz,
                "is_dst": target_is_dst,
                "timezone_abbreviation": converted_dt.strftime("%Z"),
            },
            "time_difference_hours": (
                converted_dt.utcoffset().total_seconds() - 
                dt.utcoffset().total_seconds()
            ) / 3600,
        }
    
    def get_timezone_info(self, timezone: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a timezone.
        
        Args:
            timezone: Timezone to get info for (optional, defaults to default_timezone)
            
        Returns:
            Dict with timezone information
        """
        tz = timezone or self.default_timezone
        self._validate_timezone(tz)
        
        tz_obj = pytz.timezone(tz)
        now = datetime.datetime.now(tz_obj)
        
        # Get DST information
        is_dst = now.dst() != datetime.timedelta(0)
        
        # Get the next DST transition (if any)
        next_dst_transition = None
        next_dst_transition_type = None
        
        # Try to find transitions within the next year
        transitions = []
        try:
            transitions = [
                (dt.replace(tzinfo=None), tz_obj._dst)
                for dt, _, _ in tz_obj._utc_transition_times
            ]
        except:
            # Some timezones don't have transitions
            pass
        
        if transitions:
            one_year_from_now = datetime.datetime.now() + datetime.timedelta(days=365)
            future_transitions = [
                (dt, dst) for dt, dst in transitions
                if dt > datetime.datetime.now() and dt < one_year_from_now
            ]
            
            if future_transitions:
                next_transition, next_dst = future_transitions[0]
                next_dst_transition = next_transition.strftime("%Y-%m-%d %H:%M:%S")
                next_dst_transition_type = "start" if next_dst else "end"
        
        # Return timezone information
        return {
            "timezone": tz,
            "country": self._get_timezone_country(tz),
            "utc_offset": now.strftime('%z'),
            "utc_offset_hours": float(now.strftime('%z')[:-2]) + float(now.strftime('%z')[-2:]) / 60,
            "is_dst": is_dst,
            "dst_abbreviation": now.strftime("%Z") if is_dst else None,
            "standard_abbreviation": None if is_dst else now.strftime("%Z"),
            "next_dst_transition": next_dst_transition,
            "next_dst_transition_type": next_dst_transition_type,
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def list_timezones(self, country_code: Optional[str] = None, 
                       region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available timezones, optionally filtered by country or region.
        
        Args:
            country_code: ISO country code to filter by (optional)
            region: Region string to filter by (e.g., 'Australia', 'Europe') (optional)
            
        Returns:
            List of timezone information dicts
        """
        filtered_zones = pytz.all_timezones
        
        # Filter by country if provided
        if country_code:
            country_code = country_code.upper()
            country_timezones = pytz.country_timezones.get(country_code, [])
            if country_timezones:
                filtered_zones = country_timezones
        
        # Filter by region if provided
        if region:
            filtered_zones = [tz for tz in filtered_zones if region in tz]
        
        # Convert to list of timezone info dicts
        result = []
        for tz in filtered_zones:
            try:
                tz_obj = pytz.timezone(tz)
                now = datetime.datetime.now(tz_obj)
                
                result.append({
                    "timezone": tz,
                    "utc_offset": now.strftime('%z'),
                    "utc_offset_hours": float(now.strftime('%z')[:-2]) + float(now.strftime('%z')[-2:]) / 60,
                    "is_dst": now.dst() != datetime.timedelta(0),
                    "abbreviation": now.strftime("%Z"),
                })
            except Exception as e:
                logger.warning(f"Error processing timezone {tz}: {e}")
        
        # Sort by UTC offset
        result.sort(key=lambda x: x["utc_offset_hours"])
        
        return result
    
    def get_melbourne_time(self) -> Dict[str, Any]:
        """
        Get current time in Melbourne, Australia.
        
        Returns:
            Dict with Melbourne time information
        """
        return self.get_current_time("Australia/Melbourne")
    
    def _get_timezone_country(self, timezone: str) -> Optional[str]:
        """
        Get the country for a timezone.
        
        Args:
            timezone: Timezone string
            
        Returns:
            Country name or None if not found
        """
        for country_code, timezones in pytz.country_timezones.items():
            if timezone in timezones:
                return pytz.country_names.get(country_code)
        return None
