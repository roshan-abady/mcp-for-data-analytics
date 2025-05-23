"""
Resources for the Time MCP Server.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs

from fastmcp import Server
from fastmcp.schemas import ResourceInfo

from server.utils.config import Config
from server.utils.timezone_utils import TimezoneUtils

logger = logging.getLogger(__name__)

def register_resources(server: Server, config: Config) -> None:
    """Register time resources with the MCP server."""
    
    # Create timezone utilities
    tz_utils = TimezoneUtils(default_timezone=config.default_timezone)
    
    @server.resource_provider("time://")
    async def time_resource_provider(uri: str) -> Optional[ResourceInfo]:
        """
        Provide time resources using the time:// URI scheme.
        
        This handler processes time:// URIs and returns time-related information
        based on the requested resource path.
        
        Args:
            uri: The time:// URI to resolve
            
        Returns:
            ResourceInfo if the resource is valid, None otherwise
            
        Examples:
            time://current?timezone=Australia/Melbourne  -> Current time in Melbourne
            time://melbourne                            -> Current time in Melbourne
            time://timezone/Australia/Melbourne         -> Timezone info for Melbourne
            time://timezones?country=AU                 -> List of Australian timezones
        """
        logger.info(f"Processing time resource URI: {uri}")
        
        try:
            # Parse the URI
            parsed = urlparse(uri)
            path_parts = parsed.path.strip('/').split('/')
            query_params = parse_qs(parsed.query)
            
            # Convert query params from lists to single values
            params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
            
            # Handle different resource paths
            if not path_parts or path_parts[0] == 'current':
                # Current time resource
                timezone = params.get('timezone', config.default_timezone)
                data = tz_utils.get_current_time(timezone)
                return ResourceInfo(
                    uri=uri,
                    content_type="application/json",
                    content=json.dumps(data),
                    metadata={
                        "resource_type": "time",
                        "timezone": timezone,
                        "description": f"Current time in {timezone}",
                    }
                )
            
            elif path_parts[0] == 'melbourne':
                # Melbourne time resource
                data = tz_utils.get_melbourne_time()
                return ResourceInfo(
                    uri=uri,
                    content_type="application/json",
                    content=json.dumps(data),
                    metadata={
                        "resource_type": "time",
                        "timezone": "Australia/Melbourne",
                        "description": "Current time in Melbourne, Australia",
                    }
                )
            
            elif path_parts[0] == 'timezone' and len(path_parts) > 1:
                # Timezone info resource
                # Reconstruct the timezone path (could contain multiple slashes)
                timezone = '/'.join(path_parts[1:])
                data = tz_utils.get_timezone_info(timezone)
                return ResourceInfo(
                    uri=uri,
                    content_type="application/json",
                    content=json.dumps(data),
                    metadata={
                        "resource_type": "timezone_info",
                        "timezone": timezone,
                        "description": f"Timezone information for {timezone}",
                    }
                )
            
            elif path_parts[0] == 'timezones':
                # Timezone listing resource
                country_code = params.get('country')
                region = params.get('region')
                
                timezones = tz_utils.list_timezones(country_code, region)
                
                # Limit the number of timezones if necessary
                if len(timezones) > config.max_timezones:
                    timezones = timezones[:config.max_timezones]
                
                data = {
                    "timezones": timezones,
                    "count": len(timezones),
                    "filter_country": country_code,
                    "filter_region": region
                }
                
                description = "List of timezones"
                if country_code:
                    description += f" in {country_code}"
                if region:
                    description += f" in {region} region"
                
                return ResourceInfo(
                    uri=uri,
                    content_type="application/json",
                    content=json.dumps(data),
                    metadata={
                        "resource_type": "timezone_list",
                        "description": description,
                        "count": len(timezones),
                    }
                )
            
            elif path_parts[0] == 'convert' and len(params) >= 1:
                # Time conversion resource
                time_str = params.get('time')
                source_tz = params.get('from', config.default_timezone)
                target_tz = params.get('to', config.default_timezone)
                
                if not time_str:
                    logger.error("Missing 'time' parameter for conversion")
                    return None
                
                data = tz_utils.convert_time(time_str, source_tz, target_tz)
                return ResourceInfo(
                    uri=uri,
                    content_type="application/json",
                    content=json.dumps(data),
                    metadata={
                        "resource_type": "time_conversion",
                        "description": f"Time conversion from {source_tz} to {target_tz}",
                        "source_timezone": source_tz,
                        "target_timezone": target_tz,
                    }
                )
            
            # If we get here, the resource wasn't found
            logger.warning(f"Invalid time resource path: {parsed.path}")
            return None
            
        except Exception as e:
            logger.error(f"Error processing time resource URI {uri}: {e}")
            return None
