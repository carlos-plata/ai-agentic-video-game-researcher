"""
Visualization Dashboard for UdaPlay Agent
Stand-out feature: Provides visualization of game collection data
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import argparse

# For ChromaDB connection
import chromadb

class VisualizationDashboard:
    """Dashboard for visualizing game collection statistics."""
    
    def __init__(self):
        """Initialize dashboard with ChromaDB connection."""
        # Connect to ChromaDB (in-memory or persistent)
        try:
            # Try persistent first
            self.client = chromadb.PersistentClient(path="./chromadb_storage")
        except:
            # Fall back to in-memory
            self.client = chromadb.Client()
        
        # Get collection
        try:
            self.collection = self.client.get_collection(name="udaplay_games")
        except:
            print("Collection not found. Please run Notebook 1 first to create the collection.")
            self.collection = None
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics from the game collection."""
        if not self.collection:
            return {}
        
        stats = {}
        try:
            # Get total count
            stats['total_games'] = self.collection.count()
            
            # Get all documents to analyze
            if stats['total_games'] > 0:
                all_docs = self.collection.get()
                
                # Analyze platforms
                platforms = {}
                years = {}
                genres = {}
                publishers = {}
                
                for metadata in all_docs['metadatas']:
                    # Count platforms
                    platform = metadata.get('Platform', 'Unknown')
                    platforms[platform] = platforms.get(platform, 0) + 1
                    
                    # Count years
                    year = metadata.get('YearOfRelease', 'Unknown')
                    years[str(year)] = years.get(str(year), 0) + 1
                    
                    # Count genres
                    genre = metadata.get('Genre', 'Unknown')
                    genres[genre] = genres.get(genre, 0) + 1
                    
                    # Count publishers
                    publisher = metadata.get('Publisher', 'Unknown')
                    publishers[publisher] = publishers.get(publisher, 0) + 1
                
                stats['platforms'] = dict(sorted(platforms.items(), key=lambda x: x[1], reverse=True))
                stats['years'] = dict(sorted(years.items()))
                stats['genres'] = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
                stats['publishers'] = dict(sorted(publishers.items(), key=lambda x: x[1], reverse=True)[:10])  # Top 10
                
        except Exception as e:
            print(f"Error getting collection stats: {e}")
        
        return stats
    
    def text_dashboard(self):
        """Display text-based dashboard in terminal."""
        print("\n" + "="*70)
        print("🎮 UDAPLAY GAME COLLECTION DASHBOARD")
        print("="*70)
        
        stats = self.get_collection_stats()
        
        if not stats:
            print("No data available. Please run the notebooks to load game data.")
            return
        
        # Display total games
        print(f"\n📊 COLLECTION STATISTICS")
        print("-"*40)
        print(f"Total Games: {stats.get('total_games', 0)}")
        
        # Display platforms
        platforms = stats.get('platforms', {})
        if platforms:
            print("\n🎮 GAMES BY PLATFORM")
            print("-"*40)
            for platform, count in list(platforms.items())[:10]:  # Top 10
                bar = "█" * int((count / max(platforms.values())) * 20)
                print(f"{platform:20s}: {bar:20s} {count:3d}")
        
        # Display genres
        genres = stats.get('genres', {})
        if genres:
            print("\n🎯 GAMES BY GENRE")
            print("-"*40)
            for genre, count in list(genres.items())[:10]:  # Top 10
                bar = "█" * int((count / max(genres.values())) * 20)
                print(f"{genre:20s}: {bar:20s} {count:3d}")
        
        # Display years
        years = stats.get('years', {})
        if years:
            print("\n📅 GAMES BY YEAR")
            print("-"*40)
            # Show last 10 years with data
            recent_years = sorted(years.items())[-10:]
            for year, count in recent_years:
                bar = "▓" * int((count / max(years.values())) * 20)
                print(f"{year:10s}: {bar:20s} {count:3d}")
        
        # Display top publishers
        publishers = stats.get('publishers', {})
        if publishers:
            print("\n🏢 TOP PUBLISHERS")
            print("-"*40)
            for publisher, count in list(publishers.items())[:5]:  # Top 5
                print(f"  • {publisher}: {count} games")
        
        # Summary statistics
        if years:
            year_values = [int(y) for y in years.keys() if y != 'Unknown' and y.isdigit()]
            if year_values:
                print("\n📈 SUMMARY")
                print("-"*40)
                print(f"  Year Range: {min(year_values)} - {max(year_values)}")
                print(f"  Unique Platforms: {len(platforms)}")
                print(f"  Unique Genres: {len(genres)}")
                print(f"  Unique Publishers: {len(stats.get('publishers', {}))}")
        
        print("\n" + "="*70)
        print("💡 This dashboard shows statistics from the ChromaDB game collection")
        print("="*70 + "\n")
    
    def test_search(self, query="racing games"):
        """Test the search functionality."""
        if not self.collection:
            print("Collection not available.")
            return
        
        print(f"\n🔍 Testing Search: '{query}'")
        print("-"*40)
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            
            if results and results['ids'][0]:
                print("Top 3 Results:")
                for i, metadata in enumerate(results['metadatas'][0], 1):
                    print(f"\n{i}. {metadata.get('Name', 'Unknown')}")
                    print(f"   Platform: {metadata.get('Platform', 'Unknown')}")
                    print(f"   Year: {metadata.get('YearOfRelease', 'Unknown')}")
                    print(f"   Genre: {metadata.get('Genre', 'Unknown')}")
            else:
                print("No results found.")
                
        except Exception as e:
            print(f"Search error: {e}")


def main():
    """Main entry point for dashboard."""
    parser = argparse.ArgumentParser(description="UdaPlay Visualization Dashboard")
    parser.add_argument(
        '--search',
        type=str,
        help='Test search with a query'
    )
    
    args = parser.parse_args()
    
    dashboard = VisualizationDashboard()
    
    # Display main dashboard
    dashboard.text_dashboard()
    
    # Run search test if requested
    if args.search:
        dashboard.test_search(args.search)
    else:
        # Show example search
        dashboard.test_search()


if __name__ == "__main__":
    main()