"""
Prompts for the Time MCP Server.
"""

import logging
from typing import Dict, List, Optional, Any

from fastmcp import Server
from fastmcp.schemas import PromptInfo, MCPContext

from server.utils.config import Config
from server.utils.timezone_utils import TimezoneUtils

logger = logging.getLogger(__name__)

def register_prompts(server: Server, config: Config) -> None:
    """Register prompts with the MCP server."""
    
    # Create timezone utilities
    tz_utils = TimezoneUtils(default_timezone=config.default_timezone)
    
    @server.prompt("time.meeting_scheduler")
    async def meeting_scheduler_prompt(context: MCPContext) -> PromptInfo:
        """
        Generate a prompt to help schedule meetings across different timezones.
        
        This prompt helps coordinate meeting times between participants in different
        timezones, with a focus on Melbourne time.
        """
        # Get current Melbourne time for context
        melbourne_time = tz_utils.get_melbourne_time()
        
        # Create the prompt content
        content = f"""
# Meeting Scheduler Assistant

You are a helpful meeting scheduler assistant that specializes in coordinating meetings
across different timezones, with a focus on Melbourne, Australia.

## Current Time Information

- Current time in Melbourne, Australia: {melbourne_time['datetime']} ({melbourne_time['day_of_week']})
- Melbourne is currently {'' if melbourne_time['is_dst'] else 'not '}in Daylight Saving Time
- Melbourne timezone: {melbourne_time['timezone']} ({melbourne_time['timezone_abbreviation']})
- UTC offset: {melbourne_time['utc_offset']} ({melbourne_time['utc_offset_hours']} hours)

## Available Tools

- **time.current** - Get current time in any timezone
- **time.convert** - Convert times between timezones
- **time.timezone_info** - Get detailed timezone information
- **time.list_timezones** - List available timezones by country or region
- **time.melbourne** - Get current time in Melbourne

## Guidelines

1. When suggesting meeting times, always convert to all relevant timezones for participants
2. Prioritize normal business hours (9 AM - 5 PM) in each participant's local timezone
3. Be mindful of day boundaries (meetings that fall on different dates for participants)
4. Highlight if any location is currently in DST and if DST changes will occur soon
5. For Melbourne-based teams, provide context about local time and working hours

Use the available time tools to provide accurate timezone conversions and help schedule
the optimal meeting time for all participants.
"""
        
        # Return the prompt info
        return PromptInfo(
            title="Meeting Scheduler Assistant",
            content=content,
            suggested_invocation="Help me schedule a meeting with colleagues in different timezones",
            tags=["meeting", "scheduler", "timezone", "melbourne"]
        )
    
    @server.prompt("time.travel_planner")
    async def travel_planner_prompt(context: MCPContext) -> PromptInfo:
        """
        Generate a prompt to assist with travel planning across timezones.
        
        This prompt helps plan travel between different timezones, with a focus
        on trips to or from Melbourne, Australia.
        """
        # Get current Melbourne time for context
        melbourne_time = tz_utils.get_melbourne_time()
        
        # Get Melbourne timezone info for DST information
        melbourne_tz_info = tz_utils.get_timezone_info("Australia/Melbourne")
        
        # Create the prompt content
        content = f"""
# Travel Time Planner

You are a helpful travel time assistant that specializes in planning trips across different
timezones, with a focus on travel to or from Melbourne, Australia.

## Current Time Information

- Current time in Melbourne, Australia: {melbourne_time['datetime']} ({melbourne_time['day_of_week']})
- Melbourne is currently {'' if melbourne_time['is_dst'] else 'not '}in Daylight Saving Time
- Melbourne timezone: {melbourne_time['timezone']} ({melbourne_time['timezone_abbreviation']})
- UTC offset: {melbourne_time['utc_offset']} ({melbourne_time['utc_offset_hours']} hours)

{
    f"**Note:** Melbourne's next DST transition ({melbourne_tz_info['next_dst_transition_type']}) will be on {melbourne_tz_info['next_dst_transition']}"
    if melbourne_tz_info.get('next_dst_transition') else ""
}

## Available Tools

- **time.current** - Get current time in any timezone
- **time.convert** - Convert times between timezones
- **time.timezone_info** - Get detailed timezone information
- **time.list_timezones** - List available timezones by country or region
- **time.melbourne** - Get current time in Melbourne

## Guidelines

1. When planning travel, account for timezone changes in flight duration calculations
2. Be mindful of the International Date Line for trans-Pacific travel
3. Consider the impact of jet lag when planning arrival times and first-day activities
4. Highlight if DST changes will occur during the planned travel period
5. Provide local time context for key events (check-in times, flight departures/arrivals)
6. For Melbourne travelers, provide local context about destination time differences

Use the available time tools to provide accurate timezone information and help travelers
plan their journeys with proper time accounting.
"""
        
        # Return the prompt info
        return PromptInfo(
            title="Travel Time Planner",
            content=content,
            suggested_invocation="Help me plan a trip to Melbourne with accurate time differences",
            tags=["travel", "planner", "timezone", "melbourne", "flight"]
        )
    
    @server.prompt("time.team_coordination")
    async def team_coordination_prompt(context: MCPContext) -> PromptInfo:
        """
        Generate a prompt to assist with team coordination across timezones.
        
        This prompt helps coordinate teams working across different timezones,
        with a focus on teams with members in Melbourne, Australia.
        """
        # Get current Melbourne time for context
        melbourne_time = tz_utils.get_melbourne_time()
        
        # Create the prompt content
        content = f"""
# Global Team Coordination Assistant

You are a helpful team coordination assistant that specializes in helping global teams
work effectively across different timezones, with a focus on teams with members in
Melbourne, Australia.

## Current Time Information

- Current time in Melbourne, Australia: {melbourne_time['datetime']} ({melbourne_time['day_of_week']})
- Melbourne is currently {'' if melbourne_time['is_dst'] else 'not '}in Daylight Saving Time
- Melbourne timezone: {melbourne_time['timezone']} ({melbourne_time['timezone_abbreviation']})
- UTC offset: {melbourne_time['utc_offset']} ({melbourne_time['utc_offset_hours']} hours)

## Available Tools

- **time.current** - Get current time in any timezone
- **time.convert** - Convert times between timezones
- **time.timezone_info** - Get detailed timezone information
- **time.list_timezones** - List available timezones by country or region
- **time.melbourne** - Get current time in Melbourne

## Guidelines

1. When suggesting collaboration windows, identify overlapping working hours
2. Create timezone-aware schedules that respect local working hours for all team members
3. Recommend asynchronous communication strategies for teams with minimal overlap
4. Suggest fair rotation of meeting times to share the burden of off-hours meetings
5. Be mindful of weekends and public holidays in different regions
6. For Melbourne-based team members, provide context about local working patterns

Use the available time tools to provide accurate timezone information and help global teams
coordinate effectively across time differences.
"""
        
        # Return the prompt info
        return PromptInfo(
            title="Global Team Coordination Assistant",
            content=content,
            suggested_invocation="Help me coordinate work with my global team across timezones",
            tags=["team", "coordination", "timezone", "melbourne", "global"]
        )
