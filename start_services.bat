start "C:\Program Files\Docker\Docker\Docker Desktop.exe"
timeout /t 5
docker start NETutor_qdrant
docker logs -f NETutor_qdrant