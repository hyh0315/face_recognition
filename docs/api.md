# 人脸识别签到系统 API 文档

## 认证相关接口

### 1. 用户登录

- **接口路径**: `/api/v1/auth/login`
- **请求方式**: POST
- **接口描述**: 用户登录接口，支持管理员、教师和学生三种角色登录
- **请求参数**:

  ```json
  {
    "username": "string",  // 用户名
    "password": "string"   // 密码
  }
  ```

- **响应参数**:

  ```json
  {
    "access_token": "string",      // JWT访问令牌
    "token_type": "bearer",        // 令牌类型
    "user_type": "string",         // 用户类型(admin/teacher/student)
    "user_id": "integer",          // 用户ID
    "username": "string",          // 用户名
    "need_change_password": false  // 是否需要修改密码
  }
  ```

- **响应状态码**:
  - 200: 登录成功
  - 401: 用户名或密码错误

### 2. 修改密码

- **接口路径**: `/api/v1/auth/change-password`
- **请求方式**: POST
- **接口描述**: 修改用户密码接口
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  ```

- **请求参数**:

  ```json
  {
    "old_password": "string",  // 旧密码
    "new_password": "string"   // 新密码
  }
  ```

- **响应参数**:

  ```json
  {
    "message": "Password changed successfully"
  }
  ```

- **响应状态码**:
  - 200: 密码修改成功
  - 400: 旧密码错误
  - 401: 未授权访问
  - 404: 用户不存在

## 认证说明

### OAuth2 认证流程

1. 调用登录接口获取访问令牌
2. 在后续请求中，在请求头中添加 `Authorization: Bearer <access_token>`

### 用户类型说明

- `admin`: 管理员
- `teacher`: 教师
- `student`: 学生

### 令牌说明

- 令牌类型: JWT
- 令牌有效期: 7天
- 令牌包含信息:
  - 用户ID
  - 用户类型
  - 用户名
  - 是否需要修改密码

## 使用示例

### 1. 登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=teacher1&password=teacher123"
```

### 2. 修改密码

```bash
curl -X POST "http://localhost:8000/api/v1/auth/change-password" \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{
           "old_password": "teacher123",
           "new_password": "new_password_here"
         }'
```

## 注意事项

1. 所有需要认证的接口都需要在请求头中携带有效的访问令牌
2. 首次登录时，如果 `need_change_password` 为 true，需要立即修改密码
3. 密码修改后会自动激活账号
4. 令牌过期后需要重新登录获取新的令牌
