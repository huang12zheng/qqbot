# how to use

`bj` someone
```
bj aa
JDquant  12:57:06
aa的被标记次数:3
```
`search`
```
805104533的情况是:
        受到伤害次数:7
        伤害者: ['805104533', 'bb', 'aa', 'cc']
        被标记次数: 1
        当日被标记次数: 1
        谁最伤害你:aa
        你当日的最大标记者是:aa
```

`swho` someone
```
sw 805104533
JDquant  13:02:11
805104533
            当日被伤害次数:1
            当日被标记次数: 1
```

----
# config change
* config.hjson
change follow in ../cqhttpxxx
```c
// QQ号
uin: xxxx
// QQ密码
password: "xxx"
reverse_url: ws://127.0.0.1:8080/cqhttp/ws
```

* docker-compose.yml
add config
> 876210974
> 6480
> 6380
```yaml
nonebot876210974:
    image: hzgood/docker-nb-cli
    env_file:
      - ".env.prod876210974" # fastapi 使用的环境变量文件
    # environment:
    #   - ENVIRONMENT=prod
    volumes:
      - "../cqhttp876210974:/app/cqhttp/"
    ports:
      - "8080:6480"
db876210974:
    image: redis
    ports:
      - 6379:6380
    volumes:
      - ./redis/data876210974:/data
      # - ./redis/conf/redis.conf:/usr/local/etc/redis/redis.conf
      - ./logs876210974:/logs
```
* .env.prod876210974
`REDIS_PORT=6380`
---

install-binary.sh