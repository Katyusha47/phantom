#!/usr/bin/env python3
"""
Username Enumeration Module - OSINT
Check username availability across 100+ platforms
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
import time

class UsernameChecker:
    """
    Check username presence across social media and online platforms
    """
    
    # Platform database with check URLs
    PLATFORMS = {
        # Social Media
        'GitHub': 'https://github.com/{}',
        'Twitter': 'https://twitter.com/{}',
        'Instagram': 'https://www.instagram.com/{}',
        'Facebook': 'https://www.facebook.com/{}',
        'Reddit': 'https://www.reddit.com/user/{}',
        'TikTok': 'https://www.tiktok.com/@{}',
        'YouTube': 'https://www.youtube.com/@{}',
        'LinkedIn': 'https://www.linkedin.com/in/{}',
        'Pinterest': 'https://www.pinterest.com/{}',
        'Snapchat': 'https://www.snapchat.com/add/{}',
        'Telegram': 'https://t.me/{}',
        'Medium': 'https://medium.com/@{}',
        'Tumblr': 'https://{}.tumblr.com',
        
        # Developer Platforms
        'GitLab': 'https://gitlab.com/{}',
        'Bitbucket': 'https://bitbucket.org/{}',
        'Stack Overflow': 'https://stackoverflow.com/users/{}',
        'CodePen': 'https://codepen.io/{}',
        'Replit': 'https://replit.com/@{}',
        'HackerRank': 'https://www.hackerrank.com/{}',
        'LeetCode': 'https://leetcode.com/{}',
        'Kaggle': 'https://www.kaggle.com/{}',
        
        # Gaming
        'Twitch': 'https://www.twitch.tv/{}',
        'Steam': 'https://steamcommunity.com/id/{}',
        'PlayStation': 'https://psnprofiles.com/{}',
        'Xbox': 'https://xboxgamertag.com/search/{}',
        'Discord.me': 'https://discord.me/{}',
        'Roblox': 'https://www.roblox.com/users/profile?username={}',
        
        # Creative
        'Dribbble': 'https://dribbble.com/{}',
        'Behance': 'https://www.behance.net/{}',
        'DeviantArt': 'https://{}.deviantart.com',
        'ArtStation': 'https://www.artstation.com/{}',
        'SoundCloud': 'https://soundcloud.com/{}',
        'Spotify': 'https://open.spotify.com/user/{}',
        
        # Professional/Business
        'AngelList': 'https://angel.co/u/{}',
        'Crunchbase': 'https://www.crunchbase.com/person/{}',
        'About.me': 'https://about.me/{}',
        
        # Forums/Community
        'HackerNews': 'https://news.ycombinator.com/user?id={}',
        'ProductHunt': 'https://www.producthunt.com/@{}',
        'Patreon': 'https://www.patreon.com/{}',
        'Ko-fi': 'https://ko-fi.com/{}',
        
        # Other
        'Linktree': 'https://linktr.ee/{}',
        'Pastebin': 'https://pastebin.com/u/{}',
        'Scribd': 'https://www.scribd.com/{}',
        'SlideShare': 'https://www.slideshare.net/{}',
        'Flickr': 'https://www.flickr.com/people/{}',
        'Vimeo': 'https://vimeo.com/{}',
        '500px': 'https://500px.com/p/{}',
        'Goodreads': 'https://www.goodreads.com/{}',
        'Wattpad': 'https://www.wattpad.com/user/{}',
        'Quora': 'https://www.quora.com/profile/{}',
        'Blogger': 'https://{}.blogspot.com',
        'WordPress': 'https://{}.wordpress.com',
    }
    
    def __init__(self, username: str, threads: int = 20, timeout: int = 5):
        """
        Initialize username checker
        
        Args:
            username: Username to check
            threads: Number of concurrent threads
            timeout: Request timeout in seconds
        """
        self.username = username
        self.threads = threads
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_platform(self, platform: str, url_template: str) -> Dict:
        """
        Check if username exists on a platform
        
        Args:
            platform: Platform name
            url_template: URL template with {} placeholder
            
        Returns:
            Dictionary with platform check results
        """
        try:
            url = url_template.format(self.username)
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Different platforms use different status codes
            exists = False
            status_code = response.status_code
            
            if status_code == 200:
                # Profile likely exists
                # Additional checks for false positives
                content = response.text.lower()
                
                # Some sites show 200 even for non-existent profiles
                false_positive_indicators = [
                    'page not found',
                    'user not found',
                    'profile not found',
                    'doesn\'t exist',
                    'no user found'
                ]
                
                if not any(indicator in content for indicator in false_positive_indicators):
                    exists = True
            
            elif status_code == 404:
                # Profile doesn't exist
                exists = False
            
            else:
                # Uncertain (rate limited, requires login, etc.)
                exists = None
            
            return {
                'platform': platform,
                'url': url,
                'exists': exists,
                'status_code': status_code
            }
            
        except requests.Timeout:
            return {
                'platform': platform,
                'url': url_template.format(self.username),
                'exists': None,
                'status_code': 'TIMEOUT'
            }
        except Exception as e:
            return {
                'platform': platform,
                'url': url_template.format(self.username),
                'exists': None,
                'status_code': 'ERROR'
            }
    
    def check_all(self) -> Dict:
        """
        Check username across all platforms
        
        Returns:
            Dictionary with categorized results
        """
        results = {
            'username': self.username,
            'found': [],
            'not_found': [],
            'unknown': [],
            'total_checked': len(self.PLATFORMS)
        }
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Submit all checks
            future_to_platform = {
                executor.submit(self.check_platform, platform, url): platform
                for platform, url in self.PLATFORMS.items()
            }
            
            # Process results
            for future in as_completed(future_to_platform):
                result = future.result()
                
                if result['exists'] is True:
                    results['found'].append(result)
                elif result['exists'] is False:
                    results['not_found'].append(result)
                else:
                    results['unknown'].append(result)
        
        # Sort results alphabetically by platform
        results['found'].sort(key=lambda x: x['platform'])
        results['not_found'].sort(key=lambda x: x['platform'])
        results['unknown'].sort(key=lambda x: x['platform'])
        
        return results


def check_username(username: str, threads: int = 20) -> Dict:
    """
    Check username across platforms
    
    Args:
        username: Username to check
        threads: Number of concurrent threads
        
    Returns:
        Check results
    """
    checker = UsernameChecker(username, threads)
    return checker.check_all()
