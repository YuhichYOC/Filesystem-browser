### Filesystem-browser by Yuichi Yoshii is licensed under the Apache License, Version2.0

### メモ
* ファイル一式をディレクトリ「Filesystem-browser」に配置して docker compose up -d を実行すると、コンテナイメージ名が「filesystem-browser-filesystem-browser」に、コンテナ名が「filesystem-browser-filesystem-browser-1」になってしまう
* コンテナ起動時に docker compose -p <プロジェクト名> up -d とするとイメージ名・コンテナ名前半の filesystem-browser を別の名前に変えることができる