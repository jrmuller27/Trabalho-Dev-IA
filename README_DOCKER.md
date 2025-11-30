**README Docker: Como rodar a API em container (Windows + WSL2)**

Este documento descreve passos claros e copiados/colados para: diagnosticar o daemon Docker, ativar/integrar WSL2 quando necessário, construir a imagem e rodar o container que expõe a API FastAPI definida em `src.main:app`.

**Pré-requisitos**:
- **Windows**: privilégios de administrador para passos que alteram recursos do sistema.
- **Docker Desktop**: instalado (se não tiver, instale via https://www.docker.com/get-started).
- **Python/venv**: apenas necessário para desenvolvimento local; o container usa o `Dockerfile` do projeto.

**Visão rápida**:
- **Imagem**: gerada pelo `Dockerfile` presente na raiz.
- **Porta exposta**: `8000` (Uvicorn configura `--port 8000`).
- **Entrada da app**: `src.main:app` (veja `CMD` no `Dockerfile`).

**1) Checagens iniciais (PowerShell do Windows)**
Cole e rode no PowerShell (não no shell da distro):

```powershell
# Confere se o Windows tem o comando wsl
Get-Command wsl -ErrorAction SilentlyContinue

# Informações do Docker (pode falhar se o daemon estiver parado)
docker info

# Lista containers e imagens locais
docker ps -a
docker images
```

Se `docker info` retornar `Docker Desktop is unable to start` ou erro parecido, siga os passos abaixo.

**2) Reiniciar o backend WSL e Docker (PowerShell do Windows)**
Se você abriu um terminal WSL por engano e recebeu `wsl: command not found`, saia do shell da distro e rode isto no PowerShell do Windows:

```powershell
# Desliga todas as distribuições WSL (necessário para reiniciar o backend)
wsl --shutdown

# Fecha processos Docker Desktop (força parada) e reabre a GUI
Get-Process -Name "Docker Desktop","com.docker.backend" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Aguarde 10-20s e verifique
Start-Sleep -Seconds 15
docker info
```

Observações: se `wsl` não for reconhecido no PowerShell, execute o bloco do passo 3 (habilitar recursos).

**3) Habilitar/instalar WSL2 (PowerShell como Administrador)**
Se os logs do Docker indicam `wslUpdateRequired` ou `Subsistema do Windows para Linux não tem distribuições instaladas`, rode o seguinte como Administrador:

```powershell
# Habilita recursos necessários (Windows 10/11)
dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Reinicie o Windows se solicitado. Depois, instale uma distro (ex.: Ubuntu) usando:
wsl --install -d Ubuntu

# Define WSL2 como padrão
wsl --set-default-version 2

# Atualiza o kernel WSL se necessário
wsl --update
```

Se o seu Windows for mais antigo e não suportar `wsl --install`, instale uma distro pela Microsoft Store (pesquise "Ubuntu") após habilitar os recursos com `dism`.

**4) Ativar integração WSL no Docker Desktop (GUI)**
1. Abra Docker Desktop (Windows).
2. Vá em Settings → Resources → WSL Integration.
3. Marque sua distro instalada (ex.: `Ubuntu`) e clique em `Apply & Restart`.

Alternativa para checar via linha (após integração ativa):

```powershell
# Desliga WSL, reinicia o Docker Desktop e confirma
wsl --shutdown
Get-Process -Name "Docker Desktop","com.docker.backend" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Start-Sleep -Seconds 15
docker info
```

**5) Verificar que o `docker` funciona dentro da distro (opcional)**
No terminal da sua distro WSL (ou pelo PowerShell):

```powershell
# Substitua <DISTRIBUICAO> pelo nome obtido em `wsl -l -v`, ex: Ubuntu-22.04
wsl -d <DISTRIBUICAO> -- docker version
wsl -d <DISTRIBUICAO> -- docker info
```

Se o retorno for `docker: command not found`, certifique-se que a integração WSL no Docker Desktop está marcada e que o Docker foi reiniciado.

**6) Build da imagem e execução do container (quando Docker estiver OK)**
Abra PowerShell no diretório do projeto `C:\Users\vitor\Desktop\trabalho01-12` e cole:

```powershell
# Opcional: remover container antigo (se existir)
docker rm -f trabalho01_api 2>$null

# Build da imagem
docker build -t trabalho01_api:latest .

# Rodar em background mapeando porta 8000
docker run -d --name trabalho01_api -p 8000:8000 trabalho01_api:latest

# Verificar container e logs
docker ps --filter name=trabalho01_api
docker logs -f trabalho01_api
```

Testar a API (PowerShell):

```powershell
Invoke-RestMethod -Uri http://localhost:8000
# ou OpenAPI
Invoke-RestMethod -Uri http://localhost:8000/openapi.json
```

**7) Comandos úteis de manutenção / troubleshooting**
- Ver status do daemon e mensagens de erro:

```powershell
docker info
```

- Ver distribuições WSL instaladas:

```powershell
wsl -l -v
```

- Parar/limpar container ou imagem para rebuild:

```powershell
docker rm -f trabalho01_api
docker rmi trabalho01_api:latest
```

- Se o `docker build` falhar por causa de dependências nativas (ex.: `uvloop`), veja se `requirements.txt` tem condições de plataforma. Este projeto já evita instalar `uvloop` no Windows usando o marcador de plataforma:

```
uvloop; sys_platform != "win32"
```

Isso previne erro de compilação do `uvloop` no Windows.

**8) Notas finais / dicas rápidas**
- Muitos problemas do Docker Desktop em Windows têm relação com WSL2 não configurado ou com permissões; habilitar `VirtualMachinePlatform` + `Microsoft-Windows-Subsystem-Linux` e instalar uma distro normalmente resolve.
- Reiniciar o Windows após habilitar recursos é comum e pode ser necessário.
- Se preferir não usar WSL2, é possível configurar Docker com Hyper-V, mas a instrução acima segue o fluxo recomendado pela Docker Desktop (WSL2).

Se quiser, posso: (A) executar os comandos de verificação/`wsl --shutdown` aqui, (B) tentar reiniciar o Docker Desktop e depois reconstruir a imagem, ou (C) apenas ficar aguardando os resultados que você colar aqui. Diga o que prefere.
