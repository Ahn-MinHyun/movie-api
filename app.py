#라이브러리
from flask import Flask
from flask_restful import Api
from config.config import Config
from Resourse.user import UserJoinResource, UserResource, UserLogoutResource, jwt_blocklist
from Resourse.memo import MemoResource, MemoReviseResource

from flask_jwt_extended import JWTManager

import mysql.connector 

# 시작
app = Flask(__name__)


# 1. 환경변수 설정
app.config.from_object(Config)
## 1-1. JWT 환경 설정
jwt = JWTManager(app)

# 2. API설정
api = Api(app)

## 로그인/로그아웃 관리를 위한 jwt설정
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

# 3. 경로연결

# 회원가입 경로
api.add_resource(UserJoinResource,'/v1/join')

# 로그인 경로
api.add_resource(UserResource,'/v1/login')

# 로그아웃 경로
api.add_resource(UserLogoutResource,'/v1/logout')

# 메모 작성/조회 경로
api.add_resource(MemoResource,'/v1/memo')

# 메모 수정/삭제 경로
api.add_resource(MemoReviseResource,'/v1/memorevise/<int:memo_id>')




if __name__=="__main__":

    app.run(port=5001)

