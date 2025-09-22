# 🎯 n8n 워크플로우 사용 가이드

## 📋 제공된 워크플로우 목록

### 1. 🔧 **setup-qdrant-collection.json**
**목적**: Qdrant 벡터 컬렉션 초기 설정
**사용 시기**: 최초 1회 실행 (시스템 설정 시)

**기능**:
- `codebase_collection` 컬렉션 존재 여부 확인
- 없으면 새로 생성 (384차원, Cosine 거리)
- 컬렉션 상태 정보 표시

**실행 순서**: 1번째

---

### 2. 📚 **indexing-workflow-improved.json**
**목적**: 코드베이스를 벡터 데이터베이스에 인덱싱
**사용 시기**: 새로운 코드베이스 추가 시 또는 업데이트 시

**기능**:
- Git 리포지토리 클론
- Swift/Kotlin 파일 검색 및 읽기
- 텍스트 청킹 (1000자 단위, 100자 오버랩)
- 임베딩 생성 및 Qdrant 저장
- 상세한 진행상황 로깅 및 오류 처리

**실행 순서**: 2번째

---

### 3. 💬 **rag-query-workflow-simple.json**
**목적**: 실시간 RAG 질의응답 API 제공
**사용 시기**: 인덱싱 완료 후 언제든지

**기능**:
- HTTP POST 웹훅으로 질문 수신
- 질문 임베딩 생성
- Qdrant에서 유사 코드 검색
- LLM으로 컨텍스트 기반 답변 생성
- JSON 응답 반환

**API 엔드포인트**: `POST /webhook/rag-chat`

---

## 🚀 설정 및 실행 가이드

### 1단계: 시스템 준비
```bash
# 모든 서비스 시작
docker compose up -d

# 서비스 상태 확인
docker compose ps

# 임베딩 서비스 준비 대기 (2-3분)
docker logs embedding_model_server -f
```

### 2단계: n8n 접속 및 계정 설정
```bash
# n8n 웹 인터페이스 접속
open http://localhost:5678

# 1. 관리자 계정 생성
# 2. 이메일/비밀번호 설정
```

### 3단계: 워크플로우 임포트
n8n UI에서 다음 순서로 워크플로우를 임포트:

#### 1️⃣ Qdrant 컬렉션 설정
```
1. 좌측 메뉴 → "Workflows" 클릭
2. "Import from file" 버튼 클릭
3. "setup-qdrant-collection.json" 파일 선택
4. "Save" 버튼 클릭
5. "Execute workflow" 버튼 클릭
```

#### 2️⃣ 인덱싱 워크플로우
```
1. "Import from file" → "indexing-workflow-improved.json"
2. "Save" 후 "Execute workflow" 클릭
3. 진행상황 모니터링 (5-10분 소요)
```

#### 3️⃣ RAG 쿼리 워크플로우
```
1. "Import from file" → "rag-query-workflow-simple.json"
2. "Save" 클릭 (자동 활성화됨)
```

### 4단계: API 테스트
```bash
# RAG API 테스트
curl -X POST http://localhost:5678/webhook/rag-chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Swift에서 ReactorKit 패턴을 어떻게 사용하나요?"
  }'

# 예상 응답
{
  "response": "ReactorKit은 반응형 단방향 아키텍처 패턴으로...",
  "context_count": 3,
  "query": "Swift에서 ReactorKit 패턴을 어떻게 사용하나요?"
}
```

---

## 🔍 워크플로우 상세 분석

### indexing-workflow-improved.json 주요 개선사항

#### ✅ 기존 LangChain 노드 제거
- ❌ `@n8n/n8n-nodes-langchain.textSplitterRecursiveCharacterTextSplitter`
- ❌ `@n8n/n8n-nodes-langchain.embeddingsOllama`
- ❌ `@n8n/n8n-nodes-langchain.vectorStoreQdrant`

#### ✅ 표준 노드로 대체
- ✅ `n8n-nodes-base.executeCommand` (Git 작업)
- ✅ `n8n-nodes-base.code` (텍스트 청킹, 로깅)
- ✅ `n8n-nodes-base.httpRequest` (임베딩, Qdrant)
- ✅ `n8n-nodes-base.if` (오류 처리)

#### ✅ 향상된 기능
- 📊 **상세한 진행상황 로깅**: 각 단계별 콘솔 출력
- 🔧 **견고한 오류 처리**: Git 클론 실패, 임베딩 실패 감지
- 📁 **향상된 파일 처리**: 재귀적 파일 검색, 타입별 분류
- 🧩 **지능형 청킹**: 파일 크기에 따른 적응형 분할
- 💾 **메타데이터 저장**: 파일 경로, 청크 인덱스, 타임스탬프

### rag-query-workflow-simple.json 특징

#### 🔗 완전한 HTTP 기반 아키텍처
```
웹훅 수신 → 임베딩 생성 → 벡터 검색 → 프롬프트 구성 → LLM 생성 → 응답 반환
```

#### 🛡️ 강화된 오류 처리
- **임베딩 실패**: 적절한 오류 메시지 반환
- **검색 결과 없음**: 사용자 안내 메시지
- **서비스 타임아웃**: 30초/120초 타임아웃 설정

#### 📊 응답 메타데이터
```json
{
  "response": "실제 답변 내용",
  "context_count": 3,
  "query": "원본 질문"
}
```

---

## 🔧 문제해결

### 임베딩 서비스 준비 확인
```bash
# 헬스체크
curl http://localhost:8080/health

# 정상 응답 예시
{
  "status": "healthy",
  "model": "all-MiniLM-L6-v2"
}
```

### Qdrant 컬렉션 상태 확인
```bash
# 컬렉션 목록
curl http://localhost:6333/collections

# 컬렉션 정보
curl http://localhost:6333/collections/codebase_collection
```

### 워크플로우 디버깅
1. **n8n UI**: 각 노드 클릭 → 입력/출력 데이터 확인
2. **실행 로그**: 워크플로우 실행 후 "Executions" 탭 확인
3. **콘솔 출력**: 각 Code 노드의 console.log 메시지 확인

### 일반적인 오류와 해결책

#### "embedding service not ready"
```bash
# 서비스 재시작
docker compose restart embedding-service

# 로그 확인
docker logs embedding_model_server -f
```

#### "collection not found"
```bash
# setup-qdrant-collection.json 워크플로우 재실행
```

#### "git clone failed"
```bash
# 네트워크 연결 확인
# 리포지토리 URL 확인
# /data/shared 폴더 권한 확인
docker exec n8n ls -la /data/shared
```

---

## 🎯 다음 단계

### 고급 기능 추가
1. **리랭킹 파이프라인**: 검색 결과 재정렬
2. **멀티모달 지원**: 이미지, 문서 임베딩
3. **A/B 테스트**: 다른 LLM 모델 비교
4. **캐싱 레이어**: 빈번한 질문 캐싱

### 프로덕션 최적화
1. **인증 추가**: API 키 기반 보안
2. **로드 밸런싱**: 다중 인스턴스 배포
3. **모니터링**: 성능 메트릭 수집
4. **백업**: 벡터 데이터베이스 정기 백업

이제 LangChain 의존성 없이 완전히 동작하는 n8n 기반 RAG 시스템을 사용할 수 있습니다! 🚀