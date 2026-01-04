# API Interface Documentation

> **API Count: 94**

> **Generated Time: 2026-01-04**

---

## Statistics

- **GET**: 41
- **DELETE**: 23
- **POST**: 19
- **PUT**: 11

---

## API Details

### 1. GET `/captchaImage`

**Method Name**: `getCode`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response
```

---

### 2. GET `/common/download`

**Method Name**: `fileDownload`

**Content-Type**: `application/json`

**Parameters**:
```java
String fileName, Boolean delete, HttpServletResponse response, HttpServletRequest request
```

---

### 3. POST `/common/upload`

**Method Name**: `uploadFile`

**Content-Type**: `multipart/form-data`

**Parameters**:
```java
MultipartFile file
```

**Smart Payload**:
```json
{
  "file": "(binary_file_content)"
}
```

---

### 4. POST `/common/uploads`

**Method Name**: `uploadFiles`

**Content-Type**: `multipart/form-data`

**Parameters**:
```java
List<MultipartFile> files
```

**Smart Payload**:
```json
{
  "file": "(binary_file_content)"
}
```

---

### 5. GET `/common/download/resource`

**Method Name**: `resourceDownload`

**Content-Type**: `application/json`

**Parameters**:
```java
String resource, HttpServletRequest request, HttpServletResponse response
```

---

### 6. GET `/monitor/cache`

**Method Name**: `getInfo`

**Content-Type**: `application/json`

---

### 7. GET `/monitor/cache/getNames`

**Method Name**: `cache`

**Content-Type**: `application/json`

---

### 8. GET `/monitor/cache/getKeys/1`

**Method Name**: `getCacheKeys`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable String cacheName
```

---

### 9. GET `/monitor/cache/getValue/1/1`

**Method Name**: `getCacheValue`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable String cacheName, @PathVariable String cacheKey
```

---

### 10. DELETE `/monitor/cache/clearCacheName/1`

**Method Name**: `clearCacheName`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable String cacheName
```

---

### 11. DELETE `/monitor/cache/clearCacheKey/1`

**Method Name**: `clearCacheKey`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable String cacheKey
```

---

### 12. DELETE `/monitor/cache/clearCacheAll`

**Method Name**: `clearCacheAll`

**Content-Type**: `application/json`

---

### 13. GET `/monitor/server`

**Method Name**: `getInfo`

**Content-Type**: `application/json`

---

### 14. GET `/monitor/logininfor/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysLogininfor logininfor
```

---

### 15. POST `/monitor/logininfor/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysLogininfor logininfor
```

---

### 16. DELETE `/monitor/logininfor/{infoIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] infoIds
```

---

### 17. DELETE `/monitor/logininfor/clean`

**Method Name**: `clean`

**Content-Type**: `application/json`

---

### 18. GET `/monitor/logininfor/unlock/{userName}`

**Method Name**: `unlock`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable("userName"
```

---

### 19. GET `/monitor/operlog/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysOperLog operLog
```

---

### 20. POST `/monitor/operlog/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysOperLog operLog
```

---

### 21. DELETE `/monitor/operlog/{operIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] operIds
```

---

### 22. DELETE `/monitor/operlog/clean`

**Method Name**: `clean`

**Content-Type**: `application/json`

---

### 23. GET `/monitor/online/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
String ipaddr, String userName
```

---

### 24. DELETE `/monitor/online/1`

**Method Name**: `forceLogout`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable String tokenId
```

---

### 25. GET `/system/config/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysConfig config
```

---

### 26. POST `/system/config/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysConfig config
```

---

### 27. DELETE `/system/config/{configIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] configIds
```

---

### 28. DELETE `/system/config/refreshCache`

**Method Name**: `refreshCache`

**Content-Type**: `application/json`

---

### 29. GET `/system/dept/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysDept dept
```

---

### 30. GET `/system/dept/list/exclude/{deptId}`

**Method Name**: `excludeChild`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable(value = "deptId", required = false
```

---

### 31. DELETE `/system/dept/1`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long deptId
```

---

### 32. GET `/system/dict/data/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysDictData dictData
```

---

### 33. POST `/system/dict/data/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysDictData dictData
```

---

### 34. DELETE `/system/dict/data/{dictCodes}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] dictCodes
```

---

### 35. GET `/system/dict/type/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysDictType dictType
```

---

### 36. POST `/system/dict/type/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysDictType dictType
```

---

### 37. DELETE `/system/dict/type/{dictIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] dictIds
```

---

### 38. DELETE `/system/dict/type/refreshCache`

**Method Name**: `refreshCache`

**Content-Type**: `application/json`

---

### 39. GET `/system/dict/type/optionselect`

**Method Name**: `optionselect`

**Content-Type**: `application/json`

---

### 40. POST `/login`

**Method Name**: `login`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody LoginBody loginBody
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 41. GET `/getInfo`

**Method Name**: `getInfo`

**Content-Type**: `application/json`

---

### 42. GET `/getRouters`

**Method Name**: `getRouters`

**Content-Type**: `application/json`

---

### 43. GET `/system/menu/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysMenu menu
```

---

### 44. GET `/system/menu/treeselect`

**Method Name**: `treeselect`

**Content-Type**: `application/json`

**Parameters**:
```java
SysMenu menu
```

---

### 45. DELETE `/system/menu/{menuId}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable("menuId"
```

---

### 46. GET `/system/notice/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysNotice notice
```

---

### 47. DELETE `/system/notice/{noticeIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] noticeIds
```

---

### 48. GET `/system/post/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysPost post
```

---

### 49. POST `/system/post/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysPost post
```

---

### 50. DELETE `/system/post/{postIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] postIds
```

---

### 51. GET `/system/post/optionselect`

**Method Name**: `optionselect`

**Content-Type**: `application/json`

---

### 52. PUT `/system/user/profile/updatePwd`

**Method Name**: `updatePwd`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody Map<String, String> params
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 53. POST `/system/user/profile/avatar`

**Method Name**: `avatar`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestParam("avatarfile"
```

---

### 54. POST `/register`

**Method Name**: `register`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody RegisterBody user
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 55. GET `/system/role/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysRole role
```

---

### 56. POST `/system/role/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysRole role
```

---

### 57. PUT `/system/role/dataScope`

**Method Name**: `dataScope`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody SysRole role
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 58. PUT `/system/role/changeStatus`

**Method Name**: `changeStatus`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody SysRole role
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 59. DELETE `/system/role/{roleIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] roleIds
```

---

### 60. GET `/system/role/optionselect`

**Method Name**: `optionselect`

**Content-Type**: `application/json`

---

### 61. GET `/system/role/authUser/allocatedList`

**Method Name**: `allocatedList`

**Content-Type**: `application/json`

**Parameters**:
```java
SysUser user
```

---

### 62. GET `/system/role/authUser/unallocatedList`

**Method Name**: `unallocatedList`

**Content-Type**: `application/json`

**Parameters**:
```java
SysUser user
```

---

### 63. PUT `/system/role/authUser/cancel`

**Method Name**: `cancelAuthUser`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody SysUserRole userRole
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 64. PUT `/system/role/authUser/cancelAll`

**Method Name**: `cancelAuthUserAll`

**Content-Type**: `application/json`

**Parameters**:
```java
Long roleId, Long[] userIds
```

---

### 65. PUT `/system/role/authUser/selectAll`

**Method Name**: `selectAuthUserAll`

**Content-Type**: `application/json`

**Parameters**:
```java
Long roleId, Long[] userIds
```

---

### 66. GET `/system/user/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysUser user
```

---

### 67. POST `/system/user/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysUser user
```

---

### 68. POST `/system/user/importData`

**Method Name**: `importData`

**Content-Type**: `multipart/form-data`

**Parameters**:
```java
MultipartFile file, boolean updateSupport
```

**Smart Payload**:
```json
{
  "file": "(binary_file_content)"
}
```

---

### 69. POST `/system/user/importTemplate`

**Method Name**: `importTemplate`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response
```

---

### 70. DELETE `/system/user/{userIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] userIds
```

---

### 71. PUT `/system/user/resetPwd`

**Method Name**: `resetPwd`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody SysUser user
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 72. PUT `/system/user/changeStatus`

**Method Name**: `changeStatus`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody SysUser user
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 73. GET `/system/user/authRole/{userId}`

**Method Name**: `authRole`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable("userId"
```

---

### 74. PUT `/system/user/authRole`

**Method Name**: `insertAuthRole`

**Content-Type**: `application/json`

**Parameters**:
```java
Long userId, Long[] roleIds
```

---

### 75. GET `/system/user/deptTree`

**Method Name**: `deptTree`

**Content-Type**: `application/json`

**Parameters**:
```java
SysDept dept
```

---

### 76. GET `/tool/gen/list`

**Method Name**: `genList`

**Content-Type**: `application/json`

**Parameters**:
```java
GenTable genTable
```

---

### 77. GET `/tool/gen/db/list`

**Method Name**: `dataList`

**Content-Type**: `application/json`

**Parameters**:
```java
GenTable genTable
```

---

### 78. POST `/tool/gen/importTable`

**Method Name**: `importTableSave`

**Content-Type**: `application/json`

**Parameters**:
```java
String tables
```

---

### 79. POST `/tool/gen/createTable`

**Method Name**: `createTableSave`

**Content-Type**: `application/json`

**Parameters**:
```java
String sql
```

---

### 80. DELETE `/tool/gen/{tableIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] tableIds
```

---

### 81. GET `/tool/gen/preview/{tableId}`

**Method Name**: `preview`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable("tableId"
```

---

### 82. GET `/tool/gen/download/{tableName}`

**Method Name**: `download`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, @PathVariable("tableName"
```

---

### 83. GET `/tool/gen/genCode/{tableName}`

**Method Name**: `genCode`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable("tableName"
```

---

### 84. GET `/tool/gen/synchDb/{tableName}`

**Method Name**: `synchDb`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable("tableName"
```

---

### 85. GET `/tool/gen/batchGenCode`

**Method Name**: `batchGenCode`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, String tables
```

---

### 86. GET `/monitor/job/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysJob sysJob
```

---

### 87. POST `/monitor/job/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysJob sysJob
```

---

### 88. PUT `/monitor/job/changeStatus`

**Method Name**: `changeStatus`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody SysJob job
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 89. PUT `/monitor/job/run`

**Method Name**: `run`

**Content-Type**: `application/json`

**Parameters**:
```java
@RequestBody SysJob job
```

**Smart Payload**:
```json
{
  "unknown_field": "placeholder"
}
```

---

### 90. DELETE `/monitor/job/{jobIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] jobIds
```

---

### 91. GET `/monitor/jobLog/list`

**Method Name**: `list`

**Content-Type**: `application/json`

**Parameters**:
```java
SysJobLog sysJobLog
```

---

### 92. POST `/monitor/jobLog/export`

**Method Name**: `export`

**Content-Type**: `application/json`

**Parameters**:
```java
HttpServletResponse response, SysJobLog sysJobLog
```

---

### 93. DELETE `/monitor/jobLog/{jobLogIds}`

**Method Name**: `remove`

**Content-Type**: `application/json`

**Parameters**:
```java
@PathVariable Long[] jobLogIds
```

---

### 94. DELETE `/monitor/jobLog/clean`

**Method Name**: `clean`

**Content-Type**: `application/json`

---

