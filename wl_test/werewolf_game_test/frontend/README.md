# nakama-js-test

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

# start 
./bin/cockroach start-single-node \
--listen-addr=0.0.0.0:26257 \
--http-addr=:9090 \
--insecure

nakama

nakama --database.address "root@127.0.0.1:26257"