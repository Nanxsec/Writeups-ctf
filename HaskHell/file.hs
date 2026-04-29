import System.IO

main :: IO ()
main = do
    contents <- readFile "/etc/passwd"
    putStrLn "Conteúdo de /etc/passwd:\n"
    putStrLn contents
