"""
Tests for ITGlue Pagination Handler
"""

from unittest.mock import Mock, patch
import pytest

from itglue.pagination import (
    PaginationInfo,
    PaginatedResponse,
    PaginationHandler,
)
from itglue.exceptions import ITGlueAPIError


class TestPaginationInfo:
    """Test pagination info functionality."""

    def test_pagination_info_initialization(self):
        """Test pagination info initialization."""
        meta = {
            "current-page": 2,
            "next-page": 3,
            "prev-page": 1,
            "total-pages": 5,
            "total-count": 100,
        }

        pagination = PaginationInfo(meta)

        assert pagination.current_page == 2
        assert pagination.next_page == 3
        assert pagination.prev_page == 1
        assert pagination.total_pages == 5
        assert pagination.total_count == 100

    def test_pagination_info_defaults(self):
        """Test pagination info with minimal meta data."""
        meta = {}

        pagination = PaginationInfo(meta)

        assert pagination.current_page == 1
        assert pagination.next_page is None
        assert pagination.prev_page is None
        assert pagination.total_pages == 1
        assert pagination.total_count == 0

    def test_has_next_true(self):
        """Test has_next when next page exists."""
        meta = {"next-page": 2}
        pagination = PaginationInfo(meta)

        assert pagination.has_next is True

    def test_has_next_false(self):
        """Test has_next when no next page."""
        meta = {}
        pagination = PaginationInfo(meta)

        assert pagination.has_next is False

    def test_has_prev_true(self):
        """Test has_prev when previous page exists."""
        meta = {"prev-page": 1}
        pagination = PaginationInfo(meta)

        assert pagination.has_prev is True

    def test_has_prev_false(self):
        """Test has_prev when no previous page."""
        meta = {}
        pagination = PaginationInfo(meta)

        assert pagination.has_prev is False

    def test_is_first_page(self):
        """Test is_first_page property."""
        meta = {"current-page": 1}
        pagination = PaginationInfo(meta)

        assert pagination.is_first_page is True

        meta = {"current-page": 2}
        pagination = PaginationInfo(meta)

        assert pagination.is_first_page is False

    def test_is_last_page(self):
        """Test is_last_page property."""
        meta = {"current-page": 5, "total-pages": 5}
        pagination = PaginationInfo(meta)

        assert pagination.is_last_page is True

        meta = {"current-page": 3, "total-pages": 5}
        pagination = PaginationInfo(meta)

        assert pagination.is_last_page is False

    def test_repr(self):
        """Test string representation."""
        meta = {"current-page": 2, "total-pages": 5, "total-count": 100}
        pagination = PaginationInfo(meta)

        repr_str = repr(pagination)
        assert "current=2" in repr_str
        assert "total=5" in repr_str
        assert "count=100" in repr_str


class TestPaginatedResponse:
    """Test paginated response functionality."""

    def test_paginated_response_initialization(self):
        """Test paginated response initialization."""
        data = [{"id": "1", "type": "organizations"}]
        meta = {"current-page": 1, "total-count": 1}
        links = {"self": "http://example.com/organizations"}

        response = PaginatedResponse(data, meta, links)

        assert response.data == data
        assert response.meta == meta
        assert response.links == links
        assert isinstance(response.pagination, PaginationInfo)

    def test_len(self):
        """Test length of paginated response."""
        data = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        meta = {}

        response = PaginatedResponse(data, meta)

        assert len(response) == 3

    def test_iter(self):
        """Test iteration over paginated response."""
        data = [{"id": "1"}, {"id": "2"}]
        meta = {}

        response = PaginatedResponse(data, meta)

        items = list(response)
        assert items == data

    def test_getitem(self):
        """Test item access by index."""
        data = [{"id": "1"}, {"id": "2"}]
        meta = {}

        response = PaginatedResponse(data, meta)

        assert response[0] == {"id": "1"}
        assert response[1] == {"id": "2"}

    def test_repr(self):
        """Test string representation."""
        data = [{"id": "1"}, {"id": "2"}]
        meta = {"current-page": 1}

        response = PaginatedResponse(data, meta)

        repr_str = repr(response)
        assert "items=2" in repr_str
        assert "pagination=" in repr_str


class TestPaginationHandler:
    """Test pagination handler functionality."""

    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client."""
        mock_client = Mock()
        return mock_client

    @pytest.fixture
    def pagination_handler(self, mock_http_client):
        """Create pagination handler instance."""
        return PaginationHandler(mock_http_client)

    def test_parse_response_list_data(self, pagination_handler):
        """Test parsing response with list data."""
        response_data = {
            "data": [{"id": "1", "type": "organizations"}],
            "meta": {"current-page": 1, "total-count": 1},
            "links": {"self": "http://example.com/organizations"},
        }

        result = pagination_handler.parse_response(response_data)

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert result.data[0]["id"] == "1"
        assert result.pagination.current_page == 1

    def test_parse_response_single_item(self, pagination_handler):
        """Test parsing response with single item (not a list)."""
        response_data = {
            "data": {"id": "1", "type": "organizations"},
            "meta": {"current-page": 1},
        }

        result = pagination_handler.parse_response(response_data)

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert result.data[0]["id"] == "1"

    def test_parse_response_empty_data(self, pagination_handler):
        """Test parsing response with empty data."""
        response_data = {"data": [], "meta": {"current-page": 1, "total-count": 0}}

        result = pagination_handler.parse_response(response_data)

        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 0

    def test_parse_response_invalid_format(self, pagination_handler):
        """Test parsing invalid response format."""
        with pytest.raises(
            ITGlueAPIError, match="Invalid response format: expected dict"
        ):
            pagination_handler.parse_response("invalid")

    def test_get_page(self, pagination_handler, mock_http_client):
        """Test getting a specific page."""
        mock_response = {
            "data": [{"id": "1"}],
            "meta": {"current-page": 2, "total-pages": 5},
        }
        mock_http_client.get.return_value = mock_response

        result = pagination_handler.get_page("/organizations", page=2, page_size=10)

        assert isinstance(result, PaginatedResponse)
        assert result.pagination.current_page == 2

        # Check that HTTP client was called with correct parameters
        mock_http_client.get.assert_called_once_with(
            "/organizations", params={"page[number]": 2, "page[size]": 10}
        )

    def test_get_page_without_page_size(self, pagination_handler, mock_http_client):
        """Test getting a page without specifying page size."""
        mock_response = {"data": [{"id": "1"}], "meta": {"current-page": 1}}
        mock_http_client.get.return_value = mock_response

        pagination_handler.get_page("/organizations")

        # Should not include page[size] parameter
        mock_http_client.get.assert_called_once_with(
            "/organizations", params={"page[number]": 1}
        )

    def test_get_next_page(self, pagination_handler, mock_http_client):
        """Test getting next page."""
        # Current response
        current_data = [{"id": "1"}]
        current_meta = {"current-page": 1, "next-page": 2}
        current_response = PaginatedResponse(current_data, current_meta)

        # Next page response
        next_response = {
            "data": [{"id": "2"}],
            "meta": {"current-page": 2, "prev-page": 1},
        }
        mock_http_client.get.return_value = next_response

        result = pagination_handler.get_next_page(current_response, "/organizations")

        assert isinstance(result, PaginatedResponse)
        assert result.pagination.current_page == 2

        mock_http_client.get.assert_called_once_with(
            "/organizations", params={"page[number]": 2}
        )

    def test_get_next_page_none_when_no_next(
        self, pagination_handler, mock_http_client
    ):
        """Test getting next page when none exists."""
        current_data = [{"id": "1"}]
        current_meta = {"current-page": 1}  # No next-page
        current_response = PaginatedResponse(current_data, current_meta)

        result = pagination_handler.get_next_page(current_response, "/organizations")

        assert result is None
        mock_http_client.get.assert_not_called()

    def test_get_prev_page(self, pagination_handler, mock_http_client):
        """Test getting previous page."""
        # Current response
        current_data = [{"id": "2"}]
        current_meta = {"current-page": 2, "prev-page": 1}
        current_response = PaginatedResponse(current_data, current_meta)

        # Previous page response
        prev_response = {
            "data": [{"id": "1"}],
            "meta": {"current-page": 1, "next-page": 2},
        }
        mock_http_client.get.return_value = prev_response

        result = pagination_handler.get_prev_page(current_response, "/organizations")

        assert isinstance(result, PaginatedResponse)
        assert result.pagination.current_page == 1

        mock_http_client.get.assert_called_once_with(
            "/organizations", params={"page[number]": 1}
        )

    def test_get_all_pages(self, pagination_handler, mock_http_client):
        """Test getting all pages."""
        # Mock responses for multiple pages
        responses = [
            {
                "data": [{"id": "1"}, {"id": "2"}],
                "meta": {"current-page": 1, "next-page": 2, "total-pages": 3},
            },
            {
                "data": [{"id": "3"}, {"id": "4"}],
                "meta": {
                    "current-page": 2,
                    "next-page": 3,
                    "prev-page": 1,
                    "total-pages": 3,
                },
            },
            {
                "data": [{"id": "5"}],
                "meta": {"current-page": 3, "prev-page": 2, "total-pages": 3},
            },
        ]
        mock_http_client.get.side_effect = responses

        result = pagination_handler.get_all_pages("/organizations", page_size=2)

        # Should return all items from all pages
        assert len(result) == 5
        assert result[0]["id"] == "1"
        assert result[4]["id"] == "5"

        # Should have made 3 API calls
        assert mock_http_client.get.call_count == 3

    def test_get_all_pages_with_max_pages(self, pagination_handler, mock_http_client):
        """Test getting pages with max_pages limit."""
        responses = [
            {
                "data": [{"id": "1"}],
                "meta": {"current-page": 1, "next-page": 2, "total-pages": 5},
            },
            {
                "data": [{"id": "2"}],
                "meta": {"current-page": 2, "next-page": 3, "total-pages": 5},
            },
        ]
        mock_http_client.get.side_effect = responses

        result = pagination_handler.get_all_pages("/organizations", max_pages=2)

        # Should only return items from first 2 pages
        assert len(result) == 2
        assert mock_http_client.get.call_count == 2

    def test_iterate_pages(self, pagination_handler, mock_http_client):
        """Test iterating over pages."""
        responses = [
            {"data": [{"id": "1"}], "meta": {"current-page": 1, "next-page": 2}},
            {"data": [{"id": "2"}], "meta": {"current-page": 2}},
        ]
        mock_http_client.get.side_effect = responses

        pages = list(pagination_handler.iterate_pages("/organizations"))

        assert len(pages) == 2
        assert all(isinstance(page, PaginatedResponse) for page in pages)
        assert pages[0].pagination.current_page == 1
        assert pages[1].pagination.current_page == 2

    def test_iterate_items(self, pagination_handler, mock_http_client):
        """Test iterating over individual items."""
        responses = [
            {
                "data": [{"id": "1"}, {"id": "2"}],
                "meta": {"current-page": 1, "next-page": 2},
            },
            {"data": [{"id": "3"}], "meta": {"current-page": 2}},
        ]
        mock_http_client.get.side_effect = responses

        items = list(pagination_handler.iterate_items("/organizations"))

        assert len(items) == 3
        assert items[0]["id"] == "1"
        assert items[1]["id"] == "2"
        assert items[2]["id"] == "3"
