# n8n GUI를 활용한 코드 분석 AI 시스템 사용 가이드

## 🚀 시스템 구축 완료!

Docker 환경과 필요한 모든 서비스가 설정되었습니다. 이제 n8n GUI를 통해 코드 분석 AI 시스템을 사용할 수 있습니다.

## 📋 구축된 구성 요소

1. **Docker 컨테이너 실행 중**
   - n8n (워크플로우 자동화)
   - Ollama (AI 모델 실행)
   - Qdrant (벡터 데이터베이스)
   - PostgreSQL (n8n 데이터 저장)

2. **AI 모델 다운로드 완료**
   - `llama3`: 답변 생성용 언어 모델
   - `nomic-embed-text`: 코드 검색용 임베딩 모델

## 🔧 n8n 워크플로우 설정하기

### 1. n8n 대시보드 접속
브라우저에서 http://localhost:5678 에 접속합니다.
- 처음 접속 시 계정 생성이 필요합니다.
- 이메일과 비밀번호를 입력하여 계정을 만드세요.

### 2. Credentials 설정

#### Ollama 연결 설정
1. 좌측 메뉴에서 **Credentials** 클릭
2. **Add credential** → **Ollama** 검색
3. 다음과 같이 설정:
   - Name: `My Local Ollama`
   - Base URL: `http://ollama:11434`
4. **Save** 클릭

#### Qdrant 연결 설정
1. **Add credential** → **Qdrant** 검색
2. 다음과 같이 설정:
   - Name: `My Local Qdrant`
   - URL: `http://qdrant:6333`
3. **Save** 클릭

### 3. 인덱싱 워크플로우 Import

1. n8n 대시보드에서 **Workflows** → **Add workflow** → **Import from file**
2. `/Users/gunter/Desktop/musinsa/self-hosted-ai-starter-kit/indexing-workflow.json` 파일 선택
3. Import 후 각 노드를 클릭하여 Credentials 확인:
   - **Embeddings Ollama** 노드: `My Local Ollama` 선택
   - **Qdrant Vector Store** 노드: `My Local Qdrant` 선택

### 4. 쿼리 워크플로우 Import

1. 동일한 방법으로 `query-workflow.json` 파일 Import
2. 각 노드의 Credentials 설정 확인
3. **Webhook** 노드를 클릭하여 URL 복사 (예: `http://localhost:5678/webhook/query`)

## 🏃‍♂️ 워크플로우 실행하기

### 1단계: 코드 인덱싱 (처음 한 번만)

1. **인덱싱 워크플로우** 열기
2. **Git Clone** 노드에서 분석할 GitHub 저장소 URL 입력
   - 예: `https://github.com/ReactorKit/ReactorKit`
3. **Read Files** 노드에서 파일 확장자 설정
   - Swift 프로젝트: `.swift`
   - Kotlin 프로젝트: `.kt`
   - 둘 다: `.swift,.kt`
4. 우측 상단 **Execute Workflow** 버튼 클릭
5. 모든 노드가 녹색으로 변하면 성공!

### 2단계: 쿼리 워크플로우 활성화

1. **쿼리 워크플로우** 열기
2. 우측 상단의 **Inactive** 토글을 클릭하여 **Active**로 변경
3. Webhook URL이 활성화됨

## 🔗 IDE 연결 (Cursor/VS Code)

### ngrok 터널 생성
```bash
# 터미널에서 실행
ngrok http 5678
```

출력된 URL을 복사합니다 (예: `https://abc123.ngrok-free.app`)

### Cursor IDE 설정

1. **Settings** → **Models** → **Add Model**
2. **Override OpenAI Base URL** 활성화
3. Base URL 입력:
   ```
   https://abc123.ngrok-free.app/webhook/query
   ```
4. 다음 정보 입력 (임의값):
   - API Key: `dummy-key`
   - Model Name: `local-ai`
5. **Save** 클릭

## 💬 사용 예시

Cursor IDE의 채팅창에서:
```
Q: "ReactorKit에서 Action이 어떻게 처리되나요?"
A: ReactorKit에서 Action은 다음과 같이 처리됩니다...

Q: "State 변경 시 View는 어떻게 업데이트되나요?"
A: View는 reactor.state를 구독하여 자동으로 업데이트됩니다...
```

## 🛠️ 문제 해결

### 컨테이너 상태 확인
```bash
docker ps
```

### 로그 확인
```bash
# n8n 로그
docker logs n8n

# Ollama 로그
docker logs ollama

# Qdrant 로그
docker logs qdrant
```

### 서비스 재시작
```bash
docker compose down
docker compose --profile cpu up -d
```

## 📈 성능 최적화 팁

1. **청크 크기 조정**: Text Splitter 노드에서
   - 코드 파일이 크면: Chunk Size를 2000으로 증가
   - 더 정확한 검색을 원하면: Chunk Size를 500으로 감소

2. **검색 결과 수 조정**: Qdrant Search 노드에서
   - Limit을 10으로 증가하면 더 많은 컨텍스트 제공
   - Limit을 3으로 감소하면 더 빠른 응답

3. **온도 조정**: Ollama Chat 노드에서
   - Temperature 0.3: 일관된 답변
   - Temperature 0.7: 창의적인 답변

## 🎉 축하합니다!

이제 코딩 한 줄 없이 강력한 AI 코드 분석 시스템을 구축했습니다!
질문이 있으시면 언제든지 물어보세요.