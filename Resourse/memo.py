from flask_restful import Resource
from flask import request
from http import HTTPStatus

# 이메일 형식 체크하기 위한 import
from mysql.connector import Error

from db.db import get_mysql_connection

# 유저인증을 위한 JWT 라이브러리 import 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt


class MemoResource(Resource):

    # 메모작성 API
    @jwt_required()
    def post(self):
        # 1. 클라이언트가 요청한 reuest의 바디에 있는 json데이터 가져오기
        data = request.get_json()
        print(data)

        ## JWT 인증토큰에서 유저아이디를 뽑아낸다.
        user_id = get_jwt_identity()
        # print('------------------------------------')
        # print(user_id)

        # 3. 데이터 베이스 커넥션 연결
        connection = get_mysql_connection()
        # 4. 커서 가져오기
        cursor = connection.cursor(dictionary=True)
        # 5. 쿼리문 만들기
        query =""" insert into memo(title, content, user_id)
                                    values(%s,%s,%s);   """

        param = [data['title'],data['content'],user_id]
        
        # 6. 쿼리문 실행
        cursor.execute(query, param)
        connection.commit()

        # 7. 커서와 커넥션 닫기
        cursor.close()
        connection.close()

        # 8. 클라이언트에 리스판스
        
        return {'message':'success'}, HTTPStatus.OK

    # 메모 조회 API
    @jwt_required()
    def get(self):

        # 내 아이디를 가지고 내가 쓴 글만 조회하도록
        # 토큰에서 아이디 찾기 
        user_id = get_jwt_identity()

        # 데이터 베이스 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)

        # 쿼리문 작성
        query ='''select m.created_at, m.updated_at, m.title, m.content
                    from memo m
                    join memo_user u
	                on m.user_id = u.id
                    where u.id = %s; '''
        
        param = (user_id,)
        # 쿼리문 실행 후 저장
        cursor.execute(query, param)
        records = cursor.fetchall()

        # 데이터베이스 닫기
        cursor.close()
        connection.close()

        print(records)

        ret=[]
        for row in records:
            row['created_at'] = row['created_at'].isoformat()
            row['updated_at'] = row['updated_at'].isoformat()
            ret.append(row)

        return {'count':len(ret), 'memo':ret}, HTTPStatus.OK
        



class MemoReviseResource(Resource):
    # 메모 업데이트 API   
    # 특정 메모를 가져오는 
    @jwt_required()
    def patch(self, memo_id):
        # 데이터에서 접속하여 user_id를 확인한다.

        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)

        qurey = '''select * from memo where id = %s;'''
        param = (memo_id, )
        cursor.execute(qurey, param)
        records = cursor.fetchall()

        print( records )

        if len(records) == 0:
            return {"err_code":1},HTTPStatus.NOT_FOUND # 찾는 데이터가 존재하지 않을때
        
        # 토큰 확인
        user_id = get_jwt_identity()
        print(user_id)
        if records[0]['user_id'] != user_id :
            return {"err_code":2},HTTPStatus.NOT_ACCEPTABLE #유저의 메모가 아닐때
        
        # 내가 가지고 있는 title과 content를 가져온다.
        title = records[0]['title']
        content = records[0]['content']

        # 클라이언트가 수정한 데이터를 가져온다.
        data = request.get_json()
        # print(data)

        # 클라이언트가 가져온 데이터에 title과 content가 중 하나라도 없으면 
        # 원래 있던 데이터를 사용한다.

        if 'title' not in data:
            data['title'] = title
        
        if 'content' not in data:
            data['content'] = content

        # 데이터를 수정한다. 

        qurey = ''' update memo set title = %s, content = %s
                    where id = %s;'''

        param = (data['title'], data['content'], memo_id)
        
        cursor.execute(qurey, param)
        connection.commit()
        
        # 데이터베이스를 닫는다.
        connection.close()
        cursor.close()

        # 리턴
        return {"changed memo": data }, HTTPStatus.OK
    

    # 메모삭제 API
    @jwt_required()
    def delete(self, memo_id):
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary= True)


        ## 유저 아이디가 이 레시피 만든 유저가 맞는지 확인해 봐야한다.
        user_id=get_jwt_identity() #헤더의 인증토큰을 가져온다.

        query = ''' select user_id from memo 
                    where id = %s;'''

        param = (memo_id,)

        cursor.execute(query, param)
        records = cursor.fetchall()
        
        if len(records) == 0:
            return {'err_code': 1 },HTTPStatus.NOT_FOUND

        if user_id != records[0]['user_id']:
            return {'err_code': 2 },HTTPStatus.NOT_ACCEPTABLE 

        query = '''delete from recipe
                    where id = %s;'''
        param = (memo_id,)
        cursor.execute(query, param) 
        connection.commit()

        cursor.close()
        connection.close()

        return {'message':'success remove'}, HTTPStatus.OK       

