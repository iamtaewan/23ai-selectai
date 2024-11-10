import streamlit as st 
import database as db
import pandas as pd
import oracledb

st.set_page_config(
    page_title="Oracle Text 2 SQL Demo",
    page_icon="./images/oracle-logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

SH_DEMO_QUERIES = [
    "2000년도의 총 판매량은 얼마인가요",
    "2000년 동안 판매된 각 제품의 총 판매 수량을 알고 싶어요",
    "Mouse Pad의 월별 판매량은 얼마인가요",
    "2001년도의 분기별 판매량을 알려주세요",
    "가장 많이 팔린 상위 5개 제품의 이름과 판매량은 무엇인가요",
    "상품 카테고리별 판매량은 얼마인가요",
    "가장 많이 판매된 제품의 이름과 총 판매 수량을 알고 싶어요",
    "각 판매 채널별 총 판매 금액이 얼마인지 알고 싶어요",
    "각 도시별로 평균 판매 금액이 얼마인지 알고 싶어요",
    "직업별로 평균 판매 금액이 얼마인지 알고 싶어요",
    "총 구매 금액이 100000을 초과한 고객의 이름과 구매 금액을 알고 싶어요",
    "Nason Mann 이 구매한 상품들의 총액은 얼마인가요",
    "각 상품별 총 매출과 매출 순위는 무엇인가요",
    "각 상품별 누적 매출과 전체 매출 대비 해당 상품의 누적 매출 비율은 무엇인가요",
    "누적 매출 기여도가 80% 이하인 상품은 무엇인가요",
    "각 프로모션의 이름과 해당 프로모션이 사용된 횟수를 알고 싶어요",
    "아시아에 있는 모든 국가의 이름을 알 수 있을까요",
    "각 나라에 고객이 몇 명 있는지 알고 싶어요",
    "결혼 상태별로 고객 수가 어떻게 되는지 알고 싶어요"]

st.sidebar.header("Oracle Select AI")
demo_phase = st.sidebar.radio("데모 순서", 
                            [
                            "1-1. DB 접속 & Select AI 설정",
                            "1-2. Select AI 기초",
                            "1-3. SH 스키마 쿼리 데모", 
                            "1-4. Movie 테이블 추가",
                            "1-5. Movie 프로파일 등록",
                            "1-6. Movie 데이터 조회",
                            "2-1. Select AI RAG",
                            "3-1. NoCode RAG: OCI Gen AI Agent", 
                            "4-1. Naive RAG With ADB & Cohere"]) 

# 데모 준비 단계
if demo_phase == "1-1. DB 접속 & Select AI 설정":
    st.title("데이터베이스 접속 & Select AI 설정")
    
    st.subheader("1. 데이터베이스 접속 정보 설정")
    with st.form("database_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            dbuser = st.text_input("DB User", "ADMIN")
        
        with col2: 
            dbpw = st.text_input("DB User Passwd", "Welcome123456!")
        
        with col1:     
            walletpw = st.text_input("Wallet Passwd", "Welcome123456!")
        
        with col2:
            dsn = st.text_input("Wallet Passwd", "selectaidemo_medium")
            
        submitted = st.form_submit_button("Datbase 설정")
        
        if submitted:
            st.session_state.database_user = dbuser
            st.session_state.database_user_password = dbpw
            st.session_state.database_wallet_password = walletpw
            st.session_state.dsn = dsn
            
            st.write("데이터베이스 접속 설정이 완료 됐습니다.")  
            
            #conn = db.get_connection()
            #st.write(conn.version)
   
    st.markdown("""---""")

    st.subheader("2. 데이터베이스 접속 테스트")
    if st.button("데이터베이스 접속 테스트"):
        result = db.get_connection()
        if result is not None:
         # 연결이 정상적으로 반환됨
            st.write(f"데이터베이스 접속 성공: 버전 {result.version}")
        else:
            # 연결이 실패한 경우
            st.write("데이터베이스 접속 실폐")

    st.markdown("""---""")
    
    st.subheader("3. Select AI 설정 요약")
    st.markdown("- Sales Histroy 스키마")
    st.image("./images/01.sh-schema.jpg")
    
    st.markdown("- 설정 코드: LLM Credential")
    
    st.image("./images/05-select-ai-flow.jpg")
    llm_credential_code="""
BEGIN
    DBMS_CLOUD.CREATE_CREDENTIAL (
        credential_name  => 'OPENAI_CRED',
        username => 'demo@gmail.com',
        password => 'sk-I9P-dvEZeQmDqWC...'
    );
END;
    """
    
    st.code(llm_credential_code, language="sql")
    
    st.markdown("- 설정 코드: Select AI 대상 프로파일")    
    target_profile_code="""
BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'OPENAI',
        attributes => '{
            "provider": "openai",
            "credential_name": "OPENAI_CRED",
            "object_list": [
              {"owner": "SH","name":"CHANNELS"},
              {"owner": "SH","name":"COSTS"},
              {"owner": "SH","name":"COUNTRIES"},
              {"owner": "SH","name":"CUSTOMERS"},
              {"owner": "SH","name":"PRODUCTS"},
              {"owner": "SH","name":"PROMOTIONS"},
              {"owner": "SH","name":"SALES"},
              {"owner": "SH","name":"TIMES"},
            ],
            "max_tokens":512,
            "stop_tokens": [";"],
            "model": "gpt-4o",
            "temperature": 0.1,
            "comments": true
        }'
    );
END;
    """    
    st.code(target_profile_code, language="sql")
    st.markdown("""---""")
    
    st.subheader("4. Select AI 설정 실행")
    
    # 데이터 조회 버튼
    if st.button("Select AI 구성을 위한 설정"):
        db.execute_openai_procedure()
        profile_name="OPENAI"
        profile_df = db.execute_profile_sql(profile_name)
        st.write(f"DBA_CLOUD_AI_PROFILES Table for '{profile_name}' Profile")
        st.dataframe(profile_df)  # Streamlit에서 DataFrame을 출력

if demo_phase == "1-2. Select AI 기초":
    st.subheader("1. Select AI 기초") 
    st.image("./images/02.selectai-actions.jpg")
    
    st.markdown("- Ex01 쿼리: LLM 직접 질의")
    query01 = "select AI CHAT 안녕하세요"
    st.code(query01, language="sql")
    
    if st.button("Ex01: 쿼리 실행"):
        conn = db.get_profile_connection("openai")
        cursor = conn.cursor()  
        df = pd.read_sql(query01, con=conn)
        st.dataframe(df)
        cursor.close()
        conn.close()        
        
    st.markdown("""---""") 
    st.markdown("- Ex02 쿼리: LLM 직접 질의")       
    quer02 = """
        select AI CHAT "What is Oracle Database''s market share(한국어로 대답해줘)"
    """
    st.code(quer02, language="sql")
    
    if st.button("Ex02: 쿼리 실행"):
        conn = db.get_profile_connection("openai")
        cursor = conn.cursor()  
        df = pd.read_sql(quer02, con=conn)
        st.dataframe(df)
        cursor.close()
        conn.close()        
        st.markdown("""---""")
        
    st.subheader("2. SH 스키마 대상 SQL 생성") 
    st.markdown("- Query02_01 쿼리: Select AI RUNSQL")    
    query02_01 = """
        select AI RUNSQL 얼마나 많은 상품이 있나요
    """
    
    st.code(query02_01, language="sql")
    
    if st.button("Query02_01: 쿼리 실행"):
        conn = db.get_profile_connection("openai")
        cursor = conn.cursor()  
        df = pd.read_sql(query02_01, con=conn)
        st.dataframe(df)
        cursor.close()
        conn.close()        
    
    st.markdown("""---""")    
    st.markdown("- Query02_02 쿼리: 생성 Query 출력")    
    query02_02 = """
        select AI SHOWSQL 얼마나 많은 상품이 있나요
    """
    
    st.code(query02_02, language="sql")
    
    if st.button("query02_02 쿼리 실행"):
        conn = db.get_profile_connection("openai")
        cursor = conn.cursor()  
        df = pd.read_sql(query02_02, con=conn)
        st.dataframe(df)
        cursor.close()
        conn.close()        
        
    st.markdown("""---""")    
    st.markdown("- Query02_03 쿼리: 실행 결과 자연어로 변환")  
    query02_03 = """
        select AI NARRATE 얼마나 많은 상품이 있나요
    """
    st.code(query02_03, language="sql")
    
    if st.button("query02_03 쿼리 실행"):
        conn = db.get_profile_connection("openai")
        cursor = conn.cursor()  
        df = pd.read_sql(query02_03, con=conn)
        st.dataframe(df)
        cursor.close()
        conn.close()        
        st.markdown("""---""")   
    

if demo_phase == "1-3. SH 스키마 쿼리 데모":  
    selected_item = st.selectbox("SH Query 목록", SH_DEMO_QUERIES)
    
    if st.button("SH 복합 쿼리 실행"):
        runsql_query=f"select ai runsql {selected_item}"
        showsql_query=f"select ai showsql {selected_item}"
        narrate_query=f"select ai narrate {selected_item}(한글로 출력해주세요) "
        conn = db.get_profile_connection("openai")
        
        st.markdown(f"- RUNSQL: {selected_item}") 
        st.code(runsql_query, language="sql")
        cursor = conn.cursor()  
        runsql_df = pd.read_sql(runsql_query, con=conn)
        st.dataframe(runsql_df)
        cursor.close()
        
        st.markdown(f"- SHOWSQL: {selected_item}") 
        st.code(showsql_query, language="sql")
        cursor = conn.cursor()  
        showsql_df = pd.read_sql(showsql_query, con=conn)
        st.dataframe(showsql_df)
        cursor.close()
        
        st.markdown(f"- Narrate: {selected_item}") 
        st.code(narrate_query, language="sql", )
        cursor = conn.cursor()  
        narrate_df = pd.read_sql(narrate_query, con=conn)
        st.dataframe(narrate_df)
        cursor.close()
        
        conn.close()        
    st.markdown("""---""")
    
if demo_phase == "1-4. Movie 테이블 추가":
    st.subheader("4. Movie 테이블 생성") 
    st.markdown("## 4.1 테이블 목록 조회")
    
    movie_tables_query= """
    SELECT table_name
    FROM user_tables
    """
    conn = db.get_connection()
    cursor = conn.cursor()  
    df = pd.read_sql(movie_tables_query, con=conn)
    st.code(movie_tables_query, language="sql")
    st.dataframe(df)
    cursor.close()
    conn.close()
    st.markdown("---")
    if st.button("Movie 테이블 삭제"):     
        db.drop_movie_schema()
        movie_tables_query= """
        SELECT table_name
        FROM user_tables
        """
        conn = db.get_connection()
        cursor = conn.cursor()  
        df = pd.read_sql(movie_tables_query, con=conn)
        st.code(movie_tables_query, language="sql")
        st.dataframe(df)
        cursor.close()
        conn.close()
        st.markdown("---")

    st.markdown("## 4.2 Movie 테이블 생성")    
    st.image("./images/12.model_schema.jpg")
    ddl="""
    CREATE TABLE director (
        director_id NUMBER PRIMARY KEY,
        name VARCHAR2(100)
    );

    CREATE TABLE movie (
        movie_id NUMBER PRIMARY KEY,
        title VARCHAR2(100),
        release_date DATE,
        genre VARCHAR2(50),
        director_id NUMBER,
        audience_count NUMBER,
        FOREIGN KEY (director_id) REFERENCES director(director_id)
    );

    CREATE TABLE actor (
        actor_id NUMBER PRIMARY KEY,
        name VARCHAR2(100)
    );

    CREATE TABLE movie_actor (
        movie_actor_id NUMBER PRIMARY KEY,
        movie_id NUMBER,
        actor_id NUMBER,
        FOREIGN KEY (movie_id) REFERENCES movie(movie_id),
        FOREIGN KEY (actor_id) REFERENCES actor(actor_id)
    );
    """
    st.code(ddl,language="sql")
    if st.button("Movie 스키마 생성"):
        db.create_movie_schema()
        
        conn = db.get_connection()
        cursor = conn.cursor()  
        df = pd.read_sql(movie_tables_query, con=conn)
        st.code(movie_tables_query, language="sql")
        st.dataframe(df)
        cursor.close()
        conn.close()

    st.markdown("## 4.3 Movie 데이터 생성: 합성 데이터")
    st.code(db.SYNTHETIC_PROCEDURE, language="sql", )
    if st.button("Movie 스키마 데이터 합성"):
        db.synthetic_data_for_movie()
        st.write("Data 생성 완료")
        st.markdown("----")
    
    if st.button("Movie 스키마 합성 데이터 조회"):        
        conn = db.get_connection()
        cursor = conn.cursor()  
        df = pd.read_sql("select * from actor", con=conn)
        st.markdown("- actor table")
        st.dataframe(df)        
        cursor.close()
        
        cursor = conn.cursor()  
        df = pd.read_sql("select * from director", con=conn)
        st.markdown("- director table")
        st.dataframe(df)        
        cursor.close()

        cursor = conn.cursor()  
        df = pd.read_sql("select * from movie", con=conn)
        st.markdown("- movie table")
        st.dataframe(df)        
        cursor.close()

        cursor = conn.cursor()  
        df = pd.read_sql("select * from movie_actor", con=conn)
        st.markdown("- movie_actor table")
        st.dataframe(df)        
        cursor.close()
        conn.close()
        
if demo_phase == "1-5. Movie 프로파일 등록":        
    st.markdown("- 설정 코드: Select AI 대상 프로파일")    
    target_profile_code="""
BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'OPENAI',
        attributes => '{
            "provider": "openai",
            "credential_name": "OPENAI_CRED",
            "object_list": [
              {"owner": "SH","name":"CHANNELS"},
              {"owner": "SH","name":"COSTS"},
              {"owner": "SH","name":"COUNTRIES"},
              {"owner": "SH","name":"CUSTOMERS"},
              {"owner": "SH","name":"PRODUCTS"},
              {"owner": "SH","name":"PROMOTIONS"},
              {"owner": "SH","name":"SALES"},
              {"owner": "SH","name":"TIMES"},
              {"owner": "ADMIN","name":"ACTOR"},
              {"owner": "ADMIN","name":"MOVIE"},
              {"owner": "ADMIN","name":"DIRECTOR"},
              {"owner": "ADMIN","name":"movie_actor"}
            ],
            "max_tokens":512,
            "stop_tokens": [";"],
            "model": "gpt-4o",
            "temperature": 0.1,
            "comments": true
        }'
    );
END;
    """    
    st.code(target_profile_code, language="sql")
    st.markdown("""---""")
    
    # 데이터 조회 버튼
    if st.button("Select AI 구성을 위한 설정"):
        db.execute_openai_procedure_with_movies()
        profile_name="OPENAI"
        profile_df = db.execute_profile_sql(profile_name)
        st.write(f"DBA_CLOUD_AI_PROFILES Table for '{profile_name}' Profile")
        st.dataframe(profile_df)  # Streamlit에서 DataFrame을 출력

if demo_phase == "1-6. Movie 데이터 조회":           
    text_query = st.text_input("자연어 쿼리", "2020년 개봉한 영화를 알려주세요.")
    
    if st.button("Movie 쿼리 실행"):
        runsql_query=f"select ai runsql {text_query}"
        showsql_query=f"select ai showsql {text_query}"
        narrate_query=f"select ai narrate {text_query}(한글로 출력해주세요) "
        conn = db.get_profile_connection("openai")
        
        st.markdown(f"- RUNSQL: {text_query}") 
        st.code(runsql_query, language="sql")
        cursor = conn.cursor()  
        runsql_df = pd.read_sql(runsql_query, con=conn)
        st.dataframe(runsql_df)
        cursor.close()
        
        st.markdown(f"- SHOWSQL: {text_query}") 
        st.code(showsql_query, language="sql")
        cursor = conn.cursor()  
        showsql_df = pd.read_sql(showsql_query, con=conn)
        st.dataframe(showsql_df)
        cursor.close()
        
        st.markdown(f"- Narrate: {text_query}") 
        st.code(narrate_query, language="sql", )
        cursor = conn.cursor()  
        narrate_df = pd.read_sql(narrate_query, con=conn)
        st.dataframe(narrate_df)
        cursor.close()
        
        conn.close()        
    st.markdown("""---""") 

if demo_phase == "2-1. Select AI RAG": 
    st.markdown("## 2. Select AI RAG")
    st.markdown("- text 파일 업로드: rocket.txt")
    st.image("./images/11.selectai-rag.jpg")
    
    st.markdown("- text 메타 조회")
    sql = """
SELECT * FROM DBMS_CLOUD.LIST_OBJECTS('OCI$RESOURCE_PRINCIPAL',
'https://objectstorage.us-chicago-1.oraclecloud.com/n/apackrsct01/b/selectairag/o/')
    """
    conn = db.get_connection()
    st.code(sql, language="sql")
    cursor = conn.cursor()  
    runsql_df = pd.read_sql(sql, con=conn)
    st.dataframe(runsql_df)
    cursor.close()
    conn.close()

    st.markdown("- select ai rag용 프로파일 생성")
    st.code(db.profile_for_select_ai_rag, language="sql", ) 
    if st.button("select ai rag 프로파일 생성"):
        db.execute_profile_for_select_ai_rag()
    profile_df = db.execute_profile_sql("GENAI_TEXT_TRANSFORMER")
    st.dataframe(profile_df)
    st.markdown("---")
    
    st.markdown("- select ai rag용 Vector Index 생성")
    st.code(db.create_vector_index, language="sql", ) 
    if st.button("select ai rag용 vector index 생성"):
        db.create_vector_index_for_select_ai_rag()
        
    conn = db.get_connection()
    st.code("select content, attributes from my_vector_table", language="sql")
    cursor = conn.cursor()  
    vector_index_df = pd.read_sql("select content, attributes from my_vector_table", con=conn)
    st.dataframe(vector_index_df)
    cursor.close()
    conn.close()
    st.markdown("---")
    
    if st.button("Select AI Without RAG 실행"):
        st.markdown("- select ai rag 쿼리 수행 without RAG")
        sql_without_rag = """
            SELECT AI chat OraBooster란?
        """
        conn = db.get_profile_connection("GENAI_TEXT_TRANSFORMER")
        st.code(sql_without_rag, language="sql")
        cursor = conn.cursor()  
        runsql_df = pd.read_sql(sql_without_rag, con=conn)
        st.dataframe(runsql_df)
        cursor.close()
        conn.close()
    
    if st.button("Select AI With RAG 실행"):
        st.markdown("- select ai rag 쿼리 수행 with RAG")
        sql_with_rag = """
            SELECT AI narrate OraBooster에 대해서 알려주세요
        """    
        conn = db.get_selectairag_profile_connection()
        st.code(sql_with_rag, language="sql")
        cursor = conn.cursor()  
        runsql_df = pd.read_sql(sql_with_rag, con=conn)
        st.dataframe(runsql_df)
        cursor.close()
        conn.close()
       
    
if demo_phase == "3-1. NoCode RAG: OCI Gen AI Agent":
    st.markdown("## 3. NoCode RAG - OCI Gen AI Agent")
    st.markdown("- PDF 파일")
    st.image("./images/06-pdf.jpg")
    st.markdown("---")
    st.markdown("- Object Storage Bucket")
    st.image("./images/07-knowledgestore.jpg")
    st.markdown("---")
    st.markdown("- 지식 저장소 유형")
    st.image("./images/08-knowledgestore-type.jpg")
    st.markdown("---")
    st.markdown("- OCI Gen AI Agent")
    st.image("./images/09.agent.jpg")
    st.markdown("---")
    st.markdown("- OCI Gen AI Agent UI")
    st.image("./images/10.agent-ui.jpg")
    st.markdown("---")
    st.markdown("- OCI Gen AI Agent 아키텍처")
    st.image("./images/10.agent-architecture.jpg")
    st.markdown("---")

if demo_phase == "4-1. Naive RAG With ADB & Cohere":
    st.markdown("## 4. Naive RAG")
    st.write("Naive RAG Demo: http://132.226.15.254:8888")      
    st.markdown("---")
    st.image("./images/03.naive_rag_notebook.jpg")
    st.markdown("---")
    st.image("./images/04.naive_rag_gr.jpg")
    
    
   
