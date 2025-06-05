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

## 管理员管理接口

### 1. 创建管理员账号

- **接口路径**: `/api/v1/admin/admin`
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

### 2. 删除管理员账号

- **接口路径**: `/api/v1/admin/admin/{admin_id}`
- **请求方式**: DELETE
- **接口描述**: 删除指定ID的管理员账号，需要超级管理员权限
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  ```

- **路径参数**:
  - `admin_id`: 管理员ID

- **响应参数**:

  ```json
  {
    "message": "Successfully deleted admin {admin_id}",
    "admin_id": "integer"
  }
  ```

- **响应状态码**:
  - 200: 删除成功
  - 403: 权限不足或不能删除自己/最后一个超级管理员
  - 404: 管理员不存在

## 教师管理接口

### 1. 创建教师账号

- **接口路径**: `/api/v1/teacher/teacher`
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

### 2. 批量导入教师

- **接口路径**: `/api/v1/teacher/teachers/batch`
- **请求方式**: POST
- **接口描述**: 通过Excel文件批量导入教师账号
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  Content-Type: multipart/form-data
  ```

- **请求参数**:

  ```
  excel_file: Excel文件 (.xlsx 或 .xls)
  ```

- **Excel文件格式要求**:
  - 必须包含以下列：
    - 教师编号
    - 姓名
    - 邮箱
    - 职称
    - 院系
    - 手机号
  - 示例数据：

    ```
    教师编号,姓名,邮箱,职称,院系,手机号
    T2024001,张老师,zhang@example.com,副教授,计算机科学系,13800138001
    T2024002,李老师,li@example.com,讲师,计算机科学系,13800138002
    ```

- **响应参数**:

  ```json
  [
    {
      "id": "integer",           // 用户ID
      "username": "string",      // 用户名（教师编号）
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

### 3. 删除教师账号

- **接口路径**: `/api/v1/teacher/teacher/{teacher_id}`
- **请求方式**: DELETE
- **接口描述**: 删除指定教师编号的教师账号
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  ```

- **路径参数**:
  - `teacher_id`: 教师编号

- **响应参数**:

  ```json
  {
    "message": "Successfully deleted teacher {teacher_id}",
    "teacher_id": "string"
  }
  ```

- **响应状态码**:
  - 200: 删除成功
  - 403: 权限不足
  - 404: 教师不存在

## 学生管理接口

### 1. 创建学生账号

- **接口路径**: `/api/v1/student/student`
- **请求方式**: POST
- **接口描述**: 创建新的学生账号，需要管理员权限
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  Content-Type: multipart/form-data
  ```

- **请求参数**:

  ```
  student_data: JSON字符串，包含以下字段：
  {
    "student_id": "string",    // 学号，3-20个字符
    "email": "string",         // 邮箱地址
    "name": "string",          // 姓名，2-50个字符
    "class_name": "string",    // 班级，2-50个字符
    "department": "string",    // 院系，2-100个字符
    "major": "string",         // 专业，2-100个字符
    "grade": "string"          // 年级，4位
  }
  face_image: 图片文件 (.jpg 或 .png)
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

### 2. 查询学生列表

- **接口路径**: `/api/v1/student/students`
- **请求方式**: GET
- **接口描述**: 查询学生列表，支持多种筛选条件
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

### 3. 批量导入学生

- **接口路径**: `/api/v1/student/students/batch`
- **请求方式**: POST
- **接口描述**: 通过Excel文件和zip文件批量导入学生账号
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  Content-Type: multipart/form-data
  ```

- **请求参数**:

  ```
  excel_file: Excel文件 (.xlsx 或 .xls)
  face_images: zip文件，包含人脸图片
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

- **人脸图片要求**:
  - 图片命名格式：`学号.jpg`
  - 图片要求：
    - 格式：JPG或PNG
    - 大小：不超过2MB
    - 内容：正面免冠照片，光线充足，面部清晰

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

### 4. 删除学生账号

- **接口路径**: `/api/v1/student/student/{student_id}`
- **请求方式**: DELETE
- **接口描述**: 删除指定学号的学生账号
- **请求头**:

  ```
  Authorization: Bearer <access_token>
  ```

- **路径参数**:
  - `student_id`: 学号

- **响应参数**:

  ```json
  {
    "message": "Successfully deleted student {student_id}",
    "student_id": "string"
  }
  ```

- **响应状态码**:
  - 200: 删除成功
  - 403: 权限不足
  - 404: 学生不存在

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
9. 批量导入学生时：
   - Excel文件必须使用UTF-8编码
   - 学号和邮箱不能重复
   - 如果学号或邮箱已存在，该条记录会被跳过
   - 需要同时上传包含所有人脸图片的zip文件
10. 删除管理员账号时：
    - 不能删除自己
    - 不能删除最后一个超级管理员
    - 会同时删除该管理员创建的所有账号记录
11. 删除教师账号时：
    - 会同时删除教师相关的课程记录
    - 会同时删除教师相关的考勤记录
12. 删除学生账号时：
    - 会同时删除学生的人脸编码数据
    - 会同时删除学生的考勤记录

## 文件上传说明

### 文件存储结构

```
uploads/
├── excel_files/          # Excel文件
│   ├── students/         # 学生导入文件
│   │   └── YYYYMMDD_HHMMSS/
│   │       └── students.xlsx
│   └── teachers/         # 教师导入文件
│       └── YYYYMMDD_HHMMSS/
│           └── teachers.xlsx
└── face_images/          # 人脸图片
    └── students/         # 学生人脸图片
        └── YYYYMMDD_HHMMSS/
            ├── S2024001.jpg
            ├── S2024002.jpg
            └── ...
```

### 文件上传要求

1. **Excel文件**:
   - 格式：.xlsx 或 .xls
   - 编码：UTF-8
   - 大小：不超过2MB
   - 必须包含指定的列名

2. **人脸图片**:
   - 格式：JPG或PNG
   - 大小：不超过2MB
   - 命名规则：学号.jpg
   - 内容要求：正面免冠照片，光线充足，面部清晰

### 性能优化建议

1. **前端优化**:
   - 使用文件分片上传
   - 添加进度条显示
   - 实现文件队列管理
   - 使用异步操作处理文件
   - 添加文件类型和大小验证

2. **服务器优化**:
   - 使用异步IO处理文件
   - 配置合理的超时时间
   - 启用文件压缩
   - 配置缓存策略
   - 定期清理临时文件

3. **安全建议**:
   - 使用HTTPS确保传输安全
   - 限制文件大小
   - 验证文件类型
   - 定期清理临时文件
   - 监控异常访问
   - 记录文件操作日志
