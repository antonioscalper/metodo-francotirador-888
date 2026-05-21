#!/usr/bin/env python3
import os
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class AssetDownloader(HTMLParser):
    def __init__(self, base_url, save_dir):
        super().__init__()
        self.base_url = base_url
        self.save_dir = save_dir
        self.assets_dir = os.path.join(save_dir, 'assets')
        os.makedirs(self.assets_dir, exist_ok=True)
        self.links = []
        self.styles = []
        self.scripts = []
        self.images = []
        self.fonts = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'link':
            href = attrs_dict.get('href', '')
            if href and not href.startswith('data:'):
                self.links.append(href)
        elif tag == 'script':
            src = attrs_dict.get('src', '')
            if src:
                self.scripts.append(src)
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            if src and not src.startswith('data:'):
                self.images.append(src)
                
    def download_asset(self, url, subdir=''):
        if not url or url.startswith('data:') or url.startswith('javascript:'):
            return None
            
        try:
            parsed = urllib.parse.urlparse(url)
            filename = parsed.path.split('/')[-1] or f'asset_{hash(url)}'
            
            if subdir:
                asset_subdir = os.path.join(self.assets_dir, subdir)
                os.makedirs(asset_subdir, exist_ok=True)
                filepath = os.path.join(asset_subdir, filename)
            else:
                filepath = os.path.join(self.assets_dir, filename)
            
            # Avoid duplicates
            if os.path.exists(filepath):
                return filepath
                
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
            
            with open(filepath, 'wb') as f:
                f.write(content)
                
            print(f"Downloaded: {url[:80]} -> {filepath}")
            return filepath
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return None

def download_page(url, save_dir):
    html_path = os.path.join(save_dir, 'index.html')
    
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    else:
        print("index.html not found in save directory")
        return
    
    downloader = AssetDownloader(url, save_dir)
    
    # Find all assets in HTML
    href_pattern = re.compile(r'href="([^"]+)"')
    src_pattern = re.compile(r'src="([^"]+)"')
    url_pattern = re.compile(r'url\("?([^"]+)"?\)')
    
    assets_to_download = []
    
    # Extract from href
    for match in href_pattern.finditer(html_content):
        assets_to_download.append(match.group(1))
    
    # Extract from src
    for match in src_pattern.finditer(html_content):
        assets_to_download.append(match.group(1))
    
    # Extract from CSS url()
    for match in url_pattern.finditer(html_content):
        assets_to_download.append(match.group(1))
    
    # Download images from content.app-sources.com
    img_pattern = re.compile(r'https://content\.app-sources\.com/s/\d+/uploads/[^"\']+')
    for match in img_pattern.finditer(html_content):
        assets_to_download.append(match.group(0))
    
    # Dedupe
    assets_to_download = list(set(assets_to_download))
    
    # Download each asset
    for asset_url in assets_to_download:
        if asset_url and not asset_url.startswith('data:'):
            downloader.download_asset(asset_url)
    
    # Download fonts
    fonts_url = 'https://content.app-sources.com/s/65745510315481012/uploads/Fuentes/'
    font_files = ['good_times_rg-1321967.ttf', 'AaronHand-1788763.ttf', 'Stencil_Std_Bold-3797873.ttf']
    for font in font_files:
        downloader.download_asset(fonts_url + font, 'fonts')
    
    # Download logo
    logo_url = 'https://content.app-sources.com/s/65745510315481012/uploads/Logos/logo_scalper_negro_2023-6905641.png'
    downloader.download_asset(logo_url, 'images')
    
    logo_url_white = 'https://content.app-sources.com/s/65745510315481012/uploads/Logos/logo_scalper_2023-6905641.png'
    downloader.download_asset(logo_url_white, 'images')
    
    print(f"\nDownload complete. Assets saved to: {downloader.assets_dir}")

if __name__ == '__main__':
    import sys
    save_dir = '/Users/albertogala/Library/CloudStorage/Dropbox/Scalper 2026/metodo-francotirador-888'
    download_page('https://antonioscalper.com/metodo-francotirador-888', save_dir)