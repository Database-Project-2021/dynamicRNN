@echo on

call echo "Exporting Server.jar"
call ant -f server.xml
call echo "Exporting Client.jar"
call ant -f client.xml

call echo "Moving Jars"
call move server.jar "C:\Users\user\"
call move client.jar "C:\Users\user\"

call CD /D C:\Users\user\
call set mypath=%cd%
call echo %mypath%

call echo "Pushing Server.jar to The Remote Host"
scp -o "ProxyCommand=C:\Windows\System32\OpenSSH\ssh.exe -q -W %%h:%%p 140.114.88.21" -i ".ssh/bujo-plus" server.jar ccchen@netdb-bujoplus0:/home/ccchen/sychou/dynamic_RNN/data_collection/jars

call echo "Pushing Client.jar to The Remote Host"
scp -o "ProxyCommand=C:\Windows\System32\OpenSSH\ssh.exe -q -W %%h:%%p 140.114.88.21" -i ".ssh/bujo-plus" client.jar ccchen@netdb-bujoplus0:/home/ccchen/sychou/dynamic_RNN/data_collection/jars

call del "C:\Users\user\server.jar" "C:\Users\user\client.jar"