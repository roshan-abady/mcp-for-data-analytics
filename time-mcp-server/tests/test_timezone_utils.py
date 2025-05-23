"""
Tests for timezone utilities.
"""

import pytest
from datetime import datetime
import pytz

from server.utils.timezone_utils import TimezoneUtils
from server.utils.config import Config


class TestTimezoneUtils:
    """Test the TimezoneUtils class."""

    def setup_method(self):
        """Set up the test case."""
        self.config = Config()
        self.tz_utils = TimezoneUtils(default_timezone=self.config.default_timezone)

    def test_init_with_valid_timezone(self):
        """Test initialization with valid timezone."""
        tz_utils = TimezoneUtils(default_timezone="Australia/Melbourne")
        assert tz_utils.default_timezone == "Australia/Melbourne"

    def test_init_with_invalid_timezone(self):
        """Test initialization with invalid timezone."""
        with pytest.raises(ValueError):
            TimezoneUtils(default_timezone="Invalid/Timezone")

    def test_get_current_time(self):
        """Test getting current time."""
        result = self.tz_utils.get_current_time("Australia/Melbourne")
        
        # Check that all required fields are present
        assert "timezone" in result
        assert "datetime" in result
        assert "date" in result
        assert "time" in result
        assert "timestamp" in result
        assert "utc_offset" in result
        assert "utc_offset_hours" in result
        assert "is_dst" in result
        assert "day_of_week" in result
        assert "day_of_year" in result
        assert "week_of_year" in result
        assert "timezone_abbreviation" in result
        
        # Check that the timezone is correct
        assert result["timezone"] == "Australia/Melbourne"
        
        # Verify the timestamp is close to now
        now_timestamp = datetime.now().timestamp()
        assert abs(result["timestamp"] - now_timestamp) < 5  # Within 5 seconds

    def test_get_current_time_invalid_timezone(self):
        """Test getting current time with invalid timezone."""
        with pytest.raises(ValueError):
            self.tz_utils.get_current_time("Invalid/Timezone")

    def test_convert_time_same_timezone(self):
        """Test converting time in the same timezone."""
        result = self.tz_utils.convert_time(
            time_str="12:00",
            source_timezone="Australia/Melbourne",
            target_timezone="Australia/Melbourne"
        )
        
        # Check that the conversion happened
        assert "original" in result
        assert "converted" in result
        assert "time_difference_hours" in result
        
        # The time difference should be 0 for same timezone
        assert result["time_difference_hours"] == 0
        
        # The original and converted times should be the same
        assert result["original"]["datetime"] == result["converted"]["datetime"]

    def test_convert_time_different_timezone(self):
        """Test converting time between different timezones."""
        result = self.tz_utils.convert_time(
            time_str="12:00",
            source_timezone="Australia/Melbourne",
            target_timezone="America/New_York"
        )
        
        # Check that the conversion happened
        assert "original" in result
        assert "converted" in result
        assert "time_difference_hours" in result
        
        # The time difference should not be 0 for different timezones
        assert result["time_difference_hours"] != 0
        
        # The original and converted times should be different
        assert result["original"]["datetime"] != result["converted"]["datetime"]

    def test_convert_time_invalid_time_str(self):
        """Test converting with invalid time string."""
        with pytest.raises(ValueError):
            self.tz_utils.convert_time(
                time_str="not a time",
                source_timezone="Australia/Melbourne",
                target_timezone="America/New_York"
            )

    def test_get_timezone_info(self):
        """Test getting timezone info."""
        result = self.tz_utils.get_timezone_info("Australia/Melbourne")
        
        # Check that all required fields are present
        assert "timezone" in result
        assert "country" in result
        assert "utc_offset" in result
        assert "utc_offset_hours" in result
        assert "is_dst" in result
        assert "current_time" in result
        
        # Check that the timezone is correct
        assert result["timezone"] == "Australia/Melbourne"
        assert result["country"] == "Australia"

    def test_get_timezone_info_invalid_timezone(self):
        """Test getting timezone info with invalid timezone."""
        with pytest.raises(ValueError):
            self.tz_utils.get_timezone_info("Invalid/Timezone")

    def test_list_timezones(self):
        """Test listing timezones."""
        result = self.tz_utils.list_timezones()
        
        # Should have multiple timezones
        assert len(result) > 0
        
        # Check that each timezone has the required fields
        for tz in result:
            assert "timezone" in tz
            assert "utc_offset" in tz
            assert "utc_offset_hours" in tz
            assert "is_dst" in tz
            assert "abbreviation" in tz

    def test_list_timezones_with_country(self):
        """Test listing timezones for a specific country."""
        result = self.tz_utils.list_timezones(country_code="AU")
        
        # Should have multiple Australian timezones
        assert len(result) > 0
        
        # All timezones should start with Australia/
        for tz in result:
            assert tz["timezone"].startswith("Australia/")

    def test_get_melbourne_time(self):
        """Test getting Melbourne time."""
        result = self.tz_utils.get_melbourne_time()
        
        # Check that all required fields are present
        assert "timezone" in result
        assert "datetime" in result
        assert "date" in result
        assert "time" in result
        assert "timestamp" in result
        assert "utc_offset" in result
        assert "utc_offset_hours" in result
        assert "is_dst" in result
        assert "day_of_week" in result
        assert "day_of_year" in result
        assert "week_of_year" in result
        assert "timezone_abbreviation" in result
        
        # Check that the timezone is correct
        assert result["timezone"] == "Australia/Melbourne"
