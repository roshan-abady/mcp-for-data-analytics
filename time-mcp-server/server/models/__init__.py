"""
Data models for the Time MCP Server.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class TimeResponse(BaseModel):
    """Model for time responses."""
    
    timezone: str = Field(..., description="The timezone identifier")
    datetime: str = Field(..., description="The full datetime string")
    date: str = Field(..., description="The date component")
    time: str = Field(..., description="The time component")
    timestamp: float = Field(..., description="Unix timestamp")
    utc_offset: str = Field(..., description="UTC offset in format +/-HHMM")
    utc_offset_hours: float = Field(..., description="UTC offset in decimal hours")
    is_dst: bool = Field(..., description="Whether daylight saving time is active")
    day_of_week: str = Field(..., description="The day of week")
    day_of_year: int = Field(..., description="Day of year (1-366)")
    week_of_year: int = Field(..., description="Week of year")
    timezone_abbreviation: str = Field(..., description="Timezone abbreviation")


class ConversionRequest(BaseModel):
    """Model for time conversion requests."""
    
    time_str: str = Field(..., description="Time string to convert")
    source_timezone: Optional[str] = Field(None, description="Source timezone")
    target_timezone: Optional[str] = Field(None, description="Target timezone")
    
    @validator('source_timezone', 'target_timezone')
    def validate_timezone(cls, v):
        """Validate timezone strings."""
        if v is not None:
            import pytz
            if v not in pytz.all_timezones:
                raise ValueError(f"Invalid timezone: {v}")
        return v


class ConversionResponse(BaseModel):
    """Model for time conversion responses."""
    
    original: Dict[str, Any] = Field(..., description="Original time information")
    converted: Dict[str, Any] = Field(..., description="Converted time information")
    time_difference_hours: float = Field(..., description="Time difference in hours")


class TimezoneInfo(BaseModel):
    """Model for timezone information."""
    
    timezone: str = Field(..., description="The timezone identifier")
    country: Optional[str] = Field(None, description="Country associated with timezone")
    utc_offset: str = Field(..., description="UTC offset in format +/-HHMM")
    utc_offset_hours: float = Field(..., description="UTC offset in decimal hours")
    is_dst: bool = Field(..., description="Whether daylight saving time is active")
    dst_abbreviation: Optional[str] = Field(None, description="DST timezone abbreviation")
    standard_abbreviation: Optional[str] = Field(None, description="Standard timezone abbreviation")
    next_dst_transition: Optional[str] = Field(None, description="Next DST transition datetime")
    next_dst_transition_type: Optional[str] = Field(None, description="Type of next DST transition (start/end)")
    current_time: str = Field(..., description="Current time in this timezone")


class TimezoneListItem(BaseModel):
    """Model for items in timezone listings."""
    
    timezone: str = Field(..., description="The timezone identifier")
    utc_offset: str = Field(..., description="UTC offset in format +/-HHMM")
    utc_offset_hours: float = Field(..., description="UTC offset in decimal hours")
    is_dst: bool = Field(..., description="Whether daylight saving time is active")
    abbreviation: str = Field(..., description="Timezone abbreviation")


class TimezoneList(BaseModel):
    """Model for timezone listings."""
    
    timezones: List[TimezoneListItem] = Field(..., description="List of timezones")
    count: int = Field(..., description="Number of timezones in the list")
    filter_country: Optional[str] = Field(None, description="Country filter applied, if any")
    filter_region: Optional[str] = Field(None, description="Region filter applied, if any")
