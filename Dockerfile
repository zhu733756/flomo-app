FROM zhu733756/alpine-py3:3.14-gcc

# fix install wechat_sdk
RUN apk add --no-cache python3-dev 

WORKDIR /workdir
ADD ./flomo/ /workdir/

# RUN pip3 config set global.index-url http://mirrors.aliyun.com/pypi/simple
# RUN pip3 config set install.trusted-host mirrors.aliyun.com

RUN pip3 install -r /workdir/requirements.txt

EXPOSE 5000
CMD ["/workdir/app.py"]
ENTRYPOINT [ "python3"]