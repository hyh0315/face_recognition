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

## 用户管理接口

### 1. 创建管理员账号

- **接口路径**: `/api/v1/users/admin`
- **请求方式**: POST
- **接口描述**: 创建新的管理员账号，需要超级管理员权限
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  ```

- **请求参数**:

  ```json
  {
    "username": "string",        // 用户名，3-50个字符
    "email": "string",          // 邮箱地址
    "password": "string",       // 密码，最少6个字符
    "name": "string",          // 姓名，2-50个字符
    "is_super_admin": false,   // 是否为超级管理员
    "phone": "string"          // 联系电话（可选）
  }
  ```

- **响应参数**:

  ```json
  {
    "id": "integer",           // 用户ID
    "username": "string",      // 用户名
    "email": "string",         // 邮箱
    "name": "string",          // 姓名
    "created_at": "string"     // 创建时间
  }
  ```

- **响应状态码**:
  - 201: 创建成功
  - 400: 参数错误或用户名/邮箱已存在
  - 403: 权限不足

### 2. 创建教师账号

- **接口路径**: `/api/v1/users/teacher`
- **请求方式**: POST
- **接口描述**: 创建新的教师账号，需要管理员权限
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  ```

- **请求参数**:

  ```json
  {
    "teacher_id": "string",     // 教师编号，3-20个字符
    "email": "string",         // 邮箱地址
    "name": "string",          // 姓名，2-50个字符
    "title": "string",         // 职称，2-50个字符
    "department": "string",    // 院系，2-100个字符
    "phone": "string"          // 联系电话，11位
  }
  ```

- **响应参数**:

  ```json
  {
    "id": "integer",           // 用户ID
    "username": "string",      // 用户名（教师编号）
    "email": "string",         // 邮箱
    "name": "string",          // 姓名
    "created_at": "string"     // 创建时间
  }
  ```

- **响应状态码**:
  - 201: 创建成功
  - 400: 参数错误或教师编号/邮箱已存在
  - 403: 权限不足

### 3. 创建学生账号

- **接口路径**: `/api/v1/users/student`
- **请求方式**: POST
- **接口描述**: 创建新的学生账号，需要管理员权限
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  ```

- **请求参数**:

  ```json
  {
    "student_id": "string",    // 学号，3-20个字符
    "email": "string",         // 邮箱地址
    "name": "string",          // 姓名，2-50个字符
    "class_name": "string",    // 班级，2-50个字符
    "department": "string",    // 院系，2-100个字符
    "major": "string",         // 专业，2-100个字符
    "grade": "string",         // 年级，4位
    "face_image": "string"     // Base64编码的人脸图片数据
  }
  ```

- **响应参数**:

  ```json
  {
    "id": "integer",           // 用户ID
    "username": "string",      // 用户名（学号）
    "email": "string",         // 邮箱
    "name": "string",          // 姓名
    "created_at": "string"     // 创建时间
  }
  ```

- **响应状态码**:
  - 201: 创建成功
  - 400: 参数错误、学号/邮箱已存在或人脸识别失败
  - 403: 权限不足

### 4. 查询学生列表

- **接口路径**: `/api/v1/users/students`
- **请求方式**: GET
- **接口描述**: 查询学生列表，支持多种筛选条件，需要管理员或教师权限
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  ```

- **查询参数**:

  ```
  class_name: string    // 班级（可选）
  department: string    // 院系（可选）
  major: string        // 专业（可选）
  grade: string        // 年级（可选）
  is_active: boolean   // 账号状态（可选）
  is_graduated: boolean // 是否毕业（可选）
  ```

- **响应参数**:

  ```json
  {
    "total": "integer",        // 总记录数
    "items": [                 // 学生列表
      {
        "id": "integer",       // 用户ID
        "username": "string",  // 用户名（学号）
        "email": "string",     // 邮箱
        "name": "string",      // 姓名
        "created_at": "string" // 创建时间
      }
    ]
  }
  ```

- **响应状态码**:
  - 200: 查询成功
  - 403: 权限不足

### 5. 批量导入学生

- **接口路径**: `/api/v1/users/students/batch`
- **请求方式**: POST
- **接口描述**: 通过Excel文件批量导入学生账号
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  Content-Type: multipart/form-data
  ```

- **请求参数**:

  ```
  file: Excel文件 (.xlsx 或 .xls)
  ```

- **Excel文件格式要求**:
  - 必须包含以下列：
    - 学号
    - 姓名
    - 邮箱
    - 班级
    - 院系
    - 专业
    - 年级
  - 示例数据：

    ```
    学号,姓名,邮箱,班级,院系,专业,年级
    S2024001,张三,zhangsan@example.com,计算机2401,计算机科学系,计算机科学与技术,2024
    S2024002,李四,lisi@example.com,计算机2401,计算机科学系,计算机科学与技术,2024
    ```

- **响应参数**:

  ```json
  [
    {
      "id": "integer",           // 用户ID
      "username": "string",      // 用户名（学号）
      "email": "string",         // 邮箱
      "name": "string",          // 姓名
      "created_at": "string"     // 创建时间
    }
  ]
  ```

- **响应状态码**:
  - 201: 导入成功
  - 400: 文件格式错误或数据验证失败
  - 403: 权限不足

- **使用示例**:

```bash
curl -X POST "http://localhost:8000/api/v1/users/students/batch" \
     -H "Authorization: Bearer <access_token>" \
     -F "file=@students.xlsx"
```

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

### 3. 创建教师账号

```bash
curl -X POST "http://localhost:8000/api/v1/users/teacher" \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{
           "teacher_id": "T2024001",
           "email": "teacher1@example.com",
           "name": "张老师",
           "title": "副教授",
           "department": "计算机科学系",
           "phone": "13800138001"
         }'
```

### 4. 创建学生账号

```bash
# 将图片转换为Base64
base64_image=$(base64 -i student_face.jpg)

curl -X POST "http://localhost:8000/api/v1/users/student" \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{
           "student_id": "S2024001",
           "email": "student1@example.com",
           "name": "李同学",
           "class_name": "计算机2401",
           "department": "计算机科学系",
           "major": "计算机科学与技术",
           "grade": "2024",
           "face_image": "'$base64_image'"
         }'
```

### 5. 查询学生列表

```bash
curl -X GET "http://localhost:8000/api/v1/users/students?class_name=计算机2401&department=计算机科学系" \
     -H "Authorization: Bearer <access_token>"
```

## 注意事项

1. 所有需要认证的接口都需要在请求头中携带有效的访问令牌
2. 首次登录时，如果 `need_change_password` 为 true，需要立即修改密码
3. 密码修改后会自动激活账号
4. 令牌过期后需要重新登录获取新的令牌
5. 创建教师和学生账号时会自动生成随机初始密码
6. 教师和学生账号默认未激活，需要首次登录修改密码后激活
7. 查询学生列表支持多个筛选条件组合使用
8. 创建学生账号时必须提供清晰的人脸图片，图片要求：
   - 格式：JPG或PNG
   - 大小：不超过2MB
   - 内容：正面免冠照片，光线充足，面部清晰
   - 编码：Base64格式
9. 批量导入学生时：
   - Excel文件必须使用UTF-8编码
   - 学号和邮箱不能重复
   - 如果学号或邮箱已存在，该条记录会被跳过
   - 导入后需要单独上传每个学生的人脸图片
