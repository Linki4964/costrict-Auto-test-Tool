# 若依系统后端接口安全测试报告

- **扫描时间**: `2025-12-05 16:25:19`
- **耗时**: `14.8 秒`
- **目标地址**: `http://192.168.236.141`
- **源码路径**: `D:\desktop\RuoYi-Vue`
- **发现接口数**: `117`

## 📊 测试概览

| 测试维度 | 通过数 | 总数 | 通过率 |
|----------|--------|------|--------|
| 正常请求成功 | 45 | 117 | 38.5% |
| 鉴权机制有效 | 114 | 117 | 97.4% |
| 健壮性良好 | 117 | 117 | 100.0% |

## ⚠️ 高风险接口（鉴权可能失效）

| 接口路径 | 完整 URL | 问题说明 |
|----------|----------|----------|
| `/captchaImage` | [http://192.168.236.141/prod-api/captchaImage](http://192.168.236.141/prod-api/captchaImage) | 无 Token 返回成功！; 无效 Token 返回成功！ |

## 📋 详细测试结果

| 接口路径 | 方法 | 正常 | 无 Token | 无效 Token | 健壮 | 备注 |
|----------|------|:----:|:--------:|:-----------:|:----:|------|
| `/captchaImage` | GET | ✅ | ❌ | ❌ | ✅ | 无 Token 返回成功！<br>无效 Token 返回成功！ |
| `/common/common` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/common/download` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/common/download/resource` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/common/upload` | POST | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/common/uploads` | POST | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/getInfo` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/getRouters` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/login` | POST | ❌ | ❌ | ❌ | ✅ | 业务错误 code=500<br>无 Token 返回成功！<br>无效 Token 返回成功！ |
| `/monitor/cache/clearCacheAll` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/cache/clearCacheKey/{cacheKey}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/cache/clearCacheName/{cacheName}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/cache/getKeys/{cacheName}` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/cache/getNames` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/cache/getValue/{cacheName}/{cacheKey}` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/cache/monitor/cache` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/monitor/job/changeStatus` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/job/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/job/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/job/monitor/job` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/monitor/job/run` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/job/{jobIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/jobLog/clean` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/jobLog/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/jobLog/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/jobLog/monitor/jobLog` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/monitor/jobLog/{jobLogIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/logininfor/clean` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/logininfor/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/logininfor/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/logininfor/monitor/logininfor` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/monitor/logininfor/unlock/{userName}` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/logininfor/{infoIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/online/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/online/monitor/online` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/monitor/online/{tokenId}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/operlog/clean` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/operlog/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/operlog/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/monitor/operlog/monitor/operlog` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/monitor/operlog/{operIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/monitor/server/monitor/server` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/register` | POST | ❌ | ❌ | ❌ | ✅ | 业务错误 code=500<br>无 Token 返回成功！<br>无效 Token 返回成功！ |
| `/system/config/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/system/config/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/config/refreshCache` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/config/system/config` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/config/{configIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/dept/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/dept/list/exclude/{deptId}` | GET | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/dept/system/dept` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/dept/{deptId}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/dict/data/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/system/dict/data/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/dict/data/system/dict/data` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/dict/data/{dictCodes}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/dict/type/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/system/dict/type/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/dict/type/optionselect` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/dict/type/refreshCache` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/dict/type/system/dict/type` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/dict/type/{dictIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/menu/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/menu/system/menu` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/menu/treeselect` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/menu/{menuId}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/notice/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/notice/system/notice` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/notice/{noticeIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/post/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/system/post/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/post/optionselect` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/post/system/post` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/post/{postIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/role/authUser/allocatedList` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/role/authUser/cancel` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/role/authUser/cancelAll` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/role/authUser/selectAll` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/role/authUser/unallocatedList` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/role/changeStatus` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/role/dataScope` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/role/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/system/role/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/role/optionselect` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/role/system/role` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/role/{roleIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/user/authRole` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/user/authRole/{userId}` | GET | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/user/changeStatus` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/user/deptTree` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/user/export` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/system/user/importData` | POST | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/user/importTemplate` | POST | ✅ | ✅ | ✅ | ✅ | - |
| `/system/user/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/system/user/profile/avatar` | POST | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/user/profile/system/user/profile` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/user/profile/updatePwd` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/user/resetPwd` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/system/user/system/user` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/system/user/{userIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/test/user/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/test/user/save` | POST | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/test/user/test/user` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/test/user/update` | PUT | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/test/user/{userId}` | GET | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/test/user/{userId}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/tool/gen/batchGenCode` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/tool/gen/createTable` | POST | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/tool/gen/db/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/tool/gen/download/{tableName}` | GET | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/tool/gen/genCode/{tableName}` | GET | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/tool/gen/importTable` | POST | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/tool/gen/list` | GET | ✅ | ✅ | ✅ | ✅ | - |
| `/tool/gen/preview/{tableId}` | GET | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/tool/gen/synchDb/{tableName}` | GET | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |
| `/tool/gen/tool/gen` | UNKNOWN | ❌ | ✅ | ✅ | ✅ | 状态码 404 |
| `/tool/gen/{tableIds}` | DELETE | ❌ | ✅ | ✅ | ✅ | 业务错误 code=500 |