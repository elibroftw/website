openssl rsa -in elijahlopez.ca.key -out elijahlopez.ca.raw.key
heroku certs:add elijahlopez_ca.crt elijahlopez.ca.raw.key -a elijahlopez --bypass
