# Directory Traversal

### NGINX Misconfiguration

Missing `/` in `location` header
```cs
location /img {
    alias /data/images/;
}
```
`/img../x` points to `/data/x` instead of `/data/images/x`