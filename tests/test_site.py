"""Tests for the site generation module."""
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.resultathle.scraper import CompetitionHeader
from src.resultathle.site import render_site


def test_render_site_basic():
    """Test basic site rendering."""
    header = CompetitionHeader(
        name='Test Competition',
        location='Paris',
        date='01/01/2024',
        department='75',
        label='National'
    )
    
    results = pd.DataFrame({
        'Athlete': ['John DOE', 'Jane SMITH'],
        'FirstName': ['John', 'Jane'],
        'LastName': ['DOE', 'SMITH'],
        'Category': ['SEM', 'SEF'],
        'League': ['IDF', 'BFC'],
        'BirthYear': [1990, 1995],
        'Performance': ['N1', 'R3'],
        'DurationHMS': ['01:00:00', '01:05:00'],
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_dir = Path(tmpdir) / 'output'
        output_path = render_site(dest_dir, header, results)
        
        assert output_path.exists()
        assert output_path == dest_dir / 'index.html'
        
        # Read and check content
        html = output_path.read_text()
        assert 'Test Competition' in html
        assert 'Paris' in html
        assert '01/01/2024' in html
        assert '75' in html
        assert 'National' in html
        assert 'John DOE' in html
        assert 'Jane SMITH' in html


def test_render_site_minimal_header():
    """Test rendering with minimal header information."""
    header = CompetitionHeader(
        name='Simple Race',
        location='Lyon',
        date='15/03/2024',
        department=None,
        label=None
    )
    
    results = pd.DataFrame({
        'Athlete': ['Runner ONE'],
        'FirstName': ['Runner'],
        'LastName': ['ONE'],
        'Category': ['SEM'],
        'League': [''],
        'BirthYear': [2000],
        'Performance': [''],
        'DurationHMS': ['00:45:00'],
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_dir = Path(tmpdir)
        output_path = render_site(dest_dir, header, results)
        
        assert output_path.exists()
        html = output_path.read_text()
        assert 'Simple Race' in html
        assert 'Lyon' in html
        assert '15/03/2024' in html
        assert 'Runner ONE' in html


def test_render_site_creates_directory():
    """Test that render_site creates output directory if it doesn't exist."""
    header = CompetitionHeader(
        name='Test',
        location='Test',
        date='01/01/24',
        department=None,
        label=None
    )
    
    results = pd.DataFrame({
        'Athlete': ['Test ATHLETE'],
        'FirstName': ['Test'],
        'LastName': ['ATHLETE'],
        'Category': [None],
        'League': [''],
        'BirthYear': [None],
        'Performance': [''],
        'DurationHMS': ['01:00:00'],
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_dir = Path(tmpdir) / 'nested' / 'output'
        assert not dest_dir.exists()
        
        output_path = render_site(dest_dir, header, results)
        
        assert dest_dir.exists()
        assert output_path.exists()


def test_render_site_empty_results():
    """Test rendering with empty results."""
    header = CompetitionHeader(
        name='Empty Competition',
        location='Nowhere',
        date='01/01/24',
        department=None,
        label=None
    )
    
    results = pd.DataFrame({
        'Athlete': [],
        'FirstName': [],
        'LastName': [],
        'Category': [],
        'League': [],
        'BirthYear': [],
        'Performance': [],
        'DurationHMS': [],
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_dir = Path(tmpdir)
        output_path = render_site(dest_dir, header, results)
        
        assert output_path.exists()
        html = output_path.read_text()
        assert 'Empty Competition' in html
        # Should still have table structure even with no results
        assert '<table>' in html


def test_render_site_html_structure():
    """Test that rendered HTML has proper structure."""
    header = CompetitionHeader(
        name='Structure Test',
        location='Test City',
        date='01/01/24',
        department='99',
        label='Test Label'
    )
    
    results = pd.DataFrame({
        'Athlete': ['Test RUNNER'],
        'FirstName': ['Test'],
        'LastName': ['RUNNER'],
        'Category': ['SEM'],
        'League': ['TST'],
        'BirthYear': [2000],
        'Performance': ['N1'],
        'DurationHMS': ['01:23:45'],
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = render_site(Path(tmpdir), header, results)
        html = output_path.read_text()
        
        # Check for HTML structure
        assert '<!doctype html>' in html.lower()
        assert '<html' in html
        assert '<head>' in html
        assert '<body>' in html
        assert '<table>' in html
        assert '<thead>' in html
        assert '<tbody>' in html
        
        # Check for expected headers
        assert 'Athlete' in html
        assert 'Category' in html
        assert 'League' in html
        assert 'Performance' in html
        assert 'Finish time' in html
