# 🚀 n8n 기반 로컬 RAG 시스템 구축 가이드

## 📋 목차
1. [시스템 아키텍처](#시스템-아키텍처)
2. [빠른 시작](#빠른-시작)
3. [워크플로우 구성](#워크플로우-구성)
4. [API 사용법](#api-사용법)
5. [프로덕션 배포](#프로덕션-배포)
6. [문제해결](#문제해결)

## 🏗️ 시스템 아키텍처

이 시스템은 FastAPI 기반 RAG를 n8n 시각적 워크플로우로 전환한 현대적인 아키텍처입니다:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   클라이언트     │───▶│  n8n Webhook     │───▶│ 임베딩 서비스    │
│   (HTTP POST)   │    │  (API Gateway)   │    │ (BGE-M3 모델)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   응답 스트리밍  │◀───│  Ollama LLM      │◀───│  Qdrant 벡터DB   │
│                 │    │  (llama3.2)      │    │  (검색 결과)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 핵심 구성 요소
- **n8n**: 시각적 워크플로우 오케스트레이터 (FastAPI 대체)
- **Qdrant**: 벡터 데이터베이스 (컨텍스트 저장)
- **Ollama**: 로컬 LLM 서버 (llama3.2 모델)
- **텍스트 임베딩 서비스**: Hugging Face BGE-M3 모델
- **PostgreSQL**: n8n 메타데이터 저장

## 🚀 빠른 시작

### 1단계: 환경 설정

`.env` 파일을 생성하세요:
```bash
# PostgreSQL 설정
POSTGRES_USER=n8n_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=n8n_db

# n8n 보안 설정
N8N_ENCRYPTION_KEY=your-very-long-encryption-key-here
N8N_USER_MANAGEMENT_JWT_SECRET=your-jwt-secret-here

# 선택사항: Hugging Face 토큰 (프라이빗 모델용)
HUGGING_FACE_HUB_TOKEN=your_hf_token_here
```

### 2단계: 시스템 실행

```bash
# 전체 RAG 스택 시작
docker compose up -d

# 로그 확인
docker compose logs -f n8n
docker compose logs -f ollama
docker compose logs -f embedding-service
```

### 3단계: 서비스 확인

```bash
# n8n 웹 인터페이스
http://localhost:5678

# Qdrant 대시보드
http://localhost:6333/dashboard

# 임베딩 서비스 상태
curl http://localhost:8080/health
```

### 4단계: 초기 설정

1. **n8n 계정 생성**: http://localhost:5678에서 관리자 계정 생성
2. **Ollama 모델 다운로드**:
   ```bash
   docker exec ollama ollama pull llama3.2
   docker exec ollama ollama pull nomic-embed-text  # 백업용
   ```
3. **Qdrant 컬렉션 생성**: indexing-workflow.json로 코드베이스 인덱싱 실행

## 🔧 워크플로우 구성

### 인덱싱 워크플로우 (기존)
`indexing-workflow.json` - 코드베이스를 벡터 데이터베이스에 저장

### RAG 쿼리 워크플로우 (신규)
`rag-query-workflow.json` - 실시간 질의응답 API

#### 주요 노드 구성:

1. **RAG Chat Webhook**
   - 엔드포인트: `POST /webhook/rag-chat`
   - 스트리밍 응답 지원

2. **Get Query Embedding**
   - 사용자 질문을 벡터로 변환
   - BGE-M3 모델 사용

3. **Vector Search**
   - Qdrant에서 유사한 코드 검색
   - 상위 3개 결과 반환

4. **Construct RAG Prompt**
   - 검색된 컨텍스트와 질문 결합
   - 프롬프트 템플릿 적용

5. **Generate Response**
   - Ollama로 최종 답변 생성
   - 실시간 스트리밍

#### 오류 처리 노드:
- **Check Embedding Success**: 임베딩 실패 감지
- **Check Search Results**: 검색 결과 없음 처리
- **Error Response 노드들**: 적절한 오류 메시지 반환

### 워크플로우 임포트

```bash
# n8n에 워크플로우 임포트
curl -X POST http://localhost:5678/api/v1/workflows/import \
  -H "Content-Type: application/json" \
  -d @rag-query-workflow.json

# 또는 n8n UI에서 Import → JSON 파일 업로드
```

## 📡 API 사용법

### RAG 쿼리 API

**엔드포인트**: `POST http://localhost:5678/webhook/rag-chat`

**요청 예시**:
```bash
curl -X POST http://localhost:5678/webhook/rag-chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Swift에서 ReactorKit 패턴은 어떻게 구현하나요?"
  }'
```

**스트리밍 응답**:
```bash
# 스트리밍으로 실시간 응답 받기
curl -X POST http://localhost:5678/webhook/rag-chat \
  -H "Content-Type: application/json" \
  -d '{"query": "MVVM과 ReactorKit의 차이점은?"}' \
  --no-buffer
```

**JavaScript 클라이언트**:
```javascript
async function queryRAG(question) {
  const response = await fetch('http://localhost:5678/webhook/rag-chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: question })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    console.log(chunk); // 실시간 응답 스트림
  }
}
```

### 오류 응답

**임베딩 실패**:
```json
{
  "error": "Embedding service failed",
  "message": "Unable to generate embeddings for your query"
}
```

**검색 결과 없음**:
```json
{
  "message": "질문에 대한 관련 정보를 찾을 수 없습니다.",
  "suggestion": "Try rephrasing your question or asking about a different topic"
}
```

## 🔒 프로덕션 배포

### 보안 설정

#### 1. 웹훅 인증 추가
RAG Chat Webhook 노드 설정에서:
- Authentication 탭 활성화
- Header Auth 선택
- Header Name: `X-API-Key`
- Header Value: `your-secret-api-key`

사용 시:
```bash
curl -X POST http://localhost:5678/webhook/rag-chat \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "안전한 API 호출"}'
```

#### 2. 환경 변수 강화
```bash
# 프로덕션 .env
N8N_ENCRYPTION_KEY=very-long-256-bit-encryption-key
N8N_USER_MANAGEMENT_JWT_SECRET=secure-jwt-secret
N8N_SECURE_COOKIE=true
WEBHOOK_URL=https://your-domain.com/
N8N_PROTOCOL=https
N8N_HOST=your-domain.com
```

### 확장성 및 성능

#### 1. 리소스 제한 설정
```yaml
# docker-compose.prod.yml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 4G
          cpus: '2'

  embedding-service:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
```

#### 2. 고가용성 설정
```yaml
# 다중 인스턴스 배포
services:
  n8n:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

## 🔧 문제해결

### 일반적인 문제들

#### 1. Python 코드 노드 실행 안됨
**증상**: "Code in Python (Beta)" 노드 실행 실패
**해결책**:
```bash
# Task Runners가 활성화되었는지 확인
docker logs n8n | grep "runners"

# Python 환경 확인
docker exec n8n-python-runner python3 --version
```

#### 2. 임베딩 서비스 연결 실패
**증상**: "Get Query Embedding" 노드에서 연결 오류
**해결책**:
```bash
# 서비스 상태 확인
docker compose ps embedding-service

# 네트워크 연결 테스트
docker exec n8n curl http://embedding-service:80/health
```

#### 3. Qdrant 컬렉션 없음
**증상**: "Vector Search" 노드에서 컬렉션 not found 오류
**해결책**:
```bash
# 컬렉션 생성 확인
curl http://localhost:6333/collections

# indexing-workflow.json 실행으로 컬렉션 생성
```

#### 4. Ollama 모델 로딩 실패
**증상**: "Generate Response" 노드에서 모델 not found
**해결책**:
```bash
# 모델 다운로드 확인
docker exec ollama ollama list

# 수동 모델 다운로드
docker exec ollama ollama pull llama3.2
```

### 성능 최적화

#### 1. 임베딩 캐싱
Code 노드에 캐싱 로직 추가:
```javascript
// 임베딩 캐시 확인
const cache = $workflow.staticData.embeddingCache || {};
const queryHash = require('crypto').createHash('md5').update(query).digest('hex');

if (cache[queryHash]) {
  return { embedding: cache[queryHash] };
}
```

#### 2. 벡터 검색 튜닝
Qdrant 노드 설정:
- Limit: 5개 결과
- Score Threshold: 0.7 이상
- Exact Search: false (속도 우선)

### 디버깅 도구

#### 1. n8n 워크플로우 디버깅
- n8n UI에서 각 노드의 입력/출력 데이터 확인
- 실행 로그에서 오류 메시지 분석
- Test Workflow로 단계별 실행

#### 2. 로그 수집
```bash
# 전체 로그 모니터링
docker compose logs -f --tail=100

# 특정 서비스 로그
docker compose logs embedding-service
docker compose logs qdrant
docker compose logs ollama
```

---

## 🎯 다음 단계

1. **커스텀 프롬프트 템플릿**: Code 노드에서 도메인별 프롬프트 개선
2. **리랭킹 추가**: Vector Search 후 결과 재정렬 노드 추가
3. **멀티모달 지원**: 이미지/문서 임베딩 파이프라인 확장
4. **A/B 테스트**: 다른 LLM 모델들과 성능 비교
5. **Kubernetes 배포**: 대규모 프로덕션 환경으로 확장

이 가이드를 통해 FastAPI 기반의 전통적인 RAG 시스템을 n8n의 혁신적인 시각적 워크플로우로 성공적으로 전환할 수 있습니다! 🚀