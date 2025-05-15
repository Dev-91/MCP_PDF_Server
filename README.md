# MCP PDF Server

MCP PDF Server는 PDF 파일을 효율적으로 관리할 수 있는 Model Context Protocol(MCP) 기반 서버입니다.

이 프로젝트는 임베디드 개발자인 제가, Cursor와 같은 AI 코딩 도구에서 PDF 데이터시트 문서를 직접 읽고 요약하거나, 질의응답 등으로 개발 업무를 더 편리하게 할 수 있도록 만들었습니다. 즉, AI가 PDF 데이터시트의 내용을 빠르게 파악하고, 필요한 정보를 바로 제공해줄 수 있도록 지원하는 것이 주된 목적입니다.

이 프로젝트는 두 개의 주요 컴포넌트로 구성되어 있습니다:

- **manager_server**: FastAPI 기반의 웹페이지로, 사용자가 웹 UI를 통해 PDF 파일을 업로드하거나 다운로드하고, 파일 목록을 조회·관리할 수 있는 기능을 제공합니다. 또한 외부 시스템과의 연동을 위한 RESTful API도 함께 제공합니다.
- **mcp_server**: manager_server에서 관리하는 PDF 파일을 기반으로, 파일명 검색 및 텍스트 추출 기능을 제공합니다. 추출된 텍스트는 MCP 프로토콜을 통해 외부 시스템(예: Cursor 등)과 연동할 수 있습니다.

주요 기능:
- PDF 텍스트 추출 (로컬 파일 및 URL 지원)
- 파일명 기반 PDF 검색
- PDF 목록 조회 및 관리
- PDF 파일 웹 업로드/다운로드 지원
- RESTful API 및 웹 서비스 제공
- MCP 프로토콜을 통한 외부 시스템(Curator, Cursor 등) 연동

RESTful API와 웹 UI를 통해 외부 시스템과 쉽게 연동할 수 있으며, Docker와 로컬 환경 모두에서 손쉽게 배포 및 운영이 가능합니다. 데이터시트·논문·계약서 등 다양한 PDF 문서의 자동화된 관리와 검색에 적합합니다.

## 주요 특징

- 로컬 PDF 파일 및 URL로 접근 가능한 PDF에서 텍스트 추출
- `/app/datasheets` 하위의 PDF 파일 목록 제공
- 파일명으로 PDF 검색 기능 제공
- PyPDF2 기반의 안정적인 텍스트 추출 및 예외 처리
- FastMCP 기반의 표준화된 MCP 툴 제공

## 도커(Docker)로 실행하기

1. **이미지 빌드**
   ```bash
   docker build -t mcp-pdf-server:1.0.0 .
   ```

2. **컨테이너 실행**
   ```bash
   docker run -d \
     -v /호스트/경로/데이터:/app/datasheets \
     -p 5050:5050 \
     -p 5080:5080 \
     --name mcp-pdf-server \
     mcp-pdf-server:1.0.0
   ```
   - `/호스트/경로/데이터`에 PDF 파일을 넣으면 컨테이너 내부 `/app/datasheets`에서 접근할 수 있습니다.
   - 5050, 5080 포트가 사용됩니다.

3. **docker-compose 사용시**
    ```bash
    # docker-compose.yml의 /path/to/your/datasheets를 실제 PDF 폴더 경로로 수정하세요.
    docker-compose up -d --build
    ```

## 로컬(Python)에서 직접 실행하기

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **서버 실행**
   ```bash
   python mcp_server/mcp_pdf_server.py
   # 또는
   uvicorn manager_server.main:app --host 0.0.0.0 --port 5080
   ```

## MCP 툴(API) 설명

- **read_local_pdf**  
  로컬 PDF 파일 경로를 입력받아 텍스트를 추출합니다.

- **read_url_pdf**  
  PDF 파일의 URL을 입력받아 텍스트를 추출합니다.

- **server_pdf_list**  
  `/app/datasheets` 하위의 모든 PDF 파일 목록을 반환합니다.

- **server_pdf_search**  
  파일명을 입력받아 서버에 있는 PDF 파일을 검색하고, 해당 PDF의 텍스트를 추출합니다.

## 경로 안내

- PDF 데이터는 반드시 `/app/datasheets` 경로(도커 컨테이너 내부)에 위치해야 합니다.
- 도커 사용 시, 호스트의 PDF 폴더를 `/app/datasheets`로 마운트하세요.
- 소스코드는 `/app/mcp_server`에 위치합니다(컨테이너 내부 기준).

## 라이선스

Apache License 2.0  
저자: Dev91
