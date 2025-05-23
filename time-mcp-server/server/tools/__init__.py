"""
Tools for the Time MCP Server.
"""

import logging
from typing import Dict, List, Optional, Any

from fastmcp import Server
from fastmcp.schemas import Tool, Function, FunctionCall

from server.utils.config import Config
from server.utils.timezone_utils import TimezoneUtils
from server.models import (
    TimeResponse, ConversionRequest, ConversionResponse, 
    TimezoneInfo, TimezoneList, TimezoneListItem
)

logger = logging.getLogger(__name__)

def register_tools(server: Server, config: Config) -> None:
    """Register all time-related tools with the MCP server."""
    
    # Create timezone utilities
    tz_utils = TimezoneUtils(default_timezone=config.default_timezone)
    
    @server.tool("time.current")
    async def get_current_time(timezone: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the current time in a specific timezone.
        
        Args:
            timezone: The timezone to get the current time for (optional, defaults to Australia/Melbourne)
            
        Returns:
            Current time information in the specified timezone
            
        Example:
            time.current(timezone="America/New_York") -> Current time in New York
        """
        logger.info(f"Getting current time for timezone: {timezone or config.default_timezone}")
        try:
            result = tz_utils.get_current_time(timezone)
            return TimeResponse(**result).dict()
        except ValueError as e:
            logger.error(f"Error getting current time: {e}")
            return {"error": str(e)}
    
    @server.tool("time.convert")
    async def convert_time(
        time_str: str,
        source_timezone: Optional[str] = None,
        target_timezone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert a time from one timezone to another.
        
        Args:
            time_str: The time string to convert (formats: "HH:MM", "HH:MM:SS", "YYYY-MM-DD HH:MM:SS")
            source_timezone: The source timezone (optional, defaults to Australia/Melbourne)
            target_timezone: The target timezone (optional, defaults to Australia/Melbourne)
            
        Returns:
            Time conversion information
            
        Example:
            time.convert(time_str="14:30", source_timezone="Australia/Melbourne", target_timezone="America/New_York")
            -> Converts 2:30 PM in Melbourne to the equivalent time in New York
        """
        logger.info(f"Converting time '{time_str}' from {source_timezone or config.default_timezone} "
                   f"to {target_timezone or config.default_timezone}")
        
        try:
            # Validate the request
            request = ConversionRequest(
                time_str=time_str,
                source_timezone=source_timezone,
                target_timezone=target_timezone
            )
            
            # Perform the conversion
            result = tz_utils.convert_time(
                time_str=request.time_str,
                source_timezone=request.source_timezone,
                target_timezone=request.target_timezone
            )
            
            return ConversionResponse(**result).dict()
        except ValueError as e:
            logger.error(f"Error converting time: {e}")
            return {"error": str(e)}
    
    @server.tool("time.timezone_info")
    async def get_timezone_info(timezone: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a timezone.
        
        Args:
            timezone: The timezone to get information for (optional, defaults to Australia/Melbourne)
            
        Returns:
            Detailed timezone information
            
        Example:
            time.timezone_info(timezone="Australia/Melbourne") -> Detailed info about Melbourne timezone
        """
        logger.info(f"Getting timezone info for: {timezone or config.default_timezone}")
        
        try:
            result = tz_utils.get_timezone_info(timezone)
            return TimezoneInfo(**result).dict()
        except ValueError as e:
            logger.error(f"Error getting timezone info: {e}")
            return {"error": str(e)}
    
    @server.tool("time.list_timezones")
    async def list_timezones(
        country_code: Optional[str] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List available timezones, optionally filtered by country or region.
        
        Args:
            country_code: ISO country code to filter by (e.g., "AU" for Australia)
            region: Region string to filter by (e.g., "Australia", "Europe")
            
        Returns:
            List of timezone information
            
        Example:
            time.list_timezones(country_code="AU") -> List of Australian timezones
        """
        logger.info(f"Listing timezones with filters - country: {country_code}, region: {region}")
        
        try:
            timezones = tz_utils.list_timezones(country_code, region)
            
            # Limit the number of timezones if necessary
            if len(timezones) > config.max_timezones:
                timezones = timezones[:config.max_timezones]
            
            # Convert to model
            timezone_items = [TimezoneListItem(**tz) for tz in timezones]
            
            result = TimezoneList(
                timezones=timezone_items,
                count=len(timezone_items),
                filter_country=country_code,
                filter_region=region
            )
            
            return result.dict()
        except ValueError as e:
            logger.error(f"Error listing timezones: {e}")
            return {"error": str(e)}
    
    @server.tool("time.melbourne")
    async def get_melbourne_time() -> Dict[str, Any]:
        """
        Get the current time in Melbourne, Australia.
        
        Returns:
            Current time information for Melbourne
            
        Example:
            time.melbourne() -> Current time in Melbourne
        """
        logger.info("Getting Melbourne time")
        
        try:
            result = tz_utils.get_melbourne_time()
            return TimeResponse(**result).dict()
        except Exception as e:
            logger.error(f"Error getting Melbourne time: {e}")
            return {"error": str(e)}
