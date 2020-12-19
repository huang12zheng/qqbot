<!-- * git checkout xxx -->
<!-- > select with merge branch (keep version) -->

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
`REDIS_PORT=6W380`