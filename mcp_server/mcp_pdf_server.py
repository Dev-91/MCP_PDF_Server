import os
import io
import sys
import logging

from typing import Dict, Any

import PyPDF2
import requests
from mcp.server.fastmcp import FastMCP

# 컬러 로그를 위한 colorlog 패키지 사용
# colorlog가 설치되어 있지 않다면: pip install colorlog
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

mcp = FastMCP("mcp-pdf-server", debug=True)

def extract_text_from_pdf(pdf, filename=None) -> str:
    try:
        if filename:
            logger.info(f"Extracting text from PDF: {filename}")
        reader = PyPDF2.PdfReader(pdf)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        if filename:
            logger.info(f"Successfully extracted text from PDF: {filename}")
        return text.strip()
    except Exception as e:
        if filename:
            logger.error(f"Failed to extract text from PDF '{filename}': {str(e)}")
        else:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

@mcp.tool()
async def server_pdf_search(filename: str) -> Dict[str, Any]:
    try:
        datasheets_dir = "/app/datasheets"
        for root, dirs, files in os.walk(datasheets_dir):
            if filename in files:
                file_path = os.path.join(root, filename)
                logger.info(f"Found PDF file: {file_path}")
                with open(file_path, 'rb') as file:
                    text = extract_text_from_pdf(file, filename=filename)
                return {
                    "success": True,
                    "data": {
                        "text": text
                    }
                }
        logger.error(f"PDF file not found: {filename}")
        return {
            "success": False,
            "error": f"PDF file not found: {filename}"
        }
    except Exception as e:
        logger.error(f"Error in server_pdf_search for '{filename}': {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def server_pdf_list() -> Dict[str, Any]:
    try:
        datasheets_dir = "/app/datasheets"
        pdf_files = []
        for root, dirs, files in os.walk(datasheets_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        return {
            "success": True,
            "data": {
                "pdf_files": pdf_files
            }
        }
    except Exception as e:
        logger.error(str(e))
        return {
            "success": False,
            "error": str(e)
        }
    
@mcp.tool()
async def read_local_pdf(path: str) -> Dict[str, Any]:
    try:
        logger.info(f"Reading local PDF: {path}")
        with open(path, 'rb') as file:
            text = extract_text_from_pdf(file, filename=path)
            return {
                "success": True,
                "data": {
                    "text": text
                }
            }
    except FileNotFoundError:
        logger.error(f"PDF file not found: {path}")
        return {
            "success": False,
            "error": f"PDF file not found: {path}"
        }
    except Exception as e:
        logger.error(f"Error reading local PDF '{path}': {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def read_url_pdf(url: str) -> Dict[str, Any]:
    try:
        logger.info(f"Fetching PDF from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
        text = extract_text_from_pdf(pdf_file, filename=url)
        return {
            "success": True,
            "data": {
                "text": text
            }
        }
    except requests.RequestException as e:
        logger.error(f"Failed to fetch PDF from URL: {url} - {str(e)}")
        return {
            "success": False,
            "error": f"Failed to fetch PDF from URL: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error reading PDF from URL '{url}': {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    
if __name__ == "__main__":
    try:
        logger.info(f"Run MCP PDF server")
        mcp.run(transport="sse")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise
