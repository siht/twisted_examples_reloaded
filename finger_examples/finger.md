# el ejemplo de finger

## que es finger
es un servicio que da la información de un usuario en un sistema. Si ejecutabas ```finger nail``` o ```finger nail@example.com``` te devolvía información de usuario nail. Algo como esto:

```
Login: nail                           Name: Nail Sharp
Directory: /home/nail                 Shell: /usr/bin/sh
Last login Wed Mar 31 18:32 2004 (PST)
New mail received Thu Apr  1 10:50 2004 (PST)
     Unread since Thu Apr  1 10:50 2004 (PST)
No Plan.
```

bueno, vamos a hacer algo similar, y tendrás que navegar commit por commit para ver que hacemos diferente, en este caso trataré de llevar la versión con deferred y la versión con async/await.

Primero vamos a hacer que no haga nada, o en todo caso que rechaze cualquier petición (por que no hay código que procese algo)