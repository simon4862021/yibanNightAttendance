# yibanNightAttendance-2021.10.18
使用python进行易班自动晚点签到，使用Actions的schedule实现自动化部署，并发送邮件到QQ邮箱进行通知，需配置secrets。<br>
ps：只有当在未签到状态下，才会进行签到并发送邮件，否则返回{'code': 500, 'msg': '非法签到', 'data': None}

## 食用方法
1、代码第26-27行为宿舍的经纬度和地址，具体需在secrets内进行配置<br>
2、代码第143-144行为自己的手机号和密码，具体需在secrets内进行配置<br>
3、工作流第7行配置执行时间，为UTC时间，国内需+8h<br>
4、工作流第48-49行为qq邮箱账号和smtp授权码，具体需在secrets内进行配置<br>
详细教程可参考博客：https://yonniye.com/archives/23.html

## Secrets详细配置
| Name              | Description                                |
| ----------------- | ------------------------------------------ |
| ADDRESS           | 地址全称                                    |
| LNGLAT            | 宿舍经纬度                                   |
| MAIL_PASSWORD     | QQ邮箱的smtp授权码        |
| MAIL_USERNAME     | QQ邮箱全称                                  |
| MOBILE            | 易班手机号                                  |
| PASSWORD          | 易班密码                                  |

## 参考资料
> https://hub.fastgit.org/rookiesmile/yibanAutoSgin <br>
> https://blog.csdn.net/TengWan_Alunl/article/details/105065966
