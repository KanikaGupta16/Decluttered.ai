"""
Web Client for Decluttered.ai API
Python client library for interacting with the web API
Can be used for testing or as a reference for frontend implementation
"""

import aiohttp
import asyncio
import json
from typing import List, Dict, Any, Optional
import time
from pathlib import Path

class DeclutteredAIClient:
    """Client for interacting with Decluttered.ai Web API"""

    def __init__(self, api_url: str = "http://localhost:8006"):
        self.api_url = api_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        async with self.session.get(f"{self.api_url}/health") as response:
            response.raise_for_status()
            return await response.json()

    async def upload_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Upload files for processing"""
        data = aiohttp.FormData()

        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(path, 'rb') as f:
                data.add_field('files',
                             f,
                             filename=path.name,
                             content_type=self._get_content_type(path.suffix))

        async with self.session.post(f"{self.api_url}/upload", data=data) as response:
            response.raise_for_status()
            return await response.json()

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get processing session status"""
        async with self.session.get(f"{self.api_url}/session/{session_id}") as response:
            response.raise_for_status()
            return await response.json()

    async def get_session_results(self, session_id: str) -> Dict[str, Any]:
        """Get detailed processing results"""
        async with self.session.get(f"{self.api_url}/session/{session_id}/results") as response:
            response.raise_for_status()
            return await response.json()

    async def download_cropped_object(self, filename: str, save_path: str) -> bool:
        """Download a cropped object image"""
        async with self.session.get(f"{self.api_url}/download/cropped/{filename}") as response:
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)

            return True

    async def list_sessions(self) -> Dict[str, Any]:
        """List all processing sessions"""
        async with self.session.get(f"{self.api_url}/sessions") as response:
            response.raise_for_status()
            return await response.json()

    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a processing session"""
        async with self.session.delete(f"{self.api_url}/session/{session_id}") as response:
            response.raise_for_status()
            return await response.json()

    async def wait_for_completion(self, session_id: str, timeout: int = 300, poll_interval: int = 5) -> Dict[str, Any]:
        """Wait for processing to complete"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = await self.get_session_status(session_id)

            if status['status'] == 'completed':
                return await self.get_session_results(session_id)
            elif status['status'] == 'failed':
                raise Exception(f"Processing failed: {status.get('error_message', 'Unknown error')}")

            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Processing timeout after {timeout} seconds")

    def _get_content_type(self, suffix: str) -> str:
        """Get content type for file extension"""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.webm': 'video/webm'
        }
        return content_types.get(suffix.lower(), 'application/octet-stream')

# Example usage functions
async def process_files_example(file_paths: List[str]):
    """Example: Process files and wait for results"""
    async with DeclutteredAIClient() as client:
        # Check API health
        health = await client.health_check()
        print(f"API Status: {health['api_status']}")

        # Upload files
        print(f"Uploading {len(file_paths)} files...")
        upload_result = await client.upload_files(file_paths)
        session_id = upload_result['session_id']
        print(f"Session ID: {session_id}")

        # Wait for completion
        print("Waiting for processing to complete...")
        results = await client.wait_for_completion(session_id)

        print(f"Processing completed!")
        print(f"Analysis Report: {results['analysis_report'][:200]}...")
        print(f"Cropped Objects: {len(results['cropped_objects'])}")

        # Download cropped objects
        for obj in results['cropped_objects']:
            print(f"Cropped object available: {obj['filename']}")

        return results

async def monitor_session_example(session_id: str):
    """Example: Monitor an existing session"""
    async with DeclutteredAIClient() as client:
        while True:
            status = await client.get_session_status(session_id)
            print(f"Status: {status['status']}")

            if status['status'] in ['completed', 'failed']:
                break

            await asyncio.sleep(2)

if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        files = sys.argv[1:]
        print(f"Processing files: {files}")
        asyncio.run(process_files_example(files))
    else:
        print("Usage: python web_client.py <file1> <file2> ...")
        print("Example: python web_client.py test_captures/test_frame_*.jpg")