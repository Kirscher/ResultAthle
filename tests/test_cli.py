"""Tests for the CLI module."""
import argparse
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.resultathle.cli import build_arg_parser, main, _write_csv, _write_json
from src.resultathle.scraper import CompetitionHeader


def test_build_arg_parser():
    """Test that argument parser is built correctly."""
    parser = build_arg_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    
    # Test with valid arguments
    args = parser.parse_args(['http://example.com', '5'])
    assert args.url == 'http://example.com'
    assert args.pages == 5
    assert args.out == Path('output/results.csv')
    assert args.json is None
    
    # Test with optional arguments
    args = parser.parse_args([
        'http://example.com', '3',
        '--out', 'custom.csv',
        '--json', 'custom.json'
    ])
    assert args.url == 'http://example.com'
    assert args.pages == 3
    assert args.out == Path('custom.csv')
    assert args.json == Path('custom.json')


def test_write_csv():
    """Test CSV writing functionality."""
    df = pd.DataFrame({
        'Athlete': ['John DOE', 'Jane SMITH'],
        'DurationSeconds': [3600, 3700]
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / 'test.csv'
        _write_csv(output_path, df)
        
        assert output_path.exists()
        
        # Read back and verify
        df_read = pd.read_csv(output_path)
        assert len(df_read) == 2
        assert list(df_read.columns) == ['Athlete', 'DurationSeconds']


def test_write_json():
    """Test JSON writing functionality."""
    header = CompetitionHeader(
        name='Test Competition',
        location='Paris',
        date='01/01/2024',
        department='75',
        label='National'
    )
    df = pd.DataFrame({
        'Athlete': ['John DOE'],
        'DurationSeconds': [3600]
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / 'test.json'
        _write_json(output_path, header, df)
        
        assert output_path.exists()
        
        # Read back and verify
        import json
        with open(output_path) as f:
            data = json.load(f)
        
        assert 'header' in data
        assert 'results' in data
        assert data['header']['name'] == 'Test Competition'
        assert data['header']['location'] == 'Paris'
        assert len(data['results']) == 1


@patch('src.resultathle.cli.scrape_competition')
def test_main_csv_only(mock_scrape):
    """Test main function with CSV output only."""
    # Mock the scraper
    mock_header = CompetitionHeader(
        name='Test',
        location='Paris',
        date='01/01/2024',
        department='75',
        label=None
    )
    mock_df = pd.DataFrame({
        'Athlete': ['Test ATHLETE'],
        'DurationSeconds': [3600]
    })
    mock_scrape.return_value = (mock_header, mock_df)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / 'results.csv'
        argv = ['http://example.com', '1', '--out', str(output_path)]
        
        result = main(argv)
        
        assert result == 0
        assert output_path.exists()
        mock_scrape.assert_called_once_with('http://example.com', 1)


@patch('src.resultathle.cli.scrape_competition')
def test_main_with_json(mock_scrape):
    """Test main function with both CSV and JSON output."""
    mock_header = CompetitionHeader(
        name='Test',
        location='Paris',
        date='01/01/2024',
        department='75',
        label='National'
    )
    mock_df = pd.DataFrame({
        'Athlete': ['Test ATHLETE'],
        'DurationSeconds': [3600]
    })
    mock_scrape.return_value = (mock_header, mock_df)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / 'results.csv'
        json_path = Path(tmpdir) / 'results.json'
        argv = [
            'http://example.com', '2',
            '--out', str(csv_path),
            '--json', str(json_path)
        ]
        
        result = main(argv)
        
        assert result == 0
        assert csv_path.exists()
        assert json_path.exists()
        mock_scrape.assert_called_once_with('http://example.com', 2)


def test_main_creates_output_directories():
    """Test that main creates parent directories if needed."""
    with patch('src.resultathle.cli.scrape_competition') as mock_scrape:
        mock_header = CompetitionHeader(
            name='Test',
            location='Paris',
            date='01/01/2024',
            department=None,
            label=None
        )
        mock_df = pd.DataFrame({'Athlete': ['Test']})
        mock_scrape.return_value = (mock_header, mock_df)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'nested' / 'dir' / 'results.csv'
            argv = ['http://example.com', '1', '--out', str(output_path)]
            
            result = main(argv)
            
            assert result == 0
            assert output_path.parent.exists()
            assert output_path.exists()
