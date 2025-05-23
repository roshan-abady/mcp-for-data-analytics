#!/usr/bin/env python3
"""
Example client for the Time MCP Server.

This script demonstrates how to use the Time MCP Server tools and resources
from a client application.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any

from fastmcp import Client


async def get_current_time(client: Client, timezone: str = None) -> None:
    """Get current time using the time.current tool."""
    print(f"\n=== Getting current time {f'for {timezone}' if timezone else 'for default timezone'} ===\n")
    
    params = {}
    if timezone:
        params["timezone"] = timezone
    
    result = await client.run_tool("time.current", params)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print time information
    print(f"Current time in {result['timezone']}:")
    print(f"  Date and time: {result['datetime']} ({result['day_of_week']})")
    print(f"  Timezone: {result['timezone']} ({result['timezone_abbreviation']})")
    print(f"  UTC offset: {result['utc_offset']} ({result['utc_offset_hours']} hours)")
    print(f"  DST active: {'Yes' if result['is_dst'] else 'No'}")
    print(f"  Week of year: {result['week_of_year']}, Day of year: {result['day_of_year']}")


async def convert_time(client: Client, time_str: str, source_tz: str = None, target_tz: str = None) -> None:
    """Convert time between timezones using the time.convert tool."""
    print(f"\n=== Converting time: {time_str} ===\n")
    
    params = {"time_str": time_str}
    if source_tz:
        params["source_timezone"] = source_tz
    if target_tz:
        params["target_timezone"] = target_tz
    
    result = await client.run_tool("time.convert", params)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print conversion information
    print(f"Time conversion result:")
    print(f"  Original: {result['original']['datetime']} in {result['original']['timezone']} ({result['original']['timezone_abbreviation']})")
    print(f"  Converted: {result['converted']['datetime']} in {result['converted']['timezone']} ({result['converted']['timezone_abbreviation']})")
    print(f"  Time difference: {result['time_difference_hours']} hours")
    print(f"  DST status - Original: {'Active' if result['original']['is_dst'] else 'Inactive'}, "
          f"Converted: {'Active' if result['converted']['is_dst'] else 'Inactive'}")


async def get_timezone_info(client: Client, timezone: str = None) -> None:
    """Get timezone information using the time.timezone_info tool."""
    print(f"\n=== Getting timezone info {f'for {timezone}' if timezone else 'for default timezone'} ===\n")
    
    params = {}
    if timezone:
        params["timezone"] = timezone
    
    result = await client.run_tool("time.timezone_info", params)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print timezone information
    print(f"Timezone information for {result['timezone']}:")
    print(f"  Country: {result['country'] or 'Unknown'}")
    print(f"  Current time: {result['current_time']}")
    print(f"  UTC offset: {result['utc_offset']} ({result['utc_offset_hours']} hours)")
    print(f"  DST active: {'Yes' if result['is_dst'] else 'No'}")
    
    if result['is_dst']:
        print(f"  DST abbreviation: {result['dst_abbreviation']}")
    else:
        print(f"  Standard abbreviation: {result['standard_abbreviation']}")
    
    if result['next_dst_transition']:
        print(f"  Next DST transition: {result['next_dst_transition']} ({result['next_dst_transition_type']})")
    else:
        print("  No upcoming DST transitions")


async def list_timezones(client: Client, country_code: str = None, region: str = None) -> None:
    """List timezones using the time.list_timezones tool."""
    print(f"\n=== Listing timezones {f'for country {country_code}' if country_code else ''} "
          f"{f'in region {region}' if region else ''} ===\n")
    
    params = {}
    if country_code:
        params["country_code"] = country_code
    if region:
        params["region"] = region
    
    result = await client.run_tool("time.list_timezones", params)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print timezone list
    print(f"Found {result['count']} timezones:")
    
    if result['filter_country']:
        print(f"  Country filter: {result['filter_country']}")
    if result['filter_region']:
        print(f"  Region filter: {result['filter_region']}")
    
    print("\nTimezones:")
    for tz in result['timezones']:
        dst_status = "DST" if tz['is_dst'] else "STD"
        print(f"  {tz['timezone']} - {tz['utc_offset']} ({tz['utc_offset_hours']} hours) - {tz['abbreviation']} ({dst_status})")


async def get_melbourne_time(client: Client) -> None:
    """Get Melbourne time using the time.melbourne tool."""
    print("\n=== Getting Melbourne time ===\n")
    
    result = await client.run_tool("time.melbourne", {})
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print Melbourne time information
    print(f"Current time in Melbourne, Australia:")
    print(f"  Date and time: {result['datetime']} ({result['day_of_week']})")
    print(f"  Timezone: {result['timezone']} ({result['timezone_abbreviation']})")
    print(f"  UTC offset: {result['utc_offset']} ({result['utc_offset_hours']} hours)")
    print(f"  DST active: {'Yes' if result['is_dst'] else 'No'}")


async def access_time_resource(client: Client, resource_uri: str) -> None:
    """Access a time resource using the provided URI."""
    print(f"\n=== Accessing time resource: {resource_uri} ===\n")
    
    try:
        # Fetch the resource
        resource = await client.get_resource(resource_uri)
        
        if not resource:
            print(f"Resource not found: {resource_uri}")
            return
        
        # Parse and display the resource content
        content = json.loads(resource.content)
        metadata = resource.metadata
        
        print(f"Resource: {resource_uri}")
        print(f"Content type: {resource.content_type}")
        
        if metadata:
            print("\nMetadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        
        print("\nContent:")
        print(json.dumps(content, indent=2))
        
    except Exception as e:
        print(f"Error accessing resource: {e}")


async def main():
    """Main entry point for the example client."""
    parser = argparse.ArgumentParser(description="Time MCP Server Example Client")
    parser.add_argument("--action", type=str, required=True, 
                       choices=["current", "convert", "timezone", "list", "melbourne", "resource"],
                       help="Action to perform")
    parser.add_argument("--timezone", type=str, help="Timezone")
    parser.add_argument("--time", type=str, help="Time string for conversion")
    parser.add_argument("--source", type=str, help="Source timezone for conversion")
    parser.add_argument("--target", type=str, help="Target timezone for conversion")
    parser.add_argument("--country", type=str, help="Country code for timezone listing")
    parser.add_argument("--region", type=str, help="Region for timezone listing")
    parser.add_argument("--resource", type=str, help="Resource URI to access")
    args = parser.parse_args()
    
    # Create MCP client
    client = Client()
    
    try:
        # Connect to the server
        await client.connect()
        
        # Perform the requested action
        if args.action == "current":
            await get_current_time(client, args.timezone)
        elif args.action == "convert":
            if not args.time:
                print("Error: --time is required for conversion")
                return
            await convert_time(client, args.time, args.source, args.target)
        elif args.action == "timezone":
            await get_timezone_info(client, args.timezone)
        elif args.action == "list":
            await list_timezones(client, args.country, args.region)
        elif args.action == "melbourne":
            await get_melbourne_time(client)
        elif args.action == "resource":
            if not args.resource:
                print("Error: --resource is required")
                return
            await access_time_resource(client, args.resource)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect from the server
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
