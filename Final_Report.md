# API 接口集成文档

> 源码静态分析结果

## 统计信息

- **接口总数**: 118

- **接口分布**:
  - 🗑️ DELETE: 24 个
  - 🔍 GET: 41 个
  - ➕ POST: 20 个
  - ✏️ PUT: 12 个
  - 📡 REQUEST: 21 个

## 接口列表

---
### 📍 `GET /captchaImage`

- **方法**: `GET`
- **路径**: `/captchaImage`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /common`

- **方法**: `REQUEST`
- **路径**: `/common`
- **Content-Type**: `application/json`

---
### 📍 `GET /common/download`

- **方法**: `GET`
- **路径**: `/common/download`
- **Content-Type**: `multipart/form-data`
- **请求体示例**:
```json
{
  "file": "(binary_file_content)"
}
```

---
### 📍 `POST /common/upload`

- **方法**: `POST`
- **路径**: `/common/upload`
- **Content-Type**: `multipart/form-data`
- **请求体示例**:
```json
{
  "file": "(binary_file_content)"
}
```

---
### 📍 `POST /common/uploads`

- **方法**: `POST`
- **路径**: `/common/uploads`
- **Content-Type**: `multipart/form-data`
- **请求体示例**:
```json
{
  "file": "(binary_file_content)"
}
```

---
### 📍 `GET /common/download/resource`

- **方法**: `GET`
- **路径**: `/common/download/resource`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /monitor/cache`

- **方法**: `REQUEST`
- **路径**: `/monitor/cache`
- **Content-Type**: `application/json`

---
### 📍 `GET /monitor/cache/getNames`

- **方法**: `GET`
- **路径**: `/monitor/cache/getNames`
- **Content-Type**: `application/json`

---
### 📍 `GET /monitor/cache/getKeys/{cacheName}`

- **方法**: `GET`
- **路径**: `/monitor/cache/getKeys/{cacheName}`
- **Content-Type**: `application/json`
- **参数**:
  - `cacheName` (String) - path - 必填

---
### 📍 `GET /monitor/cache/getValue/{cacheName}/{cacheKey}`

- **方法**: `GET`
- **路径**: `/monitor/cache/getValue/{cacheName}/{cacheKey}`
- **Content-Type**: `application/json`
- **参数**:
  - `cacheName` (String) - path - 必填
  - `cacheKey` (String) - path - 必填

---
### 📍 `DELETE /monitor/cache/clearCacheName/{cacheName}`

- **方法**: `DELETE`
- **路径**: `/monitor/cache/clearCacheName/{cacheName}`
- **Content-Type**: `application/json`
- **参数**:
  - `cacheName` (String) - path - 必填

---
### 📍 `DELETE /monitor/cache/clearCacheKey/{cacheKey}`

- **方法**: `DELETE`
- **路径**: `/monitor/cache/clearCacheKey/{cacheKey}`
- **Content-Type**: `application/json`
- **参数**:
  - `cacheKey` (String) - path - 必填

---
### 📍 `DELETE /monitor/cache/clearCacheAll`

- **方法**: `DELETE`
- **路径**: `/monitor/cache/clearCacheAll`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /monitor/server`

- **方法**: `REQUEST`
- **路径**: `/monitor/server`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /monitor/logininfor`

- **方法**: `REQUEST`
- **路径**: `/monitor/logininfor`
- **Content-Type**: `application/json`

---
### 📍 `GET /monitor/logininfor/list`

- **方法**: `GET`
- **路径**: `/monitor/logininfor/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /monitor/logininfor/export`

- **方法**: `POST`
- **路径**: `/monitor/logininfor/export`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /monitor/logininfor/{infoIds}`

- **方法**: `DELETE`
- **路径**: `/monitor/logininfor/{infoIds}`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /monitor/logininfor/clean`

- **方法**: `DELETE`
- **路径**: `/monitor/logininfor/clean`
- **Content-Type**: `application/json`

---
### 📍 `GET /monitor/logininfor/unlock/{userName}`

- **方法**: `GET`
- **路径**: `/monitor/logininfor/unlock/{userName}`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /monitor/operlog`

- **方法**: `REQUEST`
- **路径**: `/monitor/operlog`
- **Content-Type**: `application/json`

---
### 📍 `GET /monitor/operlog/list`

- **方法**: `GET`
- **路径**: `/monitor/operlog/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /monitor/operlog/export`

- **方法**: `POST`
- **路径**: `/monitor/operlog/export`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /monitor/operlog/{operIds}`

- **方法**: `DELETE`
- **路径**: `/monitor/operlog/{operIds}`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /monitor/operlog/clean`

- **方法**: `DELETE`
- **路径**: `/monitor/operlog/clean`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /monitor/online`

- **方法**: `REQUEST`
- **路径**: `/monitor/online`
- **Content-Type**: `application/json`

---
### 📍 `GET /monitor/online/list`

- **方法**: `GET`
- **路径**: `/monitor/online/list`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /monitor/online/{tokenId}`

- **方法**: `DELETE`
- **路径**: `/monitor/online/{tokenId}`
- **Content-Type**: `application/json`
- **参数**:
  - `tokenId` (String) - path - 必填

---
### 📍 `REQUEST /system/config`

- **方法**: `REQUEST`
- **路径**: `/system/config`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/config/list`

- **方法**: `GET`
- **路径**: `/system/config/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /system/config/export`

- **方法**: `POST`
- **路径**: `/system/config/export`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/config/{configIds}`

- **方法**: `DELETE`
- **路径**: `/system/config/{configIds}`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/config/refreshCache`

- **方法**: `DELETE`
- **路径**: `/system/config/refreshCache`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /system/dept`

- **方法**: `REQUEST`
- **路径**: `/system/dept`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/dept/list`

- **方法**: `GET`
- **路径**: `/system/dept/list`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/dept/list/exclude/{deptId}`

- **方法**: `GET`
- **路径**: `/system/dept/list/exclude/{deptId}`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/dept/{deptId}`

- **方法**: `DELETE`
- **路径**: `/system/dept/{deptId}`
- **Content-Type**: `application/json`
- **参数**:
  - `deptId` (Long) - path - 必填

---
### 📍 `REQUEST /system/dict/data`

- **方法**: `REQUEST`
- **路径**: `/system/dict/data`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/dict/data/list`

- **方法**: `GET`
- **路径**: `/system/dict/data/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /system/dict/data/export`

- **方法**: `POST`
- **路径**: `/system/dict/data/export`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/dict/data/{dictCodes}`

- **方法**: `DELETE`
- **路径**: `/system/dict/data/{dictCodes}`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /system/dict/type`

- **方法**: `REQUEST`
- **路径**: `/system/dict/type`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/dict/type/list`

- **方法**: `GET`
- **路径**: `/system/dict/type/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /system/dict/type/export`

- **方法**: `POST`
- **路径**: `/system/dict/type/export`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/dict/type/{dictIds}`

- **方法**: `DELETE`
- **路径**: `/system/dict/type/{dictIds}`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/dict/type/refreshCache`

- **方法**: `DELETE`
- **路径**: `/system/dict/type/refreshCache`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/dict/type/optionselect`

- **方法**: `GET`
- **路径**: `/system/dict/type/optionselect`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /`

- **方法**: `REQUEST`
- **路径**: `/`
- **Content-Type**: `application/json`

---
### 📍 `POST /login`

- **方法**: `POST`
- **路径**: `/login`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "username": "test_data",
  "password": "test_data",
  "code": "test_data",
  "uuid": "test_data"
}
```

---
### 📍 `GET /getInfo`

- **方法**: `GET`
- **路径**: `/getInfo`
- **Content-Type**: `application/json`

---
### 📍 `GET /getRouters`

- **方法**: `GET`
- **路径**: `/getRouters`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /system/menu`

- **方法**: `REQUEST`
- **路径**: `/system/menu`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/menu/list`

- **方法**: `GET`
- **路径**: `/system/menu/list`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/menu/treeselect`

- **方法**: `GET`
- **路径**: `/system/menu/treeselect`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/menu/{menuId}`

- **方法**: `DELETE`
- **路径**: `/system/menu/{menuId}`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /system/notice`

- **方法**: `REQUEST`
- **路径**: `/system/notice`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/notice/list`

- **方法**: `GET`
- **路径**: `/system/notice/list`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/notice/{noticeIds}`

- **方法**: `DELETE`
- **路径**: `/system/notice/{noticeIds}`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /system/post`

- **方法**: `REQUEST`
- **路径**: `/system/post`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/post/list`

- **方法**: `GET`
- **路径**: `/system/post/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /system/post/export`

- **方法**: `POST`
- **路径**: `/system/post/export`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/post/{postIds}`

- **方法**: `DELETE`
- **路径**: `/system/post/{postIds}`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/post/optionselect`

- **方法**: `GET`
- **路径**: `/system/post/optionselect`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /system/user/profile`

- **方法**: `REQUEST`
- **路径**: `/system/user/profile`
- **Content-Type**: `application/json`

---
### 📍 `PUT /system/user/profile/updatePwd`

- **方法**: `PUT`
- **路径**: `/system/user/profile/updatePwd`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "unknown_field": "unknown_value"
}
```

---
### 📍 `POST /system/user/profile/avatar`

- **方法**: `POST`
- **路径**: `/system/user/profile/avatar`
- **Content-Type**: `multipart/form-data`
- **请求体示例**:
```json
{
  "file": "(binary_file_content)"
}
```

---
### 📍 `POST /register`

- **方法**: `POST`
- **路径**: `/register`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /system/role`

- **方法**: `REQUEST`
- **路径**: `/system/role`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/role/list`

- **方法**: `GET`
- **路径**: `/system/role/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /system/role/export`

- **方法**: `POST`
- **路径**: `/system/role/export`
- **Content-Type**: `application/json`

---
### 📍 `PUT /system/role/dataScope`

- **方法**: `PUT`
- **路径**: `/system/role/dataScope`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "roleId": 1,
  "roleName": "test_data",
  "roleKey": "test_data",
  "roleSort": 1,
  "dataScope": "test_data",
  "menuCheckStrictly": false,
  "deptCheckStrictly": false,
  "status": "test_data",
  "delFlag": "test_data",
  "menuIds": "Long[]_value",
  "deptIds": "Long[]_value",
  "permissions": "Set<String>_value"
}
```

---
### 📍 `PUT /system/role/changeStatus`

- **方法**: `PUT`
- **路径**: `/system/role/changeStatus`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "roleId": 1,
  "roleName": "test_data",
  "roleKey": "test_data",
  "roleSort": 1,
  "dataScope": "test_data",
  "menuCheckStrictly": false,
  "deptCheckStrictly": false,
  "status": "test_data",
  "delFlag": "test_data",
  "menuIds": "Long[]_value",
  "deptIds": "Long[]_value",
  "permissions": "Set<String>_value"
}
```

---
### 📍 `DELETE /system/role/{roleIds}`

- **方法**: `DELETE`
- **路径**: `/system/role/{roleIds}`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/role/optionselect`

- **方法**: `GET`
- **路径**: `/system/role/optionselect`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/role/authUser/allocatedList`

- **方法**: `GET`
- **路径**: `/system/role/authUser/allocatedList`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/role/authUser/unallocatedList`

- **方法**: `GET`
- **路径**: `/system/role/authUser/unallocatedList`
- **Content-Type**: `application/json`

---
### 📍 `PUT /system/role/authUser/cancel`

- **方法**: `PUT`
- **路径**: `/system/role/authUser/cancel`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "userId": 1,
  "roleId": 1
}
```

---
### 📍 `PUT /system/role/authUser/cancelAll`

- **方法**: `PUT`
- **路径**: `/system/role/authUser/cancelAll`
- **Content-Type**: `application/json`

---
### 📍 `PUT /system/role/authUser/selectAll`

- **方法**: `PUT`
- **路径**: `/system/role/authUser/selectAll`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /system/user`

- **方法**: `REQUEST`
- **路径**: `/system/user`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/user/list`

- **方法**: `GET`
- **路径**: `/system/user/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /system/user/export`

- **方法**: `POST`
- **路径**: `/system/user/export`
- **Content-Type**: `application/json`

---
### 📍 `POST /system/user/importData`

- **方法**: `POST`
- **路径**: `/system/user/importData`
- **Content-Type**: `multipart/form-data`
- **请求体示例**:
```json
{
  "file": "(binary_file_content)"
}
```

---
### 📍 `POST /system/user/importTemplate`

- **方法**: `POST`
- **路径**: `/system/user/importTemplate`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /system/user/{userIds}`

- **方法**: `DELETE`
- **路径**: `/system/user/{userIds}`
- **Content-Type**: `application/json`

---
### 📍 `PUT /system/user/resetPwd`

- **方法**: `PUT`
- **路径**: `/system/user/resetPwd`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "userId": 1,
  "deptId": 1,
  "userName": "test_data",
  "nickName": "test_data",
  "email": "test_data",
  "phonenumber": "test_data",
  "sex": "test_data",
  "avatar": "test_data",
  "password": "test_data",
  "status": "test_data",
  "delFlag": "test_data",
  "loginIp": "test_data",
  "loginDate": "2026-01-04 00:00:00",
  "pwdUpdateDate": "2026-01-04 00:00:00",
  "dept": "SysDept_value",
  "roles": "List<SysRole>_value",
  "roleIds": "Long[]_value",
  "postIds": "Long[]_value",
  "roleId": 1
}
```

---
### 📍 `PUT /system/user/changeStatus`

- **方法**: `PUT`
- **路径**: `/system/user/changeStatus`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "userId": 1,
  "deptId": 1,
  "userName": "test_data",
  "nickName": "test_data",
  "email": "test_data",
  "phonenumber": "test_data",
  "sex": "test_data",
  "avatar": "test_data",
  "password": "test_data",
  "status": "test_data",
  "delFlag": "test_data",
  "loginIp": "test_data",
  "loginDate": "2026-01-04 00:00:00",
  "pwdUpdateDate": "2026-01-04 00:00:00",
  "dept": "SysDept_value",
  "roles": "List<SysRole>_value",
  "roleIds": "Long[]_value",
  "postIds": "Long[]_value",
  "roleId": 1
}
```

---
### 📍 `GET /system/user/authRole/{userId}`

- **方法**: `GET`
- **路径**: `/system/user/authRole/{userId}`
- **Content-Type**: `application/json`

---
### 📍 `PUT /system/user/authRole`

- **方法**: `PUT`
- **路径**: `/system/user/authRole`
- **Content-Type**: `application/json`

---
### 📍 `GET /system/user/deptTree`

- **方法**: `GET`
- **路径**: `/system/user/deptTree`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /test/user`

- **方法**: `REQUEST`
- **路径**: `/test/user`
- **Content-Type**: `application/json`

---
### 📍 `GET /test/user/list`

- **方法**: `GET`
- **路径**: `/test/user/list`
- **Content-Type**: `application/json`

---
### 📍 `GET /test/user/{userId}`

- **方法**: `GET`
- **路径**: `/test/user/{userId}`
- **Content-Type**: `application/json`
- **参数**:
  - `userId` (Integer) - path - 必填

---
### 📍 `POST /test/user/save`

- **方法**: `POST`
- **路径**: `/test/user/save`
- **Content-Type**: `application/json`

---
### 📍 `PUT /test/user/update`

- **方法**: `PUT`
- **路径**: `/test/user/update`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "unknown_field": "unknown_value"
}
```

---
### 📍 `DELETE /test/user/{userId}`

- **方法**: `DELETE`
- **路径**: `/test/user/{userId}`
- **Content-Type**: `application/json`
- **参数**:
  - `userId` (Integer) - path - 必填

---
### 📍 `REQUEST /tool/gen`

- **方法**: `REQUEST`
- **路径**: `/tool/gen`
- **Content-Type**: `application/json`

---
### 📍 `GET /tool/gen/list`

- **方法**: `GET`
- **路径**: `/tool/gen/list`
- **Content-Type**: `application/json`

---
### 📍 `GET /tool/gen/db/list`

- **方法**: `GET`
- **路径**: `/tool/gen/db/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /tool/gen/importTable`

- **方法**: `POST`
- **路径**: `/tool/gen/importTable`
- **Content-Type**: `application/json`

---
### 📍 `POST /tool/gen/createTable`

- **方法**: `POST`
- **路径**: `/tool/gen/createTable`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /tool/gen/{tableIds}`

- **方法**: `DELETE`
- **路径**: `/tool/gen/{tableIds}`
- **Content-Type**: `application/json`

---
### 📍 `GET /tool/gen/preview/{tableId}`

- **方法**: `GET`
- **路径**: `/tool/gen/preview/{tableId}`
- **Content-Type**: `application/json`

---
### 📍 `GET /tool/gen/download/{tableName}`

- **方法**: `GET`
- **路径**: `/tool/gen/download/{tableName}`
- **Content-Type**: `application/json`

---
### 📍 `GET /tool/gen/genCode/{tableName}`

- **方法**: `GET`
- **路径**: `/tool/gen/genCode/{tableName}`
- **Content-Type**: `application/json`

---
### 📍 `GET /tool/gen/synchDb/{tableName}`

- **方法**: `GET`
- **路径**: `/tool/gen/synchDb/{tableName}`
- **Content-Type**: `application/json`

---
### 📍 `GET /tool/gen/batchGenCode`

- **方法**: `GET`
- **路径**: `/tool/gen/batchGenCode`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /monitor/job`

- **方法**: `REQUEST`
- **路径**: `/monitor/job`
- **Content-Type**: `application/json`

---
### 📍 `GET /monitor/job/list`

- **方法**: `GET`
- **路径**: `/monitor/job/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /monitor/job/export`

- **方法**: `POST`
- **路径**: `/monitor/job/export`
- **Content-Type**: `application/json`

---
### 📍 `PUT /monitor/job/changeStatus`

- **方法**: `PUT`
- **路径**: `/monitor/job/changeStatus`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "jobId": 1,
  "jobName": "test_data",
  "jobGroup": "test_data",
  "invokeTarget": "test_data",
  "cronExpression": "test_data",
  "concurrent": "test_data",
  "status": "test_data"
}
```

---
### 📍 `PUT /monitor/job/run`

- **方法**: `PUT`
- **路径**: `/monitor/job/run`
- **Content-Type**: `application/json`
- **请求体示例**:
```json
{
  "jobId": 1,
  "jobName": "test_data",
  "jobGroup": "test_data",
  "invokeTarget": "test_data",
  "cronExpression": "test_data",
  "concurrent": "test_data",
  "status": "test_data"
}
```

---
### 📍 `DELETE /monitor/job/{jobIds}`

- **方法**: `DELETE`
- **路径**: `/monitor/job/{jobIds}`
- **Content-Type**: `application/json`

---
### 📍 `REQUEST /monitor/jobLog`

- **方法**: `REQUEST`
- **路径**: `/monitor/jobLog`
- **Content-Type**: `application/json`

---
### 📍 `GET /monitor/jobLog/list`

- **方法**: `GET`
- **路径**: `/monitor/jobLog/list`
- **Content-Type**: `application/json`

---
### 📍 `POST /monitor/jobLog/export`

- **方法**: `POST`
- **路径**: `/monitor/jobLog/export`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /monitor/jobLog/{jobLogIds}`

- **方法**: `DELETE`
- **路径**: `/monitor/jobLog/{jobLogIds}`
- **Content-Type**: `application/json`

---
### 📍 `DELETE /monitor/jobLog/clean`

- **方法**: `DELETE`
- **路径**: `/monitor/jobLog/clean`
- **Content-Type**: `application/json`

