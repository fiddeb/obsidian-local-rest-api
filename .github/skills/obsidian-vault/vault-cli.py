#!/usr/bin/env python3
"""
Vault CLI - A command-line tool for AI agents to interact with Obsidian vaults.

Usage:
    vault-cli search <query> [--max-results N] [--context-length N]
    vault-cli get <path> [--metadata-only] [--max-chars N]
    vault-cli list [<path>]
    vault-cli create <path> --content <content>
    vault-cli create <path> --stdin
    vault-cli create <path> --file <filepath>
    vault-cli append <path> --content <content>
    vault-cli append <path> --stdin
    vault-cli patch <path> --heading <target> --operation <op> --content <content>
    vault-cli patch <path> --frontmatter <field> --operation <op> --content <content>
    vault-cli patch <path> --block <ref> --operation <op> --content <content>
    vault-cli daily [--content <content>] [--date YYYY-MM-DD] [--period daily|weekly|monthly]
    vault-cli delete <path>

Environment:
    OBSIDIAN_API_KEY - Required. Your Obsidian Local REST API key.
    OBSIDIAN_API_URL - Optional. Default: https://127.0.0.1:27124
"""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


class VaultClient:
    """HTTP client for Obsidian Local REST API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        # Create SSL context that doesn't verify (for self-signed cert)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def _request(self, method: str, path: str, data: bytes = None, 
                 headers: dict = None, content_type: str = None) -> dict:
        """Make HTTP request to the API."""
        url = f"{self.base_url}{path}"
        
        req_headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        if headers:
            req_headers.update(headers)
        if content_type:
            req_headers['Content-Type'] = content_type
        
        request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        
        try:
            with urllib.request.urlopen(request, context=self.ssl_context) as response:
                content = response.read()
                if content:
                    # Try to parse as JSON
                    try:
                        return {'ok': True, 'data': json.loads(content.decode('utf-8'))}
                    except json.JSONDecodeError:
                        return {'ok': True, 'data': content.decode('utf-8')}
                return {'ok': True, 'data': None}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            try:
                error_data = json.loads(error_body)
                return {'ok': False, 'error': error_data.get('message', str(e)), 'code': e.code}
            except:
                return {'ok': False, 'error': str(e), 'code': e.code}
        except urllib.error.URLError as e:
            return {'ok': False, 'error': f"Connection failed: {e.reason}"}
    
    def search(self, query: str, context_length: int = 100) -> dict:
        """Search for notes matching query."""
        params = urllib.parse.urlencode({'query': query, 'contextLength': context_length})
        return self._request('POST', f'/search/simple/?{params}')
    
    def get_note(self, path: str, metadata_only: bool = False) -> dict:
        """Get note content and/or metadata."""
        encoded_path = urllib.parse.quote(path, safe='')
        headers = {'Accept': 'application/vnd.olrapi.note+json'}
        result = self._request('GET', f'/vault/{encoded_path}', headers=headers)
        
        if result['ok'] and metadata_only and isinstance(result['data'], dict):
            # Remove content for metadata-only requests
            result['data'].pop('content', None)
        
        return result
    
    def list_dir(self, path: str = '') -> dict:
        """List directory contents."""
        if path:
            encoded_path = urllib.parse.quote(path.rstrip('/'), safe='') + '/'
            return self._request('GET', f'/vault/{encoded_path}')
        return self._request('GET', '/vault/')
    
    def create_note(self, path: str, content: str) -> dict:
        """Create a new note."""
        encoded_path = urllib.parse.quote(path, safe='')
        return self._request('PUT', f'/vault/{encoded_path}', 
                           data=content.encode('utf-8'),
                           content_type='text/markdown')
    
    def append_note(self, path: str, content: str) -> dict:
        """Append content to a note."""
        encoded_path = urllib.parse.quote(path, safe='')
        return self._request('POST', f'/vault/{encoded_path}',
                           data=content.encode('utf-8'),
                           content_type='text/markdown')
    
    def patch_note(self, path: str, target_type: str, target: str, 
                   operation: str, content: str, content_type: str = 'text/markdown') -> dict:
        """Patch a note at a specific location."""
        encoded_path = urllib.parse.quote(path, safe='')
        headers = {
            'Operation': operation,
            'Target-Type': target_type,
            'Target': target,
        }
        return self._request('PATCH', f'/vault/{encoded_path}',
                           data=content.encode('utf-8'),
                           headers=headers,
                           content_type=content_type)
    
    def daily_append(self, content: str, period: str = 'daily', 
                     year: int = None, month: int = None, day: int = None) -> dict:
        """Append to a periodic note."""
        if year and month and day:
            path = f'/periodic/{period}/{year}/{month}/{day}/'
        else:
            path = f'/periodic/{period}/'
        
        return self._request('POST', path,
                           data=content.encode('utf-8'),
                           content_type='text/markdown')
    
    def delete_note(self, path: str) -> dict:
        """Delete a note."""
        encoded_path = urllib.parse.quote(path, safe='')
        return self._request('DELETE', f'/vault/{encoded_path}')


def main():
    parser = argparse.ArgumentParser(
        description='Vault CLI - Interact with Obsidian vaults via Local REST API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for notes')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--max-results', '-n', type=int, default=10,
                               help='Maximum number of results (default: 10)')
    search_parser.add_argument('--context-length', '-c', type=int, default=100,
                               help='Context length around matches (default: 100)')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get note content')
    get_parser.add_argument('path', help='Path to note')
    get_parser.add_argument('--metadata-only', '-m', action='store_true',
                           help='Return only metadata, not content')
    get_parser.add_argument('--max-chars', type=int,
                           help='Truncate content to N characters')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List directory contents')
    list_parser.add_argument('path', nargs='?', default='', help='Directory path')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new note')
    create_parser.add_argument('path', help='Path for new note')
    content_group = create_parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument('--content', '-c', help='Note content')
    content_group.add_argument('--stdin', action='store_true', help='Read content from stdin')
    content_group.add_argument('--file', '-f', help='Read content from file')
    
    # Append command
    append_parser = subparsers.add_parser('append', help='Append to a note')
    append_parser.add_argument('path', help='Path to note')
    append_content = append_parser.add_mutually_exclusive_group(required=True)
    append_content.add_argument('--content', '-c', help='Content to append')
    append_content.add_argument('--stdin', action='store_true', help='Read content from stdin')
    append_content.add_argument('--file', '-f', help='Read content from file')
    
    # Patch command
    patch_parser = subparsers.add_parser('patch', help='Patch note at specific location')
    patch_parser.add_argument('path', help='Path to note')
    target_group = patch_parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('--heading', help='Target heading (use :: for nested)')
    target_group.add_argument('--frontmatter', help='Target frontmatter field')
    target_group.add_argument('--block', help='Target block reference')
    patch_parser.add_argument('--operation', '-o', required=True,
                             choices=['append', 'prepend', 'replace'],
                             help='Patch operation')
    patch_content = patch_parser.add_mutually_exclusive_group(required=True)
    patch_content.add_argument('--content', '-c', help='Content to insert')
    patch_content.add_argument('--stdin', action='store_true', help='Read from stdin')
    patch_content.add_argument('--file', '-f', help='Read content from file')
    
    # Daily command
    daily_parser = subparsers.add_parser('daily', help='Append to periodic note')
    daily_parser.add_argument('--date', '-d', help='Date (YYYY-MM-DD), default: today')
    daily_parser.add_argument('--period', '-p', default='daily',
                             choices=['daily', 'weekly', 'monthly', 'quarterly', 'yearly'],
                             help='Period type (default: daily)')
    daily_content = daily_parser.add_mutually_exclusive_group(required=True)
    daily_content.add_argument('--content', '-c', help='Content to append')
    daily_content.add_argument('--stdin', action='store_true', help='Read from stdin')
    daily_content.add_argument('--file', '-f', help='Read content from file')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a note')
    delete_parser.add_argument('path', help='Path to note')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Get API key from environment
    api_key = os.environ.get('OBSIDIAN_API_KEY')
    if not api_key:
        print(json.dumps({'ok': False, 'error': 'OBSIDIAN_API_KEY environment variable not set'}))
        sys.exit(1)
    
    base_url = os.environ.get('OBSIDIAN_API_URL', 'https://127.0.0.1:27124')
    client = VaultClient(base_url, api_key)
    
    # Helper to get content from various sources
    def get_content(args_obj) -> str:
        if hasattr(args_obj, 'content') and args_obj.content:
            return args_obj.content
        if hasattr(args_obj, 'stdin') and args_obj.stdin:
            return sys.stdin.read()
        if hasattr(args_obj, 'file') and args_obj.file:
            with open(args_obj.file, 'r', encoding='utf-8') as f:
                return f.read()
        return ''
    
    # Execute command
    result = None
    
    if args.command == 'search':
        result = client.search(args.query, args.context_length)
        if result['ok'] and isinstance(result['data'], list):
            # Limit results
            result['data'] = result['data'][:args.max_results]
            # Simplify output for token efficiency
            simplified = []
            for item in result['data']:
                entry = {
                    'path': item.get('filename', ''),
                    'score': item.get('score', 0),
                }
                matches = item.get('matches', [])
                if matches:
                    entry['snippets'] = [m.get('context', '')[:200] for m in matches[:3]]
                simplified.append(entry)
            result['data'] = simplified
    
    elif args.command == 'get':
        result = client.get_note(args.path, args.metadata_only)
        if result['ok'] and args.max_chars and isinstance(result['data'], dict):
            content = result['data'].get('content', '')
            if len(content) > args.max_chars:
                result['data']['content'] = content[:args.max_chars] + '\n...[truncated]'
    
    elif args.command == 'list':
        result = client.list_dir(args.path)
    
    elif args.command == 'create':
        content = get_content(args)
        result = client.create_note(args.path, content)
        if result['ok']:
            result['data'] = {'created': args.path}
    
    elif args.command == 'append':
        content = get_content(args)
        result = client.append_note(args.path, content)
        if result['ok']:
            result['data'] = {'appended_to': args.path}
    
    elif args.command == 'patch':
        content = get_content(args)
        if args.heading:
            target_type, target = 'heading', args.heading
        elif args.frontmatter:
            target_type, target = 'frontmatter', args.frontmatter
        else:
            target_type, target = 'block', args.block
        
        # Use JSON content type for frontmatter
        content_type = 'application/json' if args.frontmatter else 'text/markdown'
        result = client.patch_note(args.path, target_type, target, 
                                  args.operation, content, content_type)
        if result['ok']:
            result['data'] = {'patched': args.path, 'target': target}
    
    elif args.command == 'daily':
        content = get_content(args)
        if args.date:
            try:
                dt = datetime.strptime(args.date, '%Y-%m-%d')
                result = client.daily_append(content, args.period, dt.year, dt.month, dt.day)
            except ValueError:
                result = {'ok': False, 'error': f'Invalid date format: {args.date}. Use YYYY-MM-DD'}
        else:
            result = client.daily_append(content, args.period)
        if result and result['ok']:
            result['data'] = {'appended_to': f'{args.period} note'}
    
    elif args.command == 'delete':
        result = client.delete_note(args.path)
        if result['ok']:
            result['data'] = {'deleted': args.path}
    
    # Output result as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result and result.get('ok') else 1)


if __name__ == '__main__':
    main()
